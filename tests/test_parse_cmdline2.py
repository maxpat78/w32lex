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

def ctypes_split(s):
    argc = c_int()
    argv = CommandLineToArgvW(s, byref(argc))
    result = [argv[i] for i in range(0, argc.value)]
    LocalFree(argv)
    return result

stdargv = CDLL('.\\stdargv\\STDARGV98.dll')
#~ stdargv = CDLL('.\\stdargv\\STDARGV2005.dll') # rules change
#~ stdargv = CDLL('.\\stdargv\\argv_parsing.dll')

def parse_cmdline(s):
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
    for i in range(0, numargs.value-1): # omit first command name (fake) and last NULL (None)
        r += [argv[i].decode()] # returns str, not bytes
    return r

# from https://github.com/smoofra/mslex
examples = [
    (r"", []),
    (r'"', [""]),
    (r"x", ["x"]),
    (r'x"', ["x"]),
    (r"foo", ["foo"]),
    (r'foo    "bar baz"', ["foo", "bar baz"]),
    (r'"abc" d e', ["abc", "d", "e"]),
    (r'a\\\b d"e f"g h', [r"a\\\b", "de fg", "h"]),
    (r"a\\\"b c d", [r"a\"b", "c", "d"]),
    (r'a\\\\"b c" d e', [r"a\\b c", "d", "e"]),
    ('"" "" ""', ["", "", ""]),
    ('" x', [" x"]),
    ('"" x', ["", "x"]),
    ('""" x', ['"', "x"]),
    ('"""" x', ['" x']),
    ('""""" x', ['"', "x"]),
    ('"""""" x', ['""', "x"]),
    ('""""""" x', ['"" x']),
    ('"""""""" x', ['""', "x"]),
    ('""""""""" x', ['"""', "x"]),
    ('"""""""""" x', ['""" x']),
    ('""""""""""" x', ['"""', "x"]),
    ('"""""""""""" x', ['""""', "x"]),
    ('""""""""""""" x', ['"""" x']),
    ('"aaa x', ["aaa x"]),
    ('"aaa" x', ["aaa", "x"]),
    ('"aaa"" x', ['aaa"', "x"]),
    ('"aaa""" x', ['aaa" x']),
    ('"aaa"""" x', ['aaa"', "x"]),
    ('"aaa""""" x', ['aaa""', "x"]),
    ('"aaa"""""" x', ['aaa"" x']),
    ('"aaa""""""" x', ['aaa""', "x"]),
    ('"aaa"""""""" x', ['aaa"""', "x"]),
    ('"aaa""""""""" x', ['aaa""" x']),
    ('"aaa"""""""""" x', ['aaa"""', "x"]),
    ('"aaa""""""""""" x', ['aaa""""', "x"]),
    ('"aaa"""""""""""" x', ['aaa"""" x']),
    ('"aaa\\ x', ["aaa\\ x"]),
    ('"aaa\\" x', ['aaa" x']),
    ('"aaa\\"" x', ['aaa"', "x"]),
    ('"aaa\\""" x', ['aaa""', "x"]),
    ('"aaa\\"""" x', ['aaa"" x']),
    ('"aaa\\""""" x', ['aaa""', "x"]),
    ('"aaa\\"""""" x', ['aaa"""', "x"]),
    ('"aaa\\""""""" x', ['aaa""" x']),
    ('"aaa\\"""""""" x', ['aaa"""', "x"]),
    ('"aaa\\""""""""" x', ['aaa""""', "x"]),
    ('"aaa\\"""""""""" x', ['aaa"""" x']),
    ('"aaa\\""""""""""" x', ['aaa""""', "x"]),
    ('"aaa\\"""""""""""" x', ['aaa"""""', "x"]),
    ('"aaa\\\\ x', ["aaa\\\\ x"]),
    ('"aaa\\\\" x', ["aaa\\", "x"]),
    ('"aaa\\\\"" x', ['aaa\\"', "x"]),
    ('"aaa\\\\""" x', ['aaa\\" x']),
    ('"aaa\\\\"""" x', ['aaa\\"', "x"]),
    ('"aaa\\\\""""" x', ['aaa\\""', "x"]),
    ('"aaa\\\\"""""" x', ['aaa\\"" x']),
    ('"aaa\\\\""""""" x', ['aaa\\""', "x"]),
    ('"aaa\\\\"""""""" x', ['aaa\\"""', "x"]),
    ('"aaa\\\\""""""""" x', ['aaa\\""" x']),
    ('"aaa\\\\"""""""""" x', ['aaa\\"""', "x"]),
    ('"aaa\\\\""""""""""" x', ['aaa\\""""', "x"]),
    ('"aaa\\\\"""""""""""" x', ['aaa\\"""" x']),
    ('"aaa\\\\\\ x', ["aaa\\\\\\ x"]),
    ('"aaa\\\\\\" x', ['aaa\\" x']),
    ('"aaa\\\\\\"" x', ['aaa\\"', "x"]),
    ('"aaa\\\\\\""" x', ['aaa\\""', "x"]),
    ('"aaa\\\\\\"""" x', ['aaa\\"" x']),
    ('"aaa\\\\\\""""" x', ['aaa\\""', "x"]),
    ('"aaa\\\\\\"""""" x', ['aaa\\"""', "x"]),
    ('"aaa\\\\\\""""""" x', ['aaa\\""" x']),
    ('"aaa\\\\\\"""""""" x', ['aaa\\"""', "x"]),
    ('"aaa\\\\\\""""""""" x', ['aaa\\""""', "x"]),
    ('"aaa\\\\\\"""""""""" x', ['aaa\\"""" x']),
    ('"aaa\\\\\\""""""""""" x', ['aaa\\""""', "x"]),
    ('"aaa\\\\\\"""""""""""" x', ['aaa\\"""""', "x"]),
    ('"aaa\\\\\\\\ x', ["aaa\\\\\\\\ x"]),
    ('"aaa\\\\\\\\" x', ["aaa\\\\", "x"]),
    ('"aaa\\\\\\\\"" x', ['aaa\\\\"', "x"]),
    ('"aaa\\\\\\\\""" x', ['aaa\\\\" x']),
    ('"aaa\\\\\\\\"""" x', ['aaa\\\\"', "x"]),
    ('"aaa\\\\\\\\""""" x', ['aaa\\\\""', "x"]),
    ('"aaa\\\\\\\\"""""" x', ['aaa\\\\"" x']),
    ('"aaa\\\\\\\\""""""" x', ['aaa\\\\""', "x"]),
    ('"aaa\\\\\\\\"""""""" x', ['aaa\\\\"""', "x"]),
    ('"aaa\\\\\\\\""""""""" x', ['aaa\\\\""" x']),
    ('"aaa\\\\\\\\"""""""""" x', ['aaa\\\\"""', "x"]),
    ('"aaa\\\\\\\\""""""""""" x', ['aaa\\\\""""', "x"]),
    ('"aaa\\\\\\\\"""""""""""" x', ['aaa\\\\"""" x']),
    (" x", ["x"]),
    ('" x', [" x"]),
    ('"" x', ["", "x"]),
    ('""" x', ['"', "x"]),
    ('"""" x', ['" x']),
    ('""""" x', ['"', "x"]),
    ('"""""" x', ['""', "x"]),
    ('""""""" x', ['"" x']),
    ('"""""""" x', ['""', "x"]),
    ('""""""""" x', ['"""', "x"]),
    ('"""""""""" x', ['""" x']),
    ('""""""""""" x', ['"""', "x"]),
    ('"""""""""""" x', ['""""', "x"]),
    ("\\ x", ["\\", "x"]),
    ('\\" x', ['"', "x"]),
    ('\\"" x', ['" x']),
    ('\\""" x', ['"', "x"]),
    ('\\"""" x', ['""', "x"]),
    ('\\""""" x', ['"" x']),
    ('\\"""""" x', ['""', "x"]),
    ('\\""""""" x', ['"""', "x"]),
    ('\\"""""""" x', ['""" x']),
    ('\\""""""""" x', ['"""', "x"]),
    ('\\"""""""""" x', ['""""', "x"]),
    ('\\""""""""""" x', ['"""" x']),
    ('\\"""""""""""" x', ['""""', "x"]),
    ("\\\\ x", ["\\\\", "x"]),
    ('\\\\" x', ["\\ x"]),
    ('\\\\"" x', ["\\", "x"]),
    ('\\\\""" x', ['\\"', "x"]),
    ('\\\\"""" x', ['\\" x']),
    ('\\\\""""" x', ['\\"', "x"]),
    ('\\\\"""""" x', ['\\""', "x"]),
    ('\\\\""""""" x', ['\\"" x']),
    ('\\\\"""""""" x', ['\\""', "x"]),
    ('\\\\""""""""" x', ['\\"""', "x"]),
    ('\\\\"""""""""" x', ['\\""" x']),
    ('\\\\""""""""""" x', ['\\"""', "x"]),
    ('\\\\"""""""""""" x', ['\\""""', "x"]),
    ("\\\\\\ x", ["\\\\\\", "x"]),
    ('\\\\\\" x', ['\\"', "x"]),
    ('\\\\\\"" x', ['\\" x']),
    ('\\\\\\""" x', ['\\"', "x"]),
    ('\\\\\\"""" x', ['\\""', "x"]),
    ('\\\\\\""""" x', ['\\"" x']),
    ('\\\\\\"""""" x', ['\\""', "x"]),
    ('\\\\\\""""""" x', ['\\"""', "x"]),
    ('\\\\\\"""""""" x', ['\\""" x']),
    ('\\\\\\""""""""" x', ['\\"""', "x"]),
    ('\\\\\\"""""""""" x', ['\\""""', "x"]),
    ('\\\\\\""""""""""" x', ['\\"""" x']),
    ('\\\\\\"""""""""""" x', ['\\""""', "x"]),
    ("\\\\\\\\ x", ["\\\\\\\\", "x"]),
    ('\\\\\\\\" x', ["\\\\ x"]),
    ('\\\\\\\\"" x', ["\\\\", "x"]),
    ('\\\\\\\\""" x', ['\\\\"', "x"]),
    ('\\\\\\\\"""" x', ['\\\\" x']),
    ('\\\\\\\\""""" x', ['\\\\"', "x"]),
    ('\\\\\\\\"""""" x', ['\\\\""', "x"]),
    ('\\\\\\\\""""""" x', ['\\\\"" x']),
    ('\\\\\\\\"""""""" x', ['\\\\""', "x"]),
    ('\\\\\\\\""""""""" x', ['\\\\"""', "x"]),
    ('\\\\\\\\"""""""""" x', ['\\\\""" x']),
    ('\\\\\\\\""""""""""" x', ['\\\\"""', "x"]),
    ('\\\\\\\\"""""""""""" x', ['\\\\""""', "x"]),
# my additional cases
    ('"a', ['a']), # 1 "
    ('""a', ['a']),
    ('"""a', ['"a']),
    ('""""a', ['"a']),
    ('"""""a', ['"a']),
    ('""""""a', ['""a']),
    ('"""""""a', ['""a']),
    ('""""""""a', ['""a']),
    ('"""""""""a', ['"""a']),
    ('""""""""""a', ['"""a']),
    ('"""""""""""a', ['"""a']),
    ('""""""""""""a', ['""""a']), #12 "
    ('"a b', ['a b']),             # open
    ('""a b', ['a', 'b']),         # open-close
    ('"""a b', ['"a', 'b']),       # open-quote-close
    ('""""a b', ['"a b']),         # open-quote-close-open
    ('"""""a b', ['"a', 'b']),     # open-quote-close-open-close
    ('""""""a b', ['""a', 'b']),   # open-quote-close x 2
    ('"""""""a b', ['""a b']),     # open-quote-close x 2 - open
    ('""""""""a b', ['""a', 'b']), # open-quote-close x 2 - open-close
    ('"""""""""a b', ['"""a', 'b']),
    ('""""""""""a b', ['"""a b']),
    ('"""""""""""a b', ['"""a', 'b']),
    ('""""""""""""a b', ['""""a', 'b']),
    (r'\"a b', ['"a', 'b']),         # quote
    (r'\""a b', ['"a b']),           # quote-open
    (r'\"""a b', ['"a', 'b']),       # quote-open-close
    (r'\""""a b', ['""a', 'b']),     # quote-open-quote-close
    (r'\"""""a b', ['""a b']),       # quote-open-quote-close-open
    (r'\""""""a b', ['""a', 'b']),   # quote-open-quote-close-open-close
    (r'\"""""""a b', ['"""a', 'b']), # quote-[open-quote-close x 2]
    (r'\""""""""a b', ['"""a b']),
    (r'\"""""""""a b', ['"""a', 'b']),
    (r'\""""""""""a b', ['""""a', 'b']),
    (r'\"""""""""""a b', ['""""a b']),
    (r'\""""""""""""a b', ['""""a', 'b']),
    (r'\\"a b', ['\\a b']),         # backslash-open
    (r'\\""a b', ['\\a', 'b']),     # backslash-open-close
    (r'\\"""a b', ['\\"a', 'b']),   # backslash-open-quote-close
    (r'\\""""a b', ['\\"a b']),     # backslash-open-quote-close-open
    (r'\\"""""a b', ['\\"a', 'b']), # backslash-open-quote-close-open-close
    (r'\\""""""a b', ['\\""a', 'b']),
    (r'\\"""""""a b', ['\\""a b']),
    (r'\\""""""""a b', ['\\""a', 'b']),
    (r'\\"""""""""a b', ['\\"""a', 'b']),
    (r'\\""""""""""a b', ['\\"""a b']),
    (r'\\"""""""""""a b', ['\\"""a', 'b']),
    (r'\\""""""""""""a b', ['\\""""a', 'b']),
    ('"a b" c', ['a b', 'c']),     # open-close
    ('""a b" c', ['a', 'b c']),    # open-close+a b+open
    ('"""a b" c', ['"a', 'b c']),  # open-quote-close+a b+open
    ('""""a b" c', ['"a b', 'c']), # open-quote-close-open+a b-close
    ('"""""a b" c', ['"a', 'b c']),# open-quote-close-open-close+a b+open
    ('""""""a b" c', ['""a', 'b c']),
    ('"""""""a b" c', ['""a b', 'c']),
    ('""""""""a b" c', ['""a', 'b c']),
    ('"""""""""a b" c', ['"""a', 'b c']),
    ('""""""""""a b" c', ['"""a b', 'c']),
    ('"""""""""""a b" c', ['"""a', 'b c']),
    ('""""""""""""a b" c', ['""""a', 'b c']),
    ('"a b"" c', ['a b"', 'c']),          # open+a b+quote-close
    ('""a b"" c', ['a', 'b', 'c']),       # open-close+a b+open-close c
    ('"""a b"" c', ['"a', 'b', 'c']),     # open-quote-close+a b+open-close c
    ('""""a b"" c', ['"a b"', 'c']),      # open-quote-close-open+a b+quote-close c
    ('"""""a b"" c', ['"a', 'b', 'c']),   # open-quote-close-open-close+a b c
    ('""""""a b"" c', ['""a', 'b', 'c']), # open-quote-close x 2 +a b c
    ('"""""""a b"" c', ['""a b"', 'c']),  # open-quote-close x 2 - open+a b+quote-close
    ('""""""""a b"" c', ['""a', 'b', 'c']),
    ('"""""""""a b"" c', ['"""a', 'b', 'c']),
    ('""""""""""a b"" c', ['"""a b"', 'c']),
    ('"""""""""""a b"" c', ['"""a', 'b', 'c']),
    ('""""""""""""a b"" c', ['""""a', 'b', 'c']),
    ('"a b""" c', ['a b" c']), # open+a b+close-quote-open+c
    ('""a b""" c', ['a', 'b"', 'c']),
    ('"""a b""" c', ['"a', 'b"', 'c']),
    ('""""a b""" c', ['"a b" c']),
    ('"""""a b""" c', ['"a', 'b"', 'c']),
    ('""""""a b""" c', ['""a', 'b"', 'c']),
    ('"""""""a b""" c', ['""a b" c']),
    ('""""""""a b""" c', ['""a', 'b"', 'c']),
    ('"""""""""a b""" c', ['"""a', 'b"', 'c']),
    ('""""""""""a b""" c', ['"""a b" c']),
    ('"""""""""""a b""" c', ['"""a', 'b"', 'c']),
    ('""""""""""""a b""" c', ['""""a', 'b"', 'c']),
    (' \t  \\"a     "\\"b   \\"c" \t ', ['"a', '"b   "c']),
    (r'\"a     "\"b   \"c" \\\\\\', ['"a', '"b   "c', '\\\\\\\\\\\\']),
    (r'\"a     "\"b   \"c" \\\\\\"', ['"a', '"b   "c', '\\\\\\']),
    (r'\"a     "\"b   \"c" \\\\\\"', ['"a', '"b   "c', '\\\\\\']),
    (r'a "<>||&&^', [])
]

n=0
m = 0
for ex in examples:
    exe = "foo.exe "
    a, b, c = split(exe+ex[0], 3), parse_cmdline(exe+ex[0]), ctypes_split(exe+ex[0])
    if a != b:
        print ('case=<%s>: split!=parse_cmdline: %s != %s' %(ex[0],a,b))
        n+=1
    if b != c:
        print ('case=<%s>: parse_cmdline!=ctypes_split: %s != %s' %(ex[0],b,c))
        m+=1
if n:
    print('%d/%d tests failed (split!=parse_cmdline)' % (n,len(examples)))
if m:
    print('%d/%d tests failed (parse_cmdline!=ctypes_split)' % (m,len(examples)))
if not m and not n:
    print('All %d tests passed!'%len(examples))
