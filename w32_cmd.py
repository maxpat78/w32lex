# -*- coding: latin-1 -*-

COPYRIGHT = '''Copyright (C)2024, by maxpat78.'''

import os
from w32_lex import split


class NotExpected(Exception):
    def __init__ (p, s):
        super().__init__(s + ' is not expected')


def cmd_parse(s):
    "Pre-process a command line like Windows CMD Command Prompt"
    escaped = 0
    quoted = 0
    percent = 0
    meta = 0 # special chars in a row
    arg = ''
    argv = []

    # remove (ignore) some leading chars
    for c in ' ;,=\t': s = s.lstrip(c)
    
    if not s or s[0] == ':': return []
    
    # push special batch char
    if  s[0] == '@':
        argv = ['@']
        s = s[1:]
    # some combinations at line start are prohibited
    if s[0] in '|&<>':
        raise NotExpected(s[0])
    if len(s)>1 and s[0:2] == '()':
        raise NotExpected(')')

    i = 0
    while i < len(s):
        c = s[i]
        i += 1
        if c == '"':
            if not escaped: quoted = not quoted
        if c == '^':
            if escaped or quoted:
                arg += c
                escaped = 0
            else:
                escaped = 1
            continue
        # %VAR%   -> replace with os.environ['VAR'] *if set* and even if quoted
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
            if escaped or quoted:
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
        if c in ' ,;=\t':
            percent = 0
            # exception (Windows 2000+): starting special char escaped
            if i==2 and escaped and c in ',;=':
                argv += [c]
                escaped = 0
                continue
        else:
            meta = 0
        arg += c
        escaped = 0
    argv += [arg]
    return argv

def cmd_split(s):
    "Post-process with w32_lex.split a command line parsed by cmd_parse (mimic mslex behavior)"
    argv = []
    for tok in cmd_parse(s):
        if tok in ('@','<','|','>','<<','>>','&','&&','||'):
            argv += [tok]
            continue
        argv += split(tok)
    return argv



if __name__ == '__main__':
    import mslex

    os.environ['A'] = '!subst!' # Win32 environment is case-insensitive

    cases = [
    (r'', []),
    (r':dir', []), # ignore line (Windows 2000+) or signal error
    ('@a\t==b c', ['@', 'a\t==b c']), # @ is special batch char (command)
    (r'dir "a   b   c"   d   e   f', ['dir "a   b   c"   d   e   f']), # whitespace is preserved despite of quote
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
    (r'^;;a', [';',';a']), # execute ";" with arg ";a" (Windows 2000+) or ignore
    (r'^ a', [' a']), # execute " a" (Windows 2000+) or ignore
    (r'a>>b||c', ['a', '>>', 'b', '||', 'c']),
    (r'a "<>||&&^"', ['a "<>||&&^"']), # quoted block escape all special characters except %
    (r'a "<>||&&%A%"', ['a "<>||&&!subst!"']),
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
            # Comparison with mslex has no sense, since it does CommandLineToArgvW parsing all in one
            x = mslex.split(ex[0], check=0)
            y = cmd_split(ex[0])
            if y != x:
                print('note: mslex splits "%s" differently: %s intead of %s' % (ex[0], x, y))
            else:
                print('note: mslex splits "%s" the same' % ex[0])
        except:
            if ex[1] == 'NE':
                print('Test case "%s" raised NotExpected as...expected!'%ex[0])
            else:
                print('Test case "%s" raised an unexpected exception!'%ex[0])
