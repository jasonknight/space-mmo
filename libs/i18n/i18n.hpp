#include "common/types.hpp"

// This is an internal callback function pointer, the first
// time through, we establish which language we are using, 
// and set the callback, so that we don't need to test the string
// every time
typedef int (*__internal_i18n_callback)(string);

int _t_en(string key, mut_string dest, u32 len);