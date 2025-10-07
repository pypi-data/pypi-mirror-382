#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Demo script for using boltznet package
'''

from boltznet import boltznet_tf
from importlib import resources
import boltznet.testdata as testdata_pkg


def main():
    
    print('Running self test.  If loading tensorflow for first time, this can take a little bit...')
    
    # create a tfmodel on all TFs that have been loaded into the package cache
    tfmodel=boltznet_tf.create()
    
    # load sequences from fasta file and run predictions
    # fa_name='boltznet/src/boltznet/tests/data/promoters.fa'
    fa_name=resources.files(testdata_pkg).joinpath('promoters.fa')
    y=tfmodel(fastafile=fa_name)
    
    # load annotations for the sequences
    # gff_name='boltznet/src/boltznet/tests/data/ecoli.gff'
    gff_name=resources.files(testdata_pkg).joinpath('ecoli.gff')
    tfmodel.loadGff(gff_name)
    
    # Plot the predictions for a uniques sequence by sequence index or sequence name patterns
    # Below will plot sequence number 76 as well as any sequences that contain chaC or pdhR in the 
    # name.  But will not plot the same sequence twice
    tfmodel.plotPrediction(inds=None,seqnames=['pdhR'],model_names=['pdhR','tyrR','envY','ydfH'],seqlogo=True,baseseq=False, maxN=3, savefilename='selftest')
