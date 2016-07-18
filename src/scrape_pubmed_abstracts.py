#!/usr/bin/env python

import sys
import os
import urllib2
from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm
import re


def chunk_list(a, n):
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))


def scrape(pmids, include, exclude, out, pb):
	iterable = tqdm(pmids) if pb else pmids
	for pmid in iterable:
		try:
			tmp = int(pmid)
			url = 'http://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
			print url
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html, "html.parser")

			abstracts = soup.find_all(attrs={"class": "abstr"})
			if len(abstracts) > 1:
				print >> sys.stderr, "%s has multiple abstracts" % pmid
			elif len(abstracts) == 0:
				print >> sys.stderr, "%s has no abstract" % pmid
			else:
				abstract = abstracts[0]
				text_fields = filter(lambda s: s != None, [x.string for x in abstract('p')])
				text =  ' '.join(text_fields).encode('utf-8')
				good = any(re.search(pattern, text, re.IGNORECASE) for pattern in include)
				bad = any(re.search(pattern, text, re.IGNORECASE) for pattern in exclude)
				if good and not bad:
					out.write(pmid + '\n')
		except (ValueError, urllib2.HTTPError) as e:
			print e
			print >> sys.stderr, "%s not a valid PMID" % pmid


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--pmid', dest='pmid', help='File (or comma-seperated list) of PMIDs', required=True)
	parser.add_argument('--include', action='append', help='Keywords to search for in queried abstracts', default=[])
	parser.add_argument('--exclude', action='append', help='Keywords to search for in queried abstracts', default=[])
	parser.add_argument('-o', '--out', default=sys.stdout, help='Output list of PMIDs with abstracts matching one of the input keywords')
	parser.add_argument('--chunk', default='1/1', metavar='CHUNK_NUM/NUM_CHUNKS', help='e.g. 1/100 if first of 100 chunks')
	parser.add_argument('--pb', action='store_true', help='Display progress bar')
	args = parser.parse_args()

	if len(args.chunk.split('/')) != 2:
		parser.error('Invalid --chunk argument')

	pmids = [x.strip() for x in open(args.pmid)] if os.path.isfile(args.pmid) else args.pmid.split(',')
	out = sys.stdout if args.out == sys.stdout else open(args.out, 'w')
	i, n = map(int, args.chunk.split('/'))
	chunk = list(chunk_list(pmids, n))[i - 1]
	scrape(chunk, args.include, args.exclude, out, args.pb)


