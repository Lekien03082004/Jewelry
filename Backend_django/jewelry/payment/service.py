import uuid
import hashlib
import hmac
import urllib.parse
from datetime import datetime

from django.conf import settings
from rest_framework.exceptions import ValidationError

from orders.models import Order
from .models import Payment

def generate_txn_ref() -> str:
    return uuid.uuid4().hex[:15].upper()

def _build_hmac_signature(params: dict, secret_key: str)->str:
    """
    VNPay yêu cầu:
    1. Sắp xếp params theo alphabet key
    2. Nối thành query string (đã url-encode value)
    3. HMAC-SHA512 với secret key
    """
    sorted_params = sorted(params.items())
    query_string = '&'.join(f'{key}={urllib.parse.quote_plus(str(value))}' 
                            for key, value in sorted_params
                            if value not in (None, '')
                            )
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()
    return signature, query_string

def _get_client_ip(request)->str:
    x_forwared_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwared_for:
        return x_forwared_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def create_payment_url(order: Order, request)->str:
    """
    Tạo URL thanh toán VNPay cho 1 order.
    Cho phép gọi lại nhiều lần (retry) trên cùng 1 order — mỗi lần tạo Payment + txn_ref mới.
    """
    
    if order.status != Order.STATUS_CHOICES.PENDING:
        raise ValidationError('Chỉ có thể thanh toán đơn hàng khi ở trạng thái PENDING')
    
    txn_ref = generate_txn_ref()
    
    payment = Payment.objects.create(
        order=order,
        txn_ref=txn_ref,
        amount=order.total_price,
        status='pending'
    )
    
    # VNPay yêu cầu amount * 100 (đơn vị: xu, không phải đồng)
    vnp_params = {
        'vnp_Version':'2.1.0',
        'vnp_Command':'pay',
        'vnp_TmnCode': settings.VNPAY_TMN_CODE,
        'vnp_Amount': int(order.total_price*100),
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': txn_ref,
        'vnp_OrderInfo': f'Thanh toan hoa don {order.order_code}.',
        'vnp_OrderType': 'other',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
        'vnp_IpAddr': _get_client_ip(request),
        'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
    }
    
    signature, query_string = _build_hmac_signature(vnp_params, settings.VNPAY_HASH_SECRET)
    payment_url = f'{settings.VNPAY_PAYMENT_URL}?{query_string}&vnp_SecureHash={signature}'
    
    return payment_url

def verify_signature(params: dict)->bool:
    """
    Verify chữ ký từ VNPay gửi về (dùng cho cả returnUrl và IPN).
    LUÔN phải verify trước khi tin bất kỳ dữ liệu nào VNPay gửi —
    nếu không verify, ai cũng có thể giả mạo request giống VNPay để đánh dấu order là đã thanh toán.
    """
    received_hash=params.get('vnp_SecureHash')
    params_to_verify = {
        k:v for k, v in params.items()
        if k not in ('vnp_SecureHash', 'vnp_SecureHashType')
    }
    expected_hash, _=_build_hmac_signature(params_to_verify, settings.VNPAY_HASH_SECRET)
    return hmac.compare_digest(expected_hash, received_hash)

def process_ipn(params: dict)->dict:
    """
    Xử lý IPN (Instant Payment Notification) — nguồn xác nhận thanh toán DUY NHẤT đáng tin cậy.
    Trả về dict theo đúng format VNPay yêu cầu phản hồi lại.
    """
    if not verify_signature(params):
        return {'RspCode': '97', 'Message': 'Invalid signature'}
    
    txn_ref = params.get('vnp_TxnRef')
    response_code = params.get('vnp_ResponseCode')
    amount = int(params.get('vnp_Amount', 0)) / 100 # phai chia lại vì trước đó đã *100
    
    try:
        payment = Payment.objects.select_related('order').get(txn_ref=txn_ref)
    except Payment.DoesNotExist:
        return {'RspCode': '01', 'Message': 'Order not found'}
    
    # Kiem tra số tiền khớp không chánh giả mao amount
    if int(payment.amount * 100) != int(params.get('vnp_Amount', 0)):
        return {'RspCode': '04', 'Message': 'Invalid amount'}
    
    # Nếu payment này đã xử lý rồi (VNPay có thể gọi IPN nhiều lần cho 1 giao dịch),
    # trả về thành công ngay để tránh xử lý trùng (ví dụ trừ kho 2 lần)
    if payment.status != 'pending':
        return {'RspCode': '02', 'Message': 'Order ready confirmed'}
    
    payment.transaction_id = params.get('vnp_TransactionNo')
    payment.response_code = response_code
    payment.bank_code = params.get('vnp_BankCode')
    payment.raw_response = params
    
    if response_code == '00':
        payment.status = 'success'
        payment.save()
        
        order = payment.order
        order.status = Order.STATUS_CHOICES.CONFIRMED
        order.save(update_fields=['status'])
        
    else:
        payment.status = 'failed'
        payment.save()
    
    return {'RspCode': '00', 'Message': 'Confirm Success'}
    