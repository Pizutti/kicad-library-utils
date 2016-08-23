#!/usr/bin/env python

from __future__ import print_function

import argparse
from kicad_mod import *
import sys, os
#point to the correct location for the print_color script
sys.path.append(os.path.join(sys.path[0],'..','schlib'))

from print_color import *
from rules import *

#enable windows wildcards
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('kicad_mod_files', nargs='+')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all modules and extra information about the violation', action='store_true')
args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

return_val = 0

# get all rules
all_rules = []
for f in dir():
    if f.startswith('rule'):
        all_rules.append(globals()[f].Rule)

files = []

for f in args.kicad_mod_files:
    files += glob(f)
        
for filename in files:
    try:
        module = KicadMod(filename)
    except:
        printer.red('could not parse module: %s' % filename)
        return_val = 1
        continue
    printer.green('checking module: %s' % module.name)

    n_violations = 0
    for rule in all_rules:
        rule = rule(module)
        if rule.check():
            n_violations += 1
            return_val = 1
            printer.yellow('Violating ' +  rule.name, indentation=2)
            if args.verbose:
                printer.light_blue(rule.description, indentation=4, max_width=100)

                # example of customized printing feedback by checking the rule name
                # and a specific variable of the rule
                if rule.name == 'Rule 6.6' and len(rule.f_courtyard_all) == 0:
                    printer.red('No courtyard line found in the module', indentation=4)
        if args.fix:
            rule.fix()

    if n_violations == 0:
        printer.light_green('No violations found', indentation=2)
    elif args.fix:
        module.save()

if args.fix:
    printer.light_red('Please, resave the files using KiCad to keep indentation standard.')

quit(return_val)
