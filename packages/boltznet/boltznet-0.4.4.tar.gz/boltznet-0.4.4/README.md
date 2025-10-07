# boltznet

BoltzNet is a biophysically designed neural network that learns a quantitative model of TF-DNA binding energy from ChIP-Seq data. BoltzNet mirrors a quantitative biophysical model and provides directly interpretable predictions genome-wide at nucleotide resolution. We have performed ChIP-Seq mapping of genome-wide DNA binding for 139 E. coli TFs. From these data we have generated BoltzNet models for 124 TFs.

The Boltznet models are described in our [publication](https://rdcu.be/ek2Sq) and through the companion [website](https://boltznet.bu.edu):

https://boltznet.bu.edu

This python package provides a high-level object interface for downloading pretrained models, running predictions on DNA sequences, and visualizing results.

## Installation

Create a conda environment and activate it.  Then run:

```
pip install boltznet
boltznet-init
```

This installs the package and downloads available models to the package cache dir.  To perform selftests, run 

```
boltznet-selftest
```

This builds a model on all TFs, performs predictions on a set of _E. coli_ promoter sequences, and then generates and saves a plot as selftest_pdhR,pdhR-aceE-aceF-lpd.png.  Basically runs a version of the example code in Usage below.


## USAGE

```
from boltznet import boltznet_tf

####################################
# create a tfmodel on all TFs that have been loaded into the package cache
####################################
tfmodel=boltznet_tf.create()


####################################################
# load sequences from fasta file and run predictions
# Returns a np.array of predicions at each position on both
# strands of each sequence for all TFs
#
# The numpy array has shape:
# (nseqs,2,seqlen,numtfs)
# - nseqs: number of sequences
# - 2: forward and reverse strands
# - seqlen: length of each sequence
# - numtf: number of models
####################################################
fa_name='test.fa'
y=tfmodel(fastafile=fa_name)


####################################################
# Get scores for each each sequence and tf  
# Scores are the sum of the exponentiated binding energies at every 
# position across both strands
####################################################
sc=tfmodel.getScores()


####################################################
# Get max binding site scores for each each sequence and tf
# The max of the sum of the exponentiated binding energies 
#in windows of length(weigth_matrix)
####################################################
mb=tfmodel.getMaxBindingSiteScores()


####################################################
# load annotations for the sequences for plotting
####################################################
gff_name='ecoli.gff'
tfmodel.loadGff(gff_name)


####################################################
# Plot the predictions for sequences by sequence index or sequence name patterns
# Below will plot sequence number 76 as well as any sequences that 
# contain pdhR in the name.  But will not plot the same sequence twice
# If savefilename is None, generate plots in a window
# If savefilename is given, generate plots named savefilename_<seqid>.png
# 
# Sequences are ranked and percentiled for each model in one of two ways
# according to ranking_mode
#  "full_sequence": TFs ranked by summing exp(wm+bias) over every position on both strands
#  "max_binding_site": sum exp(wm+bias) in ln(wm) windows over seq and take max 
#
# The plot will include tracks for each model in model_names.  If model_names
# is none, then plot the top maxN TFs by normalized score
# The plots include the normalized score and rank for each TF in the titles
####################################################
tfmodel.plotPrediction(inds=[76],seqnames=['aceE'],model_names=None,seqlogo=True,baseseq=False, maxN=5, ranking_mode='max_binding_site', savefilename='test')

```

## Test data

The package comes bundled with two datafiles that can be used for testing:
- promoters.fa: a fasta file with a small subset of promoters (see https://boltznet.bu.edu/ecoli/promoters)
- ecoli.gff: a gff file with annotations of genes and known binding sites

You can retrieve and use these data files with code like the following:

```
from importlib import resources
import boltznet.testdata as testdata_pkg

fa_name=resources.files(testdata_pkg).joinpath('promoters.fa')

gff_name=resources.files(testdata_pkg).joinpath('ecoli.gff')
```

## Citation

The code for BoltzNet is freely available for academic use. BoltzNet can be used by molecular biologists seeking to quantitatively predict TF binding, by synthetic biologists seeking to predictively engineer new regulatory interactions, and by computational biologists seeking to develop biophysically motivated bioinformatic tools.

- Lally, Patrick, Gómez-Romero, Laura, Tierrafría, Víctor H., Aquino, Patricia, Rioualen, Claire, Zhang, Xiaoman, Kim, Sunyoung, Baniulyte, Gabriele, Plitnick, Jonathan, Smith, Carol, Babu, Mohan, Collado-Vides, Julio, Wade, Joseph, Galagan, James E. (2025) [Predictive Biophysical Neural Network Modeling of a Compendium of in vivo Transcription Factor DNA Binding Profiles for _Escherichia coli_](https://rdcu.be/ek2Sq). Nature Communications
