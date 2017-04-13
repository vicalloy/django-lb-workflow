from lbworkflow.tests.settings import *  # NOQA

INSTALLED_APPS += ['testproject']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}