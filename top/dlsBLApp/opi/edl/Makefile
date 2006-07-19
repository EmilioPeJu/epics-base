TOP = ../../..
include $(TOP)/configure/CONFIG

DATA += $(patsubst ../%, %, $(wildcard ../*.edl))
DATA += $(patsubst ../%, %, $(wildcard ../*.gif))
DATA += $(patsubst ../%, %, $(wildcard ../*.png))
DATA += _APPNAME_.subst

.PHONY: _APPNAME_.subst

$(INSTALL_DATA)/_APPNAME_.subst: $(BLSRC)/_APPNAME_SignalList.xml
	$(BLSLSCRIPTS)/dls-export-edm-files.py -m -o -t -f -v -r --dir=$(INSTALL_DATA) _APPNAME_ $<

include $(TOP)/configure/RULES
