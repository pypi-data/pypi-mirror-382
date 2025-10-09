import base64
import json
import urllib
import urllib.parse

from pyspark.sql import SparkSession

from langchain_community.chat_models import ChatDatabricks
from databricks_langchain import DatabricksEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from . import spark_client, databricks_client, ai_query, tenant_api, ai_rag
from .genie import get_genie_descriptions

class TenantClient:

    """
    A client for interacting with a specific tenant on a Kobai instance.
    """

    def __init__(self, tenant_name: str, uri: str, schema: str):

        """
        Initialize the TenantClient

        Parameters:
        tenant_name (str): The name of the tenant to access, as seen in the Kobai Studio UI.
        tenant_id (str): The numeric identifier for the tenant.
        uri (str): The base URI of the Kobai instance. (eg: "https://example.kobai.io")
        schema (str): The catalog-qualified schema used by Kobai Saturn for this tenant.
        """

        self.token = None
        self.tenant_name = tenant_name
        self.uri = uri
        self.schema = schema
        self.id = ""
        self.tenant_json = {}
        self.databricks_client = None
        self.spark_client = None
        self.api_client = tenant_api.TenantAPI(self.token, self.uri) #initial init before token acquired
        self.model_id = ""
        self.proxies = None
        self.ssl_verify = True
        self.question_search_index = None
        self.embedding_model = None
        self.chat_model = None


    def update_proxy(self, proxies: any):
        self.proxies = proxies
        self.__api_init_session()

    def update_ssl_verify(self, verify: str | bool):
        self.ssl_verify = verify
        self.__api_init_session()

    

########################################
# MS Entra Auth
########################################

    def use_browser_token(self, access_token):

        """
        Authenticate the TenantClient with the Kobai instance. Returns nothing, but stores bearer token in client.
        This is a fall-back method for instances not using OAuth. It is inconvenient as a Kobai Bearer Token must be retrieved from the users browser.

        Parameters:
        access_token (str): Bearer token for Kobai app session.
        """
        self._init_post_auth_success(access_token)

    def use_access_token(self, access_token: str, id_token: str = None,  tenant_id: str = None):

        """
        Authenticate the TenantClient with the Kobai instance. Returns nothing, but stores bearer token in client.

        Parameters:
        access_token (str): Access token of the IDM server to be used to obtained the kobai access token.
        id_token (str): ID token of the IDM server to be used to obtained the onbehalf access token.
        tenant_id (str): Kobai tenant id.
        """

        token_request_payload={
            "tenantName" : self.tenant_name,
            "tenantId" : tenant_id,
            "idToken" : id_token,
            "accessToken" : access_token
        }

        response = self.api_client._TenantAPI__run_post(
            '/user-mgmt-svcs/auth/oauth/external/onbehalf/token',
            token_request_payload
        )

        kb_access_token = response.headers.get('Authorization')
        self.use_browser_token(kb_access_token)

    def get_tenants(self, id_token: str = None):

        """
        Get the tenants associated with the given id token of the IDM. Returns tenants list.

        Parameters:
        id_token (str): ID token of the IDM server to be used to obtain user tenants.
        """

        if (id_token is not None) :
            token_request_payload={
                "idToken" : id_token
            }

            response = self.api_client._TenantAPI__run_post(
                '/user-mgmt-svcs/auth/oauth/external/token/tenants',
                token_request_payload
            )

            self.tenant_list = response.json()       
        return self.tenant_list

    def __api_init_session(self):
        self.api_client = tenant_api.TenantAPI(self.token, self.uri, verify=self.ssl_verify, proxies=self.proxies )

    def _init_post_auth_success(self, access_token):
        self.token = access_token
        self.__api_init_session()
        self.__set_tenant_solutionid()
        print("Authentication Successful.")

########################################
# Basic Config
########################################

    def __set_tenant_solutionid(self):
 
        response = self.api_client._TenantAPI__run_get("/data-svcs/solution")

        self.id = str(response.json()[0]["id"])
        self.model_id = str(response.json()[0]["modelId"])

    def __get_tenant_export(self) -> str:

        if self.id is None:
            return

        response = self.api_client._TenantAPI__run_get("/data-svcs/solutions/export/" + self.id)
        return response.json()

    def get_graph_uri(self):

        """
        Return the uri used for this Kobai tenant.
        """

        if self.tenant_json == {}:
            self.get_tenant_config()
        return self.tenant_json["model"]["uri"]

    def get_tenant_config(self):

        """
        Return tenant configuration JSON in dict.
        """

        tenant_decoded = self.__get_tenant_export()
        for dom in enumerate(tenant_decoded['domains']):
            if dom[1]['concepts'] is not None:
                conText = base64.b64decode(dom[1]['concepts']).decode('UTF-8')
                cons = json.loads(conText)
                tenant_decoded['domains'][dom[0]]['concepts'] = cons
        for query in enumerate(tenant_decoded['queries']):
            if query[1]['queryDefinition'] is not None:
                qDefText = base64.b64decode(query[1]['queryDefinition']).decode('UTF-8')
                qDef = json.loads(qDefText)
                tenant_decoded['queries'][query[0]]['queryDefinition'] = qDef
                qDefText = base64.b64decode(query[1]['runtimeDefinition']).decode('UTF-8')
                qDef = json.loads(qDefText)
                tenant_decoded['queries'][query[0]]['runtimeDefinition'] = qDef
        for queryC in enumerate(tenant_decoded['queryCalcs']):
            if queryC[1]['expression'] is not None:
                qDefText = base64.b64decode(queryC[1]['expression']).decode('UTF-8')
                qDef = qDefText
                tenant_decoded['queryCalcs'][queryC[0]]['expression'] = qDef
                qDefText = base64.b64decode(queryC[1]['argumentDefinition']).decode('UTF-8')
                qDef = json.loads(qDefText)
                tenant_decoded['queryCalcs'][queryC[0]]['argumentDefinition'] = qDef
        for viz in enumerate(tenant_decoded['visualizations']):
            if viz[1]['definition'] is not None:
                qDefText = base64.b64decode(viz[1]['definition']).decode('UTF-8')
                qDef = json.loads(qDefText)
                tenant_decoded['visualizations'][viz[0]]['definition'] = qDef
        #TODO: Not decoding data source conn props
        self.tenant_json = tenant_decoded
        return tenant_decoded

########################################
# Spark Functions
########################################

    def spark_init_session(self, spark_session: SparkSession):

        """
        Initialize a client allowing the SDK to use a Spark Session to execute Spark SQL commands, like creating tables and views.

        Parameters:
        spark_session (SparkSession): Your spark session (eg. of the notebook you are using)
        """

        self.spark_client = spark_client.SparkClient(spark_session)

    def __spark_check_init_status(self):
        if self.spark_client is None:
            print("Spark Client has not been initialized. Please run 'spark_init_session()'")
            return False
        else:
            return True

    def spark_generate_genie_views(self, domains = None, concepts = None, not_concepts=None, enforce_map=True):

        """
        Use the Spark Client to generate views for this tenant required to populate a Genie Data Room.
        """

        tables = self.__get_view_sql(domains=domains, concepts=concepts, not_concepts=not_concepts, enforce_map=enforce_map)
        for t in tables:
            #print(t["sql"])
            try:
                self.spark_client._SparkClient__run_sql(t["sql"])
            except Exception as e:
                print("Error creating view.", e)
                print(t["sql"])
        print("Updated " + str(len(tables)) + " views for Genie.")

    def spark_remove_genie_views(self):

        """
        Use the Spark Client to remove any views previously created for this tenant.
        """

        tables = self.__get_view_sql()
        for t in tables:
            self.spark_client._SparkClient__run_sql("DROP VIEW " + t["table"])
        print("Removed " + str(len(tables)) + " views.")


########################################
# Databricks Functions
########################################

    def databricks_init_notebook(self,  notebook_context, warehouse_id: str):

        """
        Initialize a client allowing the SDK to use a Databricks Notebook context to access configuration parameters required to call Databricks APIs.

        Parameters:
        notebook_context: Your notebook context. Suggestion: dbutils.notebook.entry_point.getDbutils().notebook().getContext()
        warehouse_id (str): Identifier for a Databricks SQL Warehouse. When resources are created that require compute to be configured (eg. Data Rooms), this warehouse will be used. 
        """

        self.databricks_client = databricks_client.DatabricksClient(notebook_context, warehouse_id)

    def databricks_build_genie(self, domains=None, concepts=None, not_concepts=None, enforce_map=True, add_questions=False):

        """
        Use the Databricks Client to create a Genie Data Room for this tenant.
        """
        data_rooms = self.databricks_client._DatabricksClient__api_get("/api/2.0/data-rooms")
        room_id = "-1"
        if data_rooms:
            for dr in data_rooms["data_rooms"]:
                if dr["display_name"] == self.tenant_name:
                    room_id = dr["id"]

        payload = {"display_name":self.tenant_name,"description":"Genie for Kobai tenant " + self.tenant_name,"stage":"DRAFT","table_identifiers":[],"warehouse_id":self.databricks_client.warehouse_id,"run_as_type":"VIEWER"}
        if room_id == "-1":
            response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms", payload)
            room_id = response["id"]

        for t in self.__get_view_sql(domains=domains, concepts=concepts, not_concepts=not_concepts, enforce_map=enforce_map):
            payload["table_identifiers"].append(t["table"])
            print(t["table"])
        response = self.databricks_client._DatabricksClient__api_patch("/api/2.0/data-rooms/" + room_id, payload)

        payload = {"title":"Notes","content":"When filtering for a named entity, use a like comparison instead of equality. All tables are denormalized, so columns may have repeated rows for the same primary identifier. You should handle this by putting each table in a subquery and using the DISTINCT keyword. The first column in each view is a unique identifier that should only be used for joins, and never shown to a user. Find another column to identify the subject of the table.","instruction_type":"TEXT_INSTRUCTION"}
        instructions = self.databricks_client._DatabricksClient__api_get("/api/2.0/data-rooms/" + room_id + "/instructions")
        inst_id = "-1"

        question_titles = {}

        if instructions:
            for i in instructions["instructions"]:
                if i["title"] == "Notes":
                    inst_id = i["id"]
                if i["instruction_type"] == "SQL_INSTRUCTION":
                    question_titles[i["title"]] = i["id"]

            response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions/" + inst_id, payload)
        else:
            response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions", payload)


        if add_questions:
            print("Finding questions")
            remaining_questions = 5
            questions = self.__get_questions()
            for question in questions:
                payload = {"title": question["name"], "content": question["sql"], "instruction_type": "SQL_INSTRUCTION"}

                inst_id = "-1"
                if question["name"] in question_titles:
                    inst_id = question_titles[question["name"]]
                    response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions/" + inst_id, payload)
                else:
                    response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions", payload)
                remaining_questions = remaining_questions - 1
                if remaining_questions < 1:
                    break

        print("Done creating your Data Room. You can access it here: https://" + self.databricks_client.workspace_uri + "/data-rooms/rooms/" + room_id)

########################################
# Semantic Profile
########################################

    def __get_descriptions(self):

        tenant_config = self.get_tenant_config()
        descriptions = get_genie_descriptions(self.model_id, tenant_config, self.schema)
        return descriptions

    def __get_view_sql(self, domains=None, concepts=None, not_concepts=None, enforce_map=True):
        sql_list = []
        descriptions = self.__get_descriptions()
        
        for dom in descriptions["domains"]:
            for con in dom["concepts"]:
                hasProps = False
                hasRels = False
                hasEither = False
                if "properties" in con and len(con["properties"]) > 0:
                    hasProps = True
                if "relations" in con and len(con["relations"]) > 0:
                    hasRels = True
                if hasProps or hasRels:
                    hasEither = True
                con_label = dom["name"] + "_" + con["label"]
                out_table = con["schema_table"].replace(".data_", ".genie_").replace("_np", "")
                sql = "CREATE OR REPLACE VIEW " + out_table + " "
                sql += "(" + con_label + " COMMENT '" + con["schema_id_sentence"] + "' "
                if hasEither:
                    sql += ", "
                from_sql = "(SELECT DISTINCT _conceptid, p1 FROM " + con["schema_table"] + ") AS " + dom["name"] + "_" + con["label"] + "_ID "
                as_sql = "SELECT DISTINCT " + con_label + "_ID._conceptid " + con_label
                if hasEither:
                    as_sql += ", "
                as_props = []
                top_props = []
                for prop in con["properties"]:
                    prop_label = con_label + "_" + prop["label"]
                    prop_name = self.model_id + "/" + prop["uri"].split("/")[-2] + "/" + prop["uri"].split("/")[-1]
                    from_sql += "LEFT JOIN " + con["schema_table"] + " AS " + prop_label + " ON " + prop_label + ".type='l' AND " + prop_label + ".name='" + prop_name + "' AND " + prop_label + ".scenario='' AND " + con_label + "_ID.p1=" + prop_label + ".p1 AND " + con_label + "_ID._conceptid=" + prop_label + "._conceptid "
                    as_props.append(prop_label + ".value " + prop_label)
                    top_props.append(prop_label + " COMMENT '" + prop["schema_sentence"] + "'")
                for prop in con["relations"]:
                    prop_label = con_label + "_" + prop["label"]
                    prop_name = self.model_id + "/" + prop["uri"].split("/")[-2] + "/" + prop["uri"].split("/")[-1]
                    from_sql += "LEFT JOIN " + con["schema_table"] + " AS " + prop_label + " ON " + prop_label + ".type='r' AND " + prop_label + ".name='" + prop_name + "' AND " + prop_label + ".scenario='' AND " + con_label + "_ID.p1=" + prop_label + ".p1 AND " + con_label + "_ID._conceptid=" + prop_label + "._conceptid "
                    as_props.append(prop_label + ".value " + prop_label)
                    top_props.append(prop_label + " COMMENT '" + prop["schema_sentence"].replace("_w", "").replace(".data_", ".genie_") + "'")
                as_sql += ", ".join(as_props)
                as_sql += " FROM " + from_sql
                sql += ", ".join(top_props) + ") "
                sql += "COMMENT '" + con["schema_sentence"].replace("_w", "").replace(".data_", ".genie_") + "' "
                sql += "AS " + as_sql


                if not_concepts is not None:
                    if con["label"] in not_concepts:
                        continue

                concept_added = False
                if domains is None and concepts is None:
                    if enforce_map and con["map_count"] > 0:
                        sql_list.append({"table": out_table, "sql": sql})
                
                if domains is not None:
                    if dom["name"] in domains:
                        if enforce_map and con["map_count"] > 0:
                            concept_added = True
                            sql_list.append({"table": out_table, "sql": sql})
                        else:
                            concept_added = True
                            sql_list.append({"table": out_table, "sql": sql})
                if concepts is not None:
                    if con["label"] in concepts and not concept_added:
                        if enforce_map and con["map_count"] > 0:
                            sql_list.append({"table": out_table, "sql": sql})
                        else:
                            sql_list.append({"table": out_table, "sql": sql})

        return sql_list

    def __get_questions(self):
        
        #response = self.api_client._TenantAPI__run_get("/episteme-svcs/api/questions")

        #tenant_config = self.get_tenant_config()
        #questions = get_genie_questions(self.id, tenant_config)

        #return_questions = []
        #for q in questions:
        #    sql = q["sql"]
        #    sql = sql[2:-2]
        #    sql = sql.replace(".data_", ".genie_").replace("_Literals", "").replace("_w", "")
        #    return_questions.append({"name": q["name"], "sql": sql})

        #return return_questions
        return []
    
########################################
# RAG Functions
########################################

    def get_ai_context(self):
        context = ai_rag.AIContext()
        context.model_id = self.model_id
        context.schema = self.schema
        context.tenant_json = self.get_tenant_config()
        context.spark_session = self.spark_client.spark_session
        context.api_client = self.api_client
        return context

    def rag_generate_sentences(self, replica_schema=None, concept_white_list=None, use_questions=False, debug=False):
        """
        Extract Semantic Data from Graph to Delta Table

        Parameters:
        replica_schema (str) OPTIONAL: An alternate schema (catalog.database) to create the Delta table. Useful when the base Kobai schema is not on a Unity Catalog.
        concept_white_list ([str]) OPTIONAL: A list of Domain and Concept names for extraction.
        use_questions (bool) OPTIONAL: Extract facts from published Kobai questions. 
        """
        ai_rag.generate_sentences(self.get_ai_context(), replica_schema=replica_schema, concept_white_list=concept_white_list, use_questions=use_questions, debug=debug)

    def rag_encode_to_delta_local(self, st_model: Embeddings, replica_schema=None, batch_size=100000):
        """
        Encode Semantic Data to Vectors in Delta Table

        Parameters:
        st_model (SentenceTransformer): A sentence_transformers model to use for encoding.
        replica_schema (str) OPTIONAL: An alternate schema (catalog.database) to create the Delta table. Useful when the base Kobai schema is not on a Unity Catalog.
        """
        ai_rag.encode_to_delta_local(self.get_ai_context(), st_model=st_model, replica_schema=replica_schema, batch_size=batch_size)

    def rag_delta(self, emb_model: Embeddings, chat_model: BaseChatModel, question, k=5, replica_schema=None):
        """
        Run a RAG query using vectors in Delta table.

        Parameters:
        emb_model (UNION[SentenceTransformer, Embeddings]): A sentence_transformers or langchain embedding model to use for encoding the query.
        chat_model (BaseChatModel): A langchain chat model to use in the RAG pipeline.
        question (str): The user's query.
        k (int) OPTIONAL: The number of RAG documents to retrieve.
        replica_schema (str) OPTIONAL: An alternate schema (catalog.database) to create the Delta table. Useful when the base Kobai schema is not on a Unity Catalog.
        """
        return ai_rag.rag_delta(self.get_ai_context(), emb_model=emb_model, chat_model=chat_model, question=question, k=k, replica_schema=replica_schema)

########################################
# AI Functions
########################################

    def followup_question(self, user_question, question_id=None, use_inmem_vectors=False, k=50, dynamic_filters: dict = None):
        """
        Use LLM to answer question in the context of a Kobai Studio question.

        Parameters:
        user_question (str): A natural language question to apply.
        question_id (int) OPTIONAL: A Kobai question to use as a data source. Otherwise, an appropriate question will be automatically found.
        use_inmem_vectors (bool) OPTIONAL: For large query sets, this secondary processing can reduce the data required in the context window.
        """

        if question_id is None:
            suggestions = self.question_search(user_question, k=1)
            question_id = suggestions[0]["id"]
        
        question_results = self.run_question_remote(question_id, dynamic_filters=dynamic_filters)

        question_def = self.get_question(question_id)
        question_name = question_def["description"]

        return ai_query.followup_question(user_question, question_results, question_name, question_def, self.embedding_model, self.chat_model, use_inmem_vectors=use_inmem_vectors, k=k)

    def init_ai_components(self, embedding_model: Embeddings, chat_model: BaseChatModel):
        """
        Set Chat and Embedding models for AI functions to use. If no arguments provided, Databricks hosted services are used.

        Parameters:
        embedding_model (Embeddings): A Langchain Embedding model.
        chat_model (BaseChatModel): A Langchain BaseChatModel chat model.
        """
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.question_search_index = ai_query.init_question_search_index(self.list_questions(), self.embedding_model)

    def question_search(self, search_text, k: int = 1):
        """
        Retrieve metadata about Kobai Questions based on user search text.

        Parameters:
        search_text (str): Text to compare against question names.
        k (int) OPTIONAL: Number of top-k matches to return.
        """

        question_list = ai_query.question_search(search_text, self.question_search_index, self.embedding_model, k)
        return question_list



########################################
# Tenant Questions
########################################

    def run_question_remote(self, question_id, dynamic_filters: dict = None):

        """
        Returns JSON formatted result of Kobai question.

        Parameters:
        question_id (int): Numeric identifier of Kobai question.
        """

        uri = '/data-svcs/api/query/' + str(question_id) + '/execute?' #'/data-svcs/api/query/4518/solution/9/execute/tabular?'

        queryParams = {'jsontype': 'tableau'}

        if bool(dynamic_filters):
            queryParams.update(dynamic_filters)

        uri += urllib.parse.urlencode(queryParams)

        json={
                'simulations': {'concepts': {}, 'data': None}
                }
        response = self.api_client._TenantAPI__run_post(uri, json)

        return response.json()
    
    def run_question_remote_spark(self, question_id, dynamic_filters: dict = None, schema=None):

        """
        Returns result of Kobai question in PySpark Dataframe.

        Parameters:
        question_id (int): Numeric identifier of Kobai question.
        """

        if not self.__spark_check_init_status():
            return None

        question_data = self.run_question_remote(question_id, dynamic_filters)

        if question_data is None:
            return None
        else:
            return self.spark_client._SparkClient__get_df(question_data)


########################################
# Tenant CRUD
########################################

    #DOMAINS

    def create_domain(self, label, color="#6EA6B6"):

        """
        Create Kobai domain.

        Parameters:
        label (string): Label for new domain.
        """

        self.api_client._TenantAPI__run_post(
            '/data-svcs/model/domain',
            {
                'name': label,
                'color': color
            }
        )

    def list_domains(self):

        """
        Return JSON list of Kobai domains with label and identifier.
        """

        return self.api_client._TenantAPI__run_get(
            '/data-svcs/model/domain'
        ).json()
    
    def get_domain_id(self, label):

        """
        Return domain identifier given label.

        Parameters:
        label (string): Label for domain.
        """

        domain_json = self.list_domains()
        for d in domain_json:
            if label.lower() == d["name"].lower():
                return d["id"]
        print("Domain not found")
        return None


    #CONCEPTS

    def create_concept(self, domain_label, label):

        """
        Create Kobai concept.

        Parameters:
        domain_label (string): Label for domain to place concept.
        label (string): Label for new concept.
        """

        domain_id = self.get_domain_id(domain_label)
        if domain_id is None:
            return None
        
        self.api_client._TenantAPI__run_post(
            '/data-svcs/model/domain/' + str(domain_id) + '/concept',
            {
                'inheritedConcepts': [],
                'label': label,
                'uri': 'http://kobai/b67e36ec-b9d2-43ce-9d73-f106aae4572c/AssetModel/' + domain_label + '#' + label
                }
        )

    def get_model(self):

        """
        Return entire Kobai model in JSON format.
        """

        return self.api_client._TenantAPI__run_get(
            '/data-svcs/model/domain/all'
        ).json()

    #PROPERTY

    def create_property(self, domain_label, concept_label, label, data_type):

        """
        Create Kobai property.

        Parameters:
        domain_label (string): Label of domain containing new property.
        concept_label (string): Label of concept containing new property.
        label (string): Label for new property.
        data_type (string): One of "string", "dateTime", "boolean", "number"
        """

        domain_id = self.get_domain_id(domain_label)
        if domain_id is None:
            raise Exception("domain not found")
        
        #had issues upgrading to python 3.10, but would much rather have a MATCH here
        if data_type == "string":
            data_type_url = 'http://www.w3.org/2001/XMLSchema#string'
        elif data_type == "dateTime":
            data_type_url = 'http://www.w3.org/2001/XMLSchema#dateTime'
        elif data_type == "boolean":
            data_type_url = 'http://www.w3.org/2001/XMLSchema#boolean'
        elif data_type == "number":
            data_type_url = 'http://www.w3.org/2001/XMLSchema#number'
        else:
            raise Exception("invalid data type")

        uri = '/data-svcs/model/domain/' + str(domain_id) + '/concept/property?'
        queryParams = {'conceptUri': 'http://kobai/b67e36ec-b9d2-43ce-9d73-f106aae4572c/AssetModel/' + domain_label + "#" + concept_label}

        uri += urllib.parse.urlencode(queryParams)

        self.api_client._TenantAPI__run_post(
            uri,
            {
                'dataClassTags': [],
                'label': label,
                'propTypeUri': data_type_url,
                'uri': 'http://kobai/b67e36ec-b9d2-43ce-9d73-f106aae4572c/AssetModel/' + domain_label + '/' + concept_label + '#' + label
                }
        )
        
    #DATA SOURCE

    def create_data_source(self, label, catalog, schema, token):

        """
        Create Databricks schema as Kobai Data Source.

        Parameters:
        label (string): Label for new data source
        catalog (string): Databricks catalog name.
        schema (string): Databricks schema name.
        token (string): Databricks PAT with access to schema.
        """

        existing = self.list_data_sources()
        for d in existing["unUsed"]:
            if label.lower() == d["name"].lower():
                print("Data source already exists")
                return
        for d in existing["used"]:
            if label.lower() == d["name"].lower():
                print("Data source already exists")
                return


        if self.databricks_client is None:
            print("Initialize Databricks notebook client first")
            return
        
        connection_url = f"""jdbc:databricks://{self.databricks_client.workspace_uri}:443;transportMode=http;ssl=1;AuthMech=3;httpPath=/sql/1.0/warehouses/{self.databricks_client.warehouse_id};UserAgentEntry=KobaiSDK;ConnCatalog={catalog};ConnSchema={schema};"""

        self.api_client._TenantAPI__run_post(
            '/data-svcs/dataSource',
            {
                'connectionUrl': connection_url,
                'dataSourceType': 11,
                'id': None,
                'ingestionSchedule': [],
                'name': label,
                #'password': self.databricks_client.token,
                'password': token,
                'props': {},
                'userName': self.databricks_client.user_name
                }
        )

    def list_data_sources(self):

        """
        Return JSON list of Kobai data sources.
        """

        return self.api_client._TenantAPI__run_get(
            '/data-svcs/dataSource'
        ).json()
    
    def delete_data_source(self, label):

        """
        Remove Kobai data source.

        Parameters:
        label (string): Label of data source to remove.
        """

        existing = self.list_data_sources()
        for d in existing["used"]:
            if label.lower() == d["name"].lower():
                print("Data source is used and cannot be deleted")
                return
        for d in existing["unUsed"]:
            if label.lower() == d["name"].lower():
                data_source_id = d["id"]
               
                response = self.api_client._TenantAPI__run_delete('/data-svcs/dataSource/' + str(data_source_id))
                return
        print("Data source does not exist")
        return


    #QUESTION

    def create_question(self, label, definition={}):

        """
        Create Kobai question.

        Parameters:
        label (string): Name for new question.
        def (Kobai question def) OPTIONAL: Definition JSON for new question. If not specified, empty question created. 
        """

        self.api_client._TenantAPI__run_post(
            '/data-svcs/queries',
            {
                'definition': definition,
                'description': label,
                'id': None,
                'runtimeParams': {"limit": None, "sort": []},
                'solutionId': None,
                'tsParams': {}
                }
        )

    def __list_domain_questions(self, domain_id):
        
        return self.api_client._TenantAPI__run_get(
            '/data-svcs/queries/model/domain/' + str(domain_id)
        ).json()

    def list_questions(self, domain_label=None):

        """
        Return JSON list of Kobai questions with name and identifier.

        Parameters:
        domain_label (str) OPTIONAL: Domain label to filter.
        """

        question_list = []

        if domain_label is not None:
            domain_id = self.get_domain_id(domain_label)
            if domain_id is None:
                return None
            
            response = self.__list_domain_questions(domain_id)
            
            if response is None:
                print("Failed to get questions for domain", domain_label)
            else:
                for q in response:
                    question_list.append({"id": q["id"], "description": q["description"]})
        else:
            
            for d in self.list_domains():
                response = self.__list_domain_questions(d["id"])

                if response is None:
                    print("Failed to get questions for domain", d["name"])
                else:
                    for q in response:
                        question_list.append({"id": q["id"], "description": q["description"]})
            
            response = self.api_client._TenantAPI__run_get('/data-svcs/model/domain/questions/count')
            for q in response.json()["drafts"]:
                question_list.append({"id": q["id"], "description": q["description"]})

        visited_ids = []
        unique_question_list = []
        for q in question_list:
            if q["id"] not in visited_ids:
                visited_ids.append(q["id"])
                unique_question_list.append(q)
        return unique_question_list
    
    def get_question_id(self, label, domain_label=None):

        """
        Helper function to get numeric identifier for Kobai question by name.

        Parameters:
        label (str): Question name to search.
        domain_label (str) OPTIONAL: Domain label to filter.
        """

        question_json = self.list_questions(domain_label)
        if question_json is not None:
            for d in question_json:
                if label.lower() == d["description"].lower():
                    return d["id"]
            
        question_json = self.list_questions()
        for d in question_json:
            if label.lower() == d["description"].lower():
                return d["id"]
        print("Question not found")
        return None
    

    def get_question(self, question_id):
        
        """
        Returns standard Kobai definition of question in JSON format.

        Parameters:
        question_id: Numeric identifier of Kobai question.
        """

        return self.api_client._TenantAPI__run_get(
            '/data-svcs/queries/' + str(question_id)
        ).json()

    def update_question(self, question_id, label, definition):

        """
        Create Kobai question.

        Parameters:
        question_id (int): Numeric identifier of Kobai question to modify
        label (string): Name for question.
        def (Kobai question def): Updated definition JSON for new question.
        """
        
        self.api_client._TenantAPI__run_put(
            '/data-svcs/queries/' + str(question_id),
            {
                'definition': definition,
                'description': label,
                'id': question_id,
                'removalConfirmed': False,
                'runtimeParams': {"limit": None, "sort": [], "calcs": None},
                'solutionId': self.id,
                'tsParams': {}
                }
        )

    #MAPPING

    def add_data_set(self, question_id, datasource_label, table_name):

        """
        Create Kobai dataset.

        Parameters:
        question_id (int): Identifier of Kobai question to attach dataset.
        datasource_label (string): Label of datasource to use.
        table_name (string): Name of table to use from specified datasource.
        """
        data_source_id = 0
        existing_datasource = self.list_data_sources()
        for d in existing_datasource["used"]:
            if datasource_label.lower() == d["name"].lower():
                data_source_id = d["id"]
                
        for d in existing_datasource["unUsed"]:
            if datasource_label.lower() == d["name"].lower():
                data_source_id = d["id"]

        uri = '/data-svcs/dataSet/query/' + str(question_id) + '/solution/' + str(self.id) + '/dataSource/' + str(data_source_id) + '/?'
        query_params = {'tableName': table_name, 'columnName': -1, 'selected': "true"}
        uri += urllib.parse.urlencode(query_params)

        self.api_client._TenantAPI__run_put(
            uri,
            {}
        )

    def list_data_sets(self, question_id):

        """
        Return JSON list of Kobai datasets for given question
        
        Parameters:
        question_id (int): Question identifier to search.
        """
    
        return self.api_client._TenantAPI__run_get(
            '/data-svcs/dataSet/query/' + str(question_id) + '/solution/' + str(self.id)
        ).json()
    
    def add_mapping(self, question_id, definition={}):

        """
        Create Kobai mapping.

        Parameters:
        question_id (int): Identifier for question.
        definition (Kobai mapping def) OPTIONAL: Definition JSON for new mapping. If not specified, empty mapping created. 
        """

        self.api_client._TenantAPI__run_put(
            '/data-svcs/mapping/query/' + str(question_id) + '/solution/' + str(self.id) + '/defs',
            definition
        )


    #clear tenant
    def clear_tenant(self):

        """
        Restore tenant to empty configuration.
        """

        EMPTY_TENANT_JSON = """
        {
            "solutionId": 84,
            "model": {
                "name": "AssetModel",
                "uri": "http://kobai/b67e36ec-b9d2-43ce-9d73-f106aae4572c/AssetModel"
            },
            "tenantId": "b67e36ec-b9d2-43ce-9d73-f106aae4572c",
            "dataAccessTags": [],
            "conceptAccessTags": [],
            "dataSources": [],
            "dataSets": [],
            "domains": [],
            "collections": [],
            "visualizations": [],
            "queries": [],
            "mappingDefs": [],
            "dataSourceFileKeys": [],
            "apiQueryProfiles": [],
            "collectionVizs": [],
            "collectionVizOrders": [],
            "queryDataTags": [],
            "queryCalcs": [],
            "dataSourceSettings": [],
            "publishedAPIs": [],
            "scenarios": []
        }
        """

        self.api_client._TenantAPI__run_post(
            '/data-svcs/solution/snapshot/import/upload',
            {'file': EMPTY_TENANT_JSON}
        )
