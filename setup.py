from setuptools import find_packages, setup
from lbworkflow import __version__

setup(
    name='django-lb-workflow',
    version=__version__,
    url='https://github.com/vicalloy/django-lb-workflow',
    author='vicalloy',
    author_email='vicalloy@gmail.com',
    description="Reusable workflow library for Django",
    license='BSD',
    packages=find_packages(exclude=['tests']),
    python_requires=">=3.5",
    include_package_data=True,
    install_requires=[
        'django>=1.10,<3.0',
        'jsonfield>=1.0.1',
        'pygraphviz>=1.3',
        'xlsxwriter>=0.9.6',
        'jinja2>=2.9.6',
        'django-lbutils>=1.0.3',
        'django-lbattachment>=1.0.2',
        'django_select2>=7.2.0',
    ],
    tests_require=[
        'coverage',
        'flake8>=2.0,<3.0',
        'isort',
    ],
    extras_require={
        'options': [
            'django-compressor>=2.1.1',
            'django-bower>=5.2.0',
            'django-crispy-forms>=1.6',
            'django-lb-adminlte>=0.9.4',
            'django-el-pagination>=3.0.1',
            'django-impersonate',
            'django-stronghold',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
