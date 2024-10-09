# -*- coding: latin-1 -*-

COPYRIGHT = '''Copyright (C)2024, by maxpat78.'''

import os

""" Some annotations about a Windows Command Prompt (CMD) parser.

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
find that `>b` was passed literally, as expected"""



class NotExpected(Exception):
    def __init__ (p, s):
        super().__init__(s + ' is not expected')


def cmd_parse(s):
    "Pre-process a command line like Windows CMD Command Prompt"
    escaped = 0
    percent = 0
    meta = 0 # special chars in a row
    arg = ''
    argv = []

    if not s or s[0] == ':': return []

    # remove (ignore) some leading chars
    for c in ' ;,=': s = s.lstrip(c)
    
    # some combinations at line start are prohibited
    if s[0] in '|&<>':
        raise NotExpected(s[0])
    if len(s)>1 and s[0:2] == '()':
        raise NotExpected(')')

    i = 0
    while i < len(s):
        c = s[i]
        i += 1
        if c == '^':
            if escaped:
                arg += c
                escaped = 0
            else:
                escaped = 1
            continue
        # %VAR%   -> replace with os.environ['VAR'] *if set*
        # ^%VAR%  -> same as above
        # %VAR^%
        # ^%VAR^% -> keep literal %VAR%
        # %%VAR%% -> replace internal %VAR% only
        if c == '%':
            arg += c
            if percent and percent != i-1:
                if not escaped:
                    vname = s[percent:i-1]
                    val = os.environ.get(vname)
                    #~ print('debug: "%s": trying to replace var "%s" with "%s"' %(s,vname,val))
                    if val: arg = arg.replace('%'+vname+'%', val)
                percent = 0
                continue
            percent = i # record percent position
            continue
        # pipe, redirection, &, && and ||: break argument, and set aside special char/couple
        # multiple pipe, redirection, &, && and || in sequence are forbidden
        if c in '|<>&':
            if escaped:
                arg += c
                escaped = 0
                continue
            meta += 1
            # 3 specials in a row is forbidden
            if meta == 3: raise NotExpected(c)
            # if 2 specials undoubled
            if len(argv) >= 2 and argv[-1] in '|<>&' and c != argv[-1]: raise NotExpected(c)
            # push argument, if any, and special char/couple
            if arg: argv += [arg]
            argv += [c]
            # if doubled operator: ||, <<, >>, &&
            if i < len(s) and s[i] == c:
                argv[-1] = 2*c
                i += 1
                meta += 1
            arg = ''
            continue
        if c in ' ,;=':
            percent = 0
            #~ if escaped:
                #~ argv += [c]
                #~ continue
        else:
            meta = 0
        arg += c
        escaped = 0
    argv += [arg]
    return argv



if __name__ == '__main__':
    import mslex

    os.environ['A'] = '!subst!' # Win32 environment is case-insensitive

    cases = [
    (r'', []),
    (r':dir', []),
    (r'dir "a   b   c"   d   e   f', ['dir "a   b   c"   d   e   f']),
    (r'dir ^"a b^"', ['dir "a b"']), 
    (r'dir %a%', ['dir !subst!']), # dir <a replaced>
    (r'dir ^%a%', ['dir !subst!']), # dir <a replaced>
    (r'dir %%a%%', ['dir %!subst!%']), # dir %<a replaced>%
    (r'dir ^%a^%', ['dir %a%']),
    (r'dir %a^%', ['dir %a%']),
    (r'dir %a %b c', ['dir %a %b c']),
    (r'a|b', ['a', '|', 'b']),
    (r'a||b', ['a', '||', 'b']),
    (r'a&b', ['a', '&', 'b']),
    (r'a&&b', ['a', '&&', 'b']),
    (r'a>b', ['a', '>', 'b']),
    (r'a "b c" | b "c d" | c', ['a "b c" ', '|', ' b "c d" ', '|', ' c']),
    (r';;;a,, b, c===', ['a,, b, c===']), # ignore leading special chars
    (r'^;;a', [';',';a']), # CMD try to execute ";"
    (r'^ a', [' a']),
    (r'a>>b||c', ['a', '>>', 'b', '||', 'c']),
    (r'a>>>b||c', 'NE'), # NE = raise NotExpected exception
    (r'a>>b||>>c', 'NE'),
    (r'a >> b || >> c', 'NE'),
    (r'a >| b', 'NE'),
    (r'&whoami', 'NE'),
    ]

    for ex in cases:
        try:
            if ex[1] != cmd_parse(ex[0]):
                print('Test case "%s" failed with %s' % (ex[0], cmd_parse(ex[0])))
            x = mslex.split(ex[0], check=0)
            if ex[1] != x:
                print('note: mslex splits "%s" differently: %s' % (ex[0], x))
            else:
                print('note: mslex splits "%s" the same' % ex[0])
        except:
            if ex[1] == 'NE':
                print('Test case "%s" raised NotExpected as...expected!'%ex[0])
            else:
                print('Test case "%s" raised an unexpected exception!'%ex[0])
