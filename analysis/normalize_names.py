import csv
import inspect
from collections import namedtuple
if not hasattr(inspect, 'getargspec'):
    ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')
    def getargspec(func):
        spec = inspect.getfullargspec(func)
        return ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)
    inspect.getargspec = getargspec
import pymorphy2

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
input_file = os.path.join(project_root, "data/processed/pdf_actor_signatures.csv")
output_file = os.path.join(project_root, "data/processed/actor_roles_nominative.csv")

morph = pymorphy2.MorphAnalyzer()
unique_pairs = set()

def normalize_name(name):
    # Only process Cyrillic tokens, keep initials/latin as is
    tokens = name.split()
    norm_tokens = []
    for token in tokens:
        if any("А" <= c <= "я" or c in "Ёё" for c in token):
            p = morph.parse(token)[0]
            norm_tokens.append(p.normal_form.capitalize())
        else:
            norm_tokens.append(token)
    return " ".join(norm_tokens)

with open(input_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        role = row['role_match'].strip()
        name = row['name_match'].strip()
        if role and name:
            norm_name = normalize_name(name)
            unique_pairs.add((role, norm_name))

with open(output_file, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["role", "name_nominative"])
    for role, name in sorted(unique_pairs):
        writer.writerow([role, name])

print(f"Deduplicated and normalized pairs written to {output_file}")