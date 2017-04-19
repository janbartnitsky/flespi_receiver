import io
import urllib3

""" This module is pulled out from auto-generated swagger python client for flespi gateway"""


class ApiException(Exception):

    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """
        Custom error messages for exception
        """
        error_message = "({0})\n"\
                        "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(
                self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message


class RESTResponse(io.IOBase):

    def __init__(self, resp):
        self.urllib3_response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = resp.data

    def getheaders(self):
        """
        Returns a dictionary of the response headers.
        """
        return self.urllib3_response.getheaders()

    def getheader(self, name, default=None):
        """
        Returns a given response header.
        """
        return self.urllib3_response.getheader(name, default)


def get_messages_request(flespi_recv_obj, query_params):
    headers = {}

    headers['Authorization'] = flespi_recv_obj.auth_header
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    try:
        r = flespi_recv_obj.pool_manager.request('GET', flespi_recv_obj.target_url,
                                                 fields=query_params,
                                                 headers=headers)
    except urllib3.exceptions.SSLError as e:
        msg = "{0}\n{1}".format(type(e).__name__, str(e))
        raise ApiException(status=0, reason=msg)

    r = RESTResponse(r)
    r.data = r.data.decode('utf8')

    if r.status != 200:
        raise ApiException(http_resp=r)

    return r
