test:
	coverage run ./runtests.py

run:
	cd testproject;python manage.py runserver 0.0.0.0:9000

isort:
	isort --recursive lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload

wfgen:
	python testproject/wfgen.py

wfgen_clean:
	python testproject/wfgen.py clean

reload_test_data:
	cd testproject;python manage.py callfunc lbworkflow.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.leave.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.issue.wfdata.load_data
