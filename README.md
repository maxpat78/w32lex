w32_lex
=======

This package contains a pure Python 3 implementation of `split`, `join` and
`quote` functions similar to those found in the builtin `shlex.py` module, but
suitable for the Windows world.

It was tested against optimum [mslex](https://github.com/smoofra/mslex) project and it
gives the same results (but with no regexes used), except that only the
equivalent CommandLineToArgvW (and parse_cmdline from VC run-time) parser is
implemented, not the CMD.EXE (Windows command prompt) one.

At a glance, a compatible modern Win32 parser follows such rules when splitting a command line:
- leading and trailing spaces are stripped from command line
- unquoted whitespace separates arguments
- quotes:
  * `"` opens a block
  * `""` opens and closes a block;
  * `"""` opens, adds a literal `"` and closes a block
- backslashes, only if followed by `"`:
  * `2n -> n`, and opens/closes a block
  * `(2n+1) -> n`, and adds a literal `"`
- all other characters are simply copied

`split` accepts an optional argument `mode` to set the compatibility level:
with mode=0 (default), it behaves like mslex parser; if mode&1, first argument
is parsed in a simplified way (i.e. argument is everything up to the first space if
unquoted, or the second quote otherwise); if mode&2, emulate parse_cmdline from
2005 onward (a `""` inside a quoted block emit a literal quote _without_ ending
such block).

w32_cmd
=======

This experimental module tries to provide a conformant CMD parser with `cmd_parse`.

Some annotations about a Windows Command Prompt (CMD) parser.

CMD itself parses the command line before invoking commands, in an indipendent
way from `parse_cmdline` (used internally by C apps).

With the help of a simple C Windows app, we can look at the command line that 
CMD passes to an external command:
```
#include <windows.h>
#pragma comment(linker,"/DEFAULTLIB:USER32.lib")
int WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    return MessageBox(0, lpCmdLine, "lpCmdLine=", MB_OK);
}
```
The results we see, show that the parsing work CMD carries on is not trivial,
not always clear and, perhaps, not constant in time. Some points:

- `:` at line start make the parser ignore the rest;
- ` ;,=` at line start are ignored, elsewhere are treated mostly as whitespace;
- `|&<>`, and their doubled counterparts, are forbidden at line start;
- `()` at line start is forbidden;
- `^` escapes the character following;
- pipe `|`, redirection `<, <<, >, >>` and boolean operators `&, &&, ||` split
a line in subparts, since one or more commands have to be issued; white space
is not needed between them;
- longer or different sequences of pipe, redirection or boolean operators are
forbidden;
- `%var%` or `^%var%` are replaced with the corresponding environment variable,
if set (while `^%var^%` and `%var^%` are both considered escaped);
- all the other characters are simply copied and passed to the external
commands; if the internal ones are targeted, further/different processing could
occur; the same if special CMD environment variables are set.

Some curious samples:
- `&a [b (c ;d !e %f ^g ,h =i` are valid file system names
- `;;a` calls "a", `^ a` calls " a", but `^;;a` calls ";"
- given a `;d` file (the same with `,h` and `=i`):
  * `dir;d` -> not found
  * `dir ;d`  -> not found
  * `dir ^;d` -> not found
  * `dir ";d"` -> OK
  * `dir "?d"` -> OK
- `dir ^>b` -> lists [b file above (!?), but using our simple Windows app we
find that `>b` was passed literally, as expected
