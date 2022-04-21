# Author: "Lasha Bukhnikashvili"
#
# Description:
#   Calculates 'Average' gene outline in genome.
#   Genes is divided into 6 region: UTR'5_Procession, UTR'5,
#   inner CDSs, inner Introns, UTR'3, UTR'3_Procession and each
#   region is divided into k subregions, where ATCG
#   occurrences are calculated. Based each nucleotide occurrences,
#   graph is built from 6*k point where X axis corresponds to points,
#   and Y axis corresponds  to nucleotide occurences.
#
# Usage:
#   base_occurrences.py <annotation> <subregions> <procession_length>
#
# Params (possible) to run:
#   annotation: NCBI / Ensembl
#   subregions: k - number of subregions within each region
#   procession_length: l - length of processions at the end of gene (before UTR5' or after UTR3')
#
# Example:
#   python base_occurrences.py Ensembl 50 1000
#
# Output:
#   created image in ./results/images folder

import genome_lib_tools as genome
from genome_lib_tools import ANNOTATION
from genome_lib_tools import ANNOTATION_LOAD
from genome_lib_tools import SEQUENCE_LOAD

import plotly.express as px
import pandas as pd
import time
import sys


def add_matrix(a, b, parts):
    for i in range(0, 6):
        for j in range(0, parts):
            for k in range(0, 4):
                a[i][j][k] += b[i][j][k]
    return a


start_time = time.time()

assert len(sys.argv) == 4

annotation = ANNOTATION.NCBI if sys.argv[1] == 'NCBI' else ANNOTATION.ENSEMBL
k = int(sys.argv[2])
procession_length = int(sys.argv[3])

# distributions[region][part][base] = [6][k][4]
total_occurrences = []
for i in range(0, 6):
    occurrences_on_region = []
    for j in range(0, k):
        base_distributions_on_part = [0, 0, 0, 0]
        occurrences_on_region.append(base_distributions_on_part)
    total_occurrences.append(occurrences_on_region)

# Load necessary annotation data, we need all fragments (cds,exons,utrs) to calculate occurrences in each region
genome.preprocess_annotation(annotation, ANNOTATION_LOAD.GENES_AND_TRANSCRIPTS_AND_FRAGMENTS,
                             SEQUENCE_LOAD.LOAD)

# excluding mitochondria DNA
for chr_id in range(1, genome.chromosomes_count()):
    print("calculating occurrences in chromosome: " + str(chr_id))
    genes_cnt = genome.genes_count_on_chr(chr_id)

    for i in range(0, genes_cnt):
        gene = genome.gene_by_ind(chr_id, i)
        gene_occurrences = genome.analyze_gene_occurrences_by_parts(chr_id, gene, k, procession_length)
        add_matrix(total_occurrences, gene_occurrences, k)

region_by_part = []
distribution = []
nucleotide = []
lineind = []

region_id = 0
for region in range(0, 6):
    if region != 0: region_id += k
    for part in range(0, k):

        region_by_part.append(region_id + part)
        region_by_part.append(region_id + part)
        region_by_part.append(region_id + part)
        region_by_part.append(region_id + part)

        nucleotide.append('C')
        nucleotide.append('G')
        nucleotide.append('A')
        nucleotide.append('T')
        total = total_occurrences[region][part][0] + total_occurrences[region][part][1] + \
                total_occurrences[region][part][2] + total_occurrences[region][part][3]

        dist1 = total_occurrences[region][part][0] / total

        dist2 = total_occurrences[region][part][1] / total

        dist3 = -total_occurrences[region][part][2] / total

        dist4 = -total_occurrences[region][part][3] / total

        distribution.append(dist1)
        distribution.append(dist2)
        distribution.append(dist3)
        distribution.append(dist4)

        ind = 0
        if region == 2: ind = 4
        if region == 3: ind = 8
        if region > 3: ind = 12

        lineind.append(ind)
        lineind.append(ind + 1)
        lineind.append(ind + 2)
        lineind.append(ind + 3)

df = pd.DataFrame(dict(
    regional_parts=region_by_part,
    distribution=distribution,
    nucleotide=nucleotide,
    lineind=lineind
))

fig = px.line(df, x="regional_parts", y="distribution", line_group=lineind, color="nucleotide")
fig.write_image(
    "results/images/average gene (" + sys.argv[1] + ", k=" + sys.argv[2] + ", procc=" + sys.argv[3] + ").png",
    scale=4.0)

print("--- script was running for %s seconds. ---" % (time.time() - start_time))