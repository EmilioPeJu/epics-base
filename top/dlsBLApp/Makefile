TOP=..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
# In a Diamond IOC Application, build xml files from
# database files like this
#
ROOTNAME = _APPNAME_

# List database files required.
USES_DB += $(MOTION)/db/_APPNAME_-MO-IOC-01.db
USES_DB += $(VACUUM)/db/_APPNAME_-VA-IOC-01.db

include $(TOP)/configure/RULES
	
#----------------------------------------
#  ADD RULES AFTER THIS LINE

$(ROOTNAME) : $(USES_DB)
	/home/diamond/common/python/diamond/parser/Rx_y/epicsparser.py $(USES_DB) -r $(ROOTNAME) > $(ROOTNAME)
	@echo "Installing postprocessor files"
	@$(INSTALL_PRODUCT) -d -m 555 $(ROOTNAME)-* $(INSTALL_DATA)

buildInstall: $(ROOTNAME)

