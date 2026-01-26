.PHONY: help env test docs tox clean release

help:
	@echo "Common targets:"
	@echo "  make env        Create dev environment"
	@echo "  make test       Run unit tests"
	@echo "  make docs       Run doctests + build docs"
	@echo "  make tox        Run tox matrix"
	@echo "  make clean      Clean build artifacts"
	@echo "  make release    Build + upload to PyPI"

env:
	./scripts/create_dev_env.sh dev_env_20260126

test:
	pytest -xvs

docs:
	rm -rf ./docs/auto_examples
	./scripts/copy_reference_images_to_static.sh
	cd docs && make clean && make doctest && make html 

tox:
	./scripts/run_tox_tests.sh

clean:
	rm -rf dist build *.egg-info 

release: clean
	python -m build
	twine upload dist/*

