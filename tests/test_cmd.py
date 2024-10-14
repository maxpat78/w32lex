# Requires Windows and special STDARGVxxx.DLL to compare results
from w32lex import *
from ctypes import *
import sys

try:
    stdargv98 = CDLL('.\\stdargv\\STDARGV98.dll')
    stdargv05 = CDLL('.\\stdargv\\STDARGV2005.dll')
except FileNotFoundError:
    print('STDARGVxxxx.DLL not found, cannot test against C Runtime parse_cmdline!')
    sys.exit(1)

def parse_cmdline(s, new=0):
    stdargv = stdargv98
    if new: stdargv = stdargv05
    numargs = c_int(0)
    numchars = c_int(0)
    cmdline = create_string_buffer(s.encode())
    # void parse_cmdline(char *cmdstart, char **argv, char *args, int *numargs, int *numchars);
    stdargv.parse_cmdline(cmdline, c_void_p(0), c_char_p(0), byref(numargs), byref(numchars))

    argv = (c_char_p * numargs.value)()
    args = create_string_buffer(numchars.value)
    stdargv.parse_cmdline(cmdline, argv, args, byref(numargs), byref(numchars))

    # build a result list similar to ctypes_split
    r = []
    for i in range(0, numargs.value-1): # omit last NULL (None)
        r += [argv[i].decode()] # returns str, not bytes
    return r


cases = [
r'a b',
r'a^b',
r'a|b', # from split: ['a|b'] != ['a','|','b']
r'a&&b', # from split: ['a&&b'] != ['a','&&','b']
r'"a b"',
r'\"a b"\c\d',
r'\""a b""\c\d',
r'\"""a b"""\c\d',
]
for case in cases:
    if [case] != cmd_split(cmd_quote(case)):
        print('cmd_quote failed with', case, 'emitting', cmd_split(cmd_quote(case)))
