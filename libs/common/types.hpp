#ifndef U_TYPES_HEADER
#define U_TYPES_HEADER
#include <windows.h>
#define string char const*
#define mut_string char*
#define u32 unsigned const int
#define mut_u32 unsigned int
#define i32 signed const int
#define mut_i32 signed int

#ifdef _MSC_VER
#define u64 unsigned const __int64
#define mut_u64 unsigned __int64
#define i64 signed const __int64
#define mut_i64 signed __int64
#else
#define u64 unsigned const long long
#define mut_u64 usigned long long
#define u64 signed const long long
#define mut_u64 signed long long
#endif
#define u16 unsigned const short
#define mut_u16 unsigned short
#define i16 signed const short
#define mut_i16 signed short
#define u8 unsigned const char
#define mut_u8 unsigned char
#define i8 const char
#define mut_i8 char

#ifndef uptr
#if defined(__ppc64__) || defined(__powerpc64__) || defined(__aarch64__) || defined(_M_X64) || defined(__x86_64__) || defined(__x86_64) || defined(__s390x__)
#define uptr u64 const*
#define mut_uptr mut_u64*
#else
#define uptr u32 const*
#define mut_uptr mut_u32*
#endif
#endif

#endif