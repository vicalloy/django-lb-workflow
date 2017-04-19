test:
	coverage run --parallel-mode ./runtests.py

isort:
	isort --recursive lbworkflow

upload:
	python setup.py sdist --formats=gztar register upload
