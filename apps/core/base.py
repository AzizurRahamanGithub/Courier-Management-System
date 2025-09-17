from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BaseAPIView(APIView):
    
    def success_response(self, message="Thank you for your request", data=None, status_code=status.HTTP_200_OK):
        return Response(
            {
                "success": True,
                "message": message,
                "status_code": status_code,
                "data": data if data is not None else {}
            }, 
            status=status_code
        )
        
    def error_response(self, message="I am sorry for your request", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "success": False,
                "message": message,
                "status_code": status_code,
                "data": data if data is not None else {}
            }, 
            status=status_code
        )
