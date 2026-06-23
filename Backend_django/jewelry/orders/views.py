from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from .serializers import(OrderSerializer, CreateOrderSerializer,UpdateOrderStatusSerializer)
from account.permissions import IsAdminOrManager
from . import services

# Create your views here.


class OrderViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    # POST /orders/
    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = services.create_order(
            user=request.user,
            **serializer.validated_data
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    # GET /orders/
    def list(self, request):
        orders = services.get_user_orders(request.user)
        return Response(OrderSerializer(orders, many=True).data)

    # GET /orders/<order_code>/
    def retrieve(self, request, pk=None):
        order = services.get_order_by_code(order_code=pk, user=request.user)
        return Response(OrderSerializer(order).data)

    # POST /orders/<order_code>/cancel/
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = services.get_order_by_code(order_code=pk, user=request.user)
        services.cancel_order(order)
        return Response({'detail': 'Đơn hàng đã được hủy thành công.'})


class AdminOrderViewSet(GenericViewSet):
    permission_classes = [IsAdminOrManager]

    # GET /admin/orders/?status=pending
    def list(self, request):
        status_filter = request.query_params.get('status')
        orders = services.get_all_orders(status_filter=status_filter)
        return Response(OrderSerializer(orders, many=True).data)

    # GET /admin/orders/<order_code>/
    def retrieve(self, request, pk=None):
        order = services.get_order_by_code(order_code=pk)
        return Response(OrderSerializer(order).data)

    # PATCH /admin/orders/<order_code>/status/
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = services.get_order_by_code(order_code=pk)
        updated_order = services.update_order_status(
            order=order,
            new_status=serializer.validated_data['status']
        )
        return Response(OrderSerializer(updated_order).data)