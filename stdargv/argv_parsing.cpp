/***
*stdargv.c - standard & wildcard _setargv routine
*
*       Copyright (c) Microsoft Corporation. All rights reserved.
*
*Purpose:
*       processes program command line, with or without wildcard expansion
*
*******************************************************************************/

#include <limits.h>
#include <mbstring.h>
#include <stdlib.h>

/***
*static void parse_cmdline(cmdstart, argv, args, argument_count, char_count)
*
*Purpose:
*       Parses the command line and sets up the argv[] array.
*       On entry, cmdstart should point to the command line,
*       argv should point to memory for the argv array, args
*       points to memory to place the text of the arguments.
*       If these are nullptr, then no storing (only counting)
*       is done.  On exit, *argument_count has the number of
*       arguments (plus one for a final nullptr argument),
*       and *char_count has the number of bytes used in the buffer
*       pointed to by args.
*
*Entry:
*       char *cmdstart - pointer to command line of the form
*           <progname><nul><args><nul>
*       char **argv - where to build argv array; nullptr means don't
*                       build array
*       char *args - where to place argument text; nullptr means don't
*                       store text
*
*Exit:
*       no return value
*       int *argument_count - returns number of argv entries created
*       int *char_count - number of chars used in args buffer
*
*Exceptions:
*
*******************************************************************************/


// should_copy_another_char helper functions
// should_copy_another_char is *ONLY* checking for DBCS lead bytes to see if there
// might be a following trail byte.  This works because the callers are only concerned
// about escaped quote sequences and other codepages aren't using those quotes.
static bool __cdecl should_copy_another_char(char const c) throw()
{
    // This is OK for UTF-8 as a quote is never a trail byte.
    return _ismbblead(c) != 0;
}

static bool __cdecl should_copy_another_char(wchar_t) throw()
{
    // This is OK for UTF-16 as a quote is never part of a surrogate pair.
    return false;
}

extern "C" __declspec( dllexport ) void __cdecl parse_cmdline(
    char*  cmdstart,
    char** argv,
    char*  args,
    size_t*     argument_count,
    size_t*     char_count
    ) throw()
{
    *char_count = 0;
    *argument_count  = 1; // We'll have at least the program name

    char c;
    int copy_char;                   /* 1 = copy char to *args */
    unsigned numslash;              /* num of backslashes seen */

    /* first scan the program name, copy it, and count the bytes */
    char* p = cmdstart;
    if (argv)
        *argv++ = args;

    // A quoted program name is handled here. The handling is much
    // simpler than for other arguments. Basically, whatever lies
    // between the leading double-quote and next one, or a terminal null
    // char is simply accepted. Fancier handling is not required
    // because the program name must be a legal NTFS/HPFS file name.
    // Note that the double-quote chars are not copied, nor do they
    // contribute to char_count.
    bool in_quotes = false;
    do
    {
        if (*p == '"')
        {
            in_quotes = !in_quotes;
            c = *p++;
            continue;
        }

        ++*char_count;
        if (args)
            *args++ = *p;

        c = *p++;

        if (should_copy_another_char(c))
        {
            ++*char_count;
            if (args)
                *args++ = *p; // Copy 2nd byte too
            ++p; // skip over trail byte
        }
    }
    while (c != '\0' && (in_quotes || (c != ' ' && c != '\t')));

    if (c == '\0')
    {
        p--;
    }
    else
    {
        if (args)
            *(args - 1) = '\0';
    }

    in_quotes = false;

    // Loop on each argument
    for (;;)
    {
        if (*p)
        {
            while (*p == ' ' || *p == '\t')
                ++p;
        }

        if (*p == '\0')
            break; // End of arguments

        // Scan an argument:
        if (argv)
            *argv++ = args;

        ++*argument_count;

        // Loop through scanning one argument:
        for (;;)
        {
            copy_char = 1;

            // Rules:
            // 2N     backslashes   + " ==> N backslashes and begin/end quote
            // 2N + 1 backslashes   + " ==> N backslashes + literal "
            // N      backslashes       ==> N backslashes
            numslash = 0;

            while (*p == '\\')
            {
                // Count number of backslashes for use below
                ++p;
                ++numslash;
            }

            if (*p == '"')
            {
                // if 2N backslashes before, start/end quote, otherwise
                // copy literally:
                if (numslash % 2 == 0)
                {
                    if (in_quotes && p[1] == '"')
                    {
                        p++; // Double quote inside quoted string
                    }
                    else
                    {
                        // Skip first quote char and copy second:
                        copy_char = 0; // Don't copy quote
                        in_quotes = !in_quotes;
                    }
                }

                numslash /= 2;
            }

            // Copy slashes:
            while (numslash--)
            {
                if (args)
                    *args++ = '\\';
                ++*char_count;
            }

            // If at end of arg, break loop:
            if (*p == '\0' || (!in_quotes && (*p == ' ' || *p == '\t')))
                break;

            // Copy char into argument:
            if (copy_char)
            {
                if (args)
                    *args++ = *p;

                if (should_copy_another_char(*p))
                {
                    ++p;
                    ++*char_count;

                    if (args)
                        *args++ = *p;
                }

                ++*char_count;
            }

            ++p;
        }

        // Null-terminate the argument:
        if (args)
            *args++ = '\0'; // Terminate the string

        ++*char_count;
    }

    // We put one last argument in -- a null pointer:
    if (argv)
        *argv++ = nullptr;

    ++*argument_count;
}
