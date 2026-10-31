
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY") or ("clave-solo-para-desarrollo-local" if DEBUG else "")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    
    "usuarios",
    "marcas",
    "piezas",
    "inventario",
    "movimientos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # base.html, login.html... compartidos por todas las demas modulos
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


if os.getenv("DB_ENGINE", "mysql") == "sqlite":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "gestor_inventario_piezas"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  

SESSION_COOKIE_AGE = 60 * 60 * 8          
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   
SESSION_COOKIE_HTTPONLY = True

# ---------- API REST ----------
REST_FRAMEWORK = {
    # La API usa la misma sesión del login; exige CSRF en escritura.
    "DEFAULT_AUTHENTICATION_CLASSES": ["usuarios.api_auth.SesionUsuarioAuthentication"],
    # Lectura: cualquier usuario con sesión. Escritura: solo administrador.
    "DEFAULT_PERMISSION_CLASSES": ["usuarios.api_auth.AccesoPorRol"],
}
