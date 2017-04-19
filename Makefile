test:
	coverage run ./runtests.py

isort:
	isort --recursive lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload
