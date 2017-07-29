from __future__ import unicode_literals, print_function, absolute_import
import json
from jsonpath_rw import parse, lexer

d = {'d': {'b': 'f'}}

print(json.dumps(d, indent=4))

p = parse('$.d.b')

print(p.find(d).pop().value)

ignore_cases = ['$', '[', ']', '.']
parsed = []

for token in lexer.JsonPathLexer().tokenize('$[d][b]["hello.world"][0]["1.453"]'):
    if token.value not in ignore_cases:
        print(token)
        parsed.append(token.value)

print(parsed)

from path_creator import AutoDict

print(AutoDict(d))
import sys
print(sys.flags)

