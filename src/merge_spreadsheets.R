# command line tool for merging a newly created exon_skipping spreadsheet with an old one containing manual curations

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
	stop("Usage: Rscript merge_spreadsheets.R <new_spreadsheet> <curated_spreadsheet> <output>")
}

setwd('/humgen/atgu1/fs03/birnbaum/cryptic-splice/data/skip')
require(dplyr)

new = read.table(args[1], header=T, sep='\t')
old = read.table(args[2], header=T, sep='\t', quote="")
out = args[3]
var_fields = c("CHROM", "POS", "REF", "ALT", "donorDist", "acceptorDist", "Feature")

new = left_join(new, old[,c(var_fields, "reviewer", "status", "notes")], by = var_fields)
write.table(new, file=out, quote=F, row.names=F, sep='\t')  
