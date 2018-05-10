TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
# In a Diamond IOC Application, build xml files from
# database files like this
#

# List database files required.
USES_DB += $(MO)/db/_APPNAME_-MO-IOC-01.db
USES_DB += $(VA)/db/_APPNAME_-VA-IOC-01.db

include $(TOP)/configure/RULES

#----------------------------------------
#  ADD RULES AFTER THIS LINE

parser-_APPNAME_ : $(USES_DB)
	epicsparser.py $(USES_DB) -r _APPNAME_ > $@
	@echo "Installing postprocessor files"
	@$(INSTALL_PRODUCT) -d -m 555 _APPNAME_* $(INSTALL_DATA)

buildInstall: parser-_APPNAME_

