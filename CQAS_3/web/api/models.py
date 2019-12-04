import datetime
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser, PermissionsMixin
from django.db import models
from rest_framework.authtoken.models import Token as DefaultToken
from rest_framework import exceptions


class AdminTokens(DefaultToken):
    user = models.ForeignKey(
        'Admin', related_name='auth_token', on_delete=models.CASCADE,
    )

    def expired(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return now > self.created + datetime.timedelta(days=7)


class DefaultAbstract(models.Model):
    enabled = models.BooleanField(default=True, help_text='軟刪除')
    created_at = models.DateTimeField(auto_now_add=True, help_text="建立時間")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新時間", null=True)
    deleted_at = models.DateTimeField(help_text="刪除時間", null=True, blank=True)

    class Meta:
        abstract = True
        # todo check 是否要updated_at
        # ordering = ['-updated_at', '-created_at']
        ordering = ['-created_at']


class Admin(DefaultAbstract, AbstractBaseUser):
    email = models.CharField(max_length=256, unique=True, help_text='登入帳號Email')
    password = models.CharField(max_length=100, help_text='密碼')

    def __str__(self):
        return f'Admin(email={self.email})'


class Department(DefaultAbstract):
    name = models.CharField(max_length=64,help_text="部門名稱")

    class Meta:
        db_table = "Department"


class Permission(DefaultAbstract):
    name = models.CharField(max_length=64,help_text="角色權限名稱",unique=True)
    description = models.CharField(max_length=256, help_text="角色權限描述",null=True)
    role_manage = models.SmallIntegerField(default=0,help_text="帳號權限")
    daily_rate = models.SmallIntegerField(default=0,help_text="每日考核權限")
    report = models.SmallIntegerField(default=0,help_text="考核報表權限")

    class Meta:
        db_table = "Permission"


class User(DefaultAbstract):
    employee_number = models.CharField(max_length=32,unique=True,help_text="員工編號")
    account = models.EmailField(max_length=32,unique=True,help_text="員工帳號(信箱)")
    password = models.CharField(max_length=64,help_text="員工密碼")
    cn_name = models.CharField(max_length=64,help_text="員工中文姓名")
    en_name = models.CharField(max_length=64, help_text="員工英文姓名")
    department = models.ForeignKey(Department, related_name="User",on_delete=models.CASCADE,help_text="部門編號")
    status = models.BooleanField(help_text="員工啟用狀態")
    permission = models.ForeignKey(Permission, related_name="User",on_delete=models.CASCADE,help_text="權限編號")
    remarks = models.CharField(max_length=1024,null=True,help_text="備註")
    entry_date = models.DateField(help_text="入職時間", null=True, blank=True)
    leave_date = models.DateField\
        (help_text="離職時間", null=True, blank=True)

    class Meta:
        db_table = "User"


class WorkDate(DefaultAbstract):
    date = models.DateField(help_text="日期")
    status = models.BooleanField(help_text="狀態")

    class Meta:
        db_table = "WorkDate"


class DayScore(DefaultAbstract):
    rate_day = models.DateField(help_text="考核日期")
    user = models.ForeignKey(User, related_name="owner_DayScore",on_delete=models.CASCADE, help_text="員工流水號")
    complete_score = models.FloatField(help_text="完成度分數")
    quality_score = models.FloatField(help_text="品質分數")
    special_score = models.FloatField(help_text="特殊分數")
    attitude_score = models.FloatField(help_text="態度分數")
    error_mark = models.IntegerField(help_text="錯誤標記",default=0)
    avg_score = models.FloatField(help_text="日考核平均分數",null=True)
    manager = models.ForeignKey(User, related_name="rate_DayScore",on_delete=models.CASCADE,help_text="考核主管編號")
    status = models.BooleanField(help_text="考核狀態")

    class Meta:
        db_table = "DayScore"


class MonthScore(DefaultAbstract):
    rate_month = models.CharField(max_length=16,help_text="考核月份")
    user = models.ForeignKey(User, related_name="MonthScore",on_delete=models.CASCADE,help_text="員工流水號")
    complete_score = models.FloatField(help_text="完成度分數")
    quality_score = models.FloatField(help_text="品質分數")
    special_score = models.FloatField(help_text="特殊分數")
    attitude_score = models.FloatField(help_text="態度分數")
    error_mark = models.IntegerField( help_text="錯誤標記")
    avg_score = models.FloatField(help_text="月考核平均分數")
    bunus = models.IntegerField(null=True,help_text="月獎金")

    class Meta:
        db_table = "MonthScore"


class SeasonScore(DefaultAbstract):
    rate_season = models.CharField(max_length=16,help_text="考核季")
    user = models.ForeignKey(User, related_name="SeasonScore",on_delete=models.CASCADE, help_text="員工流水號")
    complete_score = models.FloatField(help_text="完成度分數")
    quality_score = models.FloatField(help_text="品質分數")
    special_score = models.FloatField(help_text="特殊分數")
    attitude_score = models.FloatField(help_text="態度分數")
    avg_score = models.FloatField(help_text="季考核平均分數")

    class Meta:
        db_table = "SeasonScore"


class RewardsAndPunishments(DefaultAbstract):
    year_month = models.CharField(max_length=16,help_text="年度月份")
    user = models.ForeignKey(User, related_name="RewardsAndPunishments",on_delete=models.CASCADE, help_text="員工流水號")
    record = models.CharField(max_length=128,help_text="紀錄")
    description = models.CharField(max_length=128,help_text='補充')

    class Meta:
        db_table = "RewardsAndPunishments"


# class Product(DefaultAbstract):
#     name = models.CharField(max_length=30, help_text='商品名稱')
#     amount = models.IntegerField(help_text='投入金額')
#     is_strategy = models.BooleanField(default=True, help_text='是否波段')
#     units = models.FloatField(null=True, help_text='投入單位')
#     unique_site = models.CharField(unique=True, max_length=50, help_text='網址')
#     in_profit = models.BooleanField(default=False, help_text='紀錄profit是否將該productamount加進去')
#     from_product = models.ForeignKey('Product', null=True, related_name='+', on_delete=models.SET_NULL,
#                                      help_text='從哪個商品結算而來')
#
#     settlement = models.BooleanField(default=False, help_text='是否結算')
#
#     class Meta:
#         ordering = ['created_at']
#
#     def save(self, force_insert=False, force_update=False, using=None,
#              update_fields=None):
#         if not self.units:
#             self.units = round(self.amount / 500000, 3)
#         if not self.unique_site:
#             import uuid
#             unique_site = str(uuid.uuid4())
#             while Product.objects.filter(unique_site=unique_site):
#                 unique_site = str(uuid.uuid4())
#
#             self.unique_site = unique_site
#         return super().save(force_insert, force_update, using)
#
#     def __str__(self):
#         return f'Proudct(name={self.name}, amount={self.amount}, is_strategy={self.is_strategy})'
#
#
# class Admin(DefaultAbstract, AbstractBaseUser):
#     email = models.CharField(max_length=256, unique=True, help_text='登入帳號Email')
#     password = models.CharField(max_length=100, help_text='密碼')
#
#     def __str__(self):
#         return f'Admin(email={self.email})'
#
#
# class FeeRatio(DefaultAbstract):
#     fee_percent = models.FloatField(help_text='手續比例')
#     memo = models.CharField(max_length=100, help_text='比例用途')
#
#     def __str__(self):
#         return f'FeeRatio(fee_percent={self.fee_percent}, memo={self.memo})'
#
#
# class Profit(DefaultAbstract):
#     original_amount = models.IntegerField(help_text='原始總金額')
#     latest_amount = models.IntegerField(help_text='最新總金額')
#     fee = models.ForeignKey(FeeRatio, related_name='profit', on_delete=models.CASCADE, help_text='feeratio:fk')
#     fee_money = models.IntegerField(help_text='手續費用')
#     earn_money = models.IntegerField(help_text='淨獲利')
#     net_profit = models.IntegerField(help_text='實收金額')
#
#     def __str__(self):
#         return f'Profit(original_amount={self.original_amount}, latest_amount={self.latest_amount}, fee_money={self.fee_money}, earn_money={self.earn_money}, net_profit={self.net_profit})'
#
#
# class ProductProfit(DefaultAbstract):
#     product = models.ForeignKey(Product, related_name='productprofit', on_delete=models.CASCADE,
#                                 help_text='商品fk')
#     profit = models.ForeignKey(Profit, null=True, on_delete=models.SET_NULL, help_text='獲利')
#     original_amount = models.IntegerField(null=True, help_text='原始金額')
#     original_percent = models.FloatField(null=True, help_text='原始比例')
#     net_profit = models.IntegerField(null=True, help_text='實收獲利')
#     cumulative_profit = models.IntegerField(null=True, help_text='累積獲利')
#     latest_amount = models.IntegerField(null=True, help_text='最新金額')
#     latest_percent = models.FloatField(null=True, help_text='最新比例')
#     adjustment_amount = models.IntegerField(help_text='投資異動')
#
#     def __str__(self):
#         proudct_name = self.product.name if self.product else ''
#         return f'ProductProfit(product={proudct_name}, original_amount={self.original_amount}, original_percent={self.original_percent}, net_profit={self.net_profit})'
