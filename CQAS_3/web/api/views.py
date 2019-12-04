from functools import partial
from functools import wraps
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import \
    (CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested import routers
from rest_framework import viewsets
from . import permissions
from . import serializers
from .authentication import TokenAuthentication
# from .viewlib import (List2RetrieveMixin, NestedViewSetBase)
from collections import OrderedDict
import datetime
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import QueryDict
from django.db.models import Q
from rest_framework.compat import coreapi, coreschema, distinct
from rest_framework import exceptions
from rest_framework.pagination import LimitOffsetPagination
import datetime
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import (AdminTokens, Admin, Department,
                     Permission, User, WorkDate,
                     DayScore, MonthScore, SeasonScore,
                     RewardsAndPunishments)
from .serializers import (AdminTokens, Admin, DepartmentSerializer,
                     PermissionSerializer, UserSerializer, WorkDateSerializer,
                     DayScoreSerializer, MonthScoreSerializer, SeasonScoreSerializer,
                     RewardsAndPunishmentsSerializer)

router = routers.DefaultRouter()
nested_routers = []
orderdct = OrderedDict()


class UpdateModelMixin:
    """
    客製化Update 不要有partial_update
    """

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


def router_url(url, prefix=None, *args, **kwargs):
    def decorator(cls):
        if not prefix:
            router.register(url, cls, *args, **kwargs)
        else:
            prefix_router = orderdct.get(prefix, router)
            nested_router = routers.NestedDefaultRouter(prefix_router, prefix, lookup=prefix)
            nested_router.register(url, cls, *args, **kwargs)
            orderdct[url] = nested_router
            nested_routers.append(nested_router)

        @wraps(cls)
        def warp(*args, **kwargs):
            return cls(*args, **kwargs)

        return warp

    return decorator


# Create your views here.
@router_url('User')
class UserViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin,viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # queryset = serializers.User.objects.filter(enabled=True)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create' or 'update':
            serializer_class = serializers.UserCreateSerializer
        if self.action == 'list':
            serializer_class = serializers.UserGetListSerializer
        if self.action == 'retrieve':
            serializer_class = serializers.UserGetSerializer
        return serializer_class



@router_url('Department')
class DepertmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # queryset = serializers.Department.objects.filter(enabled=True)



@router_url('Permission')
class PermissionViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin,viewsets.GenericViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    # queryset = serializers.Permission.objects.filter(enabled=True)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create' or 'update':
            serializer_class = serializers.PermissionCreateSerializer
        if self.action == 'list':
            serializer_class = serializers.PermissionGetListSerializer
        if self.action == 'destroy':
            self.action == 'update'
            serializer_class = serializers.PermissionDeleteSerializer
        return serializer_class




@router_url('WorkDate')
class WorkDateViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin,viewsets.GenericViewSet):
    queryset = WorkDate.objects.all()
    serializer_class = WorkDateSerializer
    # queryset = serializers.WorkDate.objects.filter(enabled=True)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create' or 'update':
            serializer_class = serializers.WorkDateCreateSerializer
        if self.action == 'list':
            serializer_class = serializers.WorkDateGetListSerializer
        return serializer_class


@router_url('DayScore')
class DayScoreViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = DayScore.objects.all()
    serializer_class = DayScoreSerializer
    # queryset = serializers.DayScore.objects.filter(enabled=True)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create' or 'update':
            serializer_class = serializers.DayScoreCreateSerializer
        if self.action == 'list':
            serializer_class = serializers.DayScoreGetListSerializer
        if self.action == 'retrieve':
            serializer_class = serializers.DayScoreGetSerializer
        return serializer_class



@router_url('MonthScore')
class MonthScoreViewSet(RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = MonthScore.objects.all()
    serializer_class = MonthScoreSerializer
    # queryset = serializers.MonthScore.objects.filter(enabled=True)



@router_url('SeasonScore')
class SeasonScoreViewSet(RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = SeasonScore.objects.all()
    serializer_class = SeasonScoreSerializer
    # queryset = serializers.SeasonScore.objects.filter(enabled=True)


@router_url('RewardsAndPunishments')
class RewardsAndPunishmentsViewSet(RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = RewardsAndPunishments.objects.all()
    serializer_class = RewardsAndPunishmentsSerializer
    # queryset = serializers.RewardsAndPunishments.objects.filter(enabled=True)



@router_url('admin')
class AdminViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    ### Request
    ```json
    {

    }
    ```
    ### Respone
    ```json
    [
        {
            "id": 51,
            "email": "max49@conquers.co",
            "created_at": "2019-11-22T02:09:21.492561Z"
        },
        {
            "id": 50,
            "email": "max48@conquers.co",
            "created_at": "2019-11-22T02:09:21.415515Z"
        }
    ]

    ```


    create:

    ### Request
    ```json
    {
      "email": "max@conquer1.co",
      "password": "1111"
    }
    ```

    ### Response
    ```json
    {
        "id": 32,
        "email": "max@conquer1.co",
        "created_at": "2019-11-21T09:07:24.408876Z"
    }
    ```

    login:
    ### Request
    ```json
    {
      "email": "max@conquer1.co",
      "password": "1111"
    }
    ```
    ### Response
    ```json
    {
      "token": "1111"
    }
    ```

    logout:
    ### Request
    ```json
    {

    }
    ```
    ### Response
    ```json
    {
        "msg": "success"
    }
    ```

    update:
    ### Request
    ```json
    {
        "password": "1111"
    }
    ```
    ### Response
    ```json
    {
        "msg": "success"
    }
    ```



    """

    queryset = serializers.Admin.objects.filter(enabled=True)
    serializer_class = serializers.AdminSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'update':
            serializer_class = serializers.AdminUpdateSerializer
        return serializer_class

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', True)
        instance = serializers.Admin.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(dict(msg='success'))

    @action(methods=['POST'], detail=False,
            authentication_classes=[],
            permission_classes=[],
            )
    def login(self, request, *args, **kwargs):
        # for test ，problem
        data = request.data.copy()
        if isinstance(data, QueryDict):
            data = dict(data.lists())
            for key in data:
                if isinstance(data[key], list) and len(data[key]) == 1:
                    data[key] = data[key][0]

        raw_password = data['password']
        del data['password']
        try:
            user = serializers.Admin.objects.get(**data)
        except Exception as e:
            return Response(data='帳號或密碼錯誤', status=403)
        if not user.check_password(raw_password):
            return Response(data='帳號或密碼錯誤', status=403)
        token, created = serializers.AdminTokens.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(methods=['POST'], detail=False, url_path='logout',
            serializer_class=serializers.serializers.Serializer,
            permission_classes=(),
            )
    def logout(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({'msg': 'success'})


def get_urls():
    urls = router.get_urls()
    for nested_router in nested_routers:
        urls += nested_router.get_urls()
    return urls
#
#
# class UpdateModelMixin:
#     """
#     客製化Update 不要有partial_update
#     """
#
#     def update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         partial = kwargs.pop('partial', True)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             # If 'prefetch_related' has been applied to a queryset, we need to
#             # forcibly invalidate the prefetch cache on the instance.
#             instance._prefetched_objects_cache = {}
#
#         return Response(serializer.data)
#
#     def perform_update(self, serializer):
#         serializer.save()
#
#
# def router_url(url, prefix=None, *args, **kwargs):
#     def decorator(cls):
#         if not prefix:
#             router.register(url, cls, *args, **kwargs)
#         else:
#             prefix_router = orderdct.get(prefix, router)
#             nested_router = routers.NestedDefaultRouter(prefix_router, prefix, lookup=prefix)
#             nested_router.register(url, cls, *args, **kwargs)
#             orderdct[url] = nested_router
#             nested_routers.append(nested_router)
#
#         @wraps(cls)
#         def warp(*args, **kwargs):
#             return cls(*args, **kwargs)
#
#         return warp
#
#     return decorator
#
#
# @router_url('profit')
# class ProfitViewSet(ListModelMixin, CreateModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#         "id": 1,
#         "limit": 10,
#         "offset": 0
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "count": 50,
#             "next": "http://localhost:8000/profit/?limit=2&amp;offset=2",
#             "previous": null,
#             "results": [
#                 {
#                     "id": 50,
#                     "fee": {
#                         "id": 1,
#                         "date": "2019-11-22T09:52:53.434715Z",
#                         "fee_percent": 0.5,
#                         "memo": "預設"
#                     },
#                     "date": "2019-11-22T09:53:00.346376Z",
#                     "original_amount": 198288770,
#                     "latest_amount": 198538770,
#                     "fee_money": 250000,
#                     "earn_money": 500000,
#                     "net_profit": 250000
#                 },
#                 {
#                     "id": 49,
#                     "fee": {
#                         "id": 1,
#                         "date": "2019-11-22T09:52:53.434715Z",
#                         "fee_percent": 0.5,
#                         "memo": "預設"
#                     },
#                     "date": "2019-11-22T09:53:00.286893Z",
#                     "original_amount": 194538770,
#                     "latest_amount": 194788770,
#                     "fee_money": 250000,
#                     "earn_money": 500000,
#                     "net_profit": 250000
#                 }
#             ]
#     }
#     ```
#     create:
#     ### Request
#     ```json
#     {
#         "earn_money": 300000
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "id": 51,
#         "fee": {
#             "id": 1,
#             "date": "2019-11-22T09:52:53.434715Z",
#             "fee_percent": 0.5,
#             "memo": "預設"
#             },
#         "date": "2019-11-22T09:59:07.941536Z",
#         "original_amount": 198538770,
#         "latest_amount": 198688770,
#         "fee_money": 150000,
#         "earn_money": 300000,
#         "net_profit": 150000
#     }
#     ```
#     """
#     queryset = serializers.Profit.objects.filter(enabled=True)
#     serializer_class = serializers.ProfitSerializer
#     pagination_class = LimitOffsetPagination
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializers.ProfitSerializer(serializer.instance).data,
#                         status=status.HTTP_201_CREATED,
#                         headers=headers)
#
#
# class ProductFilter(filters.BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         return queryset
#
#     def get_schema_fields(self, view):
#         return (
#             coreapi.Field(
#                 name='latest_productprofit',
#                 required=False,
#                 location='query',
#                 schema=coreschema.Boolean(
#                     title='latest_productprofit',
#                     description='是否顯示最新一筆productprofit'
#                 )
#             ),
#         )
#
#
# class ProfitTestFilter(filters.BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         return queryset
#
#     def get_schema_fields(self, view):
#         return (
#             coreapi.Field(
#                 name='profit',
#                 required=False,
#                 location='query',
#                 schema=coreschema.Integer(
#                     title='profit',
#                     description='fake profit'
#                 )
#             ),
#         )
#
#
# @router_url('productprofitstatus')
# class ProductprofitStatusViewSet(ListModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "productprofit": false
#     }
#     ```
#
#     """
#     queryset = serializers.ProductProfit.objects.filter(enabled=True)
#     serializer_class = serializers.serializers.Serializer
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         productprofit = True if queryset.filter(profit=None).count() else False
#         data = dict(productprofit=productprofit)
#         return Response(data, 200)
#
#
# @router_url('products/fake')
# class FakeViewSet(ListModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#         "profit": 300000
#     }
#     ```
#     ### Respone
#     ```json
#     [
#         {
#             "id": 1,
#             "units": 12.761,
#             "unique_site": "a55426ed-5ea6-454d-b801-8101705f2765",
#             "latest_productprofit": {
#                 "id": 344,
#                 "date": "2019-11-22T09:24:20.191375Z",
#                 "original_amount": 34120557,
#                 "original_percent": 0.175,
#                 "net_profit": 43750,
#                 "cumulative_profit": 2784000,
#                 "latest_amount": 34164307,
#                 "latest_percent": 0.175,
#                 "adjustment_amount": 500000,
#                 "profit": 50
#             },
#             "amount_and_all_adjustment": null,
#             "name": "SHD",
#             "amount": 6380307,
#             "is_strategy": true
#         },
#         {
#             "id": 2,
#             "units": 1.063,
#             "unique_site": "ec887d28-50da-4189-b4ab-267f9b7e59ba",
#             "latest_productprofit": {
#                 "id": 345,
#                 "date": "2019-11-22T09:24:20.196599Z",
#                 "original_amount": 27093693,
#                 "original_percent": 0.139,
#                 "net_profit": 34750,
#                 "cumulative_profit": 1596750,
#                 "latest_amount": 27128443,
#                 "latest_percent": 0.139,
#                 "adjustment_amount": 500000,
#                 "profit": 50
#             },
#             "amount_and_all_adjustment": null,
#             "name": "LEC",
#             "amount": 531693,
#             "is_strategy": true
#         }
#     ]
#     ```
#     """
#     queryset = serializers.Product.objects.filter(enabled=True, settlement=False)
#     serializer_class = serializers.ProfitTestSerializer
#     filter_backends = [ProfitTestFilter]
#
#     def list(self, request, *args, **kwargs):
#         earn_money = request.query_params.get('profit', 0)
#         earn_money = int(earn_money)
#         ret = []
#         # todo 應該不要真的新增 這樣吃效能 但這個製作很花時間
#         try:
#             with transaction.atomic():
#                 serializer = serializers.ProfitSerializer()
#                 serializer.create(dict(earn_money=earn_money))
#                 ret = super().list(request, *args, **kwargs)
#                 # todo 改用這樣解決
#                 serializers.FeeRatio.objects.create(fee_percent='test')
#         except Exception as e:
#             pass
#
#         return ret
#
#
# @router_url('products')
# class ProductViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Respone
#     ```json
#     [
#         {
#             "id": 1,
#             "units": 12.761,
#             "unique_site": "a55426ed-5ea6-454d-b801-8101705f2765",
#             "latest_productprofit": {
#                 "id": 344,
#                 "date": "2019-11-22T09:24:20.191375Z",
#                 "original_amount": 34120557,
#                 "original_percent": 0.175,
#                 "net_profit": 43750,
#                 "cumulative_profit": 2784000,
#                 "latest_amount": 34164307,
#                 "latest_percent": 0.175,
#                 "adjustment_amount": 500000,
#                 "profit": 50
#             },
#             "amount_and_all_adjustment": 31380307,
#             "name": "SHD",
#             "amount": 6380307,
#             "is_strategy": true
#         },
#         {
#             "id": 2,
#             "units": 1.063,
#             "unique_site": "ec887d28-50da-4189-b4ab-267f9b7e59ba",
#             "latest_productprofit": {
#                 "id": 345,
#                 "date": "2019-11-22T09:24:20.196599Z",
#                 "original_amount": 27093693,
#                 "original_percent": 0.139,
#                 "net_profit": 34750,
#                 "cumulative_profit": 1596750,
#                 "latest_amount": 27128443,
#                 "latest_percent": 0.139,
#                 "adjustment_amount": 500000,
#                 "profit": 50
#             },
#             "amount_and_all_adjustment": 25531693,
#             "name": "LEC",
#             "amount": 531693,
#             "is_strategy": true
#         }
#     ]
#     ```
#
#     create:
#     ### Request
#     ```json
#     {
#         "name": "PTT",
#         "amount": 300000,
#         "is_strategy": true
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "id": 8,
#         "units": 0.6,
#         "unique_site": "1c308448-df10-4e24-8367-78c6b7af9f11",
#         "latest_productprofit": null,
#         "amount_and_all_adjustment": null,
#         "name": "PTT",
#         "amount": 300000,
#         "is_strategy": true
#     }
#     ```
#
#     productsettlement:
#     ### Request
#     ```json
#     [
#       {
#         "amount": 50,
#         "from_product": 1,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 2,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 3,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 4,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 5,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 6,
#         "is_strategy": true
#       },
#       {
#         "amount": 50,
#         "from_product": 7,
#         "is_strategy": true
#       }
#     ]
#     ```
#     ### Respone
#     ```json
#     {
#         "msg": "success"
#     }
#     ```
#
#     update:
#     ### Request
#     ```json
#     {
#         "name": "PTT",
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "id": 10,
#         "units": 0,
#         "unique_site": "c8f6f36f-7f10-436e-8b34-7c106207ffa1",
#         "latest_productprofit": null,
#         "amount_and_all_adjustment": null,
#         "name": "PTT",
#         "amount": 50,
#         "is_strategy": false
#     }
#     ```
#     """
#     queryset = serializers.Product.objects.filter(enabled=True, settlement=False)
#     serializer_class = serializers.ProductSerializer
#     filter_backends = [ProductFilter]
#
#     @action(methods=['POST'], serializer_class=serializers.ProductSettlementListSerializer, detail=False)
#     def productsettlement(self, request, *args, **kwargs):
#         data = request.data.copy()
#         if isinstance(data, QueryDict):
#             data = dict(data.lists())
#             for key in data:
#                 if isinstance(data[key], list):
#                     data_list = []
#                     for d in data[key]:
#                         data_list.append(eval(d))
#                     data[key] = data_list
#
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.create(data)
#
#         return Response(dict(msg='success'), status=status.HTTP_201_CREATED)
#
#
# @router_url('noauth/products')
# class ProductViewSet(RetrieveModelMixin, viewsets.GenericViewSet):
#     """
#     retrieve:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "id": 1,
#         "units": 12.761,
#         "unique_site": "a55426ed-5ea6-454d-b801-8101705f2765",
#         "latest_productprofit": null,
#         "amount_and_all_adjustment": null,
#         "name": "SHD",
#         "amount": 6380307,
#         "is_strategy": true
#     }
#     ```
#     """
#     queryset = serializers.Product.objects.filter(enabled=True, settlement=False)
#     serializer_class = serializers.ProductSerializer
#     filter_backends = [ProductFilter]
#     lookup_field = 'unique_site'
#
#     def get_authenticators(self):
#         authentication_classes = self.authentication_classes
#         method = self.request.method.lower()
#         self.action = self.action_map.get(method)
#
#         authentication_classes = self.authentication_classes
#         if self.action == 'retrieve':
#             authentication_classes = []
#         return [auth() for auth in authentication_classes]
#
#
# @router_url('productprofit')
# class ProductProfitViewSet(CreateModelMixin, viewsets.GenericViewSet):
#     """
#     create:
#     ### Request
#     ```json
#     {
#       "datas": [
#         {
#           "product_id": 1,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 2,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 3,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 4,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 5,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 6,
#           "adjustment_amount": 500000
#         },
#         {
#           "product_id": 7,
#           "adjustment_amount": 500000
#         }
#       ]
#     }
#     ```
#     ### Respone
#     ```json
#     [
#       {
#         "id": 351,
#         "date": "2019-11-22T09:33:06.478790Z",
#         "original_amount": 34664307,
#         "original_percent": 0.174,
#         "net_profit": null,
#         "cumulative_profit": null,
#         "latest_amount": null,
#         "latest_percent": null,
#         "adjustment_amount": 500000,
#         "profit": null
#       },
#       {
#         "id": 352,
#         "date": "2019-11-22T09:33:06.485011Z",
#         "original_amount": 27628443,
#         "original_percent": 0.139,
#         "net_profit": null,
#         "cumulative_profit": null,
#         "latest_amount": null,
#         "latest_percent": null,
#         "adjustment_amount": 500000,
#         "profit": null
#       }
#     ]
#     ```
#     """
#     queryset = serializers.ProductProfit.objects.filter(enabled=True)
#     serializer_class = serializers.ProductProfitCreateSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         ret = []
#         for ins in serializer.instance:
#             ret.append(serializers.ProductProfitSerializer(ins).data)
#         return Response(ret, status=status.HTTP_201_CREATED)
#
#
# @router_url('productprofit', prefix='products')
# class ProductProfitWithProductViewSet(NestedViewSetBase, ListModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#         "id": 344,
#         "limit": 10,
#         "offset": 0
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "count": 50,
#         "next": "http://localhost:8000/products/1/productprofit/?limit=5&amp;offset=5",
#         "previous": null,
#         "results": [
#             {
#                 "id": 344,
#                 "date": "2019-11-22T09:53:00.311845Z",
#                 "original_amount": 34120557,
#                 "original_percent": 0.175,
#                 "net_profit": 43750,
#                 "cumulative_profit": 2784000,
#                 "latest_amount": 34164307,
#                 "latest_percent": 0.175,
#                 "adjustment_amount": 500000,
#                 "profit": 50
#             },
#             {
#                 "id": 337,
#                 "date": "2019-11-22T09:53:00.254543Z",
#                 "original_amount": 33576807,
#                 "original_percent": 0.175,
#                 "net_profit": 43750,
#                 "cumulative_profit": 2740250,
#                 "latest_amount": 33620557,
#                 "latest_percent": 0.175,
#                 "adjustment_amount": 500000,
#                 "profit": 49
#             },
#             {
#                 "id": 330,
#                 "date": "2019-11-22T09:53:00.194512Z",
#                 "original_amount": 33032807,
#                 "original_percent": 0.176,
#                 "net_profit": 44000,
#                 "cumulative_profit": 2696500,
#                 "latest_amount": 33076807,
#                 "latest_percent": 0.176,
#                 "adjustment_amount": 500000,
#                 "profit": 48
#             },
#             {
#                 "id": 323,
#                 "date": "2019-11-22T09:53:00.136210Z",
#                 "original_amount": 32488807,
#                 "original_percent": 0.176,
#                 "net_profit": 44000,
#                 "cumulative_profit": 2652500,
#                 "latest_amount": 32532807,
#                 "latest_percent": 0.176,
#                 "adjustment_amount": 500000,
#                 "profit": 47
#             },
#             {
#                 "id": 316,
#                 "date": "2019-11-22T09:53:00.081210Z",
#                 "original_amount": 31944557,
#                 "original_percent": 0.177,
#                 "net_profit": 44250,
#                 "cumulative_profit": 2608500,
#                 "latest_amount": 31988807,
#                 "latest_percent": 0.177,
#                 "adjustment_amount": 500000,
#                 "profit": 46
#             }
#         ]
#     }
#     ```
#     """
#     parent_model = 'products'
#     queryset = serializers.ProductProfit.objects.filter(enabled=True)
#     serializer_class = serializers.ProductProfitSerializer
#     pagination_class = LimitOffsetPagination
#
#     def get_queryset(self):
#         parent_key = self.parent_model + '_pk'
#         parent_filter_name = self.parent_model
#         if parent_filter_name.endswith('s'):
#             parent_filter_name = parent_filter_name[:-1]
#         filter_kwargs = {
#             f'{parent_filter_name}_id': self.kwargs[parent_key]
#         }
#         return self.queryset.filter(**filter_kwargs)
#
#
# @router_url('feeratio')
# class FeeratioViewSet(ListModelMixin, CreateModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Respone
#     ```json
#     [
#         {
#             "id": 1,
#             "date": "2019-11-22T09:24:13.531118Z",
#             "fee_percent": 0.5,
#             "memo": "預設"
#         }
#     ]
#     ```
#
#     create:
#     ### Request
#     ```json
#     {
#         "fee_percent": 0.3,
#         "memo": "週年慶"
#     }
#     ```
#     ### Respone
#     ```json
#     {
#         "id": 2,
#         "date": "2019-11-22T09:27:50.489512Z",
#         "fee_percent": 0.3,
#         "memo": "週年慶"
#     }
#     ```
#
#
#     """
#     queryset = serializers.FeeRatio.objects.filter(enabled=True)
#     serializer_class = serializers.FeeRatioSerializer


# @router_url('admin')
# class AdminViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
#     """
#     list:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Respone
#     ```json
#     [
#         {
#             "id": 51,
#             "email": "max49@conquers.co",
#             "created_at": "2019-11-22T02:09:21.492561Z"
#         },
#         {
#             "id": 50,
#             "email": "max48@conquers.co",
#             "created_at": "2019-11-22T02:09:21.415515Z"
#         }
#     ]
#
#     ```
#
#
#     create:
#
#     ### Request
#     ```json
#     {
#       "email": "max@conquer1.co",
#       "password": "1111"
#     }
#     ```
#
#     ### Response
#     ```json
#     {
#         "id": 32,
#         "email": "max@conquer1.co",
#         "created_at": "2019-11-21T09:07:24.408876Z"
#     }
#     ```
#
#     login:
#     ### Request
#     ```json
#     {
#       "email": "max@conquer1.co",
#       "password": "1111"
#     }
#     ```
#     ### Response
#     ```json
#     {
#       "token": "1111"
#     }
#     ```
#
#     logout:
#     ### Request
#     ```json
#     {
#
#     }
#     ```
#     ### Response
#     ```json
#     {
#         "msg": "success"
#     }
#     ```
#
#     update:
#     ### Request
#     ```json
#     {
#         "password": "1111"
#     }
#     ```
#     ### Response
#     ```json
#     {
#         "msg": "success"
#     }
#     ```
#
#
#
#     """
#
#     queryset = serializers.Admin.objects.filter(enabled=True)
#     serializer_class = serializers.AdminSerializer
#
#     def get_serializer_class(self):
#         serializer_class = self.serializer_class
#         if self.action == 'update':
#             serializer_class = serializers.AdminUpdateSerializer
#         return serializer_class
#
#     def update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         partial = kwargs.pop('partial', True)
#         instance = serializers.Admin.objects.get(pk=kwargs['pk'])
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             # If 'prefetch_related' has been applied to a queryset, we need to
#             # forcibly invalidate the prefetch cache on the instance.
#             instance._prefetched_objects_cache = {}
#
#         return Response(dict(msg='success'))
#
#     @action(methods=['POST'], detail=False,
#             authentication_classes=[],
#             permission_classes=[],
#             )
#     def login(self, request, *args, **kwargs):
#         # for test problem
#         data = request.data.copy()
#         if isinstance(data, QueryDict):
#             data = dict(data.lists())
#             for key in data:
#                 if isinstance(data[key], list) and len(data[key]) == 1:
#                     data[key] = data[key][0]
#
#         raw_password = data['password']
#         del data['password']
#         try:
#             user = serializers.Admin.objects.get(**data)
#         except Exception as e:
#             return Response(data='帳號或密碼錯誤', status=403)
#         if not user.check_password(raw_password):
#             return Response(data='帳號或密碼錯誤', status=403)
#         token, created = serializers.AdminTokens.objects.get_or_create(user=user)
#         return Response({'token': token.key})
#
#     @action(methods=['POST'], detail=False, url_path='logout',
#             serializer_class=serializers.serializers.Serializer,
#             permission_classes=(),
#             )
#     def logout(self, request, *args, **kwargs):
#         request.auth.delete()
#         return Response({'msg': 'success'})
#
#
# def get_urls():
#     urls = router.get_urls()
#     for nested_router in nested_routers:
#         urls += nested_router.get_urls()
#     return urls
