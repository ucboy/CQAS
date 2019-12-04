# from rest_framework.test import APITestCase
# from .models import *
# from . import serializers
# from rest_framework.test import APIClient
# from django.core.management import call_command
# from pprint import pprint
# import datetime
# import json
# from django.db.models import Q
#
#
# class DefaultTestMixin():
#     @classmethod
#     def setUpTestData(cls):
#         from run_init import main
#         main()
#         cls.noauth_client = APIClient()
#         cls.super_client = APIClient()
#         cls.super_client.credentials(HTTP_AUTHORIZATION='Token ' + '1111')
#
#     def init_profit_list(self):
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         for i in range(30):
#             # create productprofit
#             url = f'/productprofit/'
#             data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#             data = dict(datas=data)
#             r = self.super_client.post(url, data=data)
#             # create profit
#             url = f'/profit/'
#             data = dict(earn_money=500000)
#             r = self.super_client.post(url, data=data)
#
#
# class TestAdmin(DefaultTestMixin, APITestCase):
#
#     def test_admin_login(self):
#         url = f'/admin/login/'
#         # check ok
#         data = dict(
#             email='max@conquers.co',
#             password='1111'
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 200)
#         self.assertTrue('token' in r.data)
#         # check not ok
#         data = dict(
#             email='max@conquers.co',
#             password='1111222'
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 403)
#         self.assertTrue('帳號或密碼錯誤' in r.data)
#         data = dict(
#             email='max123@conquers.co',
#             password='1111'
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 403)
#         self.assertTrue('帳號或密碼錯誤' in r.data)
#
#     def test_admin_logout(self):
#         url = f'/admin/logout/'
#         # check ok
#         admin = Admin.objects.get(email='max@conquers.co')
#         query = AdminTokens.objects.filter(user=admin)
#         self.assertTrue(len(query) == 1)
#         r = self.super_client.post(url)
#         self.assertEqual(r.status_code, 200)
#         # check token is killed
#         query = AdminTokens.objects.filter(user=admin)
#         self.assertTrue(len(query) == 0)
#
#     def test_admin_list(self):
#         url = f'/admin/'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, list)
#
#     def test_admin_create(self):
#         url = f'/admin/'
#         # check ok
#         data = dict(
#             email='max123@conquers.co',
#             password='1111'
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#         self.assertTrue('passwrod' not in r.data)
#         # check user password hashed
#         instance = Admin.objects.get(pk=r.data['id'])
#         self.assertTrue(len(instance.password) > 50)
#         # check same account
#         data = dict(
#             email='max@conquers.co',
#             password='1111'
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 400)
#         # check same account msg
#         self.assertEqual(r.data['email'][0], 'Email已經被註冊')
#
#     def test_admin_update(self):
#         url = f'/admin/'
#         # check ok
#         data = dict(
#             email='max123@conquers.co',
#             password='1111'
#         )
#         r = self.super_client.post(url, data=data)
#         data_id = r.data['id']
#         url = f'/admin/{data_id}/'
#         data = dict(
#             password='1111'
#         )
#         r = self.super_client.put(url, data=data)
#         self.assertEqual(r.status_code, 200)
#         self.assertEqual(r.data['msg'], 'success')
#
#
# class TestStatus(DefaultTestMixin, APITestCase):
#     def test_before_productprofit_create(self):
#         url = f'/productprofitstatus/'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertEqual(r.data['productprofit'], False)
#
#     def test_after_productprofit_create(self):
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         url = f'/productprofitstatus/'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertEqual(r.data['productprofit'], True)
#
#     def test_after_profit_create(self):
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         # profit
#         url = f'/profit/'
#         data = dict(earn_money=500000)
#         r = self.super_client.post(url, data=data)
#
#         url = f'/productprofitstatus/'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertEqual(r.data['productprofit'], False)
#
#
# class TestProduct(DefaultTestMixin, APITestCase):
#     def test_product_create(self):
#         url = f'/products/'
#         # create product
#         data = dict(
#             name='SHD',
#             amount=500000,
#             is_strategy=True,
#         )
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#         # check units
#         self.assertTrue('units' in r.data)
#         # auto create unique_site
#         self.assertTrue('unique_site' in r.data)
#
#     def test_product_create_settlement(self):
#         products = Product.objects.filter(settlement=False)
#         data = []
#         data_ids = []
#         for instance in products:
#             data_ids.append(instance.id)
#             data.append(dict(amount=50, from_product=instance.id, is_strategy=True))
#         url = f'/products/productsettlement/'
#         r = self.super_client.post(url, data=dict(data=data))
#         self.assertEqual(r.status_code, 201)
#         self.assertEqual(len(Product.objects.filter(from_product__in=data_ids)), len(data_ids))
#
#     def test_product_create_after_productprofit_create(self):
#         url = f'/products/'
#         # create product
#         data = dict(
#             name='SHD',
#             amount=500000,
#             is_strategy=True,
#         )
#         r = self.super_client.post(url, data=data)
#
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         url = f'/products/'
#         # create product
#         data = dict(
#             name='SHD',
#             amount=500000,
#             is_strategy=True,
#         )
#         r = self.super_client.post(url, data=data)
#
#     def test_product_list(self):
#         self.init_profit_list()
#         url = f'/products/'
#         # check has product
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, list)
#         # check not latest_productprofit
#         product = r.data[0]
#         self.assertIsNone(product['latest_productprofit'])
#
#     def test_product_latest(self):
#         self.init_profit_list()
#         url = f'/products/?latest_productprofit=true'
#         # check has product
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, list)
#         # check not latest_productprofit
#         product = r.data[0]
#         self.assertIsInstance(product['latest_productprofit'], dict)
#
#     def test_product_retrieve_noauth(self):
#         self.init_profit_list()
#         product = Product.objects.filter(enabled=True, settlement=False).first()
#         url = f'/noauth/products/{product.unique_site}/'
#         # check has product
#         r = self.noauth_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, dict)
#         # check not latest_productprofit
#         product = r.data
#         self.assertIsNone(product['latest_productprofit'])
#
#     def test_product_update(self):
#         self.init_profit_list()
#         # check update fail
#         product = Product.objects.filter(enabled=True, settlement=False).first()
#         url = f'/products/{product.id}/'
#         r = self.super_client.put(url, data=dict(amount=1000000))
#         self.assertEqual(r.status_code, 400)
#         # check product update sucess
#         instance = Product.objects.create(name='SHD', amount=6380307, is_strategy=True)
#         url = f'/products/{instance.id}/'
#         r = self.super_client.put(url, data=dict(amount=1000000))
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, dict)
#         # check auth fail
#         r = self.noauth_client.put(url, data=dict(amount=1000000))
#         self.assertEqual(r.status_code, 401)
#
#     def test_product_retrieve_latest(self):
#         self.init_profit_list()
#         product = Product.objects.filter(enabled=True, settlement=False).first()
#         url = f'/noauth/products/{product.unique_site}/?latest_productprofit=true'
#         # check has product
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, dict)
#         # check not latest_productprofit
#         product = r.data
#         self.assertIsInstance(product['latest_productprofit'], dict)
#
#     def test_product_latest_fake(self):
#         self.init_profit_list()
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         url = f'/products/fake/?profit=500000'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         product = r.data[0]
#         self.assertIsInstance(product['latest_productprofit'], dict)
#         self.assertIsNone(ProductProfit.objects.filter(pk=product['latest_productprofit']['id']).first().profit)
#
#
# class TestProfit(DefaultTestMixin, APITestCase):
#     def test_profit_listpage(self):
#         self.init_profit_list()
#         url = f'/profit/?limit=10&offset=10'
#         # check limit offset
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertTrue('count' in r.data)
#         self.assertTrue('results' in r.data)
#         self.assertIsInstance(r.data['results'], list)
#
#     def test_profit_create(self):
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         # check ok
#         url = f'/profit/'
#         data = dict(earn_money=500000)
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#
#     def test_pfofit_create_newproduct(self):
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         # create profit
#         url = f'/profit/'
#         data = dict(earn_money=500000)
#         r = self.super_client.post(url, data=data)
#
#         # new product
#         url = f'/products/'
#         data = dict(
#             name='SHD',
#             amount=500000,
#             is_strategy=True,
#         )
#         r = self.super_client.post(url, data=data)
#
#         url = f'/productprofit/'
#         # create productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#
#         # check ok
#         url = f'/profit/'
#         data = dict(earn_money=500000)
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#         # check no productprofit 是孤魂野鬼
#         queryset = ProductProfit.objects.filter(profit=None, enabled=True)
#         self.assertEqual(queryset.count(), 0)
#
#
# class TestProductProfit(DefaultTestMixin, APITestCase):
#     def test_productprofit_listpage(self):
#         self.init_profit_list()
#         product = Product.objects.filter(enabled=True, settlement=False).first()
#         url = f'/products/{product.id}/productprofit/?limit=10&offset=10'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertTrue('count' in r.data)
#         self.assertTrue('results' in r.data)
#         self.assertIsInstance(r.data['results'], list)
#
#     def test_productprofit_create(self):
#         url = f'/productprofit/'
#         # first productprofit
#         queryset = Product.objects.filter(enabled=True, settlement=False)
#         # create init data
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#         self.assertIsInstance(r.data, list)
#         # before profit
#         data = [dict(product_id=product.id, adjustment_amount=500000) for product in queryset]
#         data = dict(datas=data)
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 400)
#
#
# class TestFeeRatio(DefaultTestMixin, APITestCase):
#     def test_feeratio_list(self):
#         instance = FeeRatio.objects.create(fee_percent=0.2)
#         url = f'/feeratio/'
#         r = self.super_client.get(url)
#         self.assertEqual(r.status_code, 200)
#         self.assertIsInstance(r.data, list)
#
#     def test_feeratio_create(self):
#         url = f'/feeratio/'
#         data = dict(fee_percent=0.3, memo='Default')
#         r = self.super_client.post(url, data=data)
#         self.assertEqual(r.status_code, 201)
#         self.assertIsInstance(r.data, dict)
