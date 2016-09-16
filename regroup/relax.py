
from functools import reduce


def dict_merge(a, b, path=None):
    return _dict_merge(a, b, [])


def _dict_merge(a, b, path=None):
    for key, vb in b.items():
        va = a.get(key)
        if va:
            if isinstance(va, dict) and isinstance(vb, dict):
                _dict_merge(va, vb, path + [str(key)])
            elif va == vb:
                pass  # same leaf value
            else:
                raise Exception('Conflict at {}'.format('.'.join(path + [str(key)])))
        else:
            a[key] = vb
    return a


def dict_count_recursive(d):
    return sum(1 + dict_count_recursive(v)
               for k, v in d.items()) if d else 0


def dict_diff_recursive(d1, d2):
    if d1 is None:
        return dict_count_recursive(d2)
    if d2 is None:
        return dict_count_recursive(d1)
    return \
        (sum(dict_diff_recursive(v1, d2.get(k1)) for k1, v1 in d1.items()) +
         sum(dict_diff_recursive(v2, d1.get(k2)) for k2, v2 in d2.items()))


def suffixes_diff(d):
    dv = list(d.values())
    merged = reduce(dict_merge, dv, {})
    # print('merged', merged)
    return sum(dict_diff_recursive(x, merged)
               for x in dv)
