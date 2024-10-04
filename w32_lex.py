COPYRIGHT = '''Copyright (C)2024, by maxpat78. GNU GPL v2 applies.'''

__all__ = ["split", "quote", "join"]

def countc(s, i):
    "Count repetitions of s[i] and return (count, next_char)"
    c = s[i]
    n = 0
    while i < len(s) and s[i] == c:
        n += 1
        i += 1
    nc = None
    if i != len(s):
        nc = s[i]
    return (n, nc)

def split(s):
    "Split a command line like Win32 CommandLineToArgvW"
    argv = []  # resulting arguments list
    arg = ''   # current argument
    quoted = 0 # if current argument is quoted

    if not s: return []
    s = s.strip() # strip leading and trailing whitespace
    
    def nextc(s, i):
        "Next char or None"
        if len(s) > i: return s[i]

    # Special rules (post 2008?):
    # Quotes: " open block; "" open and close block; """ open, add literal " and close block
    # Backslashes, if followed by ":
    #  2n -> n, and open/close block
    #  (2n+1) -> n, and add literal "
    i = 0
    while i < len(s):
        z = nextc(s, i+1)
        if s[i] == '\\':
            # count backslashes
            backslashes, nc = countc(s, i)
            i += backslashes
            if nc == '"':
                # take 2n, emit n
                arg += (backslashes//2) * '\\'
                if backslashes%2:
                    # if odd, add the escaped literal quote
                    arg += '"'
                    i += 1
            else:
                # simply append the backslashes
                arg += backslashes * '\\'
            continue
        if s[i] == '"' and z == '"': # double or triple quote
            if quoted:
                # close and emit a quote
                quoted = not quoted
                arg += '"'
                i += 2
            else:
                # open, close and eventually emit a quote
                x = nextc(s, i+2) # 3-quotes in a row?
                if x == '"':
                    arg += '"'
                    i += 1
                i += 2
            continue
        if s[i] == '"': # single quote
            quoted = not quoted
            i += 1
            continue
        if s[i] in ' \t':
            if quoted:
                # append whitespace
                arg += s[i]
                i += 1
                continue
            # skip whitespace
            while s[i] in ' \t':
                i += 1
            # append argument
            argv += [arg]
            arg = ''
            continue
        # append normal char
        arg += s[i]
        i += 1
    # append last arg
    argv += [arg]
    return argv

def quote(s):
    "Quote a string in a way suitable for the split function"
    if not s: return '""'
    arg = ''
    i = 0
    while i < len(s):
        if s[i] == '\\':
            # count backslashes
            backslashes, nc = countc(s, i)
            i += backslashes
            if nc == '"':
                # take n \ and emit 2n+1 \ to escape following "
                arg += (backslashes*2)*'\\' + '\\"'
                i += 1
            else:
                # if at end, we emit 2n \ since we'll quote arg
                if not nc:
                    arg += (backslashes*2)*'\\'
                else:
                    arg += backslashes*'\\' # simply copy n \
            continue
        if s[i] == '"':
            arg += '\\"' # escape the "
            i += 1
            continue
        arg += s[i] # append any other char, withespace included
        i += 1
        continue
    arg = '"'+arg+'"' # always quote argument
    return arg

def join(argv):
    "Quote and join list items, so that split returns the same"
    return ' '.join([quote(arg) for arg in argv])
