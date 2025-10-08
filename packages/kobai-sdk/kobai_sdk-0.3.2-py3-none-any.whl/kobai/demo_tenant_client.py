import json
import base64

from pyspark.sql import SparkSession
from azure.storage.blob import BlobClient

from . import spark_client, databricks_client

class DemoTenantClient:

    """
    A client for interacting with Kobai's public demo tenants.
    """

    def __init__(self, schema: str, tenant_name: str = "demo1", demo_catalog: str = "kobai_demo"):

        """
        Initialize the DemoTenantClient

        Parameters:
        schema (str): The schema where the SDK should create objects, such as Genie views.
        tenant_name (str): The name of the tenant to access, as seen in the Kobai Studio UI.
        demo_catalog (str): The catalog you assigned to Kobai from the Databricks Marketplace.
        """

        self.tenant_name = tenant_name
        self.schema = schema
        self.demo_schema = demo_catalog + ".marketplace"
        self.id = ""
        self.tenant_json = {}
        self.spark_client = None
        self.databricks_client = None

########################################
# Basic Config
########################################

    def get_tenant_config(self):

        """
        Return tenant configuration JSON in dict
        """

        tenant_export = self.__get_tenant_export()
        tenant_decoded = json.loads(tenant_export)
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
# Demo Data
########################################

    def __get_tenant_solutionid(self):
        demo_df = self.spark_client._SparkClient__get_sql(f"""SELECT id FROM {self.demo_schema}.demos WHERE name='{self.tenant_name}'""")
        self.id = str(demo_df.collect()[0]["id"])
        return self.id

    def __get_tenant_sas(self):
        demo_df = self.spark_client._SparkClient__get_sql(f"""SELECT json_sas FROM {self.demo_schema}.demos WHERE name='{self.tenant_name}'""")
        return demo_df.collect()[0]["json_sas"]

    def __get_tenant_export(self):
        source_json_sas = self.__get_tenant_sas()
        blob_client = BlobClient.from_blob_url(blob_url=source_json_sas)
        blob_download = blob_client.download_blob()
        blob_content = blob_download.readall().decode("utf-8")
        return blob_content

    def __get_view_sql(self):
        tenant_id = self.__get_tenant_solutionid()
        view_df = self.spark_client._SparkClient__get_sql(f"""SELECT  table_name, genie_create_view FROM {self.demo_schema}.demo_tables WHERE demo_id={tenant_id}""")
        views = view_df.collect()
        return views

    def __get_question_view_sql(self):
        tenant_id = self.__get_tenant_solutionid()
        view_df = self.spark_client._SparkClient__get_sql(f"""SELECT  table_name, create_view FROM {self.demo_schema}.demo_questions WHERE demo_id={tenant_id}""")
        views = view_df.collect()
        return views

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

    def spark_generate_genie_views(self):

        """
        Use the Spark Client to generate views for this tenant required to populate a Genie Data Room.
        """
        tables = self.__get_view_sql()
        for t in tables:
            ct = t["genie_create_view"].replace("main.marketplace.genie", f"""{self.schema}.genie""")
            ct = ct.replace("main.marketplace.data", f"""{self.demo_schema}.data""")
            ct = ct.replace("CREATE VIEW", "CREATE OR REPLACE VIEW")
            self.spark_client._SparkClient__run_sql(ct)
        print("Updated " + str(len(tables)) + " views for Genie.")

    def spark_generate_question_views(self):

        """
        Use the Spark Client to generate views for this tenant required to populate a Genie Data Room.
        """
        tables = self.__get_question_view_sql()
        for t in tables:
            ct = t["create_view"].replace("main.marketplace.pub", f"""{self.schema}.pub""")
            ct = ct.replace("main.marketplace.data", f"""{self.demo_schema}.data""")
            ct = ct.replace("CREATE VIEW", "CREATE OR REPLACE VIEW")
            self.spark_client._SparkClient__run_sql(ct)
        print("Updated " + str(len(tables)) + " views for Questions.")


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

    def databricks_build_genie(self):

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

        for t in self.__get_view_sql():
            #table_name = t["table_name"].replace("_np", "").replace("main.marketplace.genie", f"""{self.schema}.genie""")
            table_name = self.schema + "." + t["table_name"].replace("data_", "genie_").replace("_np", "")
            payload["table_identifiers"].append(table_name)
        response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id, payload)

        payload = {"title":"Notes","content":"When filtering for a named entity, use a like comparison instead of equality.","instruction_type":"TEXT_INSTRUCTION"}
        instructions = self.databricks_client._DatabricksClient__api_get("/api/2.0/data-rooms/" + room_id + "/instructions")
        inst_id = "-1"
        if instructions:
            for i in instructions["instructions"]:
                if i["title"] == "Notes":
                    inst_id = i["id"]

            response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions/" + inst_id, payload)
        else:
            response = self.databricks_client._DatabricksClient__api_post("/api/2.0/data-rooms/" + room_id + "/instructions", payload)

        print("Done creating your Data Room. You can access it here: https://" + self.databricks_client.workspace_uri + "/data-rooms/rooms/" + room_id)
