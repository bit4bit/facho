#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.71])
AC_INIT([facho-signer], [0.0.1], [bit4bit@riseup.net])
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([src/facho_signer.c])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIRS([m4])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.
PKG_CHECK_MODULES([OPENSSL], [openssl])
PKG_CHECK_MODULES([XMLSEC1], [xmlsec1-openssl])
PKG_CHECK_MODULES([LZMA], [liblzma])
AC_CHECK_HEADER([ltdl.h], [
		AC_CHECK_LIB(
			[ltdl],
			[lt_dlopenext],
			[LIBLTDL=-lltdl],
			[LIBLTDL=]
			)
		], [ LIBLTDL= ])

AC_ARG_ENABLE([xmlsec-crypto-dynamic-loading],
        AS_HELP_STRING([--enable-xmlsec-crypto-dynamic-loading],
        [enable crypto xmlsec dynamic loading])
       )

if test "x$enable_xmlsec_crypto_dynamic_loading" == xyes; then
  AC_DEFINE([XMLSEC_CRYPTO_DYNAMIC_LOADING], [1], [enable xmlsec crypto dynamic loading])
else
  AC_DEFINE([XMLSEC_NO_CRYPTO_DYNAMIC_LOADING], [1], [disable xmlsec crypto dynamic loading])
fi

# Checks for header files.
AC_CHECK_HEADERS([sys/time.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([clock_gettime gethrtime gettimeofday memset strdup])

# libtool

LT_INIT([dlopen])

AC_CONFIG_FILES([Makefile src/Makefile])
AC_OUTPUT
