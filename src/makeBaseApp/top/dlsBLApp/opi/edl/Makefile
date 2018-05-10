TOP = ../../..
include $(TOP)/configure/CONFIG

DATA += $(patsubst ../%, %, $(wildcard ../*.edl))
DATA += $(patsubst ../%, %, $(wildcard ../*.gif))
DATA += $(patsubst ../%, %, $(wildcard ../*.png))
DATA += _APPNAME_.subst
SCRIPTS=st_APPNAME_-gui

.PHONY: _APPNAME_.subst

$(INSTALL_DATA)/_APPNAME_.subst: $(_APPNAME_)/data/_APPNAME_SignalList.xls ../_APPNAME_-overview-src.edl
	$(BLGUI)/data/dls-export-edm-files.py -e --dir=$(INSTALL_DATA) _APPNAME_ $<

include $(TOP)/configure/RULES
