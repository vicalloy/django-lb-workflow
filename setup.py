from setuptools import find_packages, setup

from lbworkflow import __version__

setup(
    name="django-lb-workflow",
    version=__version__,
    url="https://github.com/vicalloy/django-lb-workflow",
    author="vicalloy",
    author_email="vicalloy@gmail.com",
    description="Reusable workflow library for Django",
    license="BSD",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.5",
    include_package_data=True,
    install_requires=[
        "django>=2.2",
        "jsonfield>=1.0.1",
        "xlsxwriter>=0.9.6",
        "jinja2>=2.9.6",
        "django-lbutils>=1.1.0",
        "django-lbattachment>=1.1.0",
    ],
    tests_require=[
        "coverage",
        "flake8==3.7.9",
        "isort",
    ],
    extras_require={
        "options": [
            "django_select2>=7.2.0",
            "django-compressor>=2.1.1",
            "django-bower>=5.2.0",
            "django-crispy-forms>=1.6",
            "django-lb-adminlte>=1.1.0",
            "django-impersonate",
            "django-stronghold",
            "django-bootstrap-pagination>=1.7.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
