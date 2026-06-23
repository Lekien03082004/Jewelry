from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from my_jewelry.models import Product
from orders.models import Order, OrderItem
from .models import Review

class ReviewService:
    
    @staticmethod
    def can_review(user, product_id: int)->bool:
        """
        User chỉ được review nếu có ít nhất 1 đơn hàng:
        - status = DELIVERED
        - chứa product này trong order_items
        """
        return Order.objects.filter(
            order__user = user,
            order__status = Order.STATUS_CHOICES.DELIVERED,
            product_id=product_id
            ).exists()
        
        
    @staticmethod
    def create_review(user, product_id: int, rating: int, comment: str="")->Review:
        if Review.objects.filter(user, product_id).exists():
            raise ValueError('Bạn đã review sản phẩm này rồi.')
        
        if not ReviewService.can_review(user, product_id):
            raise PermissionError('Bạn cần phải mua sản phẩm này thì mới được review')
        
        product= get_object_or_404(Product, pk=product_id)
        
        return Review.objects.create(user=user, product_id=product_id, rating=rating, comment=comment)
    
    @staticmethod
    def update_review(user, review_id:int, rating: int=None, comment: str=None)->Review:
        review = get_object_or_404(Review, pk=review_id, user=user)
        if rating is not None:
            review.rating = rating
        if comment is not None: 
            review.comment = comment
        
        review.save(update_fields=['comment', 'rating', 'created_at'])
        
        return review
    
    @staticmethod
    def delete_review(user, review_id: int)->None:
        review = get_object_or_404(Review, pk=review_id, user=user)
        review.save()
        
    def get_product_reviews(product_id: int):
        return Review.objects.filter(product_id=product_id, is_active=True).select_related('user')
    
    @staticmethod
    def get_product_rating_summary(product_id: int) -> dict:
        """Tính rating trung bình + tổng số review — dùng cho trang chi tiết sản phẩm."""
        result = Review.objects.filter(
            product_id=product_id, is_active=True
        ).aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id'),
        )
        return {
            "average_rating": round(result['average_rating'] or 0, 1),
            "total_reviews": result['total_reviews'],
        }
        