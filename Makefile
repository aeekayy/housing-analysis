CURR_DIR := $(shell pwd)
GIT_REV := $(shell git rev-parse HEAD)

venv:
	python3 -m venv $(CURR_DIR)
activate:
	( source bin/activate; source .setup; pip install -r requirements.txt; )
reqs:
	pip install -r requirements.txt
build:
	docker build -t aiware-anywhere-mgmt-api .
push:
	docker tag aiware-anywhere-mgmt-api:latest registry.central.aiware.com/aiware-anywhere-mgmt-api:prod
	docker tag aiware-anywhere-mgmt-api:latest registry.central.aiware.com/aiware-anywhere-mgmt-api:$(GIT_REV)
	docker push registry.central.aiware.com/aiware-anywhere-mgmt-api:prod
	docker push registry.central.aiware.com/aiware-anywhere-mgmt-api:$(GIT_REV)
