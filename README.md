
# regroup

Given an arbitrary set of strings, what's the simplest way to accurately summarize that set?

In everyday programming terms: what is the simplest regex that exactly matches all members of a set but nothing else?

My answer is `regroup.py`, a program that converts its input to a regular expression.

![Travis CI Build Status](https://travis-ci.org/rflynn/regroup.png)

## Install Me

    git clone https://github.com/rflynn/regroup.git
    cd regroup
    make test
    echo -e 'Mississippi\nMissouri' | ./regroup.py


## Examples

```sh
# convert 2 lines of stdin to a regex
$ cat | ./regroup.py
Mississippi
Missouri
^D
Miss(issipp|our)i
```

```py
# use regroup python lib directly
# serialize 0-100 as a regex
>>> import regroup
>>> regroup.DAWG.from_iter(map(str, range(101))).serialize()
'(0|1(00?|[1-9]?)|[2-9][0-9]?)'
```

```sh
# convert a 2MB dictionary to a 1MB regex
$ ./regroup.py < /usr/share/dict/words | wc -c
 1278208
```


## Original Motivation

ref: [How can I detect common substrings in a list of strings](http://stackoverflow.com/questions/1410822/how-can-i-detect-common-substrings-in-a-list-of-strings)

Given a set of strings, for example:

    EFgreen
    EFgrey
    EntireS1
    EntireS2
    J27RedP1
    J27GreenP1
    J27RedP2
    J27GreenP2
    JournalP1Black
    JournalP1Blue
    JournalP1Green
    JournalP1Red
    JournalP2Black
    JournalP2Blue
    JournalP2Green

I want to be able to detect that these are three sets of files:

    EntireS[1,2]
    J27[Red,Green]P[1,2]
    JournalP[1,2][Red,Green,Blue]


## Solution

```sh
$ cat | ./regroup.py --cluster-prefix-len=2
EFgreen
EFgrey
EntireS1
EntireS2
J27RedP1
J27GreenP1
J27RedP2
J27GreenP2
JournalP1Black
JournalP1Blue
JournalP1Green
JournalP1Red
JournalP2Black
JournalP2Blue
JournalP2Green
^D
EFgre(en|y)
EntireS[12]
J27(Green|Red)P[12]
JournalP[12](Bl(ack|ue)|(Green|Red))
```


## Steps

| program        | tokenize            | trie | DAWG | DAWG post-processing       | serialize    |
| -------------- | ------------------- | ---- | ---- | -------------------------- | ------------ |
| `regroup.py`   | character           |      |      | `--relax`, `--cluster-...` | regex        |
| `dawg_dict.py` | word boundary       |      |      |                            | regex        |
| `dawg_tag.py`  | predefined tag      |      |      |                            | pseudo-regex |


## Approaches

### dawg_tag.py

1. Define $color/$number tags and tokenize to (token, tag) tuples similar to how NLP [part-of-speech tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging) does it
2. Group strings based on tag, or if tag is None, on the literal token
3. For each group of >1 entry, combine tagged tokens into sets, then print the list of strings/sets

Result: this gets the exact correct answer; but is fragile due to user-defined color tag and has a more complex tokenization step. The approach is simple, but the exact solution doesn't generalize well because it requires fore-knowledge of the input.

```
$ venv/bin/python dawg_tag.py
strings:
['EFgreen',
 'EFgrey',
 'EntireS1',
 'EntireS2',
 'J27GreenP1',
 'J27GreenP2',
 'J27RedP1',
 'J27RedP2',
 'JournalP1Black',
 'JournalP1Blue',
 'JournalP1Green',
 'JournalP1Red',
 'JournalP2Black',
 'JournalP2Blue',
 'JournalP2Green']
tags:
{'$color': {'Black',
            'Blue',
            'Green',
            'Red'},
 '$number': re.compile('\\d+')}
strings tokenized and tagged:
[[('EF', None), ('green', None)],
 [('EF', None), ('grey', None)],
 [('E', None), ('ntire', None), ('S', None), ('1', '$number')],
 [('E', None), ('ntire', None), ('S', None), ('2', '$number')],
 [('J', None), ('27', '$number'), ('Green', '$color'), ('P', None), ('1', '$number')],
 [('J', None), ('27', '$number'), ('Green', '$color'), ('P', None), ('2', '$number')],
 [('J', None), ('27', '$number'), ('Red', '$color'), ('P', None), ('1', '$number')],
 [('J', None), ('27', '$number'), ('Red', '$color'), ('P', None), ('2', '$number')],
 [('J', None), ('ournal', None), ('P', None), ('1', '$number'), ('Black', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('1', '$number'), ('Blue', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('1', '$number'), ('Green', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('1', '$number'), ('Red', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('2', '$number'), ('Black', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('2', '$number'), ('Blue', '$color')],
 [('J', None), ('ournal', None), ('P', None), ('2', '$number'), ('Green', '$color')]]
group lists of tokens by pattern of (tag or token):
{('E', 'ntire', 'S', '$number'): [['E', 'ntire', 'S', '1'], ['E', 'ntire', 'S', '2']],
 ('EF', 'green'): [['EF', 'green']],
 ('EF', 'grey'): [['EF', 'grey']],
 ('J', '$number', '$color', 'P', '$number'): [['J', '27', 'Green', 'P', '1'],
                                              ['J', '27', 'Green', 'P', '2'],
                                              ['J', '27', 'Red', 'P', '1'],
                                              ['J', '27', 'Red', 'P', '2']],
 ('J', 'ournal', 'P', '$number', '$color'): [['J', 'ournal', 'P', '1', 'Black'],
                                             ['J', 'ournal', 'P', '1', 'Blue'],
                                             ['J', 'ournal', 'P', '1', 'Green'],
                                             ['J', 'ournal', 'P', '1', 'Red'],
                                             ['J', 'ournal', 'P', '2', 'Black'],
                                             ['J', 'ournal', 'P', '2', 'Blue'],
                                             ['J', 'ournal', 'P', '2', 'Green']]}
describe all strings whose pattern is seen 2+ times:
EntireS[1,2]
J27[Green,Red]P[1,2]
JournalP[1,2][Black,Blue,Green,Red]
```

## Use a DAWG, then define linkage agglomerative-hierarchical-clustering-style 
1. Build a [DAWG](https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton) or similar structure using the full set of input
2. Use some metric to split subtrees of the DAWG into clusters
    a. in this case the simplest solution that gets the expected answer is prefix length=2
3. Serialize the resulting clusters as some form of automata. I chose POSIX-ish regexes

Result: this works decently well since all string groups share common prefixes. But 'JournalP1Red' causes JournalP1/JournalP2 to be split into separate groups due to differing suffixes. Though we'll need a different solution for the exact right answer, this is interesting because it generalizes fairly well.

You know... what would be handy would be a "relax" function, which took an exact-match DAWG and figured out the smallest change necessary for the biggest simplification in the resulting pattern. In this case, JournalP1's and JournalP's suffixes differ only by "Red": (Bl(ack|ue)|Green) (Bl(ack|ue)|(Green|Red)). If we could reason about near-matches and their cost/benefit with regard to the effect on the resulting DAWG, we could identify and perform "relaxations" to simplify the DAWG. While exact-matching is great in some cases, for large datasets it is no doubt overkill with regards to what a human is looking for in terms of a summary.


## Use agglomerative clustering to group strings, then a DAWG to describe them
1. Calculate a matrix of [distances between strings](https://en.wikipedia.org/wiki/String_metric)
    a. choose a distance metric. it can be character-oriented like Levenshtein or token-oriented like a regex or by using a dictionary
2. Use that distance matrix to build a [hierarchical cluster](https://en.wikipedia.org/wiki/Hierarchical_clustering) tree of strings
3. Split that tree into clusters based on some metric
    a. k-means works if you know how many groups you want to end up with. simple, but inflexible.
    b. agglomerative is more complex but adaptable
4. Use the resulting clustered subsets to generate a [DAWG or similar structure](https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton), describing the strings they contain in an efficient manner

Result: levenshtein doesn't work well due to differences in length of key tokens. Using an alternative tokenizing scheme works better, but not well enough.


## Interesting External Reading

1. https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton
2. https://en.wikipedia.org/wiki/Hierarchical_clustering
3. https://en.wikipedia.org/wiki/Longest_common_subsequence_problem
4. https://en.wikipedia.org/wiki/Regular_expression
5. https://en.wikipedia.org/wiki/Induction_of_regular_languages
6. http://brandonrose.org/clustering
