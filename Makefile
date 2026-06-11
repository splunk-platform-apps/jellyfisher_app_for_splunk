DIR := ${CURDIR}

.PHONY: package

APP_NAME := $$(cat jellyfisher/app.manifest | jq -r '.info.id.name')
APP_VERSION := $$(cat jellyfisher/app.manifest | jq -r '.info.id.version')

link:
	ln -s $(DIR)/jellyfisher $(SPLUNK_HOME)etc/apps/jellyfisher

unlink:
	rm -i $(SPLUNK_HOME)etc/apps/jellyfisher

package:
	find . -name '*.pyc' -delete
	mkdir -p build
	APP_VERSION=$(APP_VERSION) ucc-gen build --source src --ta-version $(APP_VERSION)
	APP_NAME=$(APP_NAME) cp -r output/$(APP_NAME)/lib/3rdparty jellyfisher/lib/
	tar --exclude="jellyfisher/local" --exclude="jellyfisher/metadata/local.meta" -zcvf build/jellyfisher.tgz jellyfisher
