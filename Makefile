.venv/bin/python3.11:
	python3.11 -m venv --prompt $(shell basename $(shell pwd)) .venv
	.venv/bin/pip install -U setuptools wheel pip

requirements.txt: base.in
	.venv/bin/pip-compile --generate-hashes --output-file $@ base.in

.PHONY: install
install: .venv/bin/python3.11
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

.PHONY: dev_refresh
dev_refresh: install
	./manage.py migrate
	.venv/bin/pre-commit install
