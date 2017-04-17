from lbworkflow.tests.settings import *  # NOQA

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'testproject',
    'stronghold',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STRONGHOLD_PUBLIC_URLS = [
    r'^/admin/',
]

MIDDLEWARE += [
    'impersonate.middleware.ImpersonateMiddleware',
    'testproject.middleware.LoginRequiredStrongholdMiddleware',
]

LOGIN_URL ='/admin/login/'
LOGOUT_URL = '/admin/logout/'