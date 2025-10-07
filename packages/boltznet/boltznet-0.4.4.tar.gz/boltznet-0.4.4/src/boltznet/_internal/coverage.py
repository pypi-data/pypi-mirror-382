# -*- coding: utf-8 -*-
'''
Functions for relating coverage to binding motifs
'''
import numpy as np
import math
from scipy import signal

# -----------------------
def covFromPbinding(p, bgcov):

    enrich = 10000

    l = bgcov * (1 + p * enrich)

    cov = np.zeros((len(p),))
    for i in range(len(p)):
        cov[i] = np.random.poisson(l[i])

    return cov


# -----------------------
def pbindingFromEnergy(de, minde, maxp):
    # P(binding) given de=delta_energy in units of kbT
    # scaling factor is selected so that when de=minde p=maxp

    lscale = np.log((1 / maxp) - 1) - minde
    scale = np.exp(lscale)
    w = np.exp(de)
    p = 1 / (1 + scale * w)

    return p


# -----------------------
def maxEnergy(m):

    mn = m.max(axis=0)

    mn = sum(mn)

    return mn


# -----------------------
def minEnergy(m):

    mn = m.min(axis=0)

    mn = sum(mn)

    return mn


# -----------------------
def matConvolveMult(m, seqs, **kwargs):

    dea = np.empty((seqs.shape[0], seqs.shape[2]))

    for i in range(seqs.shape[0]):

        de = matConvolve(m, seqs[i, :, :], **kwargs)
        dea[i] = de

    return dea


# -----------------------
def matConvolve(m, seq, **kwargs):
    # m and seq are shape [4,len]

    init = 0
    if "init" in kwargs:
        init = kwargs.get("init")

    slen = seq.shape[1]
    offset = math.floor(m.shape[1] / 2)  # offset relative to zero start


    cc = np.ones((slen,))
    cc[0:offset] = init
    cc[slen - offset : len(cc)] = init

    for j in range(4):

        cc2 = signal.convolve(seq[j, :], np.flip(m[j, :]), mode="valid")

        # this line sums cc2 over all seqs and shifts for buffer padding by offset
        strt = offset
        stp = offset + len(cc2)
        cc[strt:stp] = cc[strt:stp] + cc2

    return cc


