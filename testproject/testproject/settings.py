from lbworkflow.tests.settings import *  # NOQA

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "testproject",
    "stronghold",
    "impersonate",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

STRONGHOLD_PUBLIC_URLS = [
    r"^/admin/",
]

MIDDLEWARE += [
    "impersonate.middleware.ImpersonateMiddleware",
    "stronghold.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "testproject.urls"

LOGIN_URL = "/admin/login/"
LOGOUT_URL = "/admin/logout/"
IMPERSONATE_REDIRECT_URL = "/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL_ = "/media/"
MEDIA_URL = MEDIA_URL_

LBWF_APPS.update(
    {
        "issue": "lbworkflow.tests.issue",
    }
)
