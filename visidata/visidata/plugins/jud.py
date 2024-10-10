
SUFFIXES = {'Jr.', 'I', 'II', 'III', 'IV', 'V'}

"""
extract first and last name
"""

def drop_suffix(name):
    names = name.split(" ")
    suffix = None
    if  names[-1] in SUFFIXES:
        suffix = names[-1]
        names = names[:-1]
    return names


def suffix(name):
    names = names.split(" ")
    if names[-1] in SUFFIXES:
        return names[-1]

"""
First and last name, no suffix
"""
def first_last_name(name):
    names = drop_suffix(name)
    return names[0], names[-1]

