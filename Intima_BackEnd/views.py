from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]  # This ensures only authenticated users can access

    def get(self, request):
        return Response({"message": "This is your profile!"})
