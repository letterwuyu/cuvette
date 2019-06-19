# Makefile for constructing RPMs.
# Try "make" (for SRPMS) or "make rpm"

NAME = cuvette

TAG := $(shell git describe --tags --abbrev=0)
VERSION := $(shell echo $(TAG) | sed 's/^v//')

COMMIT := $(shell git rev-parse HEAD)
SHORTCOMMIT := $(shell echo $(COMMIT) | cut -c1-7)
RELEASE := $(shell git describe --tags \
             | sed 's/^v//' \
             | sed 's/^[^-]*-//' \
             | sed 's/-/./')
ifeq ($(VERSION),$(RELEASE))
  RELEASE = 1
endif
ifneq (,$(findstring beta,$(VERSION)))
    BETA := $(shell echo $(VERSION) | sed 's/.*beta/beta/')
    RELEASE := 0.$(BETA).$(RELEASE)
    VERSION := $(subst $(BETA),,$(VERSION))
endif
ifneq (,$(findstring rc,$(VERSION)))
    RC := $(shell echo $(VERSION) | sed 's/.*rc/rc/')
    RELEASE := 0.$(RC).$(RELEASE)
    VERSION := $(subst $(RC),,$(VERSION))
endif

ifneq (,$(shell echo $(VERSION) | grep [a-zA-Z]))
    # If we still have alpha characters in our Git tag string, we don't know
    # how to translate that into a sane RPM version/release. Bail out.
    $(error cannot translate Git tag version $(VERSION) to an RPM NVR)
endif

NVR := $(NAME)-$(VERSION)-$(RELEASE).el7

all: srpm

# Testing only
echo:
	echo COMMIT $(COMMIT)
	echo VERSION $(VERSION)
	echo RELEASE $(RELEASE)
	echo NVR $(NVR)

clean:
	rm -rf dist/
	rm -rf cuvette-$(VERSION)-$(SHORTCOMMIT).tar.gz
	rm -rf $(NVR).src.rpm

dist:
	git archive --format=tar.gz --prefix=cuvette-$(VERSION)/ HEAD > cuvette-$(VERSION)-$(SHORTCOMMIT).tar.gz

spec:
	sed cuvette.spec.in \
	  -e 's/@COMMIT@/$(COMMIT)/' \
	  -e 's/@VERSION@/$(VERSION)/' \
	  -e 's/@RELEASE@/$(RELEASE)/' \
	  > cuvette.spec

srpm: dist spec
	rpmbuild -bs cuvette.spec \
	  --define "_topdir ." \
	  --define "_sourcedir ." \
	  --define "_srcrpmdir ." \
	  --define "dist .el7"

rpm: dist srpm
	mock -r epel-7-x86_64 rebuild $(NVR).src.rpm \
	  --resultdir=. \
	  --define "dist .el7"

.PHONY: dist rpm srpm

