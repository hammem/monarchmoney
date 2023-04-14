builddist:
	python setup.py check
	python setup.py sdist
	python setup.py bdist_wheel --universal

install:
	pip install .

twine:
	twine upload dist/monarchmoney*

uninstall:
	pip uninstall monarchmoney

clean:
	rm -fR build dist monarchmoney.egg-info monarchmoney/__pycache__