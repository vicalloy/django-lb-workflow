run:
	cd testproject;python manage.py runserver 0.0.0.0:9000

pyenv:
	pip install pipenv --upgrade
	pipenv --python 3
	pipenv install -d --skip-lock
	pipenv shell

black:
		black ./

test:
	coverage run ./runtests.py

isort:
	isort ./lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload

wfgen:
	python testproject/wfgen.py

wfgen_clean:
	python testproject/wfgen.py clean

reload_test_data:
	cd testproject;python manage.py callfunc lbworkflow.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.simplewf.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.leave.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.issue.wfdata.load_data
	cd testproject;python manage.py callfunc lbworkflow.tests.purchase.wfdata.load_data

build_docker_image:
	docker build -t lbworkflow:0.9 .

create_docker_container:
	docker run -d -p 9000:9000 --name lbworkflow lbworkflow:0.9

install-pre-commit:
		pre-commit install
		pre-commit run --all-files
