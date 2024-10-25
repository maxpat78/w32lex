from w32lex import *

print(cmd_split('a >b c'))
print(cmd_split('a >>b c'))
print(cmd_split('a <<b c'))
print(cmd_split('a <&1 >&2'))
print(cmd_split('a 2>&1 b'))
print(cmd_split('a 2>^&1 b'))
print(cmd_split('a 2>>&1 >b c'))
print(cmd_split('a 2>>>>&1 >b c'))
print(cmd_split('a ||| b'))

print(cmd_split('a>b & c'))
print(cmd_split('a>>b & c'))
print(cmd_split('a|&2 & b'))
print(cmd_split('a&b & c'))
print(cmd_split('a||b & c'))
print(cmd_split('a>b&c'))
print(cmd_split('a b>c&d||e'))

print(cmd_split('(a b)'))
print(cmd_split('"(a b)"'))
try:
    print(cmd_split('^(a b)'))
except NotExpected:
    print("cmd_split('^(a b)')")
print(cmd_split('(a %USERNAME%)'))
print(cmd_split('((a b c))'))
print(cmd_split('(a b) (c d) (e f)'))
print(cmd_split('(a 2>b 1>&2 c)'))
try:
    print(cmd_split('(a))'))
except NotExpected:
    print("cmd_split('(a))')")

try:
    print(cmd_split('((a)'))
except NotExpected:
    print("cmd_split('((a)')")
