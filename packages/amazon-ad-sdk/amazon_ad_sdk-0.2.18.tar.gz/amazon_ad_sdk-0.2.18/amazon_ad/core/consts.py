# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

ACCOUNT_TYPES = ["agency", "vendor", "seller"]

REGIONS_ENDPOINTS = {
    "NA": {
        "AUTHORIZATION": "https://www.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.com/auth/o2/token",
        "API": "https://advertising-api.amazon.com",
    },
    "EU": {
        "AUTHORIZATION": "https://eu.account.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.co.uk/auth/o2/token",
        "API": "https://advertising-api-eu.amazon.com",
    },
    "FE": {
        "AUTHORIZATION": "https://apac.account.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.co.jp/auth/o2/token",
        "API": "https://advertising-api-fe.amazon.com",
    },
    "SANDBOX": {
        "AUTHORIZATION": "https://www.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.com/auth/o2/token",
        "API": "https://advertising-api-test.amazon.com",
    }
}

COUNTRIES_REGION = (
    ('US', 'NA'),
    ('CA', 'NA'),
    ('MX', 'NA'),  # 墨西哥
    ('BR', 'NA'),  # 巴西

    ('UK', 'EU'),
    ('DE', 'EU'),
    ('FR', 'EU'),
    ('IT', 'EU'),
    ('ES', 'EU'),
    ('AE', 'EU'),  # 阿联酋
    ('PL', 'EU'),  # 波兰
    ('NL', 'EU'),  # 尼德兰
    ('SE', 'EU'),  # 瑞典
    ('TR', 'EU'),  # 土耳其
    ('EG', 'EU'),  # 埃及
    ('SA', 'EU'),  # 沙特阿拉伯
    ('BE', 'EU'),  # 比利时
    ('IN', 'EU'),  # 印度
    ('ZA', 'EU'),  # 南非
    ('IE', 'EU'),  # 爱尔兰

    ('JP', 'FE'),
    ('AU', 'FE'),
    ('SG', 'FE'),  # 新加坡
    ('SANDBOX', 'SANDBOX'),
)

