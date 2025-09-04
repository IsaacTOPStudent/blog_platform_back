from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView


from .models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LogOutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token is None:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist() # add to blacklist

            return Response({'message': 'Successful Logout'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



""" 
class LogOutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            #block refresh token
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            #block access token
            access_token = request.auth #Authorization header
            if access_token:
                token = AccessToken(str(access_token))
                #mark it as revoked in database 
                jti = token['jti']

                try:
                    outstanding = OutstandingToken.objects.get(jti=jti)
                    BlacklistedToken.objects.get_or_create(token=outstanding)
                except OutstandingToken.DoesNotExist:
                    pass

            return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
"""



