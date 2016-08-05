
import re


# ref: http://www.regular-expressions.info/posixbrackets.html

# regex patterns in order of specificity
_Patterns = [
    ('[ \x0c\r\n\t\x0b]',),  # ascii \s
    ('[0-9]',),  # ascii \d
    ('[A-Z]',),
    ('[a-z]',),
    ('[\x00-\x08\x0b-\x0c\x0e-\x1f]',),  # low ascii, except for the commonly used tab, carriage return and newline
    ('[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]',),  # non-printable -- low ascii + 127
    ('[\x00-\x1f]',),  # low ascii
    ('[a-zA-Z]',),
    ('[a-zA-Z0-9]',),
    ('[a-zA-Z0-9_-]',),  # ascii \w
    ('[^a-zA-Z0-9_-]',),  # ascii \w
    ('[^0-9]',),  # ascii \D
    ('[^ \x0c\r\n\t\x0b]',),  # ascii \S
    ('.',),
    # ('[^\w\s]',),  # ascii [[:punct:]]
    # ('\s',),
    # ('\S',),
    # ('\d',),
    # ('\D',),
    # ('\w',),
    # ('\W',),
]


def specificity(s):
    return (s, [bool(re.match(p, s, re.UNICODE)) for p, in _Patterns])


{'ABC-123',
 'ABC-345'}

[
    '^(ABC-123|ABC-345)$',
    '^ABC-(123|345)$',
    '^ABC-(1|3)(2|4)(3|5)$',
    '^ABC-[13][24][35]$',
    '^ABC-\d\d\d$',
    '^ABC-\d{3}$',
]


if __name__ == '__main__':

    from pprint import pprint
    import sys
    # import unicodedata

    allstrs = [chr(n) for n in range(sys.maxunicode + 1)]
    sp = [(p, len([s for s in allstrs if re.match(p, s, re.U)])) for p, in _Patterns]
    sp = sorted(sp, key=lambda x: (x[1], x[0]))
    pprint(sp, width=200)
