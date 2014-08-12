#!/usr/bin/python3
import glob, imp
from os.path import splitext, basename

def load_modules(directory):
    files = glob.glob("{}/*.py".format(directory))
    return [imp.load_source(splitext(basename(module))[0], module) for module in files]

def main():
    modules = load_modules("daemons")

main()
