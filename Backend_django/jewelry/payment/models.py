from django.db import models

# Create your models here.
class Payment(models.Model):
    # ForeignKey (không phải OneToOne) vì 1 Order có thể có NHIỀU lần thử thanh toán
    # (lần 1 fail, khách bấm "Thanh toán lại" -> tạo Payment mới, cùng order)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20, default='vnpay')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # Mã giao dịch DUY NHẤT cho mỗi lần tạo link thanh toán — VNPay yêu cầu unique.
    # KHÔNG dùng order_code trực tiếp vì 1 order có thể có nhiều txn_ref (nhiều lần thử).
    txn_ref = models.CharField(max_length=100,null=True, blank=True, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    response_code = models.CharField(max_length=10, blank=True, null=True)
    # Lưu toàn bộ raw query params VNPay trả về — phục vụ audit/tranh chấp sau này
    raw_response = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f'{self.txn_ref} - {self.status}'