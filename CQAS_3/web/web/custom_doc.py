from rest_framework.renderers import DocumentationRenderer
from django.template import loader


class MyDocumentationRenderer(DocumentationRenderer):
    template = 'custom_docs/index.html'


api_doc_header = {
    'admin': [
        ('create', 'AdminCreate'),
        ('login', 'AdminLogin'),
        ('logout', 'AdminLogout'),
        ('list', 'AdminGetAll'),
        ('update', 'AdminUpdate'),
    ],
    'Department': [
        ('list', 'DepartmentGetAll'),
        ('create', 'DepartmentCreate'),
        ('update', 'DepartmentUpdate'),
    ],
    'Permission': [
        ('list', 'PermissionGetAll'),
        ('create', 'PermissionCreate'),
        ('update', 'PermissionUpdate'),
    ],
    'User': [
        ('list', 'UserGetAll'),
        ('create', 'UserCreate'),
        ('update', 'UserUpdate'),
    ],
    'WorkDate': [
        ('list', 'WorkDateGetAll'),
        ('create', 'WorkDateCreate'),
        ('update', 'WorkDateUpdate'),
    ],
    'DayScore': [
        ('list', 'DayScoreGetAll'),
        ('create', 'DayScoreCreate'),
        ('update', 'DayScoreUpdate'),
    ],
    'MonthScore': [
        ('list', 'MonthScoreGetAll'),
        ('create', 'MonthScoreCreate'),
        ('update', 'MonthScoreUpdate'),
    ],
    'SeasonScore': [
        ('list', 'SeasonScoreGetAll'),
        ('create', 'SeasonScoreCreate'),
        ('update', 'SeasonScoreUpdate'),
    ],
    'RewardsAndPunishments': [
        ('list', 'RewardsAndPunishmentsGetAll'),
        ('create', 'RewardsAndPunishmentsCreate'),
        ('update', 'RewardsAndPunishmentsUpdate'),
    ],
    # 'noauth': [
    #     ('products>read', 'ProductGet'),
    # ],
    # 'productprofit': [
    #     ('create', 'ProductProfitCreate'),
    # ],
    # 'productprofitstatus': [
    #     ('list', 'ProductProfitStatus'),
    # ],
    # 'products': [
    #     ('list', 'ProductGetAll'),
    #     ('create', 'ProductCreate'),
    #     ('update', 'ProductUpdate'),
    #     ('productsettlement', 'ProductSettlementCreate'),
    #     ('fake>list', 'ProductFake'),
    #     ('productprofit>list', 'UserProductProfitGetAll')
    # ],
    # 'profit': [
    #     ('list', 'ProfitGetAll'),
    #     ('create', 'ProfitCreate'),
    # ],
}


def update_schema(schema):
    # for key in api_doc_header:
    #     for before, after in api_doc_header[key]:
    #         if len(before.split('>')) == 1:
    #             if before not in schema._data[key]._data:
    #                 continue
    #             schema._data[key]._data[after] = schema._data[key]._data[before]
    #             del schema._data[key]._data[before]
    #         elif len(before.split('>')) == 2:
    #             before_1, before_2 = before.split('>')
    #             if (before_1 not in schema._data[key]._data
    #                     or before_2 not in schema._data[key]._data[before_1]):
    #                 continue
    #             schema._data[key]._data[after] = schema._data[key]._data[before_1]._data[before_2]
    #             del schema._data[key]._data[before_1]._data[before_2]
    #         elif len(before.split('>')) == 3:
    #             before_1, before_2, before_3 = before.split('>')
    #             if (before_1 not in schema._data[key]._data
    #                     or before_2 not in schema._data[key]._data[before_1]
    #                     or beofre_3 not in schema._data[key]._data[before_1]._data[before_2]):
    #                 continue
    #             schema._data[key]._data[after] = schema._data[key]._data[before_1]._data[before_2]._data[before_3]
    #             del schema._data[key]._data[before_1]._data[before_2]._data[before_3]
    return schema
