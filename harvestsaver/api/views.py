from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import User
from farm.models import Product, Equipment, Review
from .serializers import ProductSerializer, ProductDetailSerilizer
from .serializers import EquipmentSerializer, OwnerSerializer
from .serializers import ProductReviewSerializer, ReviewSerializer


class ProductAPIView(APIView):
    """Retrives all or creates product instances"""
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
    """Retrives or updates a single product instance"""
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
    """Retrives all matching product instances"""
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
        

@api_view(["GET"])
def equipment_list(request):
    """List all equipments"""
    if request.method == "GET":
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        return Response(serializer.data)


@api_view(["GET", "PUT", "DELETE"])
def equipment_detail(request, pk):
    """Retrives/deletes or updates a single equipment instance"""
    try:
        equipment = Equipment.objects.get(pk=pk)
    except Equipment.DoesNotExist:
        print("error from equipment get")
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = EquipmentSerializer(equipment)
        return Response(serializer.data)
    
    elif request.method == "DELETE":
        equipment.delete()
        return Response({"detail": "Equipment deleted successfully"},
                        status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = EquipmentSerializer(equipment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def equipment_search(request):
    """Retrives all matches of the query string"""
    query = request.GET.get("query", "")
    
    if not query:
        return Response({"detail": "Query parameter 'query' is required"},
                         status=status.HTTP_400_BAD_REQUEST)
    queryset = Equipment.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query)
    )

    serializer = EquipmentSerializer(queryset, many=True)
    return Response(serializer.data)


class userAPIView(APIView):
    """Retrives all or creates new user instances"""
    def get(self, request):
        users = User.objects.filter(is_farmer=True)
        serializer = OwnerSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = OwnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class userDetailView(APIView):
    """Retrives or updates user instances"""
    def get(self, request, pk):
        try:
            farmer = User.objects.get(pk=pk, is_farmer=True)
            serializer = OwnerSerializer(farmer)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"},
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            farmer = User.objects.filter(pk=pk, is_farmer=True).first()
            serializer = OwnerSerializer(farmer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"errors": "User not found"},
                            status=status.HTTP_404_NOT_FOUND)



class productreviews(generics.RetrieveUpdateAPIView):
    """Retirves all reviews for a product"""
    queryset = Product.objects.all()
    serializer_class = ProductReviewSerializer
    lookup_url_kwarg = "pk"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    
    def post(self, request, *args, **kwargs):
        product = self.get_object()

        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(product=product, customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
