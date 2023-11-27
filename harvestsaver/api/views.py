from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from farm.models import Product, Equipment
from .serializers import ProductSerializer

class ProductAPIView(APIView):
    def get(self, request):
        data = Product.objects.all()
        serializer = ProductSerializer(data, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

