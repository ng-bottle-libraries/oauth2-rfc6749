from __future__ import print_function
from uuid import uuid4
from sys import stderr

from mongoengine import connect, Document
from mongoengine.fields import StringField, ReferenceField
from mongoengine.connection import ConnectionError
from oauth2_errors import OAuth2Error

try:
    connect('namespace_users')
except ConnectionError:
    print("Could not connect to MongoDB", file=stderr)


class AccessToken(Document):
    """
    [RFC6749 - Section:] 1.4. Access Token
    Access tokens are credentials used to access protected resources.
    An access token is a string representing an authorization issued to the client.
    """

    user = ReferenceField('User', required=True)
    token = StringField()
    grant_type = StringField()

    '''
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 1814000}  # 3.1 weeks
        ]
    }
    '''

    generate = (lambda self, force_insert=False, validate=True, clean=True,
                       write_concern=None, cascade=None, cascade_kwargs=None,
                       _refs=None, **kwargs: self.save(force_insert, validate, clean,
                                                       write_concern, cascade, cascade_kwargs,
                                                       _refs, **kwargs))

    # grant_type, code, redirect_uri, client_id
    def clean(self):
        """ Generate an access token """
        self.token = uuid4().hex

        # if self.grant_type == 'refresh_token':
        # response = self.generate_with_refresh("")

    def __nonzero__(self):
        return bool(self.token)

    @staticmethod
    def email_from_token(access_token):
        """ Returns the last generated access_token, else None """
        tok = AccessToken.objects(token=access_token).first()
        if not tok:
            return
        return tok.user.email

    @staticmethod
    def token_from_email(email):
        """ Returns the last generated access_token, else None """
        from namespace_models.User import User

        return AccessToken.objects(user=User.objects(email=email).first()).first()

    @staticmethod
    def generate_with_refresh(self, refresh_token):
        raise NotImplemented
        # return dict(access_token=self.access_token, expires_in='')

    def invalidate(self, access_token):
        """ Logout user """
        from namespace_models.User import User

        user = User.objects(email=self.email_from_token(access_token)).first()
        if not user:
            return False
        AccessToken.objects(user=user).delete()
        return True


class RefreshToken(Document):
    """[...] long-lasting credentials used to request additional access tokens [...]"""
    user = ReferenceField('User', required=True)
    token = StringField()

    generate = (lambda self, force_insert=False, validate=True, clean=True,
                       write_concern=None, cascade=None, cascade_kwargs=None,
                       _refs=None, **kwargs: self.save(force_insert, validate, clean,
                                                       write_concern, cascade, cascade_kwargs,
                                                       _refs, **kwargs))

    def clean(self):
        self.token = uuid4().hex

    def old__init__(self, grant_type, refresh_token, scope=None):
        if grant_type != "refresh_token":
            raise OAuth2Error('access_denied', "`grant_type` must be: 'refresh_token'")

        response = AccessToken(grant_type=grant_type, refresh_token=refresh_token, scope=scope)


class AuthorizationToken:
    """
    [RFC6749 - Section:] 4.1.2.  Authorization Response
    If the resource owner grants the access request, the authorization
    server issues an authorization code and delivers it to the client
    """

    def __init__(self, **kwargs):
        self.response = self.generate(**kwargs)

    def generate(self, **kwargs):
        return dict(code='', state='', status_code=302)
