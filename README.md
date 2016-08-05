
# retree

given a dataset, generate a hierarchical set of regexes that match subsets.


# example

```python
retree({'a', 'b', 'c'}) = 
```

Each string character may satisfy more than one regex pattern, 

'9' matches [9], [0-9], \d, \S, .

