"""
This package leverages jsonpath_rw to take an input json payload with defined schema
and map to an output json with a defined schema

Examples to come
"""

from __future__ import unicode_literals, print_function, absolute_import

from jsonpath_rw import parse, lexer


class AutoDict(dict):
    """
    AutoDict extends a dictionary by auto creating a new
    dictionary if the key does not exist in the current dictionary.

    Example:
        >>> d = AutoDict({"foo":"bar"})
        >>> d['dne']
        {}

    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class JsonObj(dict):
    """
    JsonObj takes a dictionary loaded from a raw json
    and converts it to a serialized object, which allows for
    access of attributes via dot notation
    """

    def __init__(self, loaded_json):
        dict.__init__(self)
        self._load_object(loaded_json)

    def _load_object(self, j):
        if isinstance(j, dict):
            for k, v in j.iteritems():
                if isinstance(v, dict):
                    setattr(self, k, JsonObj(v))
                    self[k] = JsonObj(v)
                elif isinstance(v, list):
                    l = []
                    for e in v:
                        l.append(JsonObj(e))
                    setattr(self, k, l)
                    self[k] = l
                else:
                    self[k] = v
                    setattr(self, k, v)
        else:
            return j


class PathToTuple(lexer.JsonPathLexer):
    """
    This uses the JsonPathLexer to get tuples from
    a json path. These tuples are then used in OutputCreator
    """
    # TODO: create more documentation

    ignore_cases = ['$',
                    '[',
                    ']',
                    '.',
                    ]

    def __init__(self, debug=False):
        lexer.JsonPathLexer.__init__(self, debug=debug)

    def get_tuple(self, path):
        agg = []

        for token in self.tokenize(path):
            if hasattr(token, 'value'):
                if token.value not in self.ignore_cases:
                    agg.append(token.value)

        return tuple(agg)

    def validate_path(self):
        raise NotImplementedError('Need to add path validation')


class AggregatePaths(object):
    # TODO: Implement me
    pass


class OutputCreator(object):
    """
    Output creator takes an input_payload and then can generate an output
    json payload based on a set of mappings. self.create_output(path_map)
    is the main function that will generate outputs
    """
    # TODO: improve documentation

    def __init__(self, input_payload):
        self.input_payload = input_payload

    def _generate_initial_output(self, path_map):
        output = AutoDict()
        pt = PathToTuple()

        for raw_pathway, value_path in path_map.iteritems():
            path_tuple = pt.get_tuple(raw_pathway)
            p = parse(value_path)
            value_ex = p.find(self.input_payload)

            if len(value_ex):
                if hasattr(value_ex[0], 'value'):
                    value = value_ex.pop().value
                    self._recur_dict(path_tuple, value, output)
        return output

    def _recur_dict(self, pathway, value, auto_dict):
        if len(pathway) == 0:
            return
        elif len(pathway) == 1:
            auto_dict[pathway[0]] = value
        else:
            temp = auto_dict[pathway[0]]
            return self._recur_dict(pathway[1:], value, temp)

    def _fix_arrays(self, d):
        n = self._dict_to_array(d)

        if isinstance(d, dict):
            if isinstance(n, dict):
                temp = {}
                for k, v in n.iteritems():
                    temp[k] = self._fix_arrays(v)
                return temp
            if isinstance(n, list):
                temp = []
                for v in n:
                    temp.append(self._fix_arrays(v))
                return temp
        elif isinstance(d, list):
            temp = [self._fix_arrays(v) for v in n]
            return temp
        else:
            return d

    def _dict_to_array(self, d):
        nums = []
        temp = []

        if isinstance(d, dict):
            if all(isinstance(k, int) for k in d.keys()):
                for k, v in d.iteritems():
                    nums.append(int(k))
                nums.sort()
                for num in nums:
                    temp.append(d[num])
                return self._dict_to_array(temp)
        return d

    def create_output(self, path_map):

        initial_output = self._generate_initial_output(path_map)
        return self._fix_arrays(initial_output)


if __name__ == '__main__':

    i = {'key': 134123, 'data': {'point1': 1234534, 'point2': 123546765, "arr": [{"this": 23}, {"that": 345}]}}

    path_map = {
        '$.key.value': '$.data.point1',
        '$.data.point1': '$.key',
        '$.data.point3': '$.data.point2',
        '$.data.point5': '$.data.arr[0].this',
        '$.data.arr[0].this': '$.data.point1',
        '$.data.arr[1].this': '$.data.point2'
    }

    oc = OutputCreator(i)
    import json
    print(json.dumps(dict(oc.create_output(path_map)), indent=4))
