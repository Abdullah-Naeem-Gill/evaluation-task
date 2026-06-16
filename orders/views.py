from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .permissions import IsOrderOwnerOrStaff
from .serializers import OrderCreateSerializer, OrderSerializer
from .services import OrderServiceError, cancel_order


class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOrderOwnerOrStaff]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items__product')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        try:
            order = cancel_order(order)
        except OrderServiceError as exc:
            raise ValidationError({exc.field: exc.message}) from exc

        serializer = self.get_serializer(order)
        return Response(serializer.data)
