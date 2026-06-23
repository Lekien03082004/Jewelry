from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Review
from .serializers import ReviewSerializer
from .service import ReviewService
# Create your views here.

class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """GET /reviews/?product_id=1 — public, ai cũng xem được."""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id is required!'}, status=status.HTTP_400_BAD_REQUEST)
        reviews = ReviewService.get_product_reviews(product_id)
        summary = ReviewService.get_product_rating_summary(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response({
            'summary': summary,
            'results': serializer.data
        })
        
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny]
        return [IsAuthenticated]
    
    def create(self, request):
        serializer = ReviewSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            review = ReviewService.create_review(
                user=request.user,
                product_id=serializer.validated_data['product_id'],
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', ''),
            )
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({ReviewSerializer(review).data}, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        ReviewService.delete_review(user=request.user, review_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, pk=None):
        try:
            review = ReviewService.update_review(
                user=request.user,
                review_id=pk,
                rating=request.data.get('rating'),
                comment=request.data.get('comment')
            )
        except ValueError as e:
            return Response({'detail': str(e)},status=status.HTTP_400_BAD_REQUEST)
        return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def can_review(self, request):
        """GET /reviews/can_review/?product_id=1 — để UI biết hiện/ẩn nút Viết review."""
        product_id = request.query_params.get('product_id')
        allowed = ReviewService.can_review(request.user, product_id=product_id)
        already_reviewed = Review.objects.filter(
            user=request.user, product_id=product_id
        ).exists()
        return Response({
            'can_review': allowed and not already_reviewed,
            'already_reviewed': already_reviewed
        })