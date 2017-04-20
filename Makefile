test:
	coverage run ./runtests.py
run:
	cd testproject;python manage.py runserver 0.0.0.0:9000

isort:
	isort --recursive lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload
