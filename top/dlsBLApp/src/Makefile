TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
# In a Diamond IOC Application, build xml files from
# database files like this
#
SCRIPTS=st_APPNAME_-gui

# List database files required.
USES_DB += $(MO)/db/_APPNAME_-MO-IOC-01.db
USES_DB += $(VA)/db/_APPNAME_-VA-IOC-01.db

include $(TOP)/configure/RULES
	
#----------------------------------------
#  ADD RULES AFTER THIS LINE

_APPNAME_ : $(USES_DB)
	/home/diamond/common/python/diamond/parser/Rx_y/epicsparser.py $(USES_DB) -r _APPNAME_ > _APPNAME_
	@echo "Installing postprocessor files"
	@$(INSTALL_PRODUCT) -d -m 555 _APPNAME_-* $(INSTALL_DATA)


st_APPNAME_-gui: $(TOP)/configure/RELEASE
	$(BLSLSCRIPTS)/dls_generate_edm_paths.py _APPNAME_ $(TOP)/configure/RELEASE > $@
	
buildInstall: _APPNAME_ st_APPNAME_-gui

