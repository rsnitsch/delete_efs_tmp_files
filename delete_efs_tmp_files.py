#!/usr/bin/env python3.3
"""
This script recursively scans a directory for EFS*.TMP files. It is capable
of granting full permissions to these files in order to delete them.

Requires icacls (Windows Server 2003 Service Pack 2 or Windows Vista and
above).

Author:  Robert Nitsch
License: General Public License (Version 3)
"""
import argparse
import distutils
import distutils.spawn
import os
import re
import subprocess
import sys

from os.path import join, getsize

def detect_efs_tmp_files(directory, quiet):
    """
    Recursively scan the directory and return a list of files matching the
    EFS*.TMP pattern.
    
    @param quiet:
        Control whether the directories are printed to stdout as a
        progress indicator.
    """
    efs_files = []
    regexp = re.compile("EFS[0-9]+\.TMP")
    for root, dirs, files in os.walk(directory):
        try:
            if not args.quiet:
                print("Current folder: " + root)
            for f in files:
                if regexp.match(f):
                    efs_files.append(join(root, f))
        except Exception as e:
            print("ERROR: " + str(e))
    return efs_files

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('--only-grant', '--no-delete', action='store_true',
        help='Do not delete files. Only grant full permissions.')
    parser.add_argument('-q', action='store_true', dest='quiet',
        help='Do not print every directory that is scanned (faster)')
    parser.add_argument('--username', default=os.environ.get("USERNAME"),
        help="Grant permission to specific user (default: current user)")
    args = parser.parse_args()

    if not os.path.isdir(argv[1]):
        print("Not a directory: '%s'" % argv[1], file=sys.stderr)
        return 1

    print("Searching for EFS tmp files...")
    files = detect_efs_tmp_files(argv[1], args)

    if files:
        print("The following EFS tmp files have been detected:")
        for f in files:
            try:
                print(f)
            except Exception as e:
                print("ERROR: " + str(e))

        action = "change permissions, do not delete" if args.only_grant else "change permissions and delete"
        if "y" == input("Process these files (%s) or abort? [y/n]: " % action):
            icacls = distutils.spawn.find_executable("icacls.exe")

            if not icacls:
                print("Icacls.exe is not available on your system.")

            for f in files:
                subprocess.call([icacls, f, "/grant", "%s:F" % args.username], shell=True)
                if not args.only_grant:
                    try:
                        os.remove(f)
                    except Exception as e:
                        print("ERROR: " + str(e))
    else:
        print("No EFS tmp files have been found.")

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except Exception:
        print("Unknown error occurred... sorry...")
        raise
