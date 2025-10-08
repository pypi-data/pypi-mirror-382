/* solsy.f -- translated by f2c (version 20190311).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
*/

#include "f2c.h"

/* Common Block Declarations */

struct {
    doublereal rowns[209], ccmax, el0, h__, hmin, hmxi, hu, rc, tn, uround;
    integer iownd[14], iowns[6], icf, ierpj, iersl, jcur, jstart, kflag, l,
	    meth, miter, maxord, maxcor, msbp, mxncf, n, nq, nst, nfe, nje,
	    nqu;
} ls0001_;

#define ls0001_1 ls0001_

/* Table of constant values */

static integer c__9 = 9;
static integer c__1 = 1;
static integer c__3 = 3;

/* Subroutine */ int solsy_(doublereal *wm, integer *iwm, doublereal *x,
	doublereal *tem)
{
    /* System generated locals */
    integer i__1;

    /* Builtin functions */
    integer s_wsle(cilist *), do_lio(integer *, integer *, char *, ftnlen),
	    e_wsle(void);

    /* Local variables */
    static integer i__;
    static doublereal r__, di;
    static integer ml, mu;
    static doublereal hl0, phl0;
    static integer meband;

    /* Fortran I/O blocks */
    static cilist io___1 = { 0, 6, 0, 0, 0 };


/* lll. optimize */
/*     external solve */
/* ----------------------------------------------------------------------- */
/* this routine manages the solution of the linear system arising from */
/* a chord iteration.  it is called if miter .ne. 0. */
/* if miter is 1 or 2, it calls dgetrs to accomplish this. */
/* if miter = 3 it updates the coefficient h*el0 in the diagonal */
/* matrix, and then computes the solution. */
/* if miter is 4 or 5, it calls dgbtrs. */
/* communication with solsy uses the following variables.. */
/* wm    = real work space containing the inverse diagonal matrix if */
/*         miter = 3 and the lu decomposition of the matrix otherwise. */
/*         storage of matrix elements starts at wm(3). */
/*         wm also contains the following matrix-related data.. */
/*         wm(1) = sqrt(uround) (not used here), */
/*         wm(2) = hl0, the previous value of h*el0, used if miter = 3. */
/* iwm   = integer work space containing pivot information, starting at */
/*         iwm(21), if miter is 1, 2, 4, or 5.  iwm also contains band */
/*         parameters ml = iwm(1) and mu = iwm(2) if miter is 4 or 5. */
/* x     = the right-hand side vector on input, and the solution vector */
/*         on output, of length n. */
/* tem   = vector of work space of length n, not used in this version. */
/* iersl = output flag (in common).  iersl = 0 if no trouble occurred. */
/*         iersl = 1 if a singular matrix arose with miter = 3. */
/* this routine also uses the common variables el0, h, miter, and n. */
/* ----------------------------------------------------------------------- */
    /* Parameter adjustments */
    --tem;
    --x;
    --iwm;
    --wm;

    /* Function Body */
    ls0001_1.iersl = 0;
    s_wsle(&io___1);
    do_lio(&c__9, &c__1, "miter=", (ftnlen)6);
    do_lio(&c__3, &c__1, (char *)&ls0001_1.miter, (ftnlen)sizeof(integer));
    e_wsle();
/*     go to (100, 100, 300, 400, 400), miter */
    switch (ls0001_1.miter) {
	case 1:  goto L100;
	case 2:  goto L100;
	case 3:  goto L300;
	case 4:  goto L100;
	case 5:  goto L400;
    }
/*     Replaced LINPACK dgesl with LAPACK dgetrs */
/* 100  call dgesl (wm(3), n, n, iwm(21), x, 0) */
/* 100  call dgetrs ('N', n, 1, wm(3), n, iwm(21), x, n, ier) */
/* 100 call solve(x, ier) */
L100:
    return 0;

L300:
    phl0 = wm[2];
    hl0 = ls0001_1.h__ * ls0001_1.el0;
    wm[2] = hl0;
    if (hl0 == phl0) {
	goto L330;
    }
    r__ = hl0 / phl0;
    i__1 = ls0001_1.n;
    for (i__ = 1; i__ <= i__1; ++i__) {
	di = 1. - r__ * (1. - 1. / wm[i__ + 2]);
	if (abs(di) == 0.) {
	    goto L390;
	}
/* L320: */
	wm[i__ + 2] = 1. / di;
    }
L330:
    i__1 = ls0001_1.n;
    for (i__ = 1; i__ <= i__1; ++i__) {
/* L340: */
	x[i__] = wm[i__ + 2] * x[i__];
    }
    return 0;
L390:
    ls0001_1.iersl = 1;
    return 0;

L400:
    ml = iwm[1];
    mu = iwm[2];
    meband = (ml << 1) + mu + 1;
/*     Replaced LINPACK dgbsl with LAPACK dgbtrs */
/*      call dgbsl (wm(3), meband, n, ml, mu, iwm(21), x, 0) */
/*     call dgbtrs ('N', n, ml, mu, 1, wm(3), meband, iwm(21), x, n, ier) */
    return 0;
/* ----------------------- end of subroutine solsy ----------------------- */
} /* solsy_ */
