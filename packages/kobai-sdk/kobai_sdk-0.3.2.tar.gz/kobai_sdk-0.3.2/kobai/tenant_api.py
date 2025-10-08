import requests

class TenantAPI:

    """
    A client holding an authenticated Kobai session to execute CRUD functions on Kobai configuration.
    """

    def __init__(self, token: str, base_uri: str, verify: str | bool = True, proxies: any = None):

        """
        Initialize the TenantAPI client.
        
        Parameters:
        token (str): Kobai application bearer token.
        """
        self.token = token
        self.base_uri = base_uri
        self.session = requests.Session()

        if token is not None:
            if token.startswith('Bearer'):
                 self.session.headers.update({'Authorization': '%s' % self.token})
            else:
                self.session.headers.update({'Authorization': 'Bearer %s' % self.token})

        self.ssl_verify = verify
        self.session.verify = verify
        if proxies is not None:
            self.session.proxies = proxies

    def __run_post(self, uri, payload, op_desc=None):

        """
        Run a POST call against the authenticated API session.

        Parameters:
        uri (string): Relative service URI to call
        payload (any): Dict to pass to "json" service parameter.
        """

        if op_desc is None:
            op_desc = "operation"

        response = self.session.post(
            self.base_uri + uri,
            #headers={'Authorization': 'Bearer %s' % self.token},
            json=payload,
            verify=self.ssl_verify,
            timeout=5000
        )
        if response.status_code != 200:
            print(response)
            raise Exception(op_desc +" failed")
        return response
    
    def __run_post_files(self, uri, files, op_desc=None):

        """
        Run a POST call against the authenticated API session.

        Parameters:
        uri (string): Relative service URI to call
        payload (any): Dict to pass to "json" service parameter.
        """

        if op_desc is None:
            op_desc = "operation"

        response = self.session.post(
            self.base_uri + uri,
            #headers={'Authorization': 'Bearer %s' % self.token},
            files=files,
            verify=self.ssl_verify,
            timeout=5000
        )
        if response.status_code != 200:
            print(response)
            raise Exception(op_desc +" failed")
        return response
    
    def __run_put(self, uri, payload, op_desc=None):

        """
        Run a POST call against the authenticated API session.

        Parameters:
        uri (string): Relative service URI to call
        payload (any): Dict to pass to "json" service parameter.
        """

        if op_desc is None:
            op_desc = "operation"

        response = self.session.put(
            self.base_uri + uri,
            #headers={'Authorization': 'Bearer %s' % self.token},
            json=payload,
            verify=self.ssl_verify,
            timeout=5000
        )
        if response.status_code != 200:
            print(response)
            raise Exception(op_desc +" failed")
        return response

    def __run_get(self, uri, params=None, op_desc=None):

        """
        Run a GET call against the authenticated API session.

        Parameters:
        uri (string): Relative service URI to call
        """

        if op_desc is None:
            op_desc = "operation"
        
        response = self.session.get(
            self.base_uri + uri,
            params=params,
            #headers={'Authorization': 'Bearer %s' % self.token},
            verify=self.ssl_verify,
            timeout=5000
        )
        if response.status_code != 200:
            print(response)
            raise Exception(op_desc + " failed")
        return response
    
    def __run_delete(self, uri, op_desc=None):

        """
        Run a DELETE call against the authenticated API session.

        Parameters:
        uri (string): Relative service URI to call
        """

        if op_desc is None:
            op_desc = "operation"

        response = self.session.delete(
            self.base_uri + uri,
            #headers={'Authorization': 'Bearer %s' % self.token},
            verify=self.ssl_verify,
            timeout=5000
        )
        if response.status_code != 200:
            print(response)
            raise Exception(op_desc + " failed")
        return response