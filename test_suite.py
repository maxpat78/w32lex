import unittest, sys
from w32lex import *

# from https://github.com/smoofra/mslex
cases = [
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
    (r'\"a     "\"[!b()]   \"c" []\\\\\\"', ['"a', '"[!b()]   "c', '[]\\\\\\']),
    (r'^|!(["\"])', ['^|!([])']),
    (r'a "<>||&&^', ['po'])
]


if os.name == 'nt':
    from ctypes import *
    from ctypes import windll, wintypes

    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [wintypes.LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(wintypes.LPWSTR)

    LocalFree = windll.kernel32.LocalFree
    LocalFree.argtypes = [wintypes.HLOCAL]
    LocalFree.restype = wintypes.HLOCAL

    def ctypes_split(s, argv0=True):
        if argv0:
            cmdline = "foo.exe " + s
            start = 1
        else:
            cmdline = s
            start = 0
        argc = c_int()
        argv = CommandLineToArgvW(cmdline, byref(argc))
        result = [argv[i] for i in range(start, argc.value)]
        LocalFree(argv)
        return result

    try:
        stdargv05 = CDLL('.\\stdargv\\STDARGV2005.dll')
        #~ stdargv05 = CDLL('.\\stdargv\\STDARGV98.dll')
    except:
        stdargv05 = None
        print('warning: cannot test STDARGV2005 compatibility')

    if stdargv05:
        def parse_cmdline(s, stdargv=stdargv05, argv0=True):
            if argv0:
                cmdline = create_string_buffer(b"foo.exe " + s.encode())
                start = 1
            else:
                cmdline = create_string_buffer(s.encode())
                start = 0
            numargs = c_int(0)
            numchars = c_int(0)
            # void parse_cmdline(char *cmdstart, char **argv, char *args, int *numargs, int *numchars);
            stdargv.parse_cmdline(cmdline, c_void_p(0), c_char_p(0), byref(numargs), byref(numchars))

            argv = (c_char_p * numargs.value)()
            args = create_string_buffer(numchars.value)
            stdargv.parse_cmdline(cmdline, argv, args, byref(numargs), byref(numchars))

            # build a result list similar to ctypes_split
            r = []
            for i in range(start, numargs.value-1): # omit last NULL (None)
                r += [argv[i].decode()] # returns str, not bytes
            return r
    else:
            parse_cmdline = None



class w32lex(unittest.TestCase):
    def test_0(p):
        "Test default SHELL32 mode"
        for case in cases:
            p.assertEqual(split(case[0]), ctypes_split(case[0]), 'CommandLineToArgvW splits differently: '+case[0])

    def test_1(p):
        "Test quoting"
        for case in cases:
            a = split(case[0])
            p.assertEqual(a, split(join(a)), 'failed quoting: '+case[0])

    def test_2(p):
        "Test VC2005+ mode"
        if not stdargv05: return
        for case in cases:
            a, b = split(case[0], SPLIT_VC2005), parse_cmdline(case[0])
            try:
                p.assertEqual(a, b, 'VC Runtime (2005+) splits differently: '+ case[0])
            except:
                print(sys.exception())

    def test_3a(p):
        "Test full SHELL32 vs VC Runtime (2005+) (with true argv[0])"
        for case in cases:
            try:
                p.assertEqual(ctypes_split(case[0], argv0=False), parse_cmdline(case[0], argv0=False), 'CommandLineToArgvW != parse_cmdline: '+case[0])
            except:
                print(sys.exception())

    def test_3b(p):
        "Test full SHELL32 mode (with true argv[0])"
        for case in cases:
            try:
                p.assertEqual(split(case[0], SPLIT_ARGV0), ctypes_split(case[0], argv0=False), 'CommandLineToArgvW (full) splits differently: ' + case[0])
            except:
                print(sys.exception())



if __name__ == '__main__':
    if os.name != 'nt':
        print('Nothing to test outside Windows')
    else:
        unittest.main()
