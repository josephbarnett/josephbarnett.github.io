"""
Script to process markdown files, extract metadata, and generate JSON representations.

This script recursively walks through a directory, identifies markdown files,
extracts their metadata (title, abstract, last edit time), and creates JSON files
with the content of the markdown files. It also creates a directory structure map
in a JSON file.

Functions:
- determine_markdown_file(file_name): Determines if a file is a markdown file.
- get_modify_time(file_path): Gets the last modification time of a file.
- split_file_name(file_name): Splits a file name and returns the name without extension.
- get_title_and_abstract(file_path): Extracts title and abstract from a markdown file.
- mywalk(directory, append_pointer, header, copy_target): Recursively walks through a directory
  to process markdown files and create JSON representations.
"""

import os
import json

def determine_markdown_file(file_name):
    """Determines if a file is a markdown file."""
    return os.path.splitext(file_name)[1] == '.md'

def get_modify_time(file_path):
    """Gets the last modification time of a file."""
    return int(os.path.getmtime(file_path) + 0.5)

def split_file_name(file_name):
    """Splits a file name and returns the name without extension."""
    return os.path.splitext(file_name)[0]

def get_title_and_abstract(file_path):
    """
    Extracts title and abstract from a markdown file.
    Assumes that the title is the first line starting with '# ' and abstract is the
    content of the first non-empty line after the title.
    """
    title = None
    abstract = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if title is not None:
                line = line.strip()
                if len(line) == 0:
                    pass
                elif ord(line[0]) in (33, 35, 40, 45, 46, 58, 91):
                    pass
                elif len(line) > 120:
                    abstract = line[:120] + '...'
                else:
                    abstract = line
            if line[:2]=='# ':
                title = line[2:].strip()
            if title is not None and abstract is not None:
                break
    return title if title else "", abstract if abstract else ""

def mywalk(directory, append_pointer, header, copy_target):
    """
    Recursively walks through a directory to process markdown files and create JSON representations.
    """
    for current_path, sub_paths, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(current_path, file)
            if determine_markdown_file(file):
                title, abstract = get_title_and_abstract(file_path)
                last_edit_time = get_modify_time(file_path)
                append_pointer.append({
                    'name': file,
                    'path': f"{header}_{split_file_name(file).replace(' ','_')}.json",
                    'lastedittime': last_edit_time ,
                    'title': title,
                    'abstract': abstract,
                    'size': os.path.getsize(file_path),
                })
                with open(file_path,'r',encoding='utf-8') as fp:
                    content = fp.read()
                output_target = os.path.join(copy_target, f"{header}_{split_file_name(file).replace(' ','_')}.json")
                with open(output_target,'w',encoding='utf-8') as fp:
                    fp.write(json.dumps({'data':content}))
        
        for path in sub_paths:
            path_path = os.path.join(current_path, path)
            new_append_pointer = []
            append_pointer.append({
                'name': path,
                'path': '',
                'lastedittime': get_modify_time(path_path),
                'size': -1,
                'children': new_append_pointer,
            })
            mywalk(path_path, new_append_pointer, f"{header}_{path.replace(' ','_')}", copy_target)
        break

root = os.path.abspath('./blog')
copy_target = os.path.abspath('public')

# Clean existing files except for specified ones
protect_file_list = ('favicon.ico', 'index.html')
for files in os.walk(copy_target):
    files = files[2]; break

for rm_file in files:
    if rm_file not in protect_file_list:
        os.remove(os.path.join(copy_target, rm_file))

# Copy markdown files and create JSON representations
root_struct = []
append_pointer = root_struct
mywalk(root, root_struct, 'desktop', copy_target)
with open(os.path.join(copy_target, 'map.json'),'w',encoding='utf-8') as f:
    f.write(json.dumps(root_struct))
