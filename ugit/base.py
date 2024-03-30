import os
from . import data

def write_tree(directory='.'):
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full = os.path.join(directory, entry.name)
            if is_ignored(full):   
                continue

            if entry.is_file(follow_symlinks=False):
                type_ = 'blob'
                with open (full, 'rb') as f:
                    oid = data.hash_object (f.read (), type_)
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree (full)
            entries.append (f'{entry.name}\x00{type_}\x00{oid}')

    # which stands for type, oid, name
    tree = ''.join(f'{entry[0]} {entry[1]} {entry[2]}\n'
               for entry in sorted(entries))
    return data.hash_object (tree.encode(), 'tree')

def _iter_tree_entries (oid):
    if not oid:
        return
    tree = data.get_object (oid, 'tree')
    for entry in tree.decode ().splitlines ():
        type_, oid, name = entry.split (' ', 2)
        yield type_, oid, name


def get_tree(oid, base_path=''):
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = os.path.join(base_path, name)
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update(get_tree(oid, os.path.join(path, '')))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result

def read_tree(tree_oid):
    for path, oid in get_tree(tree_oid, base_path='.').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data.get_object(oid))


def is_ignored(path):
    return '.ugit' in path.split(os.sep)
