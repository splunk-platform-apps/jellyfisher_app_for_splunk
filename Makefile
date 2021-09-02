DIR := ${CURDIR}

.PHONY: package

link:
	ln -s $(DIR)/jellyfisher $(SPLUNK_HOME)etc/apps/jellyfisher

unlink:
	rm -i $(SPLUNK_HOME)etc/apps/jellyfisher

package:
	find . -name '*.pyc' -delete
	mkdir -p build
	tar --exclude="jellyfisher/local" --exclude="jellyfisher/metadata/local.meta" -zcvf build/jellyfisher.tgz jellyfisher
