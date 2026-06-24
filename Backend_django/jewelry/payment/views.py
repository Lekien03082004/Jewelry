from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from orders import services as order_service
from . import service as payment_service
# Create your views here.

class CreatePaymentUrlView(APIView):
    parser_classes = [IsAuthenticated]
    
    def post(self, request, order_code=None):
        order = order_service.get_order_by_code(order_code=order_code, user=request.user)
        payment_url = payment_service.create_payment_url(order, request)
        
        return Response({'payment_url': payment_url})

class VNPayReturnView(APIView):
    """
    GET /payment/vnpay/return/ — khách bị VNPay redirect về đây sau khi thanh toán.
    CHỈ dùng để hiển thị UI, KHÔNG dùng để xác nhận thanh toán thành công.
    """
    permission_classes = [AllowAny]
    authentication_classes=[]
    
    def get(self, request):
        params = request.query_params.dict()
        
        if not payment_service.verify_signature(params):
            return Response({
                {'message': "Chứ kí không hợp lê."}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        response_code = params.get('vnp_ResponseCode')
        txn_ref = params.get('vnp_TxnRef')
        
        # Chỉ hiển thị trạng thái tạm cho khách xem — trạng thái CHÍNH THỨC
        # do process_ipn cập nhật riêng (có thể tới sau hoặc trước returnUrl một chút).
        if response_code == '00':
            return Response(
                {
                'message': 'Thanh toan thanh cong. Don hang cua ban dang duoc xac thuc.',
                'txn_ref':txn_ref
                }, 
                status=status.HTTP_200_OK)
            
        if response_code == '04':
            return Response({
                'message': 'Thanh toan khong thanh cong hoac da bi huy',
                'txn_ref': txn_ref
            }, status=status.HTTP_400_BAD_REQUEST)
            
class VNPayIPNView(APIView):
    """
    GET /payment/vnpay/ipn/ — VNPay gọi server-to-server, đây là nguồn xác nhận DUY NHẤT đáng tin.
    Không yêu cầu authenticate (VNPay gọi trực tiếp, không có cookie người dùng).
    """
    parser_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        paprams = request.query_params.dict()
        result = payment_service.process_ipn(params=paprams)
        return Response(result, status=status.HTTP_200_OK)