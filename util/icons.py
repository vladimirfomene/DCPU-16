import base64
import os
import sys

EXTENSIONS = set([
    '.png',
])

IGNORE = set([
    'icon24.png',
    'icon48.png',
    'icon256.png',
])

def print_data(data):
    size = 70
    offset = 0
    length = len(data)
    while offset < length:
        print '    "%s"' % data[offset:offset+size]
        offset += size

def generate(folder):
    print '# Automatically generated file!'
    print 'from wx.lib.embeddedimage import PyEmbeddedImage'
    print
    for name in os.listdir(folder):
        if name in IGNORE:
            continue
        if name[-4:] not in EXTENSIONS:
            continue
        path = os.path.join(folder, name)
        base = name[:-4]
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read())
            print '%s = PyEmbeddedImage(' % base
            print_data(encoded)
            print ')'
            print

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        generate(args[0])
    else:
        print 'Usage: python icons.py folder_name'
