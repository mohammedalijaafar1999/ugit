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

    tree = ''.join(f'{type} {oid} {name}\n' 
                   for name, type, oid 
                   in sorted(entries)).encode()
    return data.hash_object (tree.encode(), 'tree')
                
def is_ignored(path):
    return '.ugit' in path.split(os.sep)
