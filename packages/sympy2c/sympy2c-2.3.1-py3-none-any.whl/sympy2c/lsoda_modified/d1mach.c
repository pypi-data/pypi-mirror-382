/* d1mach.f -- translated by f2c (version 20190311).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
/+ Standard C source for D1MACH -- remove the * in column 1 +/ */
#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>
double d1mach_(long *i)
{
  switch(*i){
      case 1: return DBL_MIN;
      case 2: return DBL_MAX;
      case 3: return DBL_EPSILON/FLT_RADIX;
      case 4: return DBL_EPSILON;
      case 5: return log10((double)FLT_RADIX);
  }
  fprintf(stderr, "invalid argument: d1mach(%ld)\n", *i);
  exit(1);
}

#undef right
#undef diver
#undef small
#undef large
#undef dmach
#undef log10
