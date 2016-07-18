"""
Inputs:
1. list of PMIDs
2. HGMD table containing both a PMID column AND chrom-pos-ref-alt information

Note: PMID -> variant mapping is one-to-many 

Outputs a .tsv or .vcf file of the variants in the range of the input PMIDs. 

Note: only includes SNPs (not indels)
"""

import argparse
from collections import defaultdict
import os
import sys


def read_hgmd_mysql_tsv(tsv, other_info_keys=[]):
	d = defaultdict(list)
	rc = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}
	with open(tsv) as f:
		header = None
		for line in f:
			split = line.strip().split('\t')
			if not header:
				header = split
			else:
				fields = dict(zip(header, split))
				ref, alt = fields['base'].split('-')
				if len(ref) != len(alt): continue # only use SNPs
				if fields['strand'] == '-':
					ref, alt = map(lambda base: rc[base], [ref, alt])
				variant = (fields['chromosome'], fields['coordSTART'], ref, alt)
				other_info = zip(other_info_keys, map(lambda key: fields[key], other_info_keys))
				d[fields['pmid']].append((variant, other_info))
	return d

def main(args):
	pmids = [x.strip() for x in open(args.pmid)] if os.path.isfile(args.pmid) else args.pmid.split(',')
	pmids = list(set(pmids))
	pmid2var = read_hgmd_mysql_tsv(args.tsv, args.info)
	
	out = sys.stdout if args.out == sys.stdout else open(args.out, 'w')
	if args.output_as_vcf:
		out.write('##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')
	else:
		line = ['chrom', 'pos', 'ref', 'alt'] + args.info
		out.write('\t'.join(line) + '\n')

	for pmid in pmids:
		rows = pmid2var[pmid]
		if not args.one_to_one or len(rows) == 1:
			for row in rows:
				var, info = row
				chrom, pos, ref, alt = var
				if args.output_as_vcf:
					info_str = ';'.join('='.join(x) for x in info) if args.info else '.'
					line = '%s\t%s\t.\t%s\t%s\t.\t.\t%s\n' % (chrom, pos, ref, alt, info_str)
				else:
					line = list(var) + map(lambda x:x[1], info)
					line = '\t'.join(line) + '\n'
				out.write(line)
	out.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--pmid', dest='pmid', help='File (or comma-seperated list) of PMIDs', required=True)
	parser.add_argument('-t', '--tsv', dest='tsv', help='Tab-seperated file containing a PMID column AND chrom-pos-ref-alt info', required=True)
	parser.add_argument('--one_to_one', action='store_true', help='Only use PMIDs that map to a single variant')
	parser.add_argument('--output_as_vcf', action='store_true')
	# parser.add_argument('--snp_only', action='store_true')
	parser.add_argument('-o', dest='out', default=sys.stdout, help='Output file')
	parser.add_argument('--info', action='append', default=[], help='TSV columns to include in output (if --output_as_vcf, will be written to INFO field)')
	args = parser.parse_args()

	main(args)

	