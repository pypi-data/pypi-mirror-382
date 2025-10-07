
#ifndef ECOLE_EXPORT_H
#define ECOLE_EXPORT_H

#ifdef ECOLE_STATIC_DEFINE
#  define ECOLE_EXPORT
#  define ECOLE_NO_EXPORT
#else
#  ifndef ECOLE_EXPORT
#    ifdef ecole_lib_EXPORTS
        /* We are building this library */
#      define ECOLE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define ECOLE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef ECOLE_NO_EXPORT
#    define ECOLE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef ECOLE_DEPRECATED
#  define ECOLE_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef ECOLE_DEPRECATED_EXPORT
#  define ECOLE_DEPRECATED_EXPORT ECOLE_EXPORT ECOLE_DEPRECATED
#endif

#ifndef ECOLE_DEPRECATED_NO_EXPORT
#  define ECOLE_DEPRECATED_NO_EXPORT ECOLE_NO_EXPORT ECOLE_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef ECOLE_NO_DEPRECATED
#    define ECOLE_NO_DEPRECATED
#  endif
#endif

#endif /* ECOLE_EXPORT_H */
