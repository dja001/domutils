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
	mamba create -n dev_env_v3 \
	    numpy scipy attrdict cartopy matplotlib dask \
	    pytest pytest-timeout pytest-cov \
	    pysteps h5py pygrib cairosvg \
	    sphinx sphinx_rtd_theme sphinx-gallery \
	    sphinx-autodoc-typehints sphinx-argparse \
	    packaging twine -c conda-forge
	pip install -e ../domcmc_package
	pip install -e .

test:
	pytest -xvs

docs:
	cd docs && make clean && make doctest && make html

tox:
	./scripts/run_tox_tests.sh

clean:
	rm -rf dist build *.egg-info

release: clean
	python -m build
	twine upload dist/*

