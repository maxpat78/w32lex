COPYRIGHT = '''Copyright (C)2024, by maxpat78.'''

__all__ = ["split", "quote", "join"]


def split(s, mode=0):
    """Split a command line like CommandLineToArgvW (SHELL32) or parse_cmdline
    (VC Runtime). With mode&1, do special simplified parsing for first argument;
    with mode&2, emulate 2005 and newer parse_cmdline."""
    argv = []       # resulting arguments list
    arg = ''        # current argument
    quoted = 0      # if current argument is quoted
    backslashes = 0 # backslashes in a row
    quotes = 0      # quotes in a row
    space = 0       # whitespace in a row

    if not s: return []

    # Parse 1st argument (executable pathname) in a simplified way, parse_cmdline conformant.
    # Argument is everything up to first space if unquoted, or second quote otherwise
    if mode&1:
        i=0
        for c in s:
            i += 1
            if c == '"':
                quoted = not quoted
                continue
            if c in ' \t':
                if quoted:
                    arg += c
                    continue
                break
            arg += c
        argv += [arg]
        arg=''
        quoted = 0
        s = s[i:] # strip processed string

    s = s.strip() # strip leading and trailing whitespace
    if not s: return argv
    
    # Special rules:
    # Quotes: " open block; "" open and close block; """ open, add literal " and close block
    # Backslashes, if followed by ":
    #  2n -> n, and open/close block
    #  (2n+1) -> n, and add literal "
    for c in s:
        # count backslashes
        if c == '\\':
            space = 0 # reset count
            backslashes += 1
            continue
        if c == '"':
            space = 0  # reset count
            if backslashes:
                # take 2n, emit n
                arg += '\\' * (backslashes//2)
                if backslashes%2:
                    # if odd, add the escaped literal quote
                    arg += c
                    backslashes = 0
                    continue
                backslashes = 0
            quoted = not quoted
            quotes += 1
            # 3" in a row unquoted or 2" quoted -> add a literal "
            if quotes == 3 or quotes == 2 and quoted:
                arg += c
                quoted = not quoted
                if mode&2:
                    quoted = not quoted # new parse_cmdline does NOT change quoting
                quotes = 0
            continue
        if backslashes:
            # simply append the backslashes
            arg += '\\' * backslashes
        quotes = backslashes = 0
        if c in ' \t':
            if quoted:
                # append whitespace
                arg += c
                continue
            # ignore whitespace in excess between arguments
            if not space:
                # append argument
                argv += [arg]
                arg = ''
            space += 1
            continue
        space = 0
        # append normal char
        arg += c
    if backslashes:
        arg += '\\' * backslashes
    # append last arg
    argv += [arg]
    return argv

def quote(s):
    "Quote a string in a way suitable for the split function"
    backslashes = 0 # backslashes in a row
    if not s: return '""'
    arg = ''
    for c in s:
        # count backslashes
        if c == '\\':
            backslashes += 1
            continue
        if c == '"':
            if backslashes:
                # take n, emit 2n
                arg += '\\' * (2*backslashes)
                backslashes = 0
            # escape the "
            arg += '\\"'
            continue
        if backslashes:
            # add literally
            arg += backslashes*'\\'
            backslashes = 0
        arg += c
    if backslashes:
        # double at end, since we quote hereafter
        arg += (2*backslashes)*'\\'
    arg = '"'+arg+'"' # always quote argument
    return arg

def join(argv):
    "Quote and join list items, so that split returns the same"
    return ' '.join([quote(arg) for arg in argv])
