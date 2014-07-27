from uuid import uuid4
from json import loads
#from hashlib import sha512
#from logging import log

from oauth2_errors import OAuth2Error
from abbrevi8_models.RedisWrapper import RedisWrapper


class Client(object):
    client = {}

    def __init__(self, client_id, client_secret, r_obj=None):
        self.r_obj = r_obj or RedisWrapper()
        self.client_id = client_id
        self.client_secret = client_secret

        if self.client_id and self.client_secret:
            self.profile_from_client()

    def __init__(self, email, r_obj=None):
        self.generate_client(email)

    def generate_client(self, email, ttl=3600):
        self.client_id = "client_id:{0}".format(uuid4().hex)
        value = '{"access_token": "%s", "token_type":""}' % (uuid4().hex,)
        self.r_obj.r_write.setex(name=self.client_id, value=value, time=ttl)

        # Associate client_id with user; and vice-versa
        self.associate_client(email=email, client_id=self.client_id)

        return self.client_id, value

    def profile_from_client(self):
        client_id = "client_id:{0}".format(self.client_id)
        read_pipe = self.r_obj.r_read.pipeline(transaction=True)
        read_pipe.multi()
        read_pipe.exists(name=client_id)
        read_pipe.get(name=client_id)
        read_pipe.ttl(name=client_id)
        results = read_pipe.execute(raise_on_error=False)

        if len(results) == 3:
            self.client = loads(results[0])
            self.client['tty'] = results[1]
            self.client['client_id'] = self.client_id
        else:
            raise OAuth2Error('unauthorized_client')

        return self.client

    @staticmethod
    def email_client_id(email):
        return "client_e:" + email

    @staticmethod
    def client_id_email(client_id):
        return "client_i:" + client_id

    def associate_client(self, email, client_id):
        """    redis.store(key='client_i:'+client_id, value=email)
            && redis.store(key='client_e:'+email, value=client_id) """
        write_pipe = self.r_obj.r_write.pipeline(transaction=True, shard_hint=None)
        write_pipe.multi()
        write_pipe.set(self.email_client_id(email), client_id)
        write_pipe.set(self.client_id_email(client_id), email)
        write_pipe.execute()


if __name__ == '__main__':
    pass
