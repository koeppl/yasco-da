#!/usr/bin/env python3
""" bla """
# pylint: disable=bad-indentation,line-too-long,invalid-name

import argparse

parser = argparse.ArgumentParser(description='abook replacement')
parser.add_argument('-i', '--input', required=True, type=str)
parser.add_argument('-o', '--output', required=True, type=str)
parser.add_argument('-l', '--length', required=False, default=0, type=int)
args = parser.parse_args()

with open(args.input, 'r', encoding='utf-8') as infile:
	with open(args.output, 'w', encoding='utf-8') as outfile:
		for (lineno, line) in enumerate(infile.readlines()):
			print(line, end='', file=outfile)
			if lineno+1 == args.length:
				break
