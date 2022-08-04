default: clean format install

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +

format:
	black .
	isort .

install:
	pip install -e .[test]

test:
	py.test

wheel:
	pip install wheel
	python setup.py sdist bdist_wheel
