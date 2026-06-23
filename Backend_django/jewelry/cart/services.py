# Service là nơi chứa logic nghiệp vụ
from django.shortcuts import get_object_or_404
from my_jewelry.models import Product
from .models import Cart, CartItem

class CartService:
    
    @staticmethod
    def get_or_create_cart(user)->Cart:
        # lấy giỏ hàng nếu không có thì tạo
        cart, _= Cart.objects.get_or_create(user=user) #(cart trả về object, _=created = True hoặc False)
        return cart
    
    @staticmethod
    def add_item(user, product_id:int, quantity:int)->CartItem:
        """Thêm sản phẩm vào giỏ.
        - Nếu sản phẩm đã có → cộng thêm số lượng.
        - Validate tồn kho trước khi lưu."""
        product = get_object_or_404(Product, pk=product_id)
        CartService._validate_stock(product, quantity)
        cart = CartService.get_or_create_cart(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity":quantity})

        if not created:
            new_qty = cart_item.quantity + quantity
            CartService._validate_stock(product, new_qty)
            cart_item.quantity = new_qty
            cart_item.save(update_fields=["quantity", "updated_at"])
            
        return cart_item
    
    @staticmethod
    def update_item(user, item_id:int, quanity: int)->CartItem:
        # Cập nhật số lượng
        cart_item= get_object_or_404(CartItem, pk=item_id, cart__user=user)#cart__user từ cartitem -> cart kiểm tra user
        CartService._validate_stock(cart_item.product, quanity)
        cart_item.quantity = quanity
        cart_item.save(update_fields=["quantity", "updated_at"])
        return cart_item
    
    @staticmethod
    def remove_item(user, item_id: int)->None:
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=user)
        cart_item.delete()

    @staticmethod
    def clear_cart(user)->None:
        # Xóa toàn bộ sản phẩm trong giỏ hàng.
        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete() #cart.items là theo related_name bên model

    @staticmethod
    def _validate_stock(product, quantity:int):
        # Raise ValueError nếu số lượng yêu cầu vượt tồn kho
        if quantity<1:
            raise ValueError("Số lương phải lớn hơn 0.")
        if product.quantity < quantity:
            raise ValueError(f"Chỉ còn {product.quantity} sản phẩm {product.name} trong kho.")

    
        