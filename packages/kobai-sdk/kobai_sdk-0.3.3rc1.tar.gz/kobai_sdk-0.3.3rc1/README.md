# Kobai SDK for Python (Alpha)

Alpha: This SDK is not currently supported for production use while we stabilize the interface.

The Kobai SDK for Python includes functionality to accelerate development with Python on the Kobai Semantic Layer. It does not cover all Kobai Studio features, but rather focuses on integrating a Kobai tenant with data science and AI activities on the backend.

## Getting Started

This exercise demonstrates using the Kobai SDK to create a Databricks "Genie" Data Room environment, enabling users to interact with Kobai data in an AI Chat interface.

1. Please install Kobai SDK for Python via `pip install kobai-sdk`, gather some configuration details of the Kobai instance and tenant to connect to, and instantiate `TenantClient`:

```python
from kobai import tenant_client, spark_client, databricks_client

schema = 'main.demo'
uri = 'https://demo.kobai.io'
tenant_name = 'My Demo Tenant'
k = tenant_client.TenantClient(tenant_name, uri, schema)
```

2. Authenticate with the Kobai instance:
Authentication can be performed using different methods, such as device code flow, on-behalf-of flow, or browser-based tokens.

#### Authentication via device code
Step 1: Obtain the access token from IDM (Identity and Access Management)

```python
from kobai import ms_authenticate

tenant_id = 'your_Entra_directory_id_here'
client_id = 'your_Entra_app_id_here'

access_token = ms_authenticate.device_code(tenant_id, client_id)
```

Step 2: Use the token to retrieve the list of Kobai tenants (unless the tenant ID is already known).

```python
tenants = k.get_tenants(id_token=access_token)
print(tenants)
```

Step 3: Authenticate with Kobai for the specific tenant using the IDM access token.

```python
kobai_tenant_id = "5c1ba715-3961-4835-8a10-6f6f963b53ff"
k.use_access_token(access_token = access_token, tenant_id=kobai_tenant_id)
```

At this point, authentication to the Kobai tenant is successfully completed.

#### Authentication via browser token

```python
k.use_browser_token(access_token="KOBAI_ACESS_TOKEN_FROM_BROWSER")
```

#### Authentication via on-behalf-of flow
The sample code demonstrating authentication via the on-behalf-of flow will be provided, if requested.

3. Initialize a Spark client using your current `SparkSession`, and generate semantically-rich SQL views describing this Kobai tenant:

```python
k.spark_init_session(spark)
k.spark_generate_genie_views()
```

4. Initialize a Databricks API client using your Notebook context, and create a Genie Data Rooms environment for this Kobai tenant.

```python
notebook_context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
sql_warehouse = '8834d98a8agffa76'

k.databricks_init_notebook(notebook_context, sql_warehouse)
k.databricks_build_genie()
```

## AI Functionality
The Kobai SDK enables users to ask follow-up questions based on the results of previous queries. This functionality currently supports models hosted on Databricks and Azure OpenAI. 

#### Prerequisites
Before asking a follow-up question, ensure that you have instantiated the TenantClient and completed the authentication process.

#### Steps to Ask a Follow-Up Question

1. List Questions: Retrieve the questionId or questionName. You can list all questions or filter by domain.

```python
k.list_questions() # List all questions
k.list_domains() # To get the domain labels
k.list_questions(domain_label="LegoCollecting") # List questions by domain
```

2. Ask a Question: Use either the questionId or questionName to submit your query.

```python
question_json = k.run_question_remote(2927) # By questionId
kobai_query_name = "Set ownership"
question_json = k.run_question_remote(k.get_question_id(kobai_query_name)) # By questionName
```

3. Ask a Follow-Up Question: Based on the initial results, you can ask a follow-up question using the user-provided chat and embedding model.

#### Using Databricks Embeddings and Chat Models in a Databricks Notebook
Initialize the AI components by specifying the embedding and chat models, then proceed with follow-up questions for interactive engagement.

```python
from databricks_langchain import DatabricksEmbeddings
from langchain_community.chat_models import ChatDatabricks
import json

# choose the embedding and chat model of your choice from the databricks serving and initialize.
embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")
chat_model = ChatDatabricks(endpoint="databricks-gpt-oss-20b")
k.init_ai_components(embedding_model=embedding_model, chat_model=chat_model)

followup_question = "Which owner owns the most sets?"
output = k.followup_question(followup_question, question_id=k.get_question_id(kobai_query_name))
print(output)
```

#### Using Azure OpenAI Embeddings and Chat Models

```python
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import json

followup_question = "Which owner owns the most sets?"

embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-3-small",
    azure_endpoint="https://kobaipoc.openai.azure.com/",
    api_key="YOUR_API_KEY",
    openai_api_version="2023-05-15"
)

chat_model = AzureChatOpenAI(
azure_endpoint="https://kobaipoc.openai.azure.com/", azure_deployment="gpt-4o-mini",
api_key = "YOUR_API_KEY",
openai_api_version="2024-02-15-preview",
temperature=0.5, 
max_tokens=150,)

k.init_ai_components(embedding_model=embedding_model, chat_model=chat_model)

followup_question = "Which theme has the most sets?"
output = k.followup_question(followup_question, question_id=k.get_question_id(kobai_query_name))
print(output)
```

## Limitations

This version of the SDK is limited to use in certain contexts, as described below:

- Authentication is limited to MS Entra AD.
- Functionality limited to Databricks Notebook environments at this time.
