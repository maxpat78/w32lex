from w32lex import *

print(cmd_parse('a >b c'))
print(cmd_parse('a >>b c'))
print(cmd_parse('a <<b c'))
print(cmd_parse('a <&1 >&2'))
print(cmd_parse('a 2>&1 b'))
print(cmd_parse('a 2>^&1 b'))
print(cmd_parse('a 2>>&1 >b c'))
print(cmd_parse('a 2>>>>&1 >b c'))
print(cmd_parse('a ||| b'))

print(cmd_parse('a>b & c'))
print(cmd_parse('a>>b & c'))
print(cmd_parse('a|&2 & b'))
print(cmd_parse('a&b & c'))
print(cmd_parse('a||b & c'))
print(cmd_parse('a>b&c'))
print(cmd_parse('a b>c&d||e'))

print(cmd_parse('(a b)'))
print(cmd_parse('"(a b)"'))
try:
    print(cmd_parse('^(a b)'))
except NotExpected:
    print("cmd_parse('^(a b)')")
print(cmd_parse('(a %USERNAME%)'))
print(cmd_parse('((a b c))'))
print(cmd_parse('(a b) (c d) (e f)'))
print(cmd_parse('(a 2>b 1>&2 c)'))
try:
    print(cmd_parse('(a))'))
except NotExpected:
    print("cmd_parse('(a))')")

try:
    print(cmd_parse('((a)'))
except NotExpected:
    print("cmd_parse('((a)')")
