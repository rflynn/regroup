# vim: set ts=4 et:

from collections import defaultdict
import re


def chars(string):
    for c in string:
        yield c


def tokenize_regex_case_sensitive(string):
    for token in re.findall('[a-z]+|[A-Z]+|\d+|\s+|.', string):
        yield token


class Tokenizer:

    def __init__(self):
        pass

    def tokenize(self, string):
        return chars(string)


class DictionaryTokenizer(Tokenizer):

    def __init__(self, wordset=None):
        wordset = set(wordset) if wordset else set()
        self.wordset = wordset
        self.wordsetlen = defaultdict(set)
        for w in self.wordset:
            self.wordsetlen[len(w)].add(w)

    def tokenize(self, string):
        matchstring = string
        while matchstring:
            nexttoken = self.nexttoken(matchstring)
            yield string[:len(nexttoken)]
            matchstring = matchstring[len(nexttoken):]
            string = string[len(nexttoken):]

    def nexttoken(self, substr):
        longest = ''
        for length, words in sorted(self.wordsetlen.items()):
            for word in words:
                if substr.startswith(word):
                    longest = word
                    break
        if not longest:
            return self.fallback(substr)
        return longest

    def fallback(self, string):
        m = re.search('^([a-z]+|[A-Z]+|\d+|\s+|.)', string)
        if m:
            return m.groups()[0]
        return string[0]


class Tagged:

    def __init__(self, string, tag):
        self.string = string
        self.tag = tag

    def __str__(self):
        return self.string


class TaggingTokenizer:

    def __init__(self, tags):
        self.tags = tags

    def tokenize(self, string):
        matchstring = string
        while matchstring:
            nexttoken, nexttag = self.nexttoken(matchstring)
            yield (nexttoken, nexttag)
            matchstring = matchstring[len(nexttoken):]
            string = string[len(nexttoken):]

    def nexttoken(self, substr):
        longest = ('', '')
        for tagname, tagdef in self.tags.items():
            match = self.tagmatch(substr, tagdef)
            if match and len(match) > len(longest[0]):
                longest = (match, tagname)
        if not longest[0]:
            longest = (self.fallback(substr), None)
        return longest

    def tagmatch(self, substr, tagdef):
        if isinstance(tagdef, (list, set)):
            for t in tagdef:
                if substr.startswith(t):
                    return substr[:len(t)]
        else:
            m = tagdef.search(substr)
            if m:
                sp = m.span()
                if sp[0] == 0:
                    return substr[:sp[1]]

    def fallback(self, string):
        m = re.search('^([a-z]+|[A-Z]+|\d+|\s+|.)', string)
        if m:
            return m.groups()[0]
        return string[0]
