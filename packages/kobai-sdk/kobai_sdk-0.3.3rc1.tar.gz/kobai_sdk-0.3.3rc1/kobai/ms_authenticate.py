from azure.identity import DeviceCodeCredential
from azure.identity import OnBehalfOfCredential
from azure.core.exceptions import AzureError

def get_scope(client_id: str = None, target_client_id: str = None, scope: str = None):

    """
    Get the default scopes 

    Parameters:
    client_id (str): Client ID or Application ID from app registration with IDM.
    target_client_id (str): Kobai IDM client ID.
    scope (str): Scope to be passed
    """
    if scope is not None:
        return scope

    if target_client_id is None:
        target_client_id = client_id

    return f"openid profile offline_access api://{target_client_id}/Kobai.Access"

def device_code(tenant_id: str, client_id: str, target_client_id: str = None, scope: str = None):

    """
    Authenticate using the device code flow and get the access token

    Parameters:
    tenant_id (str): Tenant ID or Directory ID for IDM.
    client_id (str): Client ID or Application ID from app registration with IDM.
    target_client_id (str): Kobai IDM client ID.
    scope (str): Scope to be passed
    """
    credential = DeviceCodeCredential(client_id=client_id, tenant_id=tenant_id)

    try:
        token = credential.get_token(get_scope(client_id, target_client_id, scope))
        return token.token
    except AzureError as e:
        return e

def onbehalf(tenant_id: str, client_id: str, client_secret: str, access_token: str, target_client_id: str = None, scope: str = None):

    """
    Authenticate using the onbehalf flow and get the access token

    Parameters:
    tenant_id (str): Tenant ID or Directory ID for IDM.
    client_id (str): Client ID or Application ID from app registration with IDM.
    client_secret (str): Client secret from app registration with IDM.
    access_token (str): Access token to be exchanged.
    target_client_id (str): Kobai IDM client ID.
    scope (str): Scope to be passed
    """
    credential = OnBehalfOfCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        user_assertion=access_token
    )

    try:
        token = credential.get_token(get_scope(client_id, target_client_id, scope))
        return token.token
    except AzureError as e:
        return e
