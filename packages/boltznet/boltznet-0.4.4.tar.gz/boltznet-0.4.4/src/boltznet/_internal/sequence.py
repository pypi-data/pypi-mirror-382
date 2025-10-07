#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions and variables for working with DNA sequences and motifs

@author: jamesgalagan
"""
import math
import re
import scipy.io
import numpy as np
from matplotlib import colors

from . import coverage
from . import CONFIG



letters = ['A', 'C', 'G', 'T']  # the order of letters in one hot encoding

seqcolors = colors.ListedColormap(['red', 'blue', 'yellow', 'green'])

ECOLIGENOMEFILE = '%s/ecoli_genome.mat' % CONFIG.data_dir


# ----------------------------------------
#%% ONE HOT ENCODING SUPPORT
#-----------------------------------------

# -----------------------
def str2onehot(let):
    ''' creates a one hot rep of str of letters
        order and letters are given in sequence.letters'''

    seq = np.zeros((4, len(let)))

    let = let.upper()

    for i in range(4):
        ind = [i.start() for i in re.finditer(letters[i], let)]
        seq[i, ind] = 1

    return seq

# -----------------------
def onehot2num_multi(seqs):
    ''' creates a one hot rep of list of strings of letters
        order and letters are given in sequence.letters'''
    # seq is a list of seqs in one hot
    # that are ALL THE SAME LENGTH
    # returns an array with one row per seq
    # so shape = (numseqs, seqlen)

    num = np.zeros((len(seqs), seqs[0].shape[1]))

    for i in range(len(seqs)):
        num[i, :] = onehot2num(seqs[i])

    return num


# -----------------------
def onehot2num(seq):
    ''' creates a integer rep of on hot seq
    seq is assumes to be shape (4,slen) on hot
    num is index in sequence.letters'''

    # this cannot be the most efficient way to do this!  But
    num = np.zeros(seq.shape[1])
    for i in range(4):
        ind = [i for i, v in enumerate(seq[i, :]) if v == 1]
        for j in ind:
            num[j] = int(i)

    return num

# -----------------------


def onehot2str_multi(seqs):
    ''' seq is assumes to be shape (nseqs,4,slen) one hot'''

    strs = []
    for i in range(seqs.shape[0]):
        s = seqs[i, :, :]
        strs.append(onehot2str(s))

    return strs
# -----------------------


def onehot2str(seq):
    ''' creates a string rep of on hot seq
    seq is assumes to be shape (4,slen) on hot
    the order of letters is given by sequence.letters'''

    # this cannot be the most efficient way to do this!  But
    let = '.'*seq.shape[1]
    let = list(let)
    for i in range(4):
        ind = [i for i, v in enumerate(seq[i, :]) if v == 1]
        for j in ind:
            let[j] = letters[i]

    let = ''.join(let)

    return let


# ----------------------------------------
#%% SEQUENCE TRANSFORMATIONS
#-----------------------------------------

# -----------------------
def circ_permute_seqs(seqs, numsteps):
    '''perform circ permutation on one hot sequences'''

    seqs2 = np.roll(seqs, numsteps, 2)
    return seqs2



# -----------------------
def concatenate_revcomp(sequences):
    '''Takes sequences and concatenates each with its reverse 
    complement of a set of sequences
    - sequences are one hot
    - input is shape nseq, 4, slen
    - output is shape nseq, 4, 2*slen'''
    out = np.concatenate((sequences, revcomp_multi(sequences)), axis=2)
    return out

# -----------------------
def revcomp(s):
    '''reverse complement a sequence
    s is shape (4,slen)'''

    a = letters.index('A')
    c = letters.index('C')
    g = letters.index('G')
    t = letters.index('T')

    sr = s.copy()
    sr[a, :] = s[t, :]
    sr[t, :] = s[a, :]

    sr[c, :] = s[g, :]
    sr[g, :] = s[c, :]

    sr = np.fliplr(sr)

    return sr

# ----------------------
def revcomp_multi(s):
    '''returns the reverse complement of multiple onehot sequences
    
    s is shape(n,4,slen)'''

    a = letters.index('A')
    c = letters.index('C')
    g = letters.index('G')
    t = letters.index('T')

    sr = s.copy()
    sr[:, a, :] = s[:, t, :]
    sr[:, t, :] = s[:, a, :]

    sr[:, c, :] = s[:, g, :]
    sr[:, g, :] = s[:, c, :]

    sr = np.flip(sr, axis=2)

    return sr

# -----------------------
def flatten(s):

    if (s.ndim == 3):
        s = np.reshape(s, (s.shape[0], s.shape[1]*s.shape[2]))
    elif (s.ndim == 2):
        s = np.reshape(s, (s.shape[0]*s.shape[1], 1))

    return s


# -----------------------
def deflatten(s):

    if (s.ndim == 3):
        s = np.reshape(s, (s.shape[0], 4, int(s.shape[1]/4)))
    elif (s.ndim == 2):
        s = np.reshape(s, (4, int(s.shape[0]/4)))

    return s


# -----------------------
def shuffle_sequences_multi(sequences):
    '''Shuffle multiple sequences
    sequences is shape (nseq,4,len_seq)'''

    for j in range(sequences.shape[0]):
        seq = sequences[j, :, :]
        cols = [i for i in range(seq.shape[1])]

        np.random.shuffle(cols)
        seq[:] = seq[:, cols]
        sequences[j, :, :] = seq
    return sequences
#----------------------------------------
#%% MOTIF SUPPORT FUNCTIONS
#-----------------------------------------
# -----------------------
def calc_max_motif_score(m):
    '''Given a motif, calculate the maximum score (e.g. the sum of max elements)
    '''
    sc = np.sum(np.max(m, 0))
    

    return sc


# -----------------------
def make_pfm_from_seqs(seqs):
    ''' seqs is shape (nseqs,4,seqlen) - one hot encoding
    the returned PFM will the freq of each base at each position of the seqlen
    returns PFM of shape (4,seqlen)'''

    pfm = np.sum(seqs[:, :, :], axis=0)/seqs.shape[2]

    return pfm

# -----------------------


def make_pfm_from_pam(m, seq, inth=0.3, **kwargs):
    ''' scan all sequences with m  and at every position that scores above
    include the sequence in the set that will be used to generate the PFM
    th - if 0 <th <= 1, percent of the highest possible score for the matrix
       - if th>1 then the number of sequences from seq (starting with zero) to include'''

    # first calc the max scpore for this motif m
    if (inth > 0 and inth <= 1):
        mscore = calc_max_motif_score(m)
        th = inth*mscore
    else:
        th = inth

    # Need to scan both forward and revcomp versions of the sequence
    seq = concatenate_revcomp(seq)

    cov = coverage.matConvolveMult(m, seq)

    if 'numseqs' in kwargs:
        seqinds = range(0, kwargs.get('numseqs'))
    else:
        seqinds = range(cov.shape[0])

    offset = math.floor(m.shape[1]/2)

    ssum = np.zeros(m.shape)
    slist = []
    covlist = []
    ns = 0
    # for each seq, find the positions where cov>th
    for i in seqinds:
        ind = [i for i, v in enumerate(cov[i, :]) if v > th]

        # for each position in seq i
        for j in ind:
            s = seq[i, :, j-offset:j-offset+m.shape[1]]
            if (s.shape[1] == m.shape[1]):
                ssum = ssum+s
                ns = ns+1
                slist.append(s)
                covlist.append(cov[i, j])
            # pdb.set_trace()

    if (ns > 0):
        ssum = ssum/ns
    else:
        ssum = np.ones(m.shape)

    # sort sequences by coverage
    if (len(slist) > 0):
        l = zip(covlist, slist)
        l = sorted(l, key=lambda x: -x[0])
        covlist, slist = zip(*l)

    return ssum, ns, slist, covlist


# -----------------------
def seq_from_motif(m):
    """Returns a sequence from a motif by selecting the base at each position i
    with the highest value in m[:,i]"""
    
    s = np.zeros(m.shape)

    for i in range(m.shape[1]):
        ind = np.argmax(m[:, i])
        s[ind, i] = 1

    return s


# ----------------------------------------
#%% GENERAL GENOME SUPPORT
# -----------------------
def get_genome_subseq(start=None, stop=None, genome_file: str = ECOLIGENOMEFILE):
    '''Get a subsequence of the given genome in one hot-encoded format
    
    Start and stop are one-based and the range is inclusive on both ends
    so get_genome_subseq(1, 10) returns a (4,10) matrix starting at the first base
    of the genome
    
    If start is ommited, it defaults to first position
    If stop is ommited, it defaults to the last base of the genome
    
    The default genome file is:
        
    ECOLIGENOMEFILE = '%s/ecoli_genome.mat' % CONFIG.data_dir
    
    '''

    genome_file = ECOLIGENOMEFILE if not genome_file else genome_file
    # load the genome
    genome = load_genome_matfile(genome_file)

    if start is None:
        start=1

    # if stop is None than make it the end of the genome
    if stop is None:
        result = genome[:, start-1:]
    else:
        # get the subseq region
        result = genome[:, range(start-1, stop)]

    return result


# ----------------------------------------
#%% ECOLI GENOME SUPPORT
#-----------------------------------------
# -----------------------
def load_genome_matfile(fname=ECOLIGENOMEFILE):
    '''returns genome sequence as (4,slen) np.array
    default fname points to ecoli genome file'''

    if fname is None:
        print('fname is NONE; defaulting to ECOLIGENOMEFILE...')
        fname = ECOLIGENOMEFILE

    data = scipy.io.loadmat(fname)
    if len(data) == 1:                        # should consist of single table
        seq = data.next(iter(data.values()))  # should return table, regardless of table name
    else:
        seq = data['ec_ONE']  # in default ecoli case, table must be named 'ec_ONE'

    return seq

# -----------------------
def get_ecoli_subseq(start, stop):
    '''Get a subsequenc of the ecoli genome'''

    # load the ecoli genome
    genome = load_genome_matfile(ECOLIGENOMEFILE)  # TODO: CK: Update caller to accommodate other GENOMEFILE

    # get the subseq region
    result = genome[:, range(start-1, stop)]

    return result

# ----------------------------------------
#%% RANDOM SEQUENCE AND MOTIF GENERATION
#-----------------------------------------
# -----------------------
def create_random_palindrome_motif(plen):
    '''create a randome palindromic motif'''

    odd = 0
    if (plen % 2 > 0):
        odd = 1

    hlen = int(np.ceil(plen/2))

    m1 = create_random_motif(hlen)
    if (odd == 1):
        m2 = m1[:, 0:-1]
        m2 = m2[:, ::-1]
    else:
        m2 = m1[:, ::-1]

    m = np.concatenate((m1, m2), 1)

    return m
# -----------------------
def create_random_motif(plen):
    '''Create a random motif'''

    # most bases at most positions have positive delta_e4
    m = np.random.normal(-2, 2, (4, len))
    # now  chance to pick on base at every position to insert a higher weight
    for i in range(plen):
        r = np.random.random()
        if (r < 0.1):
            m[np.random.randint(1, 4, 1), i] = np.random.normal(-6, 2)
        elif (r > 0.6):
            m[np.random.randint(1, 4, 1), i] = np.random.normal(5, 2)
            if (r > 0.8):
                m[np.random.randint(1, 4, 1), i] = np.random.normal(5, 2)

    m = m/2

    return m

# -----------------------
def create_random_sequence(plen):
    '''Create a random sequence'''
    s = np.zeros((4, plen))

    ind = np.random.random((1, plen))

    for j in range(4):
        ind2 = np.where((ind > (j)/4) & (ind <= (j+1)/4))
        s[j, ind2[1]] = 1

    return s

# -----------------------

def create_random_sequences_multi(slen, nseq):
    '''Create multiple random sequences'''

    sa = np.empty((nseq, 4, slen))

    for i in range(nseq):

        s = create_random_sequence(slen)

        sa[i] = s

    return sa
# ----------------------------------------
#%% OTHER UTILITIES
#-----------------------------------------
# ----------------------
def calc_gc(sequences):
    '''calculate GC content of each of a set of sequences
    sequences is shape(n,4,slen)
    returns a list of gc content values'''

    a = letters.index('A')
    t = letters.index('T')
    s = sequences.copy()
    s[:, a, :] = 0
    s[:, t, :] = 0

    gc_content = np.sum(s, axis=(2, 1))
    gc_content = gc_content / sequences.shape[2]

    # returns a list of the fraction gc content that each sequence contains
    return gc_content


