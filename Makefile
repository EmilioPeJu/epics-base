TOP=../..

include $(TOP)/configure/CONFIG

# Installation directory

TEMPLATES_DIR = makeBaseApp

# Diamond modifications to files which exist
# in "makeBaseApp/top/configure".
# Since "makeDlsApp" is built after "makeBaseApp" during
# the EPICS build, the Diamond versions will be installed
# in the templates directory.

TEMPLATES += top/configure/CONFIG_APP
TEMPLATES += top/configure/RELEASE
TEMPLATES += top/configure/RULES

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
TEMPLATES += top/dlsBoot/ioc/st.src@Common
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

TEMPLATES += top/dlsExampleBoot/Makefile
TEMPLATES += top/dlsExampleBoot/ioc/Makefile@Common
TEMPLATES += top/dlsExampleBoot/ioc/st.src@Common
TEMPLATES += top/dlsExampleBoot/ioc/README@Common

# Extra Diamond Rules

CONFIGS += CONFIG.Dls
CONFIGS += RULES.Dls

# Extra Diamond script

SCRIPTS_HOST += convertDlsRelease.pl

# Diamond Subversion scripts

# Python scripts (new)

SCRIPTS_HOST += scripts/python/dls-checkout-module.py
SCRIPTS_HOST += scripts/python/dls-list-branches.py
SCRIPTS_HOST += scripts/python/dls-list-modules.py
SCRIPTS_HOST += scripts/python/dlsPyLib.py
SCRIPTS_HOST += scripts/python/dls-release.py
SCRIPTS_HOST += scripts/python/dls-signalparse.py
SCRIPTS_HOST += scripts/python/dls-start-bugfix-branch.py
SCRIPTS_HOST += scripts/python/dls-start-feature-branch.py
#SCRIPTS_HOST += scripts/python/dls-start-new-module.py
#SCRIPTS_HOST += scripts/python/dls-sync-from-trunk.py
#SCRIPTS_HOST += scripts/python/dls-vendor-import.py
#SCRIPTS_HOST += scripts/python/dls-vendor-update.py
SCRIPTS_HOST += scripts/python/dlsxmlexcelparser.py

# Bash scripts (old)

#SCRIPTS_HOST += scripts/bash/dls-list-branches
#SCRIPTS_HOST += scripts/bash/dls-list-modules
#SCRIPTS_HOST += scripts/bash/dls-release
#SCRIPTS_HOST += scripts/bash/dls-start-bugfix-branch
#SCRIPTS_HOST += scripts/bash/dls-start-feature-branch
SCRIPTS_HOST += scripts/bash/dls-start-new-module
SCRIPTS_HOST += scripts/bash/dls-sync-from-trunk
SCRIPTS_HOST += scripts/bash/dls-vendor-import
SCRIPTS_HOST += scripts/bash/dls-vendor-update

include $(TOP)/configure/RULES
