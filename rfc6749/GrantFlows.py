from rfc6749.oauth2_errors import OAuth2Error, throw_invalid_request_on_key_error
from rfc6749.Tokens import AccessToken


class GrantFlow(object):
    @staticmethod
    def error_on_inequality(lhs, rhs, error='access_denied'):
        def decorate(f):
            def wrapped(*args, **kwargs):
                if kwargs.get(lhs, '') != rhs:
                    raise OAuth2Error(error, "`{0}` must be: '{1}'".format(lhs, rhs))
                return f(*args, **kwargs)

            return wrapped

        return decorate

    def __init__(self, **kwargs):
        throw_invalid_request_on_key_error(kwargs, 'grant_type')

        self.response = {'code': AuthorizationCode,
                         'token': Implicit,
                         'password': ResourceOwnerPasswordCredentials,
                         'client_credentials': ClientCredentials}[kwargs['grant_type']](**kwargs)
        # 'response_type')

    def generate_access_token(self, **kwargs):
        self.response = AccessToken(**kwargs).response


class AuthorizationCode(GrantFlow):
    """
    [RFC6749 - Section:] 4.1.  Authorization Code Grant
    The authorization code grant type is used to obtain both access
    tokens and refresh tokens and is optimized for confidential clients.
    [...] this is a redirection-based flow [...]
    """

    @GrantFlow.error_on_inequality('response_type', "code")
    def __init__(self, **kwargs):
        # kwargs: response_type, client_id, redirect_uri=None, scope=None, state=None

        throw_invalid_request_on_key_error(kwargs, 'client_id')
        super(AuthorizationCode, self).generate_access_token(**kwargs)


class Implicit(GrantFlow):
    """
    [RFC6749 - Section:] 4.2.  Implicit Grant
    The implicit grant type is used to obtain access tokens (it does not
    support the issuance of refresh tokens) and is optimized for public
    clients known to operate a particular redirection URI.
    [...] this is a redirection-based flow [...]
    """

    @GrantFlow.error_on_inequality('response_type', "token")
    def __init__(self, **kwargs):
        # response_type, client_id, redirect_uri=None, scope=None, state=None
        throw_invalid_request_on_key_error(kwargs, 'client_id')
        super(Implicit, self).generate_access_token(**kwargs)


class ResourceOwnerPasswordCredentials(GrantFlow):
    """
    [RFC6749 - Section:] Resource Owner Password Credentials Grant
    The resource owner password credentials grant type is suitable in
    cases where the resource owner has a trust relationship with the
    client, such as the device operating system or a highly privileged
    application.  The authorization server should take special care when
    enabling this grant type and only allow it when other flows are not
    viable.
    """

    @GrantFlow.error_on_inequality('grant_type', "password")
    def __init__(self, **kwargs):
        # grant_type, email, password, scope=None

        if not kwargs.get('grant_type') or not kwargs.get('email') or not kwargs.get('password'):
            raise OAuth2Error('invalid_request', "This grant type requires: "
                                                 "['grant_type':'password', 'email':'', 'password':'']")
        super(ResourceOwnerPasswordCredentials, self).generate_access_token(**kwargs)


class ClientCredentials(GrantFlow):
    """
    [RFC6749 - Section:] 4.4.  Client Credentials Grant
    The client can request an access token using only its client
    credentials (or other supported means of authentication) when the
    client is requesting access to the protected resources under its
    control, or those of another resource owner that have been previously
    arranged with the authorization server [...]
    """

    @GrantFlow.error_on_inequality('grant_type', "client_credentials")
    def __init__(self, grant_type, scope=None):
        super(ClientCredentials, self).generate_access_token(grant_type=grant_type, scope=scope)
