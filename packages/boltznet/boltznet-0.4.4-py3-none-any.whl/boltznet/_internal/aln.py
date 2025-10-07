#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for aligning motifs and kernels
@author: laura
"""
import numpy as np
import matplotlib.pyplot as plt
from . import util
import math 
from . import sequence
import pandas as pd
import os
from Bio import motifs
from . import CONFIG
from .sequence import letters
import logomaker

from . import tf_util
# from tf_models import TFModels
# TODO the import above creates a circ import issue when we try to 
# import aln in most other scripts.  NEED TO FIX THIS
from . import model_create


## match score
## this function will obtain the score to measure the difference between two single matrix positions
## normaliza to maximum weight
## sum of squared differences

## score functions
## http://embnet.ccg.unam.mx/rsat/help.compare-matrices.html#sum_of_squared_distances__ssd_

def change_score_base(b1, b2, method='dotprod', bias = -0.8):
    if method == 'mse':
        b1_norm = b1/max(b1)
        b2_norm = b2/max(b2)
        score = sum(np.square(b1_norm-b2_norm))
        
    if method == 'dotprod':
        score = np.dot(b1, b2)
        
    if method == 'ssd':
        score = sum(np.square(b1-b2))
        
    if method == 'sw':
        score = sum(2-np.square(b1-b2))
        
    if method == 'nsw':
        score = sum(2-np.square(b1-b2))
        score=score/(2*4)
        
    if method == 'eucl':
        score = np.sqrt(sum(2-np.square(b1-b2)))
        
    if method == 'nseucl':
        score = np.sqrt(sum(2-np.square(b1-b2)))
        score=score/4
 
    score = score + bias
        
    return(score)

## Initialize first row and first column
def init_mat(m1_len, m2_len):
    
    mat = np.array([[float(0) for _ in range(m1_len)] for _ in range(m2_len)])
    mat_dir = np.array([[float(0) for _ in range(m1_len)] for _ in range(m2_len)])
    
    ncol = mat.shape[1]
    nrow = mat.shape[0]
    
    for i in range(1, ncol):
        mat[0][i] = float(0)
        mat_dir[0][i] = 2
        
    for i in range(1, nrow):
        mat[i][0] = float(0)
        mat_dir[i][0] = 1
        
    return(mat, mat_dir)

## Comute all scores
def get_score_mat(m1, m2, score, **kwargs):
    
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
        
    m1_len = m1.shape[1] #### ncol
    m2_len = m2.shape[1] #### nrow
   
    mat_score = np.array([[float(0) for _ in range(m1_len)] for _ in range(m2_len)])

     
    #### i --> row, j --> col
    for i in range(1, m2_len): 
        for j in range(1, m1_len):
            mat_score[i][j] = change_score_base(m1[:,j], m2[:,i], method=score)
            
    return(mat_score)
            
## Compute best score per cell
def score_per_cell(i, j, mat, mat_dir, gap, m1, m2, score_mat, **kwargs):
    
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
        
    ### up
    up_score = mat[i-1][j] + gap
    
    ### diagonal
    #diag_score = mat[i-1][j-1] + change_score_base(m1[:,j], m2[:,i])
    diag_score = mat[i-1][j-1] + score_mat[i][j]
    
    ### down
    dw_score = mat[i][j-1] + gap
    
    ### best
    if diag_score >= up_score and diag_score >= dw_score:
        #mat[i][j] = diag_score
        #mat_dir[i][j] = 0
        return(diag_score, 0)
    
    if up_score >= diag_score and up_score >= dw_score:
        #mat[i][j] = up_score
        #mat_dir[i][j] = 1
        return(up_score, 1)
    
    if dw_score >= diag_score and dw_score >= up_score:
        #mat[i][j] = dw_score
        #mat_dir[i][j] = 2
        return(dw_score, 2)
    
    
def get_region(x, y):
    final_x = []
    for xi in range(0, len(x)):
        xi_min = min(x[xi])
        xi_max = max(x[xi])
        final_x.append([xi_min, xi_max])
        
    final_y = []
    for yi in range(0, len(y)):
        yi_min = min(y[yi])
        yi_max = max(y[yi])
        final_y.append([yi_min, yi_max])
        
    return(final_x, final_y)


## COMPUTE BACKTRACKING    
def backtrack_global(mat, mat_dir):
    
    x_final = []
    y_final = []
    
    ncol = mat.shape[1]-1
    nrow = mat.shape[0]-1
    
    x = [ncol]
    y = [nrow]
    
    while (ncol != 0 or nrow !=0):
        ## choose lowest score
        if mat_dir[nrow][ncol] == 0:
            ncol = ncol - 1
            nrow = nrow - 1
            
        elif mat_dir[nrow][ncol] == 1:
            nrow = nrow - 1
            
        elif mat_dir[nrow][ncol] == 2:
            ncol = ncol - 1
            
        x.append(ncol)
        y.append(nrow)
        
    x_final.append(x)
    y_final.append(y)
    
    (x_region, y_region) = get_region(x_final, y_final)
    return(x_final,y_final, x_region, y_region)
        

## COMPUTE BACKTRACKING    
def backtrack_local(mat, mat_dir, max_i, max_j):
    x_final = []
    y_final = []
    score_final_x = []
    score_final_y = []
    mat_col = mat.shape[1]
    mat_row = mat.shape[0] 
    
    for iteration in range(0, len(max_i)):
        ncol = max_j[iteration]
        nrow = max_i[iteration]
        
        x = [ncol]
        y = [nrow]
        
        score_x = [0] * (mat_col-ncol-1)
        score_y = [0] * (mat_row-nrow-1)
        score_x.append(mat[nrow][ncol] - mat[nrow-1][ncol-1])
        score_y.append(mat[nrow][ncol] - mat[nrow-1][ncol-1])
        
        #score_x.append(mat[nrow][ncol])
        #score_y.append(mat[nrow][ncol])
        
        
        while (mat[nrow][ncol] > 0 and (ncol != 0 or nrow != 0)):
            
            ## choose lowest score
            if mat_dir[nrow][ncol] == 0:
                ncol = ncol - 1
                nrow = nrow - 1
                
            elif mat_dir[nrow][ncol] == 1:
                nrow = nrow - 1
                
            elif mat_dir[nrow][ncol] == 2:
                ncol = ncol - 1
    
            x.append(ncol)
            y.append(nrow)
            
             
            score_x.append(mat[nrow][ncol] - mat[nrow-1][ncol-1])
            score_y.append(mat[nrow][ncol] - mat[nrow-1][ncol-1])
             
            #score_x.append(mat[nrow][ncol])
            #score_y.append(mat[nrow][ncol])
        
        if ncol != 0:
            score_x = score_x + [0]* ncol
        if nrow != 0:
            score_y = score_y + [0] * nrow
        
        x_final.append(x)
        y_final.append(y)
        score_final_x.append(score_x[::-1])
        score_final_y.append(score_y[::-1])
        
    (x_region, y_region) = get_region(x_final, y_final)
        
    return(x_final,y_final, x_region, y_region, score_final_x, score_final_y)

    
    
def plot_aln(x,y, m1, m2,  x_region, y_region, reverse, fig, ax, score_x, score_y, model_name, pfm1, pfm2):
    
    #plt.figure()
    #fig, axes = plt.subplots()
    #for i in range(0, len(x)):
    #    axes.plot(x[i], y[i])
    
    #axes.set_xlim(xmin=0, xmax = m1.shape[1]-1)
    #axes.set_ylim(ymin=0, ymax = m2.shape[1]-1)
    #plt.show()
    
   
    #fig, ax = plt.subplots(len(x_region), 2)
    
    print(len(x_region))
    print(m1.shape)
    if reverse:
        title = "REV"
    else:
        title = "FWD"
        
    if pfm1.shape[0] == 0:
        mplot1 = m1
    else:
        mplot1 = pfm1
    
    if pfm2.shape[0] == 0:
        mplot2 = m2
    else:
        mplot2 = pfm2
    
    if len(x_region) > 5:
        ax[0].set_title('no similarity')
        ax[1].set_title('no similarity')
    else:
            
        if len(x_region) == 1:
            if pfm1.shape[0] != 0:
                util.plot_info_logo(mplot1, score = score_x[0], ax=ax[0], highlightRegion = x_region[0])
                util.plot_info_logo(mplot2, score = score_y[0], ax=ax[1], highlightRegion = y_region[0], reverse=reverse)
            else:
                util.plot_logo(mplot1, score = score_x[0], ax=ax[0], highlightRegion = x_region[0])
                util.plot_logo(mplot2, score = score_y[0], ax=ax[1], highlightRegion = y_region[0], reverse=reverse)
        else:
            for highlight in range(0, len(x_region)):
                util.plot_info_logo(mplot1, score = score_x[highlight], ax=ax[highlight, 0], highlightRegion = x_region[highlight])
                #ax[2*highlight+1,0].plot(score_x[highlight])
                util.plot_info_logo(mplot2, score = score_y[highlight], ax=ax[highlight, 1], highlightRegion = y_region[highlight], reverse=reverse)
                #ax[2*highlight+1,1].plot(score_y[highlight])
        
   # gridsize = (3, 3)
   # gridsize = (3, 3)
   # fig = plt.figure(figsize=(12, 8))
   # ax1 = plt.subplot2grid(gridsize, (0, 0), colspan=1, rowspan=2)
   # ax2 = plt.subplot2grid(gridsize, (0, 1), colspan=2, rowspan=2)
   # ax3 = plt.subplot2grid(gridsize, (2, 1), colspan=2, rowspan=1)

def norm_mat(m):
    ncol = m.shape[1] #### ncol
    nrow = m.shape[0]
    
    mres = []
    
    # obtain normalization factor
    Vall = []
    for coli in range(0, ncol):
        V = 0
        for rowi in range(0, nrow):
            V = V + (pow(m[rowi][coli],2))
        V = math.sqrt(V)
        Vall.append(V)
        
    # normalize columns by norm factor
    for rowi in range(0, nrow):
        row_vec = []
        for coli in range(0, ncol):
            row_vec.append(m[rowi][coli]/Vall[coli])
        mres.append(row_vec)
            
    return(np.array(mres))
        
        
    
def compare_global(m1, m2, norm="NORM", reverse = "FALSE"):
    gap = -100
    m1_len = m1.shape[1] #### ncol
    m2_len = m2.shape[1] #### nrow
    
    #### NORM
    if norm == "NORM":
        m1 = norm_mat(m1)
        m2 = norm_mat(m2)
        

    #### INITIALIZAING 
    (mat, mat_dir) = init_mat(m1_len, m2_len)
    
    #### SCORE PER CELL
    #### i --> row, j --> col
    for i in range(1, m2_len): 
        for j in range(1, m1_len):
            (mat[i][j], mat_dir[i][j]) = score_per_cell(i, j, mat, mat_dir, gap, m1, m2)
            print(score_per_cell(i, j, mat, mat_dir, gap, m1, m2))
            print(mat[i][j])

    #### BACKTRACKING
    (x,y,x_region,y_region) = backtrack_global(mat, mat_dir)
    
    plot_aln(x,y, m1, m2, x_region, y_region, reverse)
    
    
    return(mat, mat_dir, x, y)



def compare_local(m1, m2, model_name, reverse="FALSE", **kwargs):
            
    gap = -100000000 ## MUST FIX THIS
    m1_len = m1.shape[1] #### ncol
    m2_len = m2.shape[1] #### nrow
    
    #### NORM
    if 'norm' in kwargs:
        norm=kwargs.get('norm')
    else:
        norm = "NORM"
        
    if 'pfm1' in kwargs:
        pfm1=kwargs.get('pfm1')
        
    if 'pfm2' in kwargs:
        pfm2=kwargs.get('pfm2')
    
    if norm == "NORM":
        m1 = norm_mat(m1)
        m2 = norm_mat(m2)
        
    
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
        
    #### INITIALIZAING
    (mat, mat_dir) = init_mat(m1_len, m2_len)
    
    #### GET SCORE MATRIX
    score_mat = get_score_mat(m1, m2, score)

    #### SCORE PER CELL
    max_i = []
    max_j = []
    #### i --> row, j --> col
    for i in range(1, m2_len): 
        for j in range(1, m1_len):
            (mat[i][j], mat_dir[i][j]) = score_per_cell(i, j, mat, mat_dir, gap, m1, m2, score_mat)
            if mat[i][j] < 0:
                mat[i][j] = 0
                
    print("DONE SCORING") 
           
    ### MAX SCORE
    max_score = np.max(mat)
    for i in range(1, m2_len): 
        for j in range(1, m1_len):
            if mat[i][j] == max_score:
                max_i.append(i)
                max_j.append(j)
                
    print("DONE INITIALIZE")
                
    #### BACKTRACKING
    #### FIND ALL MULTIPLE LOCAL HITS
    (x,y,x_region,y_region, score_x, score_y) = backtrack_local(mat, mat_dir, max_i, max_j)
    print("DONE BACKTRACK")
    
    #print(mat)
    print(len(x_region))
    print(len(score_x))
    print(len(score_y))
    
    if 'fig' in kwargs:
        fig=kwargs.get('fig')
        if len(x_region) > 5:
            axs=fig.subplots(1, 2)
        else:
            axs=fig.subplots(len(x_region), 2)  
    else:
        if len(x_region) > 5:
            fig, axs = plt.subplots(1, 2)
        else:
            fig, axs = plt.subplots(len(x_region), 2) 
    
   # breakpoint()
    
   #### plot aln
    plot_aln(x,y, m1, m2, x_region, y_region, reverse, fig, axs, score_x, score_y, model_name, pfm1, pfm2)
    
    
    return(mat, mat_dir, x, y, max_score)
        
 

def compare_semiglobal(m1, m2, model_name, reverse="FALSE", **kwargs):
            
    gap = -100000000 ## MUST FIX THIS
    m1_len = m1.shape[1] #### ncol
    m2_len = m2.shape[1] #### nrow
    
    #### NORM
    if 'norm' in kwargs:
        norm=kwargs.get('norm')
    else:
        norm = "NORM"
        
    if 'pfm1' in kwargs:
        pfm1=kwargs.get('pfm1')
        
    if 'pfm2' in kwargs:
        pfm2=kwargs.get('pfm2')
    
    if norm == "NORM":
        m1 = norm_mat(m1)
        m2 = norm_mat(m2)
        
    
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
    #### INITIALIZAING
    (mat, mat_dir) = init_mat(m1_len, m2_len)
    
    #### GET SCORE MATRIX
    score_mat = get_score_mat(m1, m2, score)

    #### SCORE PER CELL
    max_i = []
    max_j = []
    #### i --> row, j --> col
    for i in range(1, m2_len): 
        for j in range(1, m1_len):
            (mat[i][j], mat_dir[i][j]) = score_per_cell(i, j, mat, mat_dir, gap, m1, m2, score_mat, bias=bias)
           
            
    print("DONE SCORING") 
           
    ### MAX SCORE (of the bottom row)(regulon/meme pfm is on the rows)
    max_score = np.max(mat[-1])
    max_i = [m2_len -1]
    for j in range(0, m1_len): 
        if mat[-1][j] == max_score:
            max_j.append(j)
                
    print("DONE INITIALIZE")
    #print(max_i)
    #print(max_j)
                
    #### BACKTRACKING
    #### FIND ALL MULTIPLE LOCAL HITS
    (x,y,x_region,y_region, score_x, score_y) = backtrack_local(mat, mat_dir, max_i, max_j)
    print("DONE BACKTRACK")
    
    #print(mat)
    print(len(x_region))
    print(len(score_x))
    print(len(score_y))
    
#    if 'fig' in kwargs:
#        fig=kwargs.get('fig')
#        if len(x_region) > 5:
#            axs=fig.subplots(1, 2)
#        else:
#            axs=fig.subplots(len(x_region), 2)  
#    else:
#        if len(x_region) > 5:
#            fig, axs = plt.subplots(1, 2)
#        else:
#            fig, axs = plt.subplots(len(x_region), 2) 
    
   # breakpoint()
    
   #### plot aln
   # plot_aln(x,y, m1, m2, x_region, y_region, reverse, fig, axs, score_x, score_y, model_name, pfm1, pfm2)
    
    
    return(mat, mat_dir, x, y, max_score)
        
 



def compareKernels(mfit, model_name, th = 0.5, th_pfm = 0.75, **kwargs):
    
    if 'seq' in kwargs:
        seq=kwargs.get('seq')
    else:
        seq = ""
        
        
    if 'norm' in kwargs:
        norm=kwargs.get('norm')
    else:
        norm = "NORM"
        
    if 'pfm' in kwargs:
        pfm=kwargs.get('pfm')
    else:
        pfm = False
        
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
    
    ### REVERSE COMPLEMENT
    mfitc = sequence.revcomp(mfit)
    
    
    print(th)
    print(score)
    ### KEEP ONLY INFORMATIVE KERNELS
    mfit_final = []
    mfitc_final = []
    if pfm:
        for x in range(0, len(mfit)):
            pfmx,n,slist,covlist=sequence.make_pfm_from_pam(mfit[x], seq, th)
            pfmx_max_perc = np.max(pfmx, axis=0)
            pfmx_max = max(pfmx_max_perc)
        
            if pfmx_max >= th_pfm:
                mfit_final.append(mfit[x])
                mfitc_final.append(mfitc[x])
    else:
        mfit_final = mfit
        mfitc_final = mfitc
        
    fig=plt.figure(figsize=(66,22))
    print(model_name)
    
    if len(mfit_final) == 1:
        print("ONLY 1 INFORMATIVE KERNEL")
        return (None, None)
    
    subfigs=fig.subfigures(len(mfit_final), len(mfit_final))

    ## DO ALL PAIRED COMPARISONS BETWEEN KERNELS
    for x in range(0, len(mfit_final)):
        if pfm:
            pfm1,n,slist,covlist=sequence.make_pfm_from_pam(mfit_final[x], seq, th)
            pfm1c = sequence.revcomp(pfm1)
        else:
            pfm1 = np.empty(0, dtype=float)
            pfm1c = np.empty(0, dtype=float)
            

        for y in range(0, len(mfit_final)):
            if pfm:
                pfm2,n,slist,covlist=sequence.make_pfm_from_pam(mfit_final[y], seq, th)
                pfm2c = sequence.revcomp(pfm2)
            else:
                pfm2 = np.empty(0, dtype=float)
                pfm2c = np.empty(0, dtype=float)
                
            if x == y:
                if x == 0:
                    title = model_name
                else:
                    title = ""
                           
                figX = subfigs[x][y]
                axsX=figX.subplots(1,1)
                if pfm:
                    util.plot_info_logo(pfm1, ax=axsX, title = title)
                else:
                    util.plot_logo(mfit_final[x], ax=axsX, title = title)
            elif x < y:
                (mat, mat_dir, xm, ym, max_score) = compare_local(mfit_final[x], mfit_final[y], model_name, reverse=False, fig = subfigs[x][y], norm = norm, pfm1 = pfm1, pfm2=pfm2, score = score)
            else:
                (mat, mat_dir, xm, ym, max_score) = compare_local(mfit_final[y], mfitc_final[x], model_name, reverse=True, fig = subfigs[x][y], norm = norm, pfm1 = pfm2, pfm2=pfm1c, score = score)

    plt.show() 
    
    return(mat, max_score)
    

# TAKE TWO KERNELS PLUS ADDITIONAL SEQUENCES (OPTIONAL)
def compare_two_kernels(mfit1, mfit2, **kwargs):
    
    if 'name' in kwargs:
        name=kwargs.get('name')
    else:
        name = ""
        
    if 'norm' in kwargs:
        norm=kwargs.get('norm')
    else:
        norm = "UNNORM"

        
    if 'seq1' in kwargs:
        seq1=kwargs.get('seq1')
    else:
        seq1 = []
        
    if 'seq2' in kwargs:
        seq2=kwargs.get('seq2')
    else:
        seq2 = []
        
    if 'th' in kwargs:
        th=kwargs.get('th')
    else:
        th = 0.5
        
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
    mfitc2 = sequence.revcomp(mfit2)
    
    #fig=plt.figure(figsize=(66,22))
    print(name)
    print(th)
    print(score)
    #subfigs=fig.subfigures(2, 2)

    if len(seq1) > 0:
        pfm1,n,slist,covlist=sequence.make_pfm_from_pam(mfit1, seq1, th)
    else:
        pfm1 = np.empty(0, dtype=float)
        
        
    if len(seq2) > 0:
        pfm2,n2,slist2,covlist2=sequence.make_pfm_from_pam(mfit2, seq2, th)
        pfm2c = sequence.revcomp(pfm2)
    else:
        pfm2 = np.empty(0, dtype=float)
        pfm2c = np.empty(0, dtype=float) 
        
        
    #figX = subfigs[0][0]
    #axsX=figX.subplots(1,1)
    
    #figX2 = subfigs[1][1]
    #axsX2=figX2.subplots(1,1)
    
    
    ##### NOT PLOT FOR NOW
    if len(seq1) > 0:
        util.plot_info_logo(pfm1, ax=axsX, title = name)
    else:
        util.plot_logo(mfit1, ax=axsX, title = name)
        
    if len(seq2) > 0:
        util.plot_info_logo(pfm2, ax=axsX2, title = name)
    else:
        util.plot_logo(mfit2, ax=axsX2, title = name)
              

    #(mat, mat_dir, xm, ym, max_score1) = compare_local(mfit1, mfit2, name, reverse=False, fig = subfigs[0][1], norm = norm, pfm1 = pfm1, pfm2=pfm2, score = score)
    #(mat, mat_dir, xm, ym, max_score2) = compare_local(mfit1, mfitc2, name, reverse=True, fig = subfigs[1][0], norm = norm, pfm1 = pfm1, pfm2=pfm2c, score = score)


    #(mat, mat_dir, xm, ym, max_score1) = compare_semiglobal(mfit1, mfit2, name, reverse=False, fig = subfigs[0][1], norm = norm, pfm1 = pfm1, pfm2=pfm2, score = score, bias = bias)
    #(mat, mat_dir, xm, ym, max_score2) = compare_semiglobal(mfit1, mfitc2, name, reverse=True, fig = subfigs[1][0], norm = norm, pfm1 = pfm1, pfm2=pfm2c, score = score, bias = bias)

    (mat, mat_dir, xm, ym, max_score1) = compare_semiglobal(mfit1, mfit2, name, reverse=False, norm = norm, pfm1 = pfm1, pfm2=pfm2, score = score, bias = bias)
    (mat, mat_dir, xm, ym, max_score2) = compare_semiglobal(mfit1, mfitc2, name, reverse=True, norm = norm, pfm1 = pfm1, pfm2=pfm2c, score = score, bias = bias)

   # plt.show() 
    
    return(max_score1, max_score2)
    

def pfmVSkernel(kernel, pfm, **kwargs):
    
    if 'th' in kwargs:
        th=kwargs.get('th')
    else:
        th = 0.5
        
    if 'name' in kwargs:
        name=kwargs.get('name')
    else:
        name = ""
        
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
    if 'seq' in kwargs:
        seq=kwargs.get('seq')
    else:
        seq = []
        
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
        
    #pfm_kernel,n,slist,covlist=sequence.make_pfm_from_pam(kernel,seq,th)
    max_score1, max_score2 = compare_two_kernels(kernel, pfm, seq1=seq, th = th, name = name, score = score, bias = bias)
    
    return(max_score1, max_score2)
    
    

def bestTfMatch(kernels, seq, tfs, pfms, **kwargs):
    
    if 'name' in kwargs:
        name=kwargs.get('name')
    else:
        name = ""
        
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
        
    tfs_max = []
    scores_max = []
    for i_k in range(0, len(kernels)):
        kernel = kernels[i_k]
        scores = []

        for i_tfs in range(0, len(tfs)):
            (max_score1,max_score2) = pfmVSkernel(kernel, pfms[i_tfs], seq, name=tfs[i_tfs], score = score)
            score_tf = max(max_score1, max_score1)
            scores.append(score_tf)
        
        maxs = max(scores)
        maxi = scores.index(maxs)
        
        tfs_max.append(tfs[maxi])
        scores_max.append(maxs)

    return(tfs_max, scores_max)
    
   
def bestTfMatchPFM(pfm_model, **kwargs):
    
    if 'name' in kwargs:
        name=kwargs.get('name')
    else:
        name = ""
        
    if 'score' in kwargs:
        score=kwargs.get('score')
    else:
        score = "dotprod"
        
    if 'source' in kwargs:
        source=kwargs.get('source')
    else:
        source = "regulon"
        
    if 'bias' in kwargs:
        bias=kwargs.get('bias')
    else:
        bias = -0.8
        
       
    print("READING SOURCE ")
    
    ## READ PFMS FROM DATABANK:ETIHER REGULON OR MEME
    if source == "regulon":
        [pssm, pfms, tfs] = read_pssm(CONFIG.regulon_psssm_file)
    else:
        [pssm, pfms, tfs] = read_meme(CONFIG.meme_dir)


    print("READING SOURCE DONE")
    
    scores = []
    #for i_tfs in range(0, 2):
    for i_tfs in range(0, len(tfs)):

        (max_score1,max_score2) = pfmVSkernel(pfm_model, pfms[i_tfs], name=tfs[i_tfs], score = score, bias = bias)
        
        target_tf_len = pfms[i_tfs].shape[1]
        max_score1_norm = max_score1/target_tf_len
        max_score2_norm = max_score2/target_tf_len
        
        #score_tf = max(max_score1, max_score1)
        score_tf = max(max_score1_norm, max_score2_norm)
        scores.append(score_tf)
            
    maxs = max(scores)
    maxi = scores.index(maxs)
            
    max_tf = tfs[maxi]
    
    res = {'max_tf' : max_tf, 'maxs' : maxs, 'maxi' : maxi, 'scores' : scores}

    return(res)
    
   
    
   
def read_pssm(file):
    pssm = []
    pfm = []
    tf_names = []
    tf_n = []
    tf_found = 0
    with open(file) as handle:
         for line in handle:
             line = line.rstrip()
             info = line.split("\t")
             if "Transcription Factor Name" in line and "#" not in line:
                 A = []
                 C = []
                 G = []
                 T = []
                 name = line.split(" ")[-1]
                 tf_names.append(name)
                 
             ## Read counts for all nucleotides    
             if line.startswith("A\t"):
                 A = [int(x) for x in info[1:len(info)]]
                 
             if line.startswith("C\t"):
                 C = [int(x) for x in info[1:len(info)]]
                 
             if line.startswith("G\t"):
                 G = [int(x) for x in info[1:len(info)]]
                 
             if line.startswith("T\t"):
                 T = [int(x) for x in info[1:len(info)]]
                 tf_found = 1
                 
             # Convert counts into frequencies
             if tf_found:
                 tf = pd.DataFrame([A, C, G, T])
                 tf_sum = tf.sum(axis=0)
                 tf_freq = tf/tf_sum
                 tf_mat = tf_freq.values
            
                 pssm.append(tf.values)
                 pfm.append(tf_mat)
                 tf_n.append(tf_sum[0])
                 
                 tf_found = 0
                 
            
    return(pssm, pfm, tf_names, tf_n)

        
def rev_comp(s):
    
    a = letters.index('A')
    c = letters.index('C')
    g = letters.index('G')
    t = letters.index('T')

    sr = s.copy()
    sr.iloc[a, :] = s.iloc[t,:]
    sr.iloc[t, :] = s.iloc[a,:]

    sr.iloc[c, :] = s.iloc[g, :]
    sr.iloc[g, :] = s.iloc[c, :]

    sr = np.fliplr(sr)

    return sr


def get_info_content(df):   
    df = np.transpose(df)
    df = pd.DataFrame(data=df, columns=letters)
    df = logomaker.transform_matrix(
        df, from_type='probability', to_type='information')
    df = np.transpose(df)
    return(df)

    
def read_meme(dir,tfs=[]):
    
    tf_dirs = os. listdir(dir)
    
    pssm = []
    pfm = []
    tf_names = []
    tf_n = []
    
    
    if len(tfs)>0:
        tf_dirs=[i for i in tf_dirs if i in tfs]
    
    for tf_dir in tf_dirs:
        
    
        #meme_path = os.path.join(dir, tf_dir, "meme_out", "meme.xml")
        meme_path = os.path.join(dir, tf_dir, "meme.xml")
        print(meme_path)
        
        if not os.path.exists(meme_path):
            continue
        
        tf_names.append(tf_dir)

            
        handle = open(meme_path)
        record = motifs.parse(handle, "meme")
        handle.close()
        
        motif = record[0]
        

        A = motif.counts['A',:]       
        C =  motif.counts['C',:]         
        G =  motif.counts['G',:]         
        T =  motif.counts['T',:]
                 
        # Convert counts into frequencies
        tf = pd.DataFrame([A, C, G, T])
        tf_sum = tf.sum(axis=0)
        tf_freq = tf/tf_sum
        tf_mat = tf_freq.values
            
        pssm.append(tf.values)
        pfm.append(tf_mat)
        tf_n.append(tf_sum[0])
                 
        tf_found = 0
            
    return(pssm, pfm, tf_names, tf_n)

    

def read_pssm_claire(dir):
    pssm = []
    pfm = []
    tf_names = []
    tf_n = []
    tf_found = 0
    
    
    tf_dirs = os.listdir(dir)
    for tf_dir in tf_dirs:
        
        file_path = os.path.join(dir, tf_dir, tf_dir + ".tab")
        
        if not os.path.exists(file_path):
            continue
        
        tf_names.append(tf_dir)
        
        with open(file_path) as handle:
            A = []
            C = []
            G = []
            T = []
    
            for line in handle:
                line = line.rstrip()
                info = line.split("\t")
                          
                ## Read counts for all nucleotides    
                if line.startswith("A\t"):
                    A = [int(x) for x in info[1:len(info)]]
                 
                if line.startswith("C\t"):
                    C = [int(x) for x in info[1:len(info)]]
                 
                if line.startswith("G\t"):
                    G = [int(x) for x in info[1:len(info)]]
                 
                if line.startswith("T\t"):
                    T = [int(x) for x in info[1:len(info)]]
                 
            # Convert counts into frequencies
            tf = pd.DataFrame([A, C, G, T])
            tf_sum = tf.sum(axis=0)
            tf_freq = tf/tf_sum
            tf_mat = tf_freq.values
            
            pssm.append(tf.values)
            pfm.append(tf_mat)
            tf_n.append(tf_sum[0])
                             
            
    return(pssm, pfm, tf_names, tf_n)

#############################################################
# code for comparing model motifs to regulonDB
#############################################################
def scoring_function (bs, full_mat_a, full_mat_b, score_method, size, bs_min_mat, bs_max_mat,  info_min, info_max, topn, intersection, normalize=False, exponentiate=False):
    score = 0
    inter_specific = 0
    if exponentiate:
        full_mat_a = np.exp(full_mat_a)
        full_mat_b = np.exp(full_mat_b)
        
        
    for pos in range(0, size):
        
        ### AVOID POSITIONS THAT WERE FILLED TO ALLOW GRAPHICAL REPRESENTATION
        artificial = np.array([0.0001, 0.0001, 0.0001, 0.0001])
        if not (np.array_equal(full_mat_a[:,pos], artificial) or np.array_equal(full_mat_b[:,pos], artificial)):
            
            ### SKIP COMPARISON BETWEEN POSITION WITH LOW INFORMATION CONTENT
            inter_specific = inter_specific + 1
            if sum(full_mat_a[:,pos]) < info_max or sum(full_mat_b[:,pos]) < info_min:
                continue

            if topn == 1:
                vec_a =np.zeros(4)
                vec_a[np.argmax(full_mat_a[:,pos])] = 1   
                vec_b =np.zeros(4)
                vec_b[np.argmax(full_mat_b[:,pos])] = 1
            else:
                vec_a = full_mat_a[:,pos]
                vec_b = full_mat_b[:,pos]
                
            if normalize:
                vec_a_sum =  np.sum(full_mat_a[:,pos])
                vec_a =   full_mat_a[:,pos] / vec_a_sum
                vec_b_sum = np.sum(full_mat_b[:,pos])
                vec_b = full_mat_b[:,pos] / vec_b_sum
                
            score_base = change_score_base(vec_a, vec_b, method=score_method)
            #if score_base >= 1:
            score = score + score_base
            
    print(score)
    if score > bs:
        bs = score
        bs_max_mat = full_mat_a
        bs_min_mat = full_mat_b
        intersection = inter_specific
        
    if score == bs and inter_specific > intersection:
        bs = score
        bs_max_mat = full_mat_a
        bs_min_mat = full_mat_b
        intersection = inter_specific
        
    return(bs, bs_min_mat, bs_max_mat, intersection)



def compare_tf_model_motif(tf_name,model_name,normalize=False,exponentiate=False,topn=1,info_threshold=0.6,fig=None,score_method='dotprod',**kwargs):
    '''For a given tf_name and model_name, compare the model PFM to
    the regulonDB PFM
    Return True or False if alignment could be found
    '''
    
    
    print('----%s------'%tf_name)
    
    # tf_name = tfs['tf'][tf_x]
    # tf_name_lower = tf_name.lower()

    # check to see if we have a regulonDB motif - naming convention is first letter cap e.g. "PdhR"
    [pssm, pfms, tfs_pssm, tf_n] = read_meme(CONFIG.new_regulon_dir,tfs=[tf_name[0].upper()+tf_name[1:]])
    
    # if we cannot find a model, check for a synonym and try to load that
    if len(pssm)==0:
        db=ecoliDB()
        syns=db.getGeneSynonyms(gene_symbol=tf_name)
        db.close()
        for syn in syns[0]:
            [pssm, pfms, tfs_pssm, tf_n] = read_meme(CONFIG.new_regulon_dir,tfs=[syn[0].upper()+syn[1:]])
            if len(pssm)>0:
                break
        
    
    # could not find a motif for either the name or any synonyms, we skip
    if len(pssm)==0:
        return False
    
    # tf_index = tfs_pssm_lower.index(tf_name_lower)
    tf_index=0 # we are only getting the pfms we need now
    
    # pdb.set_trace()
    # NOT ELEGANT
    (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=model_create.parseModelName(model_name)
    dashboard_tag=model_tag.split('_')[2]
    filterpat='*%s*'%dashboard_tag
    tf_models=TFModels(tf_name,filterpat=filterpat)
    
    #data=SeqCovDB(tf_name)
    #df=data.get_info()
    
    if ( len(tf_models.exp_num) == 0):
        return False
    
    
    # just compare model 0 for the tf_models - should only ever be one model these days
    # name_res_prev = tf_name + "_" + str(0)
    # print(name_res_prev)
    (model,exp_data)=tf_models.load_model_and_data(0)
    # X=exp_data['X']
    # y=exp_data['y']
    ifirstneg=exp_data['ifirstneg']
    seq=exp_data['seq']
    # seq_start=exp_data['seq_start']
    # seq_stop=exp_data['seq_stop']
    # gcov=exp_data['gcov']
    
    (mfit,mfitc,biases)=tf_util.getModelMotifs(model)
    pfm_model,n,slist,covlist=sequence.make_pfm_from_pam(mfit[0],seq,0.6,numseqs=ifirstneg)
            
    model_size = pfm_model.shape[1]
    tf_size = pfms[tf_index].shape[1]
    
    model_info = get_info_content(pfm_model)
    kw_info = get_info_content(pfms[tf_index])
    kw_n = tf_n[tf_index]
    
    ### INFO THRESHOLD
    ### get info threshold as 60% of the top base of the lowest info content mattix
    ### 
    info_threshold_model = np.max(np.sum(model_info))*info_threshold
    info_threshold_kw = np.max(np.sum(kw_info))*info_threshold
     
    
    ## save representation of maximum size
    if model_size > tf_size:
        mx_mat = model_info
        min_mat = kw_info
        mx_mat_info = "model"
        info_min = info_threshold_kw
        info_max =info_threshold_model
    else:
        mx_mat = kw_info
        min_mat = model_info
        mx_mat_info = "regulon"
        info_min = info_threshold_model
        info_max =info_threshold_kw
        
    min_mat_rc = rev_comp(min_mat)
    motif_small_size = min_mat.shape[1]
    motif_large_size = mx_mat.shape[1]

    
#   for score_method in ['mse', 'dotprod', 'ssd', 'sw', 'nsw', 'eucl', 'nseucl' ]:


    ### save best score matrices
    bs = 0
    bs_min_mat = []
    bs_max_mat = []
    intersection = 0

    ### SLIDING WINDOW TO TEST ALL POSSIBLE SUPERPOSITIONS, FIRST HALF
    max_size = motif_large_size + motif_small_size - 1
    for i in range(0, motif_small_size):
    
        # print ("1--- " + str(i))
        size = max(motif_small_size-i+motif_large_size, motif_small_size)
        
        #pdb.set_trace()
        
        full_mat_a = np.zeros((4, size))
        full_mat_a[:] = 0.0001
        full_mat_a[:, motif_small_size-i:motif_small_size-i+motif_large_size] = mx_mat
           
        full_mat_b = np.zeros((4, size))
        full_mat_b[:] = 0.0001
        full_mat_b[:, 0:motif_small_size] = min_mat
    
    
        [bs, bs_min_mat, bs_max_mat, intersection] = scoring_function(bs, full_mat_a, full_mat_b, score_method, size, bs_min_mat, bs_max_mat, info_min, info_max, topn, intersection, normalize, exponentiate)

        ## REVERSE COMPLEMENT   
        full_mat_b = np.zeros((4, size))
        full_mat_b[:] = 0.0001
        full_mat_b[:, 0:motif_small_size] = min_mat_rc
        
        [bs, bs_min_mat, bs_max_mat, intersection] = scoring_function(bs, full_mat_a, full_mat_b, score_method, size, bs_min_mat, bs_max_mat,  info_min, info_max, topn, intersection, normalize, exponentiate)

        
                    
    ## SECOND HALF
    for i in range(0, motif_large_size):
        # print ("2--- " + str(i))
        
        size = max(motif_large_size, i+motif_small_size)
        
        full_mat_a = np.zeros((4, size))
        full_mat_a[:] = 0.0001
        full_mat_a[:, 0:motif_large_size] = mx_mat

        full_mat_b = np.zeros((4, size))
        full_mat_b[:] = 0.0001
        full_mat_b[:, i:i+motif_small_size] = min_mat
    
    
        [bs, bs_min_mat, bs_max_mat, intersection] = scoring_function(bs, full_mat_a, full_mat_b, score_method, size, bs_min_mat, bs_max_mat,  info_min, info_max, topn, intersection, normalize, exponentiate)

        ## REVERSE COMPLEMENT
        full_mat_b = np.zeros((4, size))
        full_mat_b[:] = 0.0001
        full_mat_b[:, i:i+motif_small_size] = min_mat_rc

        [bs, bs_min_mat, bs_max_mat, intersection] = scoring_function(bs, full_mat_a, full_mat_b, score_method, size, bs_min_mat, bs_max_mat,  info_min, info_max, topn, intersection, normalize, exponentiate)

            

    if bs == 0:
        # axs[0].annotate(tf_models.model_names[0] + "\n ScoreMethod:" + score_method + " IC Thr:" + str(round(info_min, 2)) + "," + str(round(info_max, 2)),
                          # (0.2, 0.2))
        return False
    else:
        
        
        if fig is None:
            fig=plt.figure(layout='constrained',figsize=(10,5))
            
        axs=fig.subplots(2,1)
        
        
        ## GET NUMBERS FOR TABLE
        info_tf = {'TF': tf_name, 'Nmodel': ifirstneg/3, 'Ncompare': kw_n}
        # info_df = info_df.append(info_tf, ignore_index = True)
        
        # do the plot on the figure
            
        if mx_mat_info == "model":
        
            util.plot_logo(bs_max_mat, ax=axs[1], 
                           #title = tf_models.model_names[index] + " IC Thr:" + str(round(info_min, 2)) + "," + str(round(info_max, 2)))
                           #title = tf_models.model_names[index])
                           ylabel = 'Model', 
                           xticks = 0, yticks = 0,**kwargs)
            
       
            util.plot_logo(bs_min_mat, ax=axs[0], title='%s'%tf_name, 
                           xticks = 0, yticks = 0,ylabel='Known',**kwargs)
       
        else:
            util.plot_logo(bs_min_mat, ax=axs[1], 
                           #title = tf_models.model_names[index] + " IC Thr:" + str(round(info_min, 2)) + "," + str(round(info_max, 2)))
                           #title = tf_models.model_names[index])
                           ylabel = 'Model' ,
                           xticks = 0, yticks = 0,**kwargs)
                                
            util.plot_logo(bs_max_mat, ax=axs[0], title='%s'%tf_name,
                           xticks = 0, yticks = 0,ylabel='Known',**kwargs)
 
        


    
    
    return True


         
            