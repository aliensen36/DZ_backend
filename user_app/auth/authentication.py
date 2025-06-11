from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'JWT authentication failed: {str(e)}')



# def verify_jwt(request):
#     """Проверка JWT в заголовке Authorization."""
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith('Bearer '):
#         logger.error("Missing or invalid Authorization header")
#         return None
#
#     token = auth_header.split(' ')[1]
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         return payload
#     except jwt.ExpiredSignatureError:
#         logger.error("JWT has expired")
#         return None
#     except jwt.InvalidTokenError:
#         logger.error("Invalid JWT")
#         return None