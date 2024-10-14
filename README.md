w32lex
======

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
- all other characters are simply copied.

`split` accepts an optional argument `mode` to set the compatibility level:
- with mode=SPLIT_SHELL32 (default), it behaves like mslex parser;
- with mode=SPLIT_ARGV0, first argument is parsed in a simplified way (i.e. argument is
everything up to the first space if unquoted, or the second quote otherwise);
- with mode=SPLIT_VC2005, it emulates parse_cmdline from 2005 onward (a `""` inside a
quoted block emit a literal quote _without_ ending such block).

To parse the line like CMD does, separate functions `cmd_split` and
`cmd_parse` are provided, with a corresponding `cmd_quote`.

`cmd_split` and `cmd_parse` accept a mode argument where a fourth value can
be specified: CMD_VAREXPAND to make the parser expand environment `%variables%`
in place.


Some annotations about a Windows Command Prompt (CMD) parser follow.

CMD itself parses the command line _before_ invoking commands, in an indipendent
way from `parse_cmdline` (used internally by C apps) or CommandLineToArgvW.

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
or, from the CMD line itself:
```
#include <windows.h>
#pragma comment(linker,"/DEFAULTLIB:USER32.lib")
void main() {
   puts(GetCommandLine());
}
```

The results we see, show that the parsing work CMD carries on is not trivial,
not always clear and not constant in time. Some points:

- `:` at line start makes the parser ignore the rest (Windows 2000+) or signal an error;
- ` ;,=@` and _TAB_ (one or more) at line start are ignored but
- a starting `@` is a special character in BAT scripts (=line echo off);
- `|&<>`, and their doubled counterparts, are forbidden at line start;
- `()` at line start is forbidden;
- `^` escapes the character following; alone at line start, it should be
forbidden (it asks for a second character to escape).
- `"` starts a quoted block, escaping all special characters inside it except
`%` , until another quote, or LF/EOS, is found. Quote belongs to the block
and only the starting quote can be escaped by `^`.
- pipe `|`, redirection `<, <<, >, >>` and boolean operators `&, &&, ||` split
a line in subparts, since one or more commands have to be issued; white space
is not needed around them;
- longer or different sequences of pipe, redirection or boolean operators are
forbidden;
- `%var%` or `^%var%` are replaced with the corresponding environment variable,
if set (while `^%var^%` and `%var^%` are both considered fully escaped);
- all the other characters are simply copied and passed to the external
commands. If the internal ones are targeted, further/different processing could
occur; the same if special CMD environment variables are set.

Some curious samples:
- `&a [b (c ;d !e %f ^g ,h =i` are valid file system names
- `^ a` calls " a" (Windows 2000+) or ignores the line
- `^;;a` calls ";" passing argument ";a" (Windows 2000+; the same with `,=` characters) or ignores the line
- given a `;d` file (the same with `,h` and `=i`):
  * `dir;d` -> not found
  * `dir ;d`  -> not found
  * `dir ^;d` -> not found
  * `dir ";d"` -> OK
  * `dir "?d"` -> OK
- `dir ^>b` -> lists `[b` file above (!?), but using our simple Windows app we
find that `>b` was passed literally, as expected

Things get even more complex if we take in account old DOS COMMAND.COM:
- a starting `@` outside BAT files is forbidden
- `^` is not recognized
- only a single `;,=` at line start is ignored
- `:` at line start is ignored (Windows 95+) or is bad
- `&, &&, ||` operators and parentheses `()` are not recognized

A sample assembly program to play with old DOS command line:
```
; compile with NASM PRL.ASM -o PRL.COM
org 100h
bits 16

; DS:0000   PSP seg preloaded by DOS
; DS:0080   command-line length (following)
cmp byte [80h], 0
jnz GO
int 20h ; terminate COM
GO:
mov di, 80h
PRINT:
inc di
mov dl, [ds:di]
cmp dl, 0Dh
jz END
mov ah, 2 ; write char in DL to STDOUT
int 21h
jmp PRINT
END:
int 20h
```
