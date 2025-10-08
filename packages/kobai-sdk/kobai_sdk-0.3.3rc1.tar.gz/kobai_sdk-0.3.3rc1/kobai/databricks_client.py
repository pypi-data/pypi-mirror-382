import requests

class DatabricksClient:

    """
    A client allowing the SDK to use a Databricks Notebook context to access configuration parameters required to call Databricks APIs.
    """

    def __init__(self, notebook_context, warehouse_id: str):

        """
        Initialize the DatabricksClient

        Parameters:
        notebook_context: Your notebook context. Suggestion: dbutils.notebook.entry_point.getDbutils().notebook().getContext()
        warehouse_id (str): Identifier for a Databricks SQL Warehouse. When resources are created that require compute to be configured (e.g., Data Rooms), this warehouse will be used. 
        """

        print("Initializing Databricks Notebook Context")
        self.notebook_context = notebook_context
        self.workspace_uri = notebook_context.browserHostName().getOrElse(None)
        self.token = notebook_context.apiToken().getOrElse(None)
        self.user_name = notebook_context.userName().getOrElse(None)
        self.warehouse_id = warehouse_id

    def __api_get(self, uri):
        response = requests.get(
            'https://%s%s' % (self.workspace_uri, uri),
            headers={'Authorization': 'Bearer %s' % self.token},
            json = {},
            timeout=5000
        )
        if response.status_code != 200:
            print(response.status_code)
        return response.json()

    def __api_post(self, uri, payload):
        response = requests.post(
            'https://%s%s' % (self.workspace_uri, uri),
            headers={'Authorization': 'Bearer %s' % self.token},
            json = payload,
            timeout=5000
        )
        if response.status_code != 200:
            print(response.status_code)
        return response.json()
    
    def __api_patch(self, uri, payload):
        response = requests.patch(
            'https://%s%s' % (self.workspace_uri, uri),
            headers={'Authorization': 'Bearer %s' % self.token},
            json = payload,
            timeout=5000
        )
        if response.status_code != 200:
            print(response.status_code)
        return response.json()
