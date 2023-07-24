from collections import defaultdict
from difflib import ndiff
import ast
from collections import defaultdict
from difflib import SequenceMatcher

def jaccard_similarity(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def group_strings(strings):
    groups = defaultdict(list)
    for i in range(len(strings)):
        for j in range(i + 1, len(strings)):
            similarity = jaccard_similarity(strings[i], strings[j])
            if similarity >= 0.8:  # Adjust the similarity threshold as needed
                groups[strings[i]].append(strings[j])
                groups[strings[j]].append(strings[i])
    return groups


# Example usage
input_string = """
apple
banana
orange
aple
bannana
oreng
"""

# Convert multiline string into a list of strings
strings = input_string.strip().split('\n')

result = group_strings(strings)
for key, value in result.items():
    print(key, ":", value)