from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import CollegeAuthToken


class CollegeTokenAuthentication(BaseAuthentication):
    keyword = b'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        if auth[0] != self.keyword:
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')

        if len(auth) > 2:
            raise AuthenticationFailed('Invalid token header.')

        token_key = auth[1].decode('utf-8')

        try:
            token = CollegeAuthToken.objects.select_related('college').get(key=token_key)
        except CollegeAuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        return (token.college, token)