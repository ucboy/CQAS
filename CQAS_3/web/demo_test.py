import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()


def main():
    from api.models import (Token, Admin, Product,
                            Profit, ProductProfit, FeeRatio)
    from django.contrib.auth.models import User
    from api import serializers

    # create product
    products = Product.objects.filter(enabled=True, settlement=False)

    # create productprofit
    productprofit = dict(datas=[dict(product_id=product.id, adjustment_amount=500000) for product in products])
    data = {'datas': [{'product_id': 4, 'adjustment_amount': 500000}, {'product_id': 3, 'adjustment_amount': 500000},
                      {'product_id': 2, 'adjustment_amount': 500000}, {'product_id': 1, 'adjustment_amount': 500000}]}
    serializer = serializers.ProductProfitCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # create profit


if __name__ == '__main__':
    main()
