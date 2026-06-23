import uuid
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Order, OrderItem
def generate_order_code()->str:
    return f'ORD-{uuid.uuid4().hex[:10].upper()}'

def validate_cart(user)->object:
    # Kiểm tra cart có tồn tại hoặc rỗng hay không.
    # carts theo related_name trong Cart 
    cart = getattr(user, 'carts', None)
    if not cart or not cart.items.exists():
        raise ValidationError('Giỏ hàng rỗng không thể đặt hàng')
    return cart

def validate_stock(cart)->None:
    # Kiểm tra những sản trong giỏ có còn trong kho không
    errors=[]
    for item in cart.items.select_related('product'):
        if item.product.quantity < item.quantity:
            errors.append(
                f'Sản phẩm {item.product.name} không đủ hàng'
                f'(yêu cầu {item.quantity} còn {item.product.quantity}).'
            )

    if errors:
        raise ValidationError(errors)
    
def create_order(user, shipping_address:str, phone: str)->Order:
    """Tạo order từ cart của user.
    1. Validate cart & stock
    2. Tạo Order + OrderItems (snapshot giá)
    3. Trừ stock
    4. Xóa cart items
    Toàn bộ trong transaction.atomic() để đảm bảo data consistency.
    """
    cart = validate_cart(user)
    
    with transaction.atomic():
        validate_stock(cart)
        
        order = Order.objects.create(
            user=user,
            order_code=generate_order_code(),
            shipping_address=shipping_address,
            phone=phone
        )
    
        total = _create_order_items(order, cart)
        
        order.total_price = total
        
        order.save(update_fields=['total_price'])
        
        cart.items.all().delete()
        
    return order
    
def _create_order_items(order: Order, cart)->float:
    # Tạo OrderItems và trừ số lượng trong kho và trả về tổng tiền
    total = 0
    items_to_update=[]
    for item in cart.items.select_related('product'):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price # snapshot giá tại thời điểm mua
        )
        
        total += item.product.price * item.quantity
        item.product.quantity -= item.quantity
        items_to_update.append(item.product)
        
    # Bulk update stock — tránh N+1 queries
    if items_to_update:
        from my_jewelry.models import Product
        Product.objects.bulk_update(items_to_update, ['quantity'])
        
    return total


def cancel_order(order: Order)->Order:
    """
    Chỉ cho hủy đơn hàng khi ở trạng thái đơn hàng PENDING,
    trả lại số lượng đơn hàng về kho.
    """
    if order.status != Order.STATUS_CHOICES.PENDING:
        raise ValidationError("Chỉ có thể xóa đơn hàng khi đang trạng thái PENDING.")
    
    with transaction.atomic():
        _restore_stock(order)
        order.status = Order.STATUS_CHOICES.CANCELED
        order.save(update_fields=['status'])
        
    return order


def _restore_stock(order: Order)->None:
    """Hoàn trả số lượng về kho."""
    items_to_update=[]
    for item in order.order_items.select_related('product'):
        item.product.quantity += item.quantity
        items_to_update.append(item.product)
        
    from my_jewelry.models import Product
    Product.objects.bulk_update(items_to_update, ['quantity'])
    
    
VALID_TRANSITIONS = {
    Order.STATUS_CHOICES.PENDING:   [Order.STATUS_CHOICES.CONFIRMED, Order.STATUS_CHOICES.CANCELED],
    Order.STATUS_CHOICES.CONFIRMED: [Order.STATUS_CHOICES.SHIPPED,   Order.STATUS_CHOICES.CANCELED],
    Order.STATUS_CHOICES.SHIPPED:   [Order.STATUS_CHOICES.DELIVERED],
    Order.STATUS_CHOICES.DELIVERED: [],
    Order.STATUS_CHOICES.CANCELED:  [],
}

def update_order_status(order: Order, new_status: str)->Order:
    """
    Admin cập nhật trạng thái — kiểm tra state machine.
    Nếu admin hủy đơn, tự động hoàn trả quantity.
    """
    
    allowed = VALID_TRANSITIONS.get(order.status, [])
    
    if new_status not in allowed:
        raise ValidationError(f'Không thể chuyển trạng thái đơn hàng từ {order.status} sang {new_status}.')
    
    with transaction.atomic():
        if new_status == Order.STATUS_CHOICES.CANCELED:
            _restore_stock(order)
            
        order.status = new_status
        order.save(update_fields=['status'])
    
    return order

def get_user_orders(user):
    """Lấy toàn bộ order của user rồi tối ưu query"""
    return (
        Order.objects
        .filter(user=user)
        .prefetch_related('order_items__product')
        .order_by('-created_at')
    )
    
def get_order_by_code(order_code: str, user=None)->Order:
    """
    Lấy order theo code.
    Nếu truyền user thì chỉ lấy order của user đó (dùng cho user endpoint).
    Không truyền user thì lấy tất cả (dùng cho admin endpoint).
    """
    qs = Order.objects.prefetch_related('order_items__product')
    if user:
        qs = qs.filter(user=user)
    order = qs.filter(order_code=order_code).first()
    if not order:
        raise ValidationError("Không tìm thấy đơn hàng.")
    return order

def get_all_orders(status_filter: str=None):
    """Admin lấy tất cả orders, có thể filter theo status."""
    qs = (
        Order.objects
        .prefetch_related('order_items__product')
        .order_by('-created_at')
    )
    if status_filter:
        qs = qs.filter(status=status_filter)
    return qs