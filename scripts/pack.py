"""Pack self-contained html application

Usage: python3 pack.py src target
"""


import re
import os
import sys
from collections import Iterable


def get_src_file_contents(path: str, filename: str) -> str:
    """Get contents of source file.

    Args:
        path (str): path to originating file
        filename (str): path from originating file to destination file

    Returns:
        str: contents of source file
    """
    full_filename = os.path.realpath(os.path.join(path, filename))
    with open(full_filename, 'rt', encoding="utf-8") as f:
        return f.read()


def assure_dir(filename: str, create: bool = False) -> str:
    """get directory of file.

    Args:
        filename (str): path to file
        create (bool, optional): create directory if it doesn't exist. Defaults to False.

    Returns:
        str: directory containing file
    """
    dirname = os.path.dirname(filename)
    if create:
        os.makedirs(dirname, exist_ok=True)
    return dirname


def process_html(filename: str) -> Iterable[str]:
    """process html line by line, filling in references to js and css

    Args:
        filename (str): path to html file

    Returns:
        str: contents of ammended file
    """
    src_dir = assure_dir(filename, create=False)

    src_pattern = re.compile("src=[\"']([\w/._-]+)[\"']")
    # kw_pattern = re.compile("([a-zA-Z]+)=([\w/._-]+|\"([\w\s'/._-]+)\"|'([\w\s\"/._-]+)')")
    with open(filename, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.lstrip().startswith('<script') and ('src=' in line):
                filename = src_pattern.findall(line)[0]
                yield '<!-- START: Contents of file: ' + filename + '-->\n'
                yield '<script>\n'
                yield get_src_file_contents(src_dir, filename)
                yield '</script>\n'
                yield '<!-- END: Contents of file: ' + filename + '-->\n'
            elif line.lstrip().startswith('<link'):
                if ('stylesheet' in line) and ("text/css" in line):
                    filename = src_pattern.findall(line)[0]
                    yield '<!-- START: Contents of file: ' + filename + '-->\n'
                    yield '<style>\n'
                    yield get_src_file_contents(src_dir, filename)
                    yield '</style>\n'
                    yield '<!-- END: Contents of file: ' + filename + '-->\n'
            else:
                yield line


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 pack.py src target")
        sys.exit()

    # Check arguments
    cm, src_file, dest_file = sys.argv
    assert src_file.endswith(('.html', '.htm'))
    dest_dir = assure_dir(dest_file, create=True)

    # Process file and write to new file
    with open(dest_file, 'wt', encoding='utf-8') as outf:
        for line in process_html(src_file):
            outf.write(line)

    print("Written packed file to: " + dest_file)
