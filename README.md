
# regroup

Given an arbitrary set of strings, what's the simplest way to accurately summarize that set?

In everyday programming terms: what is the simplest regex that exactly matches all members of a set but nothing else?


# Examples

## Problem

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

1. Build a [DAWG](https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton) or similar structure using the full set of input
2. Use some metric to split subtrees of the DAWG into clusters
    a. in this case the simplest solution that gets the expected answer is prefix length=2
3. Serialize the resulting clusters as some form of automata. I chose POSIX-ish regexes


1. Calculate a matrix of [distances between strings](https://en.wikipedia.org/wiki/String_metric)
    a. choose a distance metric. it can be character-oriented like Levenshtein or token-oriented like a regex or by using a dictionary
2. Use that distance matrix to build a [hierarchical cluster](https://en.wikipedia.org/wiki/Hierarchical_clustering) tree of strings
3. Split that tree into clusters based on some metric
    a. k-means works if you know how many groups you want to end up with. simple, but inflexible.
    b. agglomerative is more complex but adaptable
4. Use the resulting clustered subsets to generate a [DAWG or similar structure](https://en.wikipedia.org/wiki/Deterministic_acyclic_finite_state_automaton), describing the strings they contain in an efficient manner

