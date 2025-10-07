"""
This module provides the core data-level functionalities for TrackIt, a basic version control system inspired by Git. It includes functions to initialize a repository, hash and store objects, retrieve objects, manage references, and handle the HEAD pointer.
Functions:
- init(): Generates the required file directory structure for TrackIt.
- hash_object(content, obj_type="blob"): Hashes the object content and stores it in the .trackit/objects directory. Returns the object ID.
- get_object(o_id, expected='blob'): Retrieves the object content using the object ID. Returns the content in binary format.
- set_head(ref=None, o_id=None): Sets the HEAD to a specific reference or commit ID.
- get_head_branch(): Gets the branch or commit ID to which the HEAD is pointing.
- set_ref(ref, o_id): Sets or updates a reference to a specific commit ID.
- get_ref(ref): Gets the commit ID of a reference.
- iter_refs(): Iterates over all references (branches and tags) in the current TrackIt repository. Yields ref and object ID.
- check_symbolic(): Checks if the current HEAD is detached.
Constants:
- GIT_DIR: The directory name for TrackIt repository metadata.
"""


import os
import hashlib
import zlib


GIT_DIR = ".trackit"

def init():
    '''
    Generates the required file directory structure for TrackIt.
    '''
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\objects", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs\\heads", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs\\tags", exist_ok=True)
    set_head(ref = 'refs\\heads\\main')
    

def hash_object(content, obj_type="blob"):
    '''
    Hash the object content and store it in the .trackit/objects.\n
    Returns Object ID.
    '''

    # '\0' is used to divide the header with content. Again we then encode the header to binary
    header = f"{obj_type} {len(content)}\0".encode()

    # content is already in binary format
    headed_content = header + content
    o_id = hashlib.sha1(headed_content).hexdigest()     #hashes using sha1 to get the object id

    # we divide the files with respect to their oid with first 2 characters as directory and the rest as file name
    obj_dir_path = os.path.join(GIT_DIR, 'objects', o_id[:2])
    os.makedirs(obj_dir_path, exist_ok = True)

    # compress the file to save storage
    with open(os.path.join(obj_dir_path, o_id[2:]), 'wb') as f:
        f.write(zlib.compress(headed_content))
    
    return o_id

def get_object(o_id, expected = 'blob'):
    '''
    Retrieves the object content with reference to the object id.\n
    Returns Binary Codec.
    '''
    try:
        # we first get the file, then we decompress it and then get the header and content using '\0' as reference.
        # now we decode the header to original format

        obj_path = os.path.join(GIT_DIR, 'objects', o_id[:2], o_id[2:])
        
        with open(obj_path, 'rb') as f:
            r = f.read()
        
        header, content = zlib.decompress(r).split(b'\0', 1)
        content_type = header.decode().split(" ")[0]
        content_size = header.decode().split(" ")[1]

        if expected:
            if expected != content_type: return f'Expected {expected}, got {content_type}'
        # print(content)
        return content
    
    except FileNotFoundError:
        print(f"Object {o_id} not found.")
        return None
    
def set_head(ref = None, o_id = None):
    '''
    Set the head to a commit.
    '''
    with open(os.path.join(GIT_DIR, 'HEAD'), 'w') as f:
        if ref:
            f.write(f"ref: {ref}")
        else:
            f.write(f"commit: {o_id}")

def get_head_branch():
    '''
    Gets the branch or commit ID to which the head is pointing to.\n
    Use check_symbolic to know if head is detached or not.
    '''
    with open(os.path.join(GIT_DIR, 'HEAD'), 'r') as f:
        return f.read().split(" ")[1]

def set_ref(ref, o_id):
    '''
    Set / Update the reference with to a commit.
    '''
    with open(os.path.join(GIT_DIR, ref), 'w') as f:
        f.write(o_id)

def get_ref(ref):
    '''
    Gets the commit ID of the reference.
    '''
    path = os.path.join(GIT_DIR, ref)

    if ref == 'HEAD':
        with open(path, 'r') as f:
            r = f.read().split(" ")
            if r[0] == 'commit:':
                return r[1]
            path = os.path.join(GIT_DIR, r[1])
    
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def iter_refs():
    '''
    Gets all the references (Branches and Tags) present in the current TrackIt repository.\n
    Returns ref, object id
    '''
    refs = ['HEAD', 'MERGE_HEAD']

    for root, dirs, files in os.walk(os.path.join(GIT_DIR, 'refs')):
        root = os.path.relpath(root, GIT_DIR)                   # this is done in order to remove GIT_DIR part from the path
        refs.extend([os.path.join(root, i) for i in files])
    
    for ref in refs:
        yield ref, get_ref(ref)

def check_symbolic():
    '''
    Check if the current head is detached or not.\n
    '''
    with open(os.path.join(GIT_DIR, 'HEAD'), 'r') as f:
        r = f.read()
        if r.split(" ")[0] == 'commit:':
            return False
        return True