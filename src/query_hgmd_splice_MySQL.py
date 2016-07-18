"""
Query HGMD MySQL tables. Output .tsv file containing results of query.
"""

import MySQLdb
import MySQLdb.cursors
import argparse
import sys


def main(args):
	db = MySQLdb.connect(read_default_group='macarthur', db="hgmd_working", cursorclass=MySQLdb.cursors.DictCursor)
	conn = db.cursor()
	conn.execute(args.query)
	data = conn.fetchall()

	with open(args.tsv, 'w') as out:
		header = False
		for row in data:
			if not header:
				fields = row.keys()
				out.write('\t'.join(fields) + '\n')
				header = True
			line = map(str, [row[f] for f in fields])
			out.write('\t'.join(line) + '\n')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-q', '--query', dest='query', required=True, help='MySQL query on splice table in HGMD database')
	parser.add_argument('-o', '--tsv', dest='tsv', default=sys.stdout, help='Where to output results of query')
	args = parser.parse_args()
	main(args)




	
