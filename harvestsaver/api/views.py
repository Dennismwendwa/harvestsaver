from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Q

from farm.models import Product, Equipment
from .serializers import ProductSerializer, ProductDetailSerilizer


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


class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"},
                            status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductDetailSerilizer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"},
                            status=status.HTTP_404_NOT_FOUND)


class ProductSearchAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ["name", "price", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("query", None)
        if query:
            queryset = queryset.filter(Q(name__icontains=query) |
                                       Q(price__icontains=query) |
                                       Q(description__icontains=query)
                                       )
        return queryset
        
