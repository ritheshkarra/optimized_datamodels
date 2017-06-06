import falcon
import json


class Crossdomain(object):
    def process_response(self, req, resp, resource):
        resp.set_header('Access-Control-Allow-Origin', '*')  # Change in prod
        resp.set_header('Access-Control-Allow-Methods',
                        'GET, PUT, POST, DELETE')
        resp.set_header('Access-Control-Allow-Credentials', 'true')
        resp.set_header(
            'Access-Control-Allow-Headers',
            'Origin, Authorization, Content-Type, X-Requested-With')

class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')

        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token):
            description = (token)

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token):
        if token == "Basic Z2VvY29kZTpaWGFzcXcxMg==":
            return True
        else:
            return False  # Suuuuuure it's valid...

class JSONTranslator(object):
    def process_request(self, req, resp):
        if req.content_length in (None, 0):
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest(
                'Malformed JSON',
                'Could not decode the request body. The '
                'JSON was incorrect or not encoded as '
                'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])
