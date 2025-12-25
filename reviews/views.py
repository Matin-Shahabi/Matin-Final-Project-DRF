from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListCreateAPIView
from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer

class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"



class ReviewListCreateAPIView(ListCreateAPIView):
    queryset = Review.objects.all().order_by("-id")
    pagination_class = ReviewPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewListSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
