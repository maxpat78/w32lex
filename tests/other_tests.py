from w32lex import *

# Requires mslex and Windows to compare results

from ctypes import *
from ctypes import windll, wintypes

CommandLineToArgvW = windll.shell32.CommandLineToArgvW
CommandLineToArgvW.argtypes = [wintypes.LPCWSTR, POINTER(c_int)]
CommandLineToArgvW.restype = POINTER(wintypes.LPWSTR)

LocalFree = windll.kernel32.LocalFree
LocalFree.argtypes = [wintypes.HLOCAL]
LocalFree.restype = wintypes.HLOCAL

def ctypes_split(s, fake_arg=1):
    arg = s
    z = 0
    if fake_arg:
        arg = "foo.exe "+s
        z=1
    argc = c_int()
    argv = CommandLineToArgvW(arg, byref(argc))
    result = [argv[i] for i in range(z, argc.value)]
    LocalFree(argv)
    return result

try:
    stdargv98 = CDLL('.\\stdargv\\STDARGV98.dll')
    stdargv05 = CDLL('.\\stdargv\\STDARGV2005.dll')
except FileNotFoundError:
    print('STDARGVxxxx.DLL not found, cannot test against C Runtime parse_cmdline!')
    sys.exit(1)

def parse_cmdline(s, new=0, fake_arg=1):
    stdargv = stdargv98
    if new: stdargv = stdargv05
    arg = s.encode()
    z = 0
    if fake_arg:
        arg = ("foo.exe "+s).encode()
        z = 1
    numargs = c_int(0)
    numchars = c_int(0)
    cmdline = create_string_buffer(arg)
    # void parse_cmdline(char *cmdstart, char **argv, char *args, int *numargs, int *numchars);
    stdargv.parse_cmdline(cmdline, c_void_p(0), c_char_p(0), byref(numargs), byref(numchars))

    argv = (c_char_p * numargs.value)()
    args = create_string_buffer(numchars.value)
    stdargv.parse_cmdline(cmdline, argv, args, byref(numargs), byref(numchars))

    # build a result list similar to ctypes_split
    r = []
    for i in range(z, numargs.value-1): # omit first command name (fake) and last NULL (None)
        r += [argv[i].decode()] # returns str, not bytes
    return r


s = r'"quoted ""inner block"" continues"'
print(split(s, 0), parse_cmdline(s, 0))
assert split(s, 0) == parse_cmdline(s, 0)

s = r'"quoted ""inner block"" continues"'
print(split(s, 2), parse_cmdline(s, 2))
assert split(s, 2) == parse_cmdline(s, 2)

s = r'"quoted ""inner block continues"'
print(split(s, 2), parse_cmdline(s, 2))
assert split(s, 2) == parse_cmdline(s, 2)

s = r'"quoted """inner block""" continues"'
print(split(s, 2), parse_cmdline(s, 2))
assert split(s, 2) == parse_cmdline(s, 2)


# VS2005+, special ARGV0
s = r'"quoted ""inner block"" continues"'
print(split(s, 3), parse_cmdline(s, 1, 0))
assert split(s, 3) == parse_cmdline(s, 1, 0)

s = r'"quoted ""inner block"" continues"'
print(split(s, 3), parse_cmdline(s, 1, 0))
assert split(s, 3) == parse_cmdline(s, 1, 0)

s = r'"quoted ""inner block continues"'
print(split(s, 3), parse_cmdline(s, 1, 0))
assert split(s, 3) == parse_cmdline(s, 1, 0)

s = r'"quoted """inner block""" continues"'
print(split(s, 3), parse_cmdline(s, 1, 0))
assert split(s, 3) == parse_cmdline(s, 1, 0)
