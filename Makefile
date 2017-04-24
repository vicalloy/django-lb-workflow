test:
	coverage run ./runtests.py

run:
	cd testproject;python manage.py runserver 0.0.0.0:9000

reload_test_data:
	cd testproject;python manage.py callfunc lbworkflow.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.leave.wfdata.load_data


isort:
	isort --recursive lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload
