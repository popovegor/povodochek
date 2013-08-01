#!/usr/bin/python
# -*- coding: utf-8 -*-


import codecs
import sys
import os

if __name__ == "__main__":
	file_path = sys.argv[1]
	abs_path = os.path.abspath(file_path)
	dir_name = os.path.dirname(abs_path)
	with codecs.open(abs_path, "r", "utf-8") as r:
		with codecs.open(os.path.join(dir_name, \
			"formatter.txt"), "w",  "utf-8") as w:
			counter = 0
			for line in r.readlines():
				counter += 1
				w.write('%s: %s' % (counter, line))