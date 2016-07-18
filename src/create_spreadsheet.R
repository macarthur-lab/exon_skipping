setwd('/humgen/atgu1/fs03/birnbaum/cryptic-splice/data/skip')
require(dplyr)
require(tidyr)
require(Biostrings)

# read in exon skipping data set scraped from PubMed
read.table('exon_skipping.tsv', header=T) %>% select(-spliceContext) -> skip

# read/process raw HGMD data that was used as starting point for scraping
read.table('hgmd_splice_variants.tsv', header=T, sep='\t') %>% 
  separate(base, c("ref", "alt"), sep="-") -> hgmd
hgmd$ref[hgmd$strand == '-'] = as.character(reverseComplement(DNAStringSet(hgmd$ref[hgmd$strand == '-'])))
hgmd$alt[hgmd$strand == '-'] = as.character(reverseComplement(DNAStringSet(hgmd$alt[hgmd$strand == '-'])))

# join two data sets together to get PMIDs for the usable exon skippint data
left_join(skip, hgmd, by = c("CHROM" = "chromosome", "POS" = "coordSTART", "REF" = "ref", "ALT" = "alt")) %>%
  select(-EXON, -INTRON, -coordEND, -strand) %>%
  mutate(url=sprintf("http://www.ncbi.nlm.nih.gov/pubmed/%s", pmid)) -> spreadsheet

write.table(spreadsheet, 'exon_skipping_spreadsheet.tsv', sep='\t', row.names=F, quote=F)
  
