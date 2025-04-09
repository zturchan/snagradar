import os
import glob

def remove_extension(path):
    return os.path.splitext(os.path.basename(path))[0]

def cleanup(path):
    for f in glob.glob("*" + remove_extension(path) + "*"):
        os.remove(f)