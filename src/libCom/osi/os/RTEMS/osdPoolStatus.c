/*************************************************************************\
* Copyright (c) 2002 The University of Chicago, as Operator of Argonne
*     National Laboratory.
* Copyright (c) 2002 The Regents of the University of California, as
*     Operator of Los Alamos National Laboratory.
* EPICS BASE Versions 3.13.7
* and higher are distributed subject to a Software License Agreement found
* in file LICENSE that is included with this distribution. 
\*************************************************************************/
#include <rtems/malloc.h>
#include <rtems/libcsupport.h>

#define epicsExportSharedSymbols
#include "osiPoolStatus.h"

/*
 * osiSufficentSpaceInPool ()
 */
epicsShareFunc int epicsShareAPI osiSufficentSpaceInPool ( size_t contiguousBlockSize )
{
    Heap_Information_block info;
    malloc_info(&info);
    return (info.Stats.free_size > (50000 + contiguousBlockSize));
}
