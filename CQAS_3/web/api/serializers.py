import re
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
from rest_framework import serializers
import json
import datetime
from rest_framework.validators import UniqueValidator
from django.http.request import QueryDict
# check admin
from .models import (AdminTokens, Admin, Department,
                     Permission, User, WorkDate,
                     DayScore, MonthScore, SeasonScore,
                     RewardsAndPunishments)
from django.utils.functional import cached_property
from rest_framework.utils.serializer_helpers import BindingDict
from django.utils import timezone


class UpdateRequiredSerailizerMixin:
    @cached_property
    def fields(self):
        """
        A dictionary of {field_name: field_instance}.
        """
        # `fields` is evaluated lazily. We do this to ensure that we don't
        # have issues importing modules that use ModelSerializers as fields,
        # even if Django's app-loading stage has not yet run.

        # check update requires is False
        method = None
        if 'view' in self.context and hasattr(self.context['view'], 'action'):
            method = self.context['view'].action
        fields = BindingDict(self)
        for key, value in self.get_fields().items():
            if method == 'update':
                value.required = False
            fields[key] = value
        return fields


class DefaultModelSerializer(UpdateRequiredSerailizerMixin, serializers.ModelSerializer):

    def update(self, instance, validated_data):
        if hasattr(instance, 'updated_at'):
            instance.updated_at = timezone.now()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return super().create(validated_data)


class HiddenField:
    def set_context(self, serializer_field):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        pass


def hiddenfield_factory(target_class):
    cls_name = target_class.__name__

    class Mixin:
        def set_context(self, serializer_field):
            _id = serializer_field.context['view'].kwargs[f'{cls_name.lower()}_pk']
            self.target = get_object_or_404(target_class, pk=_id)

        def __call__(self, *args, **kwargs):
            return self.target

    cls = type(cls_name, (Mixin, HiddenField), dict())
    return cls()


class CommonMeta:
    exclude = [
        'enabled',
        'created_at',
        'updated_at',
        'deleted_at',
    ]


class AdminSerializer(DefaultModelSerializer):
    password = serializers.CharField(max_length=100, help_text='密碼', write_only=True)
    email = serializers.EmailField(validators=[
        UniqueValidator(
            queryset=Admin.objects.all(),
            message="Email已經被註冊",
        )]
    )

    class Meta:
        model = Admin
        fields = ['id', 'email', 'password', 'created_at', 'updated_at']

    def get_field_names(self, declared_fields, info):
        exclude_fields = ['updated_at']
        fields = super().get_field_names(declared_fields, info)
        if self.context['view'].action == 'create':
            fields = super().get_field_names(declared_fields, info)
            for exclude_field in exclude_fields:
                if exclude_field in fields:
                    fields.remove(exclude_field)
        return fields

    def create(self, validated_data):
        admin = Admin(**validated_data)
        admin.set_password(validated_data['password'])
        admin.save()
        del admin.password
        return admin


class AdminUpdateSerializer(DefaultModelSerializer):
    password = serializers.CharField(max_length=100, help_text='密碼', write_only=True)

    class Meta:
        model = Admin
        fields = ['password']

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.updated_at = timezone.now()
        instance.save()
        del instance.password
        return instance


class DepartmentSerializer(DefaultModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        # fields = ()
        queryset = Department.objects.filter(enabled=True)


class PermissionSerializer(DefaultModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
        # fields = ()
        queryset = Permission.objects.filter(enabled=True)


class PermissionCreateSerializer(DefaultModelSerializer):
    class Meta:
        model = Permission
        # fields = '__all__'
        fields = ('name', 'description', 'role_manage', 'daily_rate', 'report')
        # queryset = User.objects.filter(enabled=True)


class PermissionGetListSerializer(DefaultModelSerializer):
    class Meta:
        model = Permission
        # fields = '__all__'
        fields = ('id', 'name', 'description', 'role_manage', 'daily_rate', 'report')
        # queryset = User.objects.filter(enabled=True)2.3	UserGetList


class PermissionDeleteSerializer(DefaultModelSerializer):
    enabled = False
    class Meta:
        model = Permission
        # fields = '__all__'
        fields = ('enabled')
        # queryset = User.objects.filter(enabled=True)2.3	UserGetList


class UserSerializer(DefaultModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # queryset = User.objects.filter(enabled=True)


class UserCreateSerializer(DefaultModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('status', 'permission', 'employee_number', 'cn_name', 'en_name', 'account', 'password', 'entry_date', 'leave_date', 'department', 'remarks')
        # queryset = User.objects.filter(enabled=True)


class UserGetListSerializer(DefaultModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'employee_number', 'status', 'permission', 'cn_name')
        # queryset = User.objects.filter(enabled=True)2.3	UserGetList


class UserGetSerializer(DefaultModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('account', 'password', 'status', 'permission', 'cn_name' ,'en_name', 'department', 'remarks', 'entry_date', 'leave_date')
        # queryset = User.objects.filter(enabled=True)2.3	UserGetList


class WorkDateSerializer(DefaultModelSerializer):
    class Meta:
        model = WorkDate
        fields = '__all__'
        # fields = ()
        queryset = WorkDate.objects.filter(enabled=True)


class WorkDateCreateSerializer(DefaultModelSerializer):
    class Meta:
        model = WorkDate
        # fields = '__all__'
        fields = ('date', 'status')
        queryset = WorkDate.objects.filter(enabled=True)


class WorkDateGetListSerializer(DefaultModelSerializer):
    class Meta:
        model = WorkDate
        # fields = '__all__'
        fields = ('id', 'date', 'status')
        queryset = WorkDate.objects.filter(enabled=True)


class DayScoreSerializer(DefaultModelSerializer):
    class Meta:
        model = DayScore
        fields = '__all__'
        # fields = ()
        queryset = DayScore.objects.filter(enabled=True)


class DayScoreCreateSerializer(DefaultModelSerializer):
    class Meta:
        model = DayScore
        # fields = '__all__'
        fields = ('rate_day', 'user', 'complete_score', 'quality_score', 'special_score', 'attitude_score', 'error_mark', 'manager', 'status')
        queryset = DayScore.objects.filter(enabled=True)


class DayScoreGetListSerializer(DefaultModelSerializer):
    class Meta:
        model = DayScore
        # fields = '__all__'
        fields = ('id', 'user', 'rate_day', 'manager', 'status', 'created_at', 'updated_at')
        queryset = DayScore.objects.filter(enabled=True)


class DayScoreGetSerializer(DefaultModelSerializer):
    class Meta:
        model = DayScore
        # fields = '__all__'
        fields = ('id', 'user', 'rate_day', 'manager', 'status', 'created_at', 'updated_at', 'complete_score', 'quality_score', 'special_score', 'attitude_score', 'error_mark', 'avg_score')
        queryset = DayScore.objects.filter(enabled=True)


class MonthScoreSerializer(DefaultModelSerializer):
    user = MonthScore.user.objects.get(id=2)
    user_name = serializers.CharField(source='user.name')
    class Meta:
        model = MonthScore
        # fields = '__all__'
        fields = ('id', 'rate_month', 'user', 'user_name', 'complete_score', 'quality_score', 'special_score', 'attitude_score',  'avg_score')
        queryset = MonthScore.objects.filter(enabled=True)


class SeasonScoreSerializer(DefaultModelSerializer):
    class Meta:
        model = SeasonScore
        # fields = '__all__'
        fields = ('id', 'rate_season', 'user', 'complete_score', 'quality_score', 'special_score', 'attitude_score',  'avg_score')
        queryset = SeasonScore.objects.filter(enabled=True)


class RewardsAndPunishmentsSerializer(DefaultModelSerializer):
    class Meta:
        model = RewardsAndPunishments
        # fields = '__all__'
        fields = ('id', 'user', 'year_month', "record", 'description')
        queryset = RewardsAndPunishments.objects.filter(enabled=True)


# class UpdateRequiredSerailizerMixin:
#     @cached_property
#     def fields(self):
#         """
#         A dictionary of {field_name: field_instance}.
#         """
#         # `fields` is evaluated lazily. We do this to ensure that we don't
#         # have issues importing modules that use ModelSerializers as fields,
#         # even if Django's app-loading stage has not yet run.
#
#         # check update requires is False
#         method = None
#         if 'view' in self.context and hasattr(self.context['view'], 'action'):
#             method = self.context['view'].action
#         fields = BindingDict(self)
#         for key, value in self.get_fields().items():
#             if method == 'update':
#                 value.required = False
#             fields[key] = value
#         return fields
#
#
# class DefaultModelSerializer(UpdateRequiredSerailizerMixin, serializers.ModelSerializer):
#
#     def update(self, instance, validated_data):
#         if hasattr(instance, 'updated_at'):
#             instance.updated_at = timezone.now()
#         return super().update(instance, validated_data)
#
#     def create(self, validated_data):
#         return super().create(validated_data)
#
#
# class HiddenField:
#     def set_context(self, serializer_field):
#         raise NotImplemented
#
#     def __call__(self, *args, **kwargs):
#         pass
#
#
# def hiddenfield_factory(target_class):
#     cls_name = target_class.__name__
#
#     class Mixin:
#         def set_context(self, serializer_field):
#             _id = serializer_field.context['view'].kwargs[f'{cls_name.lower()}_pk']
#             self.target = get_object_or_404(target_class, pk=_id)
#
#         def __call__(self, *args, **kwargs):
#             return self.target
#
#     cls = type(cls_name, (Mixin, HiddenField), dict())
#     return cls()
#
#
# class CommonMeta:
#     exclude = [
#         'enabled',
#         'created_at',
#         'updated_at',
#         'deleted_at',
#     ]
#
#
# class AdminSerializer(DefaultModelSerializer):
#     password = serializers.CharField(max_length=100, help_text='密碼', write_only=True)
#     email = serializers.EmailField(validators=[
#         UniqueValidator(
#             queryset=Admin.objects.all(),
#             message="Email已經被註冊",
#         )]
#     )
#
#     class Meta:
#         model = Admin
#         fields = ['id', 'email', 'password', 'created_at', 'updated_at']
#
#     def get_field_names(self, declared_fields, info):
#         exclude_fields = ['updated_at']
#         fields = super().get_field_names(declared_fields, info)
#         if self.context['view'].action == 'create':
#             fields = super().get_field_names(declared_fields, info)
#             for exclude_field in exclude_fields:
#                 if exclude_field in fields:
#                     fields.remove(exclude_field)
#         return fields
#
#     def create(self, validated_data):
#         admin = Admin(**validated_data)
#         admin.set_password(validated_data['password'])
#         admin.save()
#         del admin.password
#         return admin
#
#
# class AdminUpdateSerializer(DefaultModelSerializer):
#     password = serializers.CharField(max_length=100, help_text='密碼', write_only=True)
#
#     class Meta:
#         model = Admin
#         fields = ['password']
#
#     def update(self, instance, validated_data):
#         instance.set_password(validated_data['password'])
#         instance.updated_at = timezone.now()
#         instance.save()
#         del instance.password
#         return instance
#
#
# class FeeRatioSerializer(DefaultModelSerializer):
#     date = serializers.DateTimeField(source='created_at', read_only=True)
#
#     class Meta(CommonMeta):
#         model = FeeRatio
#
#
# class ProfitSerializer(DefaultModelSerializer):
#     fee = FeeRatioSerializer(many=False, read_only=True)
#     date = serializers.DateTimeField(source='created_at', read_only=True)
#
#     class Meta(CommonMeta):
#         model = Profit
#
#     def get_field_names(self, declared_fields, info):
#         if self.context.get('view') and self.context.get('view').action == 'create':
#             fields = ['earn_money']
#             return fields
#         return super().get_field_names(declared_fields, info)
#
#     def validate(self, attrs):
#         queryset = ProductProfit.objects.filter(enabled=True, profit=None)
#         if queryset.count() == 0:
#             raise serializers.ValidationError('還沒有輸入資金異動')
#         return attrs
#
#     @transaction.atomic
#     def create(self, validated_data):
#         product_queryset = Product.objects.filter(enabled=True, settlement=False)
#         product_ids = [product.id for product in product_queryset]
#
#         # validate
#         productprofit_queryset = ProductProfit.objects.filter(enabled=True, product_id__in=product_ids, profit=None)
#
#         # init productprofit data
#         productprofit_product_ids = []
#         adjustment_amounts = 0
#
#         for productprofit in productprofit_queryset:
#             productprofit_product_ids.append(productprofit.product.id)
#             adjustment_amounts += productprofit.adjustment_amount
#
#         # 確認新product 金額，如果還沒有被新增profit 要加入profit 原始總金額 並且更新in_profit
#         new_product_amount = 0
#         newproduct_queryset = product_queryset.filter(in_profit=False)
#         for product in newproduct_queryset:
#             new_product_amount += product.amount
#             product.in_profit = True
#             product.save()
#
#         # init profit data
#         feeratio = FeeRatio.objects.filter(enabled=True).first()
#         last_profit = Profit.objects.filter(enabled=True).first()
#         last_original_amount = 0 if not last_profit else last_profit.latest_amount
#         # 手續費為正值
#         fee_money = round(validated_data['earn_money'] * feeratio.fee_percent)
#         fee_money = abs(fee_money)
#         net_profit = round(validated_data['earn_money'] - fee_money)
#         original_amount = last_original_amount + adjustment_amounts + new_product_amount
#         latest_amount = original_amount + net_profit
#
#         # create profit
#         profit = Profit.objects.create(
#             original_amount=original_amount,
#             latest_amount=latest_amount,
#             fee=feeratio,
#             fee_money=fee_money,
#             earn_money=validated_data['earn_money'],
#             net_profit=net_profit,
#         )
#         # update productprofit
#         all_latest_amount = 0
#         for productprofit in productprofit_queryset:
#             productprofit.profit = profit
#             productprofit.net_profit = round(net_profit * productprofit.original_percent)
#
#             last_productprofit = ProductProfit.objects.filter(~Q(profit=None), product=productprofit.product,
#                                                               enabled=True).first()
#             laat_cumulative_profit = 0 if not last_productprofit else last_productprofit.cumulative_profit
#             productprofit.cumulative_profit = productprofit.net_profit + laat_cumulative_profit
#             if productprofit.product.is_strategy:
#                 productprofit.latest_amount = productprofit.original_amount + productprofit.net_profit
#             else:
#                 productprofit.latest_amount = productprofit.original_amount
#             all_latest_amount += productprofit.latest_amount
#         for productprofit in productprofit_queryset:
#             productprofit.latest_percent = round(productprofit.latest_amount / all_latest_amount, 3)
#             productprofit.save()
#         return profit
#
#
# class ProductProfitSerializer(DefaultModelSerializer):
#     product = serializers.HiddenField(default=hiddenfield_factory(Product))
#     date = serializers.DateTimeField(source='created_at', read_only=True)
#
#     class Meta(CommonMeta):
#         model = ProductProfit
#
#
# class ProductSerializer(DefaultModelSerializer):
#     units = serializers.FloatField(help_text='投入單位', read_only=True)
#     unique_site = serializers.CharField(read_only=True, max_length=30, help_text='網址')
#     latest_productprofit = serializers.SerializerMethodField()
#     amount_and_all_adjustment = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Product
#         exclude = [
#             'enabled',
#             'created_at',
#             'updated_at',
#             'deleted_at',
#             'in_profit',
#             'settlement',
#             'from_product'
#         ]
#
#     def get_amount_and_all_adjustment(self, instance):
#         if 'request' not in self.context:
#             return
#         # check 要不要新增 latest_productprofit
#         request = self.context['request']
#         latest_productprofit_bool = request.query_params.get('latest_productprofit', False)
#         if latest_productprofit_bool == 'false':
#             latest_productprofit_bool = False
#         elif latest_productprofit_bool == 'true':
#             latest_productprofit_bool = True
#         if not latest_productprofit_bool:
#             return
#
#         queryset = instance.productprofit.filter(enabled=True)
#         ret = instance.amount
#         for q in queryset:
#             ret += q.adjustment_amount
#         return ret
#
#     def get_latest_productprofit(self, instance):
#         if 'request' not in self.context:
#             return
#         # check 要不要新增 latest_productprofit
#         request = self.context['request']
#         latest_productprofit_bool = request.query_params.get('latest_productprofit', False)
#         if latest_productprofit_bool == 'false':
#             latest_productprofit_bool = False
#         elif latest_productprofit_bool == 'true':
#             latest_productprofit_bool = True
#         if not latest_productprofit_bool:
#             return
#         instance.productprofit.first()
#         latest_productprofit = instance.productprofit.filter(~Q(profit=None), enabled=True, ).first()
#
#         return ProductProfitSerializer(latest_productprofit).data if latest_productprofit else None
#
#     def validate(self, attrs):
#         if self.context['view'].action == 'create' or self.context['view'].action == 'productsettlement':
#             queryset = ProductProfit.objects.filter(enabled=True, profit=None)
#             if queryset.count():
#                 raise serializers.ValidationError('還未新增獲利')
#         if self.context['view'].action in ['partial_update', 'update']:
#             queryset = ProductProfit.objects.filter(enabled=True, product=self.instance)
#             if queryset.count():
#                 raise serializers.ValidationError('該商品已經新增ProductProfit 無法再修改金額')
#
#         return attrs
#
#
# class ProductSettlementSerializer(UpdateRequiredSerailizerMixin, serializers.Serializer):
#     amount = serializers.IntegerField(help_text='結算後的金額 如為0 就是全部領出')
#     from_product = serializers.IntegerField(help_text='結算的product id')
#     is_strategy = serializers.BooleanField(default=True, help_text='是否波段')
#
#     def validate(self, attrs):
#         self.queryset = Product.objects.filter(pk=attrs['from_product'], enabled=True, settlement=False)
#         if not self.queryset.count():
#             raise serializers.ValidationError('錯誤的product_id')
#         return attrs
#
#     def create(self, validated_data):
#         old_proudct = self.queryset.first()
#         old_proudct.settlement = True
#         old_proudct.save()
#
#         new_product = Product(name=old_proudct.name, amount=validated_data['amount'],
#                               is_strategy=validated_data['is_strategy'], from_product=old_proudct)
#         new_product.save()
#         self.instance = new_product
#         return self.instance
#
#     def update(self, instance, validated_data):
#         pass
#
#
# class ProductSettlementListSerializer(serializers.Serializer):
#     data = ProductSettlementSerializer(many=True)
#
#     def create(self, validated_data):
#         ret = []
#         for item in validated_data['data']:
#             s = ProductSettlementSerializer(data=item)
#             s.is_valid(raise_exception=True)
#             instance = s.create(item)
#             ret.append(instance)
#         return ret
#
#     def update(self, instance, validated_data):
#         pass
#
#
# class ProfitTestSerializer(ProductSerializer):
#     def get_latest_productprofit(self, isntance):
#         isntance.productprofit.first()
#         latest_productprofit = isntance.productprofit.filter(~Q(profit=None), enabled=True, ).first()
#
#         return ProductProfitSerializer(latest_productprofit).data if latest_productprofit else None
#
#
# class ProductProfitCreateDataSerializer(UpdateRequiredSerailizerMixin, serializers.Serializer):
#     product_id = serializers.IntegerField(help_text='product.id')
#     adjustment_amount = serializers.IntegerField(help_text='異動金額')
#
#     def create(self, validated_data):
#         pass
#
#     def update(self, instance, validated_data):
#         pass
#
#
# class ProductProfitCreateSerializer(DefaultModelSerializer):
#     datas = ProductProfitCreateDataSerializer(many=True, write_only=True,
#                                               help_text="ex: [{'product_id': 4, 'adjustment_amount': 500000}]")
#
#     class Meta(CommonMeta):
#         model = ProductProfit
#
#     def to_internal_value(self, data):
#         def try_json(val):
#             if isinstance(val, list):
#                 ret = []
#                 for item in val:
#                     try:
#                         ret.append(json.loads(item.replace('\'', '"')))
#                     except Exception as e:
#                         ret.append(item)
#             else:
#                 try:
#                     ret = json.loads(val)
#                 except Exception as e:
#                     ret = val
#             return ret
#
#         if isinstance(data, QueryDict):
#             data = {k: try_json(v[0]) if len(v) == 1 else try_json(v) for k, v in data.lists()}
#         return super().to_internal_value(data)
#
#     def get_field_names(self, declared_fields, info):
#         fields = super().get_field_names(declared_fields, info)
#         if self.context.get('view') and self.context['view'].action == 'create':
#             fields = ['datas']
#         return fields
#
#     def validate(self, attrs):
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         if queryset.count() != len(attrs['datas']):
#             raise serializers.ValidationError(detail='商品數量不一致')
#         queryset = ProductProfit.objects.filter(enabled=True, profit=None)
#         if queryset.count():
#             raise serializers.ValidationError(detail='還沒有輸入獲利')
#         return attrs
#
#     @transaction.atomic
#     def create(self, validated_data):
#         # validate
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         if queryset.count() != len(validated_data['datas']):
#             raise serializers.ValidationError(detail='商品數量不一致')
#
#         instance_list = []
#         all_last_amount = 0
#         for dct in validated_data['datas']:
#             product = queryset.get(pk=dct['product_id'])
#             last_instance = ProductProfit.objects.filter(enabled=True, product=product).first()
#             if last_instance and not last_instance.profit:
#                 raise serializers.ValidationError(detail='還沒有新增獲利')
#             last_amount = last_instance.latest_amount if last_instance else product.amount
#             try:
#                 last_amount += dct['adjustment_amount']
#             except Exception as e:
#                 print()
#
#             all_last_amount += last_amount
#             instance = ProductProfit.objects.create(
#                 original_amount=last_amount,
#                 product=product,
#                 adjustment_amount=dct['adjustment_amount'],
#             )
#             instance_list.append(instance)
#         for instance in instance_list:
#             instance.original_percent = round(instance.original_amount / all_last_amount, 3)
#             instance.save()
#         return instance_list
