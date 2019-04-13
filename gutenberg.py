from collections import Counter
from glob import glob
from ruamel.yaml import YAML
yaml = YAML(typ='safe')

count = Counter()
bigrams = Counter()
initials = Counter()
finals = Counter()
for filename in glob('Gutenberg/txt/*.txt'):
    with open(filename) as f:
        text = f.read().replace('\n', ' ')
        count += Counter(text)
        bigrams += Counter(zip(text[:-1], text[1:]))
        words = [word.strip(',;:-.!?()"') for word in text.split()]
        initials += Counter(word[0] for word in words if len(word) > 0)
        finals += Counter(word[-1] for word in words if len(word) > 0)

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
all_letters = {k: count[k] + count[k.lower()] for k in alphabet}
initial_letters = {k: initials[k] + initials[k.lower()] for k in alphabet}
final_letters = {k: finals[k] + finals[k.lower()] for k in alphabet}
letter_bigrams = {l1 + l2: bigrams[(l1, l2)]
                         + bigrams[(l1, l2.lower())]
                         + bigrams[(l1.lower(), l2)]
                         + bigrams[(l1.lower(), l2.lower())]
                                    for l1 in alphabet for l2 in alphabet}

with open('all_counts.yml', 'w') as f: 
    yaml.dump(all_letters, f)
with open('inital_counts.yml', 'w') as f: 
    yaml.dump(initial_letters, f)
with open('final_counts.yml', 'w') as f: 
    yaml.dump(final_letters, f)
with open('bigram_counts.yml', 'w') as f: 
    yaml.dump(letter_bigrams, f)
