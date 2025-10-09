#!/usr/bin/env python3

"""
Copyright 2019 ARC Centre of Excellence for Climate Extremes

author: Aidan Heerdegen <aidan.heerdegen@anu.edu.au>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
from glob import glob
import os
import sys

from addmeta import find_and_add_meta, combine_meta, list_from_file, skip_comments

def parse_args(args):
    """
    Parse arguments given as list (args)
    """

    parser = argparse.ArgumentParser(description="Add meta data to one or more netCDF files")

    parser.add_argument("-c","--cmdlineargs", help="File containing a list of command-line arguments", action='store')
    parser.add_argument("-m","--metafiles", help="One or more meta-data files in YAML format", action='append')
    parser.add_argument("-l","--metalist", help="File containing a list of meta-data files", action='append')
    parser.add_argument("-f","--fnregex", help="Extract metadata from filename using regex", action='append')
    parser.add_argument("-v","--verbose", help="Verbose output", action='store_true')
    parser.add_argument("files", help="netCDF files", nargs='*')

    return (parser, parser.parse_args(args))

def main(args):
    """
    Main routine. Takes return value from parse.parse_args as input
    """
    metafiles = []
    verbose = args.verbose

    if (args.metalist is not None):
        for line in args.metalist:
            metafiles.extend(list_from_file(listfile))

    if (args.metafiles is not None):
        metafiles.extend(args.metafiles)

    if verbose: print("metafiles: "," ".join([str(f) for f in metafiles]))

    find_and_add_meta(args.files, combine_meta(metafiles), args.fnregex, verbose)

def safe_join_lists(list1, list2):
    """
    Joins two lists, handling cases where one or both might be None.
    Returns:
        A new list containing the combined elements, or None if both are None.
    """
    if list1 is None and list2 is None:
        return None
    elif list1 is None:
        return list2
    elif list2 is None:
        return list1
    else:
        return list1 + list2

def main_parse_args(args):
    """
    Call main with list of arguments. Callable from tests
    """

    parser, parsed_args = parse_args(args)

    if (parsed_args.cmdlineargs is not None):
        # If a cmdlineargs file has been specified, read every line 
        # and parse
        with open(parsed_args.cmdlineargs, 'r') as file:
            newargs = [line for line in skip_comments(file)]
        _, new_parsed_args = parse_args(newargs)

        # Expand (glob) patterns in positional arguments (files)
        filelist = []
        for file in new_parsed_args.files:
            filelist.extend(glob(file))
        if len(filelist) > 0:
            new_parsed_args.files = filelist

        # Combine new and existing parsed arguments, ommitting cmdlineargs 
        # option.  Adding additional command line arguments may require 
        # adding logic here also
        parsed_args.files = safe_join_lists(parsed_args.files, new_parsed_args.files)
        parsed_args.metafiles = safe_join_lists(parsed_args.metafiles, new_parsed_args.metafiles)
        parsed_args.fnregex = safe_join_lists(parsed_args.fnregex, new_parsed_args.fnregex)
        parsed_args.verbose = parsed_args.verbose or new_parsed_args.verbose
        parsed_args.cmdlineargs = None


    # Have to manually check positional arguments
    if len(parsed_args.files) < 1:
        parser.print_usage()
        sys.exit('Error: no files specified')
    
    # Must return so that check command return value is passed back to calling routine
    # otherwise py.test will fail
    return main(parsed_args)

def main_argv():
    """
    Call main and pass command line arguments. This is required for setup.py entry_points
    """
    main_parse_args(sys.argv[1:])

if __name__ == "__main__":

    main_argv()
