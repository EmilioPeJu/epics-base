TOP=../..

include $(TOP)/configure/CONFIG

TARGETS += $(SCRIPTS)

# Installation directory

INSTALL_LOCATION = $(EPICS_BASE)

TEMPLATES_DIR = makeBaseApp

# "dlsApp" and "dlsBoot" are empty template directories
# which just contain Makefiles

TEMPLATES += top/dlsApp/Makefile
TEMPLATES += top/dlsApp/Db/Makefile
TEMPLATES += top/dlsApp/src/Makefile
TEMPLATES += top/dlsApp/src/_APPNAME_Main.cpp
TEMPLATES += top/dlsApp/opi/Makefile
TEMPLATES += top/dlsApp/opi/edl/Makefile
TEMPLATES += top/dlsApp/opi/symbol/Makefile

TEMPLATES += top/dlsBoot/Makefile
TEMPLATES += top/dlsBoot/ioc/Makefile@Common
TEMPLATES += top/dlsBoot/ioc/st_APPNAME_.src@Common
TEMPLATES += top/dlsBoot/ioc/README@Common

# "dlsExampleApp" and "dlsExampleBoot" are the standard
# examples which come with "makeBaseApp" but they have
# the build of the startup script from source (st.src)
# added.

TEMPLATES += top/dlsExampleApp/Makefile
TEMPLATES += top/dlsExampleApp/Db/Makefile
TEMPLATES += top/dlsExampleApp/Db/dbExample1.db
TEMPLATES += top/dlsExampleApp/Db/dbExample2.db
TEMPLATES += top/dlsExampleApp/Db/dbSubExample.db
TEMPLATES += top/dlsExampleApp/src/Makefile
TEMPLATES += top/dlsExampleApp/src/xxxRecord.dbd
TEMPLATES += top/dlsExampleApp/src/xxxRecord.c
TEMPLATES += top/dlsExampleApp/src/devXxxSoft.c
TEMPLATES += top/dlsExampleApp/src/xxxSupport.dbd
TEMPLATES += top/dlsExampleApp/src/sncExample.stt
TEMPLATES += top/dlsExampleApp/src/sncProgram.st
TEMPLATES += top/dlsExampleApp/src/sncExample.dbd
TEMPLATES += top/dlsExampleApp/src/dbSubExample.c
TEMPLATES += top/dlsExampleApp/src/dbSubExample.dbd
TEMPLATES += top/dlsExampleApp/src/_APPNAME_Main.cpp
TEMPLATES += top/dlsExampleApp/opi/Makefile
TEMPLATES += top/dlsExampleApp/opi/edl/Makefile
TEMPLATES += top/dlsExampleApp/opi/symbol/Makefile

TEMPLATES += top/dlsExampleBoot/Makefile
TEMPLATES += top/dlsExampleBoot/ioc/Makefile@Common
TEMPLATES += top/dlsExampleBoot/ioc/st_APPNAME_.src@Common
TEMPLATES += top/dlsExampleBoot/ioc/README@Common

# Extra Diamond Rules

CONFIGS += CONFIG.Dls
CONFIGS += RULES.Dls

# Perl scripts

SCRIPTS += convertDlsRelease.pl

# DLS private copy of svn_load_dirs 
# (because it disappeared from the subversion distribution)

SCRIPTS += dls-svn_load_dirs

# Python scripts (new)

SCRIPTS += dls-checkout-module.py
SCRIPTS += dls-export-release.py
SCRIPTS += dls-list-branches.py
SCRIPTS += dls-list-modules.py
SCRIPTS += dls-list-releases.py
SCRIPTS += dlsPyLib.py
SCRIPTS += dls-release.py
SCRIPTS += dls-signalparse.py
SCRIPTS += dls-start-bugfix-branch.py
SCRIPTS += dls-start-feature-branch.py
SCRIPTS += dls-start-new-module.py
SCRIPTS += dls-sync-from-trunk.py
SCRIPTS += dls-vendor-import.py
SCRIPTS += dls-vendor-update.py

# signal-list python scripts

SCRIPTS += dls-export-edm-files.py
SCRIPTS += dls_generate_edm_autofill.py
SCRIPTS += dls_generate_edm_macros.py
SCRIPTS += dls_generate_edm_sum.py
SCRIPTS += dls_generate_edm_titlebar.py
SCRIPTS += dls_generate_edm_vac.py

SCRIPTS += dls-export-Db-files.py
SCRIPTS += dls_generate_Db_info.py
SCRIPTS += dls_generate_Db_sim.py
SCRIPTS += dls_generate_Db_subst.py

SCRIPTS += dlsxmlparserfunctions.py
SCRIPTS += dlsxmlexcelparser.py
SCRIPTS += dlsedmtable.py

SCRIPTS += dls-csv-to-subst.py
SCRIPTS += dls-subst-to-csv.py

# Bash scripts (old)

#SCRIPTS += dls-list-branches
#SCRIPTS += dls-list-modules
#SCRIPTS += dls-release
#SCRIPTS += dls-start-bugfix-branch
#SCRIPTS += dls-start-feature-branch
#SCRIPTS += dls-start-new-module
#SCRIPTS += dls-sync-from-trunk
#SCRIPTS += dls-vendor-import
#SCRIPTS += dls-vendor-update

include $(TOP)/configure/RULES

% : ../scripts/bash/%
	$(CP) $< $@

% : ../scripts/perl/%
	$(CP) $< $@

% : ../scripts/python/%
	$(CP) $< $@
