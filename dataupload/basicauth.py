from django.conf import settings
from django.shortcuts import render_to_response

#remember to set [WSGIPassAuthorization On] in apache, otherwise authorization headers are not forwarded to django!


class BasicAuthMiddleware(object):

    @classmethod
    def unauthed(cls):
        response = render_to_response('dataupload/unauthed.html')
        response['WWW-Authenticate'] = 'Basic realm="ClimAtlas"'
        response.status_code = 401
        return response

    @classmethod
    def process_request(cls, request):
        if not 'HTTP_AUTHORIZATION' in request.META:
            
            return cls.unauthed()
        else:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth) = authentication.split(' ', 1)
            if 'basic' != authmeth.lower():
                return cls.unauthed()
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            if username == settings.BASICAUTH_USERNAME and password == settings.BASICAUTH_PASSWORD:
                return None
            
            return cls.unauthed()
