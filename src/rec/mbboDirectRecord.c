/* recMbboDirect.c */
/* share/src/rec @(#)recMbboDirect.c	1.2	1/4/94 */

/* recMbboDirect.c - Record Support for mbboDirect records */
/*
 *      Original Author: Bob Dalesio
 *      Current Author:  Matthew Needes
 *      Date:            10-06-93
 *
 *      Experimental Physics and Industrial Control System (EPICS)
 *
 *      Copyright 1991, the Regents of the University of California,
 *      and the University of Chicago Board of Governors.
 *
 *      This software was produced under  U.S. Government contracts:
 *      (W-7405-ENG-36) at the Los Alamos National Laboratory,
 *      and (W-31-109-ENG-38) at Argonne National Laboratory.
 *
 *      Initial development by:
 *              The Controls and Automation Group (AT-8)
 *              Ground Test Accelerator
 *              Accelerator Technology Division
 *              Los Alamos National Laboratory
 *
 *      Co-developed with
 *              The Controls and Computing Group
 *              Accelerator Systems Division
 *              Advanced Photon Source
 *              Argonne National Laboratory
 *
 * Modification Log:
 * -----------------
 *     (modifications to mbbo apply, see mbbo record)
 *   1.   mcn    "Created" by borrowing mbbo record code, and modifying it.
 */

#include	<vxWorks.h>
#include	<types.h>
#include	<stdioLib.h>
#include	<lstLib.h>
#include	<string.h>

#include	<alarm.h>
#include	<dbDefs.h>
#include	<dbAccess.h>
#include	<dbFldTypes.h>
#include	<devSup.h>
#include	<errMdef.h>
#include	<recSup.h>
#include	<special.h>
#define GEN_SIZE_OFFSET
#include	<mbboDirectRecord.h>
#undef  GEN_SIZE_OFFSET

/* Create RSET - Record Support Entry Table*/
#define report NULL
#define initialize NULL
static long init_record();
static long process();
static long special();
static long get_value();
#define cvt_dbaddr NULL
#define get_array_info NULL
#define put_array_info NULL
#define get_units NULL
#define get_precision NULL
#define get_enum_str NULL
#define get_enum_strs NULL
#define put_enum_str NULL
#define get_graphic_double NULL
#define get_control_double NULL
#define get_alarm_double NULL

struct rset mbboDirectRSET={
	RSETNUMBER,
	report,
	initialize,
	init_record,
	process,
	special,
	get_value,
	cvt_dbaddr,
	get_array_info,
	put_array_info,
	get_units,
	get_precision,
	get_enum_str,
	get_enum_strs,
	put_enum_str,
	get_graphic_double,
	get_control_double,
	get_alarm_double };

struct mbbodset { /* multi bit binary output dset */
	long		number;
	DEVSUPFUN	dev_report;
	DEVSUPFUN	init;
	DEVSUPFUN	init_record;  /*returns: (0,2)=>(success,success no convert)*/
	DEVSUPFUN	get_ioint_info;
	DEVSUPFUN	write_mbbo; /*returns: (0,2)=>(success,success no convert)*/
};


static void convert();
static void monitor();
static long writeValue();

#define NUM_BITS  16

static long init_record(pmbboDirect,pass)
    struct mbboDirectRecord	*pmbboDirect;
    int pass;
{
    struct mbbodset *pdset;
    long status = 0;
    int	i;

    if (pass==0) return(0);

    /* mbbo.siml must be a CONSTANT or a PV_LINK or a DB_LINK */
    switch (pmbboDirect->siml.type) {
    case (CONSTANT) :
	recGblInitConstantLink(&pmbboDirect->siml,DBF_USHORT,&pmbboDirect->simm);
        break;
    case (PV_LINK) :
    case (DB_LINK) :
        break;
    default :
        recGblRecordError(S_db_badField,(void *)pmbboDirect,
                "mbboDirect: init_record Illegal SIML field");
        return(S_db_badField);
    }

    if(!(pdset = (struct mbbodset *)(pmbboDirect->dset))) {
	recGblRecordError(S_dev_noDSET,(void *)pmbboDirect,"mbboDirect: init_record");
	return(S_dev_noDSET);
    }
    /* must have write_mbbo function defined */
    if( (pdset->number < 5) || (pdset->write_mbbo == NULL) ) {
	recGblRecordError(S_dev_missingSup,(void *)pmbboDirect,"mbboDirect: init_record");
	return(S_dev_missingSup);
    }
    if (pmbboDirect->dol.type == CONSTANT){
	recGblInitConstantLink(&pmbboDirect->dol,DBF_USHORT,&pmbboDirect->val);
    }
    /* initialize mask*/
    pmbboDirect->mask = 0;
    for (i=0; i<pmbboDirect->nobt; i++) {
        pmbboDirect->mask <<= 1; /* shift left 1 bit*/
        pmbboDirect->mask |= 1;  /* set low order bit*/
    }
    if(pdset->init_record) {
	unsigned long rval;

	status=(*pdset->init_record)(pmbboDirect);
        /* init_record might set status */
	if(status==0){
		rval = pmbboDirect->rval;
		if(pmbboDirect->shft>0) rval >>= pmbboDirect->shft;
		pmbboDirect->val =  (unsigned short)rval;
	} else if (status == 2) status = 0;
    }
    return(status);
}

static long process(pmbboDirect)
    struct mbboDirectRecord     *pmbboDirect;
{
    struct mbbodset	*pdset = (struct mbbodset *)(pmbboDirect->dset);
    long		status=0;
    unsigned char    pact=pmbboDirect->pact;

    if( (pdset==NULL) || (pdset->write_mbbo==NULL) ) {
	pmbboDirect->pact=TRUE;
	recGblRecordError(S_dev_missingSup,(void *)pmbboDirect,"write_mbbo");
	return(S_dev_missingSup);
    }

    if (!pmbboDirect->pact) {
	if(pmbboDirect->dol.type==DB_LINK && pmbboDirect->omsl==CLOSED_LOOP){
	    long status;
	    unsigned short val;

	    pmbboDirect->pact = TRUE;
	    status = dbGetLink(&pmbboDirect->dol,DBR_USHORT,&val,0,0);
	    pmbboDirect->pact = FALSE;
	    if(status==0) {
		pmbboDirect->val= val;
	    }
	}
	/* convert val to rval */
	convert(pmbboDirect);
    }

    status=writeValue(pmbboDirect);

    /* check if device support set pact */
    if ( !pact && pmbboDirect->pact ) return(0);
    pmbboDirect->pact = TRUE;

    recGblGetTimeStamp(pmbboDirect);
    /* check event list */
    monitor(pmbboDirect);
    /* process the forward scan link record */
    recGblFwdLink(pmbboDirect);
    pmbboDirect->pact=FALSE;
    return(status);
}

static long special(paddr,after)
    struct dbAddr *paddr;
    int           after;
{
    struct mbboDirectRecord     *pmbboDirect = (struct mbboDirectRecord *)(paddr->precord);
    int special_type = paddr->special, offset = 1, i;
    char *bit;

    if(!after) return(0);
    switch(special_type) {
      case(SPC_MOD):
       /*
        *  Set a bit in VAL corresponding to the bit changed
        *    offset equals the offset in bit array.  Only do
        *    this if in supervisory mode.
        */
        if (pmbboDirect->omsl == CLOSED_LOOP)
           return(0);

        offset = 1 << (((int)paddr->pfield) - ((int) &(pmbboDirect->b0)));
 
        if (*((char *)paddr->pfield)) {
          /* set field */
           pmbboDirect->val |= offset;
        }
        else {
           /* zero field */
           pmbboDirect->val &= ~offset;
        }
 
        convert(pmbboDirect);
        return(0);
      case(SPC_RESET):
       /*
        *  If OMSL changes from closed_loop to supervisory,
        *     reload value field with B0 - B15
        */
        bit = &(pmbboDirect->b0);
        if (pmbboDirect->omsl == SUPERVISORY) {
           for (i=0; i<NUM_BITS; i++, offset = offset << 1, bit++) {
              if (*bit)
                  pmbboDirect->val |= offset;
              else
                  pmbboDirect->val &= ~offset;
            }
        }

        return(0);
      default:
        recGblDbaddrError(S_db_badChoice,paddr,"mbboDirect: special");
        return(S_db_badChoice);
    }
}

static long get_value(pmbboDirect,pvdes)
    struct mbboDirectRecord		*pmbboDirect;
    struct valueDes	*pvdes;
{
    pvdes->field_type = DBF_USHORT;
    pvdes->no_elements=1;
    (unsigned short *)(pvdes->pvalue) = &pmbboDirect->val;
    return(0);
}

static void monitor(pmbboDirect)
    struct mbboDirectRecord	*pmbboDirect;
{
	unsigned short	monitor_mask;

        monitor_mask = recGblResetAlarms(pmbboDirect);
        monitor_mask |= (DBE_LOG|DBE_VALUE);
        if(monitor_mask)
         db_post_events(pmbboDirect,pmbboDirect->val,monitor_mask);

        /* check for value change */
        if (pmbboDirect->mlst != pmbboDirect->val){
                /* post events for value change and archive change */
                monitor_mask |= (DBE_VALUE | DBE_LOG);
                /* update last value monitored */
                pmbboDirect->mlst = pmbboDirect->val;
        }
        /* send out monitors connected to the value field */
        if (monitor_mask){
                db_post_events(pmbboDirect,&pmbboDirect->val,monitor_mask);
	}
        if(pmbboDirect->oraw!=pmbboDirect->rval) {
                db_post_events(pmbboDirect,&pmbboDirect->rval,monitor_mask|DBE_VALUE);
                pmbboDirect->oraw = pmbboDirect->rval;
        }
        if(pmbboDirect->orbv!=pmbboDirect->rbv) {
                db_post_events(pmbboDirect,&pmbboDirect->rbv,monitor_mask|DBE_VALUE);
                pmbboDirect->orbv = pmbboDirect->rbv;
        }
        return;
}

static void convert(pmbboDirect)
	struct mbboDirectRecord  *pmbboDirect;
{
       /* convert val to rval */
	pmbboDirect->rval = (unsigned long)(pmbboDirect->val);
	if(pmbboDirect->shft>0)
             pmbboDirect->rval <<= pmbboDirect->shft;

	return;
}

static long writeValue(pmbboDirect)
	struct mbboDirectRecord	*pmbboDirect;
{
	long		status;
        struct mbbodset *pdset = (struct mbbodset *) (pmbboDirect->dset);

	if (pmbboDirect->pact == TRUE){
		status=(*pdset->write_mbbo)(pmbboDirect);
		return(status);
	}

	status=dbGetLink(&(pmbboDirect->siml),
		DBR_ENUM,&(pmbboDirect->simm),0,0);
	if (status)
		return(status);

	if (pmbboDirect->simm == NO){
		status=(*pdset->write_mbbo)(pmbboDirect);
		return(status);
	}
	if (pmbboDirect->simm == YES){
		status=dbPutLink(&pmbboDirect->siol,DBR_USHORT,
			&pmbboDirect->val,1);
	} else {
		status=-1;
		recGblSetSevr(pmbboDirect,SOFT_ALARM,INVALID_ALARM);
		return(status);
	}
        recGblSetSevr(pmbboDirect,SIMM_ALARM,pmbboDirect->sims);

	return(status);
}
