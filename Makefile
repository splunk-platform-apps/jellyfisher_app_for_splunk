DIR := ${CURDIR}

.PHONY: package

link:
	ln -s $(DIR)/output/TA_Carousel_Signage $(SPLUNK_HOME)etc/apps/TA_Carousel_Signage

unlink:
	rm -i $(SPLUNK_HOME)etc/apps/TA_Carousel_Signage

package:
	find . -name '*.pyc' -delete
	mkdir -p build
	tar --exclude="jellyfisher/local" --exclude="jellyfisher/metadata/local.meta" -zcvf build/jellyfisher.tgz jellyfisher
