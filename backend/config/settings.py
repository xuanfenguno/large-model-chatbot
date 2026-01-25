"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-80e!v$n3m6*y39_#r-8t+9_!x_1y#zq9@*#r0i$y%j#f#g#h')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 统一错误处理中间件
    'chatbot.middleware.ErrorHandlingMiddleware',
    # 性能监控中间件
    'config.middleware.performance.PerformanceMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# 尝试连接MySQL，如果失败则使用SQLite作为备选
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    
    # 首先尝试连接到MySQL以确认凭据是否正确
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root123'),
        charset='utf8mb4'
    )
    
    # 检查数据库是否存在，如果不存在则尝试创建
    with connection.cursor() as cursor:
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        target_db = os.getenv('DB_NAME', 'chatbot_db')
        
        if (target_db,) not in [db for db in databases]:
            # 数据库不存在，尝试创建
            try:
                cursor.execute(f"CREATE DATABASE `{target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                print(f"MySQL数据库 '{target_db}' 已创建成功!")
            except Exception as e:
                print(f"创建MySQL数据库 '{target_db}' 失败: {e}")
    
    connection.close()
    
    # 如果连接成功，则使用MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'chatbot_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'root123'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
            'TEST': {
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            },
        }
    }
except Exception as e:
    # 如果MySQL连接失败（无论是因为模块不存在还是凭据错误），则使用SQLite
    print(f"MySQL连接失败，将使用SQLite: {e}")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS settings - 生产环境中不应允许所有来源
if DEBUG:
    # 开发环境下允许所有来源
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # 生产环境下指定允许的域名
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        # 在生产环境中添加实际的前端域名
        # "https://yourdomain.com",
    ]
    
CORS_ALLOW_CREDENTIALS = True

# 安全设置
if not DEBUG:
    # 生产环境的安全设置
    SECURE_SSL_REDIRECT = True  # 强制HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'  # 防止点击劫持
    SECURE_HSTS_SECONDS = 31536000  # HSTS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# 大模型API配置
LLM_CONFIG = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    'QWEN_API_KEY': os.getenv('QWEN_API_KEY'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'KIMI_API_KEY': os.getenv('KIMI_API_KEY'),
    'DOUBAO_API_KEY': os.getenv('DOUBAO_API_KEY'),
    'QWEN_CODE_API_KEY': os.getenv('QWEN_CODE_API_KEY'),
    'DEFAULT_MODEL': 'gemini-pro',  # 默认模型
}

# 微信开放平台配置
WECHAT_CONFIG = {
    'APP_ID': os.getenv('WECHAT_APP_ID', 'your_wechat_app_id'),
    'APP_SECRET': os.getenv('WECHAT_APP_SECRET', 'your_wechat_app_secret'),
    'REDIRECT_URI': os.getenv('WECHAT_REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/wechat/callback/'),
}

# QQ互联配置
QQ_CONFIG = {
    'APP_ID': os.getenv('QQ_APP_ID', 'your_qq_app_id'),
    'APP_KEY': os.getenv('QQ_APP_KEY', 'your_qq_app_key'),
    'REDIRECT_URI': os.getenv('QQ_REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/qq/callback/'),
}

# GitHub OAuth配置
GITHUB_CONFIG = {
    'CLIENT_ID': os.getenv('GITHUB_CLIENT_ID', 'your_github_client_id'),
    'CLIENT_SECRET': os.getenv('GITHUB_CLIENT_SECRET', 'your_github_client_secret'),
    'REDIRECT_URI': os.getenv('GITHUB_REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/github/callback/'),
}