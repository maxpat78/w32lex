w32_lex
=======

This package contains a pure Python 3 implementation of `split`, `join` and
`quote` functions similar to those found in the builtin `shlex.py` module, but
suitable for the Windows world.

It was tested against optimum [mslex](https://github.com/smoofra/mslex project) and it
gives the same results, except that only the equivalent CommandLineToArgvW
parser is implemented, not the CMD.EXE (Windows command prompt) one.

At a glance, a compatible modern Win32 parser follows such rules when splitting a command line:
- leading and trailing spaces are stripped from command line
- non quoted whitespace separates arguments
- quotes: `"` opens a block; `""` opens and closes a block; `"""` opens, adds a literal `"` and closes a block
- backslashes, only if followed by `"`:
* `2n -> n`, and open/close block
* `(2n+1) -> n`, and add literal `"`
- all other characters are simply copied
