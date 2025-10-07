#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for objects the encapsulate a genome and methods for querying the genome


Base Class:
    genome
    
Derived Classes
    ecoliGenome
    
    
TODO - a helper function to be a factory for a object of a subparticular type given
a string 

@author: jgalag

"""

from . import sequence
from . import util
import numpy as np
import pandas as pd


from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from BCBio.GFF import GFF3Writer



class genome():
    '''"Abstract" Base class for genome objects that provides a signature of the methods
    that should be provided by any genome object
    
    Desiged to be subclassed to instatiate objects initialized from different sources
    
    '''
    
    
    def __init__(self):
        
        self.__init_genome_seq__()
        
        self.__init_annot__()
        
    def __init_genome_seq__(self):
        '''Initialilze the genome sequence fields'''
        self.name=None
        self.accession=None
        self.seq=None # the sequence in characters
        self.genome=None # the sequence in one-hot encoding
        self.len=None # the len of the of the sequence
        
        
    def __init_annot__(self):
        '''Initialize the annotation on this genome'''
        self.annots=None
        self.genes=None
        self.known_sites=None
        
    
    def __repr__(self):
        
        return self.__str__()

    
    def __str__(self):
        """User-friendly string representation."""
        
        s='%s genome, accession = %s, length = %s'%(self.name,self.accession,self.len)
        
        return s
    
    def getAllAnnots(self):
        '''Get a dataframe of all annotations'''
        return self.annots
    
    def getTFKnownPeaks(self):
        '''Get a dataframe of known TF binding sites'''
        
        return self.known_sites
    
    def getGenes(self):
        ''' Get a dataframe of gene annotations'''
        
        return self.genes
    
    def getSubseq(self, start=None,stop=None,extra_dim_start=True, concat=False, extra_dim_end=False):
        ''''Method for returning a one-hot encoded version of a subsequence of 
        the genome.  In 1 based indexing
        
        If start not given then start will be 1
        If stop not given then stop will be the end of the genome
        
        If extra_dim_start is True (default) will add an extra dimension of size 1
        to start of array so an array of (4,100) become (1,4,100) 
        
        if concat=True, the make the sequence be a concat of fw and reverse
        (after extradim)
        
        
        If extra_dim_end is True (default) will add an extra dimension of size 1
        to end of array so an array of (1,4,100) become (1,4,100,1) 
        
        
        Latter two are useful for passing to boltznet models
        '''
        

        genome = self.genome
        
        if start is None:
            start=1
        
        if stop is None:
            ss=genome[:, start-1:]

        else:
            ss=genome[:, start-1:stop]
        
        if extra_dim_start:
            ss = ss[np.newaxis, ...]
        
        
        if concat:
            ss=sequence.concatenate_revcomp(ss)
        
        if extra_dim_end:
            ss = ss[..., np.newaxis] 
        
        

        return ss 
        
    def getMultSubseqs(self,starts,stops,concat=False, extra_dim_end=False):
        '''Returns a N array of concatenated substrings from the genome
        
        The regions must all be the same length
        
        Returns a on-hot array of one of the following shapes depending on the extradims
        and concat arguments (see getSubseq)
        
        (N,4,len)
        (1,N,4,len)
        (1,N,4,len,1)
        (N,4,2*len)
        (1,N,4,2*len)
        (1,N,4,2*len,1)
        
        '''


        genome = self.genome

        # first check to see if all regions are the same length
        starts=np.array(starts)
        stops=np.array(stops)
        lengths=stops-starts+1
        assert np.all(lengths == lengths[0]), "All regions must be same length"

        # preallocate the necessary array for speed
        if extra_dim_end:
            ss_shape=[len(starts),4,lengths[0],1]
        else:
            ss_shape=[len(starts),4,lengths[0]]
        
        if concat:
            ss_shape[2]=ss_shape[2]*2
        
        ss = np.zeros(ss_shape, dtype=int)
        
        for ii, (st,sp) in enumerate(zip(starts,stops)):
            s=genome[:, st-1: sp]
            s = s[np.newaxis,...]
            
            if concat:
                s=sequence.concatenate_revcomp(s) # this call needs the extra dim up front
            if extra_dim_end:
                s = s[..., np.newaxis]
                
            ss[ii]=s
            
        return ss
    
    def getSubseqAnnotations(self, start=None,stop=None):
        '''Method for returning annotations for genome
        overlapping a region
        
        If start not given then start will be 1
        If stop not given then stop will be the end of the genome
        
        TODO - define the format of the output
        Could be empty if no annotations
        '''
        pass
    
    def getSubseqKnownBinding(self, tf_name,start=None,stop=None):
        '''Method for returning regions corresponding to known binding
        sites for a particular TF for this genome
        
        If start not given then start will be 1
        If stop not given then stop will be the end of the genome
        
        TODO - define the format of the output
        Could be empty if no known regions
        '''
        pass
    
    def exportFasta(self,filename):
        '''Export the genome sequence as a fasta file
        
        The header will be 
        >accession name (start=1 end=<len(genome)>)
        
        '''
    
        # convert one-hot back to sequences
        s=sequence.onehot2str(self.genome)
        
        records = [ SeqRecord(Seq(s), id=self.accession, description='%s (start=1, end=%i)'%(self.name,self.len))]

        with open(filename, "w") as output_handle:
            SeqIO.write(records, output_handle, "fasta")        

        pass
    
    
  
class fileGenome(genome):
    '''Derived genome object for genome whose information is loaded from 
    [ ] a fastafile and gff file 
    [ ] or a genbank file
    
    Right now only supports a single contigous sequence.
    
    TODO: support genomes that come in multiple contigs
    
    '''
    
    def __init__(self, fasta_file=None, gff_file=None, genbank_file=None):
        
        assert (fasta_file is not None and gff_file is not None and genbank_file is None) or (fasta_file is None and gff_file is  None and genbank_file is not None), 'Either provide fasta and gff or genbank but not both'
        
        self.fasta_file=fasta_file
        self.gff_file=gff_file
        self.genbank_file=genbank_file
        
        
        # this calls all the __init* functions
        # which will load genome and annotations in correct order
        super().__init__()
    
    def __init_annot__(self):
        '''Initialize the annotation from fasta file or gbk.  If we have a genbank file, the sequence and annots are both loaded'''
        
        # init base class
        super().__init_annot__()
        
        if self.gff_file is not None:
            self.loadAnnotGFF(self.gff_file)
            
        if self.genbank_file is not None:
            self.loadGenbank(self.genbank_file)
         

    def __init_genome_seq__(self):
        '''Initialilze the genome sequence from fasta'''
        
        # init base class
        super().__init_genome_seq__()
        
        if self.fasta_file is not None:
            self.loadFasta(self.fasta_file)
        
        
    def __parse_seqdict__(self,seqdict):
        '''Parse the seqdict returned by either loadFasta or loadGenbank'''
        
        # get the first and only entry and   
        self.accession=list(seqdict.keys())[0]
        self.name=self.accession
        self.seq=seqdict[self.accession]['seq']
        self.genome=sequence.str2onehot(self.seq)
        self.len=len(self.seq)
        
        print('Loaded sequence of length %i for accession %s'%(self.len,self.accession))
    
    def __parse_annotdict__(self,annot_dict):
        '''Parse the annot_dict from loadAnnotGFF or loadGenbank'''
        self.annots=annot_dict.get(self.accession,None)
        
        if self.annots is None:
            print('Did not find any annotations for accession %s'%self.accession)
        else:
            print('Loaded %i annotations for accession %s'%(len(self.annots),self.accession))
            
            # parse out the genes and known sites
            self.genes=self.annots[(self.annots['type']=='genes') | (self.annots['type']=='gene')]
            print('Found %i genes'%len(self.genes))
            
            self.known_sites=self.annots[self.annots['type']=='TF_binding_site']
            self.known_sites['tf']=self.known_sites['name']
            print('Found %i binding sites'%len(self.known_sites))
            
    def loadGenbank(self,gbk_name):
        '''Load sequence AND annotations from genbank file'''
        annot_dict, seqdict = util.load_genbank(gbk_name)
        
        self.__parse_seqdict__(seqdict)
        self.__parse_annotdict__(annot_dict)
        
    
    def loadFasta(self,fa_name):
        '''load genome sequence and accession from fasta file
        For now requires that the file include only one sequence
        Sets the name and accession to seqid
        Ignores any sequence position information and assumes that the genome
        sequence runs from 1 to len
        TODO handle multiseq genomes
        '''
        
        seqdict=util.load_seqs_from_fasta(fa_name)
        if len(seqdict)>1:
            raise Exception('Multiple sequences detected in fasta file.  Only single contig genomes supported at the moment')
            
        self.__parse_seqdict__(seqdict)
        
    
    def loadAnnotGFF(self,gff_file):
        '''load annotations from gff file associated with the currently loaded genome
        seuqence accession
        
        '''
        
        # we are loading features for the loaded sequence
        if self.accession is None:
            print('No sequence loaded so no annotations loaded')
            return
        
        annot_dict=util.load_annot_gff(gff_file)
        self.__parse_annotdict__(annot_dict)
        
        pass
    
    
class ecoliGenome(genome):
    '''Derived genome object for ecoli that calls the lab database for information'''
    
    
    def __init__(self):
        '''Constructor for ecoli genome object'''
        
        # this calls all the __init* functions
        super().__init__()
        
    def __init_genome_seq__(self):
        '''Load the genome sequence from mat file'''
        
        super().__init_genome_seq__()
        
        self.genome_file = sequence.ECOLIGENOMEFILE
        # load the genome
        self.genome = sequence.load_genome_matfile(self.genome_file)
        
        self.name='ecoli'
        self.accession='U0096.3'
        self.len=self.genome.shape[1]
        
    def __init_annot__(self):
        '''Load annotations from database
        Loads genes and known sites seperately into 
        self.genes and self.known_sites
        
        Then builds self.annots with mandatory fields
        # ID source, type, symbol, name, start, stop, strand
        
        '''
        
        super().__init_annot__()
        
        # seperate genes and known sites is a holdover from db
        db=ecoliDB()
        self.known_sites=db.getTFKnownPeaks()
        self.known_sites['type']='TF_binding_site'
        self.known_sites['name']=self.known_sites['tf']
        self.known_sites['symbol']=self.known_sites['name']
        self.known_sites['strand']='.'
        self.known_sites["ID"] = self.known_sites.index
        self.known_sites["source"] = '.'
        
        self.genes=db.getAllGeneLocations()
        self.genes['type']='gene'
        self.genes['name']=self.genes['symbol']
        self.genes["ID"] = self.genes.index
        self.genes["source"] = '.'

        db.close()

        # a GFF compatible annots df is the future with mandatory fields
        # ID source, type, symbol, name, start, stop, strand
        # (and potentially others)
        self.annots = pd.concat([self.genes,self.known_sites], ignore_index=True)
        self.annots = self.annots.drop('tf', axis=1)
        
    
    
        