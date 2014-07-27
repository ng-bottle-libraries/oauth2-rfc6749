dict(unauthorized_client=dict(error_description="The authenticated client is not authorized to use"
                                                "this authorization grant type.",
                              status_code=403))


class OAuth2Error(Exception):
    """
    [RFC6749 - Section:] 4.1.2.1.  Error Response
    If the request fails due to a missing, invalid, or mismatching
    redirection URI, or if the client identifier is missing or invalid,
    the authorization server SHOULD inform the resource owner of the
    error and MUST NOT automatically redirect the user-agent to the
    invalid redirection URI.

    Usage:
        raise OAuth2Error(<error>, ...)
        OR
        OAuth2Error.<error>   # Provides dictionary
    """

    unauthorized_client = dict(error_description="The client is not authorized to request "
                                                 "an authorization code using this method.",
                               status_code=401)

    access_denied = dict(error_description="The resource owner or authorization server denied the request.",
                         status_code=412)

    unsupported_response_type = dict(error_description="The authorization server does not support "
                                                       "obtaining an authorization code using this method.",
                                     status_code=501)

    invalid_scope = dict(error_description="The requested scope is invalid, unknown, or malformed.",
                         status_code=403)

    server_error = dict(error_description="The authorization server encountered an unexpected "
                                          "condition that prevented it from fulfilling the request.",
                        status_code=500)

    temporarily_unavailable = dict(
        error_description="The authorization server is currently unable to handle the request "
                          "due to a temporary overloading or maintenance of the server.",
        status_code=503)

    invalid_request = dict(
        error_description="The request is missing a required parameter, includes an invalid parameter value, "
                          "includes a parameter more than once, or is otherwise malformed.",
        status_code=412)

    # [RFC6749 - Section:] 5.2 [access token subsection]
    invalid_client = dict(error_description="Client authentication failed (e.g., unknown client, "
                                            "no client authentication included, or unsupported authentication method).",
                          status_code=401)

    invalid_grant = dict(
        error_description="The provided auth grant or refresh token is invalid, expired, revoked, mismatches"
                          "the redirect_uri used in the auth request, or was issued to another client.",
        status_code=400)

    unsupported_grant_type = dict(
        error_description="The authorization grant type is not supported by the authorization server.",
        status_code=501)

    # not in standard
    expired_token = dict(error_description="Access Token has expired. To continue, please generate a new one.",
                         status_code=419)

    def __init__(self, error, error_description=None, error_uri=None, state=None, status_code=None):
        """ Supports OAuth2Error( ... ) syntax; use this one for `raise`ing errors """

        errors = [x for x in dir(self) if x not in ('message', 'args') and '__' not in x]
        if not error in errors:
            raise KeyError("Error type '{0}' not supported, use one of: {1}".format(error, errors))

        error_description = error_description or getattr(self, error, error_description)['error_description']

        self.message = self.response = {'error': error, 'error_description': error_description,
                                        'status_code': getattr(self, error, status_code)['status_code']}

        if error_uri:
            dict(self.message).update({'error_uri': error_uri})
        if state:
            dict(self.message).update({'state': state})

    def __repr__(self):
        return repr(self.message)


def throw_invalid_request_on_key_error(dictionary, req_key):
    if not dictionary.get(req_key, False):
        raise OAuth2Error('invalid_request', "`{0}` required".format(req_key))


def error(resp, err, error_description=None):
    """ Helper to promote DRY in bottle apps, and others which support resp.status syntax """
    error_resp = OAuth2Error.__dict__[err].copy()
    resp.status = error_resp.pop('status_code')
    return {'error': err, 'error_description': error_description or error_resp}


if __name__ == '__main__':
    from pprint import PrettyPrinter

    pp = PrettyPrinter(indent=4).pprint
    try:
        raise OAuth2Error('invalid_request', 'bar')
    except OAuth2Error as e:
        pp(e)
