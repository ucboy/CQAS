import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()


def main():
    from api.models import (AdminTokens, Admin, Product,
                            Profit, ProductProfit, FeeRatio)
    from django.contrib.auth.models import User
    from api import serializers
    from django.utils import timezone

    # create admin
    user = User.objects.create_user('admin', password='1111')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    # create setting
    FeeRatio.objects.create(fee_percent=0.5, memo='預設')

    # create user
    admin = Admin(email='max@conquers.co', password='1111')
    admin.set_password(admin.password)
    admin.created_at = timezone.now()
    admin.save()
    # default key
    AdminTokens.objects.create(user=admin, key='1111')

    for i in range(50):
        admin = Admin(email=f'max{i}@conquers.co', password='1111')
        admin.set_password(admin.password)
        admin.created_at = timezone.now()
        admin.save()

    # create product
    datas = [
        dict(name='LUC',
             amount=500000, is_strategy=True),
        dict(name='FON', amount=1063385, is_strategy=True),
        dict(name='RDD', amount=1000000, is_strategy=False),
        dict(name='CHC', amount=1063385, is_strategy=True),
        dict(name='LOA', amount=500000, is_strategy=False),
        dict(name='LEC', amount=531693, is_strategy=True),
        dict(name='SHD', amount=6380307, is_strategy=True),
    ]
    products = []
    for data in datas[::-1]:
        instance = Product.objects.create(**data)
        products.append(instance)
    for i in range(50):
        # create productprofit
        productprofit = dict(datas=[dict(product_id=product.id, adjustment_amount=500000) for product in products])
        serializer = serializers.ProductProfitCreateSerializer(data=productprofit)
        serializer.create(productprofit)
        # create profit
        validated_data = {'earn_money': 500000}
        serializer = serializers.ProfitSerializer(data=validated_data)
        serializer.create(validated_data)


if __name__ == '__main__':
    main()
