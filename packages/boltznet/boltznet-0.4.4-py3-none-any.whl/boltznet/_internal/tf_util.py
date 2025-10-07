#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions specific for working with tensorflow
and associated objects

@author: jamesgalagan
"""

from . import util
from . import sequence

import pandas as pd
import numpy as np
import math
from . import coverage
import matplotlib.pyplot as plt
import seaborn as sns

import scipy.io
from . import model_disect
import tensorflow as tf
import os
from . import browser_util
from . import model_create
import copy
from .factory import Factory

import json
from . import CONFIG




def getMinLossFromHist(hist_p):
    
    minl=list()
    for k in hist_p.history.keys():
        minl.append(min(hist_p.history[k]))
    
    
    return minl


#-----------------------
def plotFitHist(hist_p):
    
    minl=list()
    for k in hist_p.history.keys():
        plt.plot(np.log10(hist_p.history[k]))
        minl.append(min(hist_p.history[k]))
    # plt.plot(hist_p.history['val_loss'])
    
    plt.title('Training History')
    
    
    plt.ylabel('Log Value')
    plt.xlabel('Epoch')
    
    
    plt.legend(list(hist_p.history.keys()))
    
    
    
    plt.show()
    

    return minl

#-----------------------
def plotRegulonPFM(tf_name,regDB=None,fs=12,tick_font=8,fig=None,ax=None,ylabel='Bits',xlabel='Position',title=None,rc=False,**kwargs):
    '''Plot the known motif for a model from RegulonDB
    Calls util.getRegulonDBPFMs() to get RegDB but can also pass a regDB dictionary of PFMs 
    useful if you are going plot multiple TF PFMs so that you do not have load all of them again and again'''
    
    if regDB is None:
        tf=tf_name[0].upper()+tf_name[1:]
        regDB=util.getRegulonDBPFMs(tfs=[tf])
    
    # set up figure and axes of necessary
    nplots=1

    if fig is None and ax is None:        
        fig,axs=plt.subplots(figsize=(11,5))
    else:

        if ax is None:
            axs=fig.subplots()
        else:
            axs=ax

    m = None
    # CK: changed this casing b/c it's already being lowered as such for the keys of regDB in getRegulonDBPFMs()
    tf_name_lowercase = tf_name[0].lower() + tf_name[1:]
    if tf_name_lowercase in regDB:
        m=regDB[tf_name_lowercase]

    if m is not None:
        #handle reverse complement
        if rc:
            m=sequence.revcomp(m)
        
        util.plot_info_logo(m, ax=axs)
        axs.set_ylabel(ylabel,fontsize=fs,)
        axs.set_xlabel(xlabel,fontsize=fs)
        axs.tick_params(axis='both', which='major', labelsize=tick_font)
        axs.spines[['top','right']].set_visible(False)
        
    else:
        axs.tick_params(axis='both', which='major', labelsize=0)
        axs.set_xticks([])
        axs.set_yticks([])
        axs.text(0.5,0.5,'None',va='center',ha='center',fontsize=fs)
        axs.spines[['top','right','bottom','left']].set_visible(False)
        
    axs.set_title(title,fontsize=fs)
        
    
    
    if 'title' in kwargs:
        axs.set_title(kwargs.get('title'),color='k',fontsize=fs)    

    

#-----------------------
def plotModelPFM(model,seq,th,fs=12,tick_font=8,fig=None,ax=None,ylabel='Bits',xlabel='Position',**kwargs):
    '''Infer and plot the PFM for a model'''    
    if 'layer_name' in kwargs:
        layer_name=kwargs.get('layer_name')
        (nkerns,msize)=getKernelInfo(model,layer_name=layer_name)
        (mfit,mfitc,biases)=getModelMotifs(model,layer_name=layer_name)
    else:        
        (nkerns,msize)=getKernelInfo(model)
        (mfit,mfitc,biases)=getModelMotifs(model)
    
    heatmap=0
    hspace=0.9
    if 'heatmap' in kwargs:
        heatmap=kwargs.get('heatmap')
        hspace=0.4
        
    
    mfit_pfm=[]
    ns=[]

    
    if (heatmap):
        nplots=len(mfit)*2
    else:
        nplots=len(mfit)

    if fig is None and ax is None:        
        if (len(mfit)>1):
            fig,axs=plt.subplots(nplots,1,figsize=(8,nplots*4))
            plt.subplots_adjust(hspace=hspace)
        else:
            fig,axs=plt.subplots(nplots,1,figsize=(11,5))
    else:
        if ax is None:
            if (len(mfit)>1):
                axs=fig.subplots(nplots,1)
                plt.subplots_adjust(hspace=hspace)
            else:
                axs=fig.subplots(nplots,1)
        else:
            axs=ax
            
    if 'cmap' in kwargs:
        cmap=kwargs.get('cmap')
    else:
        cmap = plt.get_cmap("tab10")
    
    for i in range(len(mfit)):

        # print(i)
        m,n,slist,covlist=sequence.make_pfm_from_pam(mfit[i], seq, th, **kwargs)
        # print(covlist)
        
        mfit_pfm.append(m)
        ns.append(n)
        if (nplots>1):
            
            if (heatmap):
                ii=i*2
            else:
                ii=i       
            
            util.plot_info_logo(mfit_pfm[i], ax=axs[ii])
            axs[ii].set_ylabel(ylabel,fontsize=fs,)
            axs[ii].set_xlabel(xlabel,fontsize=fs)
            axs[ii].tick_params(axis='both', which='major', labelsize=tick_font)
            axs[ii].spines['top'].set_visible(False)
            axs[ii].spines['right'].set_visible(False)
            if (not biases==[]):
                axs[ii].set_title('Kernel %d (%d sequences) (Bias = %f)'%(i,n,biases[i]),color=cmap(i),fontsize=fs)
            else:
                axs[ii].set_title('Kernel %d (%d sequences) (No Bias)'%(i,n),color=cmap(i),fontsize=fs)
            
            if (heatmap):
                if (len(slist)>0):
                    num=sequence.onehot2num_multi(slist)
                    axs[ii+1].imshow(num,cmap=sequence.seqcolors,aspect='auto')
                    axs[ii+1].set_xticks(range(num.shape[1]))
            
            if 'title' in kwargs:
                axs[ii].set_title(kwargs.get('title'),color='k',fontsize=fs)
        

            
        else:
            util.plot_info_logo(mfit_pfm[i], ax=axs)
            axs.set_ylabel(ylabel,fontsize=fs,)
            axs.set_xlabel(xlabel,fontsize=fs)
            axs.tick_params(axis='both', which='major', labelsize=tick_font)
            axs.spines['top'].set_visible(False)
            axs.spines['right'].set_visible(False)
            
            if (not biases==[]):
                axs.set_title('PFM %d (%d sequences) (Bias = %f)'%(0,n,biases[0]),color=cmap(0),fontsize=fs)
            else:
                axs.set_title('Kernel %d (%d sequences) (No Bias)'%(0,n),color=cmap(0),fontsize=fs)
            
            if 'title' in kwargs:
                axs.set_title(kwargs.get('title'),color='k',fontsize=fs)
                
    if 'savefile' in kwargs:
        filename='%s/%s_PFMs.png'%(CONFIG.model_dir,kwargs.get('savefile'))
        print('Saving file %s'%filename)
        plt.savefig(filename)
    
   

    return mfit_pfm,ns


def saveModelKernels(model, filename, save_bias=True):
    '''Save the first weight matrix for a model to filename.csv as a csv file
    The file with have four rows corresponding to sequence.letters
    and len(motif) columns
    
    And if save_bias=True will also save the bias
    as filename_bias.txt
    
    '''
    
    (mfit,mfitc,biases)=getModelMotifs(model)
    
    df=pd.DataFrame(mfit[0],index=sequence.letters)
    df.to_csv('%s.csv'%filename)
    
    if save_bias:
        with open("%s_bias.txt"%filename, "w") as file:
            file.write(str(biases[0]))
    
    
    
#------------------------
def plotModelKernels(model, exp_kernel=0, cth=-10, ylabel='Weight', xlabel='Position', fs=12,tick_font=8,**kwargs):
    
    
    if 'layer_name' in kwargs:
        (mfit,mfitc,biases)=getModelMotifs(model,layer_name=kwargs.get('layer_name'))
    
    else:
        (mfit,mfitc,biases)=getModelMotifs(model)
        
    if ('fig' in kwargs or 'ax' in kwargs):
        fig=kwargs.get('fig',None)
    else:
        fig=plt.figure(figsize=(25,8))
        
    if 'ax' in kwargs:
        axs=kwargs.get('ax')
    else:
        axs=fig.subplots(len(mfit),1)
   
    if len(mfit)>1:
        # fig,axs=plt.subplots(len(mfit),1,figsize=(8,11))
        # plt.subplots_adjust(hspace=0.6)
        for j in range(len(mfit)):
            if (exp_kernel):
                util.plot_exp_logo(mfit[j].clip(min=cth), ax=axs[j])
            else:
                util.plot_logo(mfit[j].clip(min=cth), ax=axs[j])
                
            axs[j].spines[['top','right']].set_visible(False)
            axs[j].set_ylabel(ylabel,fontsize=fs)
            axs[j].set_xlabel(xlabel,fontsize=fs)
            axs[j].tick_params(axis='both', which='major', labelsize=tick_font)
    
    else:
        # fig,axs=plt.subplots(len(mfit),1,figsize=(8,11))
        if (exp_kernel):
            util.plot_exp_logo(mfit[0].clip(min=cth), ax=axs)
        else:
            util.plot_logo(mfit[0].clip(min=cth), ax=axs)
            
            
        axs.spines[['top','right']].set_visible(False)
        axs.set_ylabel(ylabel,fontsize=fs)
        axs.set_xlabel(xlabel,fontsize=fs)
        axs.tick_params(axis='both', which='major', labelsize=tick_font)

        
        
        # fig.suptitle(model.name)
        
    if 'savefile' in kwargs and kwargs.get('savefile')==1:
        filename='%s/%s_Kernel.png'%(CONFIG.model_dir,kwargs.get('savefile'))
        print('Saving file %s'%filename)
        plt.savefig(filename)
    # else:
    #     plt.show()

#------------------------
def plotModelKernelBestSeqs(model, **kwargs):
    
    
    if 'layer_name' in kwargs:
        (mfit,mfitc,biases)=getModelMotifs(model,layer_name=kwargs.get('layer_name'))
    
    else:
        (mfit_raw,mfitc,biases)=getModelMotifs(model)
   
    mfit=np.copy(mfit_raw)
    for j in range(len(mfit)):
        
        maxv=np.amax(mfit[j],axis=0)
        #zero out all the elements except the max
        for k in range(mfit[j].shape[1]):
            for l in range(4):
                if (not mfit[j][l,k] == maxv[k] or mfit[j][l,k]<0):
                    mfit[j][l,k]=0
    
    
    cth=-10
   
    if len(mfit)>1:
        fig,axs=plt.subplots(len(mfit),1,figsize=(8,11))
        plt.subplots_adjust(hspace=0.6)
        for j in range(len(mfit)):
            util.plot_logo(mfit[j].clip(min=cth), ax=axs[j])
            if (not biases ==[]):
                axs[j].set_title('Kernel %d Best Seq (Bias = %f) '%(j,biases[j]))
            else:
                axs[j].set_title('Kernel %d Best Seq (No Bias)'%j)
            fig.suptitle(model.name)
    else:
        fig,axs=plt.subplots(len(mfit),1,figsize=(8,11))
        util.plot_logo(mfit[0].clip(min=cth), ax=axs)
        if (not biases ==[]):
            axs.set_title('Kernel %d Best Seq (Bias = %f) '%(0,biases[j]))
        else:
            axs.set_title('Kernel %d Best Seq (No Bias)'%0)
        
        fig.suptitle(model.name)
        
    if 'savefile' in kwargs:
        filename='%s/%s_Kernel Best Seqs.png'%(CONFIG.model_dir,kwargs.get('savefile'))
        print('Saving file %s'%filename)
        plt.savefig(filename)

#-----------------------
def seqKernelStats(X,model,inds):
    """ calculate stats of kernel scans on each seq in X
    X is a tensor of shape (nseqs,4,slen,1)
    inds is an array of indices into nseqs"""
    
    (mfit,mfitc,biases)=getModelMotifs(model)

    
    #outputs will be arrays of shape (nkerns,ninds)
    mout=np.empty((len(mfit),len(inds)))
    sout=np.empty((len(mfit),len(inds)))
    
    # for each kernel
    for jj in range(len(mfit)):
    
        # for each sequence
        for i in range(len(inds)):
            
            ii=inds[i]
            x0=np.reshape(X[ii,:,:,:],(1,4,X.shape[2],1))

            pdb.set_trace()
        
            c=getMotifActivation(mfit[jj],x0)
            
            mout[jj,i]=np.max(c)
            sout[jj,i]=np.sum(c)
            
        
    out=[]
    out.append(mout)
    out.append(sout)
    
    return out



#-----------------------
def plotSeqResponse(model,exp_data,inds,mode=2,highlightRegion=None,vmax=None,data_sources=None,**kwargs):
    ''' Plot of model predictions and disection on a given sequence(s)
    model is the model
    exp_data is the experimental data dictionary.  Uses the following key entries:
        - X
        - y
        - seq_start[0]
        - seq_stop[0]
    inds is an array of indices into nseqs
    mode determines which approach to use to calc base contributions
    '''
    
    X=exp_data['X']
    y=exp_data['y']
    seq_start=exp_data['seq_start'][0]
    seq_stop=exp_data['seq_stop'][0]
    
    # parse the model name
    (tf_name,exp_num,nkerns,msize,nnact,final_layer,model_tag,doubleseq,slen)=model_create.parseModelName(model.name)
    
    # handle circ perm so that we get the correct unique entries in seq
    # if circ_perm, there will be Multiple entries for each sequence, one for each permutation
    group_size=1
    if ('circ_perm') in kwargs:
        group_size=int(kwargs.get('circ_perm')+1)    
    
    inds=np.array(inds)*group_size
    
    #create the fig and subfigs
    if ('fig' in kwargs):
        fig=kwargs.pop('fig') # not we are poping not getting
    else:
        fig=plt.figure(figsize=(28,3*len(inds)), layout='constrained')
    subfigs=fig.subfigures(len(inds),hspace=0.01)
        
    if len(inds)==1:
        subfigs=[subfigs]
        
    # get the know sites for this tf if a data_source is given
    known_sites=[]
    if data_sources != None:
        known_sites=data_sources.getTFKnownPeaks(tf_name)
    
    # loop over sequences/subfigures
    ii=0
    for i in inds:
    

        x0=np.reshape(X[i,:,:,:],(1,4,X.shape[2],1))

        if (mode==1):        
            out_dict=disectSingleSeqResponse(model,msize,x0,y[i],i)
            
            PS=out_dict['ps']
            PS=out_dict['ps']
            sout=out_dict['sout']
            # mfit=out_dict['mfit']
            # pdb.set_trace()
        elif (mode==2):
            out_dict=getMotifWeightedSeqContribution(model,x0)
            sout=out_dict['sout']
            # mfit=out_dict['mfit']
            
            PS=y[i]
        else:
            raise Exception('plotSeqResponse mode must be 1 or 2 and it was %d'%mode)
        
        # this is redundant with calls above which also return mfit
        (mfit,mfitc,biases)=getModelMotifs(model)
        
        #get highlight regions
        print('%s - %s'%(seq_start[i],seq_stop[i]))

        highlight=[]
        if highlightRegion is None:
            
            #unless otherwise direct hilight known sites if present
            if len(known_sites)>0:
                ind=(known_sites['start']>=seq_start[i]) & (known_sites['stop']<=seq_stop[i])
                temp=known_sites[ind]
                highlight=[[s-seq_start[i],e-seq_start[i]] for s,e in zip(temp['start'],temp['stop'])]
                # print('highlight: \n', highlight)
        else:
            highlight=highlightRegion
              
        plotSingleSeqResponse(PS,sout,mfit,int(i/group_size),y[i],x0,pos=[seq_start[i],seq_stop[i]],doubleseq=doubleseq,fig=subfigs[ii],bias=biases[0],highlightRegion=highlight,vmax=vmax,**kwargs)
    
        ii=ii+1
    
    # plt.subplots_adjust(bottom=0.25)
    
    # if ('savefile' in kwargs and kwargs.get('savefile')==1):
    #     filename='%s_seq_response.png'%model.name
    #     plt.savefig(filename)
        
    
    return

#-----------------------
def plotSingleSeqResponse(PS,sout,mfit,i,y,x0,pos,doubleseq=1,fs=12,fig=None,act_plot=True,show_title=True,clip=None,bias=0,vmax=None,**kwargs):
    '''Plot seq logo and motif activation heatmap for a given sequence  
    
    If doubleseq then assumes the data come from concatenated revcomp sequences
    and contributions from both halves are added.
    '''
    npl=2
    wr=np.ones((npl,))
    wr=[5] # the height of the logo

    if act_plot:
        mult=1
        if doubleseq:
            mult=2
        nrows=len(mfit)*mult+npl
        wr=wr+[2]*len(mfit)*mult  # these are the heights for the activation plots
    else:
        nrows=npl
    
    wr=wr+[1] # the height of the base sequence
    
    if (fig):
        # pdb.set_trace()
        axs=fig.subplots(nrows,1, gridspec_kw={'height_ratios': wr},sharex=True)
        # fig.subplots_adjust(hspace=0.07)        
    else:
        fig,axs=plt.subplots(nrows,1,figsize=[22,10], gridspec_kw={'height_ratios': wr},sharex=True)
        # fig.subplots_adjust(hspace=0.07) 
        
    if npl==1 and not act_plot:
        axs=[axs]

    #-- Motif activation ---
    # need to plot this first because sns.heatmap messes up the xtick formatting of prior plots
    # for some reason
    if act_plot:
        
        for j in range(len(mfit)):           
                
            # calculate the motif activation
            # this is just the convolution of m on s followed by exponentiation
            # bias needs to be passed as kwargs
            c=getMotifActivation(mfit[j],x0,**kwargs)
            c=np.reshape(c,(c.shape[0],1))
        
            # the actual plotting
            if (doubleseq):
                slend=sout.shape[2]
                slen=int(slend/2)
        
                # sns.heatmap(c[0:slen].transpose(), ax=axs[j+npl-1],vmin=8,vmax=vmax,cmap='Greens',cbar=False,yticklabels='',)
                axs[j + npl - 1].imshow(c[0:slen].transpose(), aspect='auto',vmin=8,vmax=vmax,cmap='Greens',origin='upper') 
                axs[j + npl - 1].set_yticks([])
                # for spine in axs[j + npl - 1].spines.values():
                #     spine.set_visible(False)
                
                                
                # sns.heatmap(c[range(slend-1,slen-1,-1)].transpose(), ax=axs[j+npl],vmin=8,vmax=vmax, cmap='Oranges', cbar=False, yticklabels='') 
                axs[j + npl].imshow(c[range(slend - 1, slen - 1, -1)].transpose(),aspect='auto',vmin=8,vmax=vmax,cmap='Oranges', origin='upper')

                axs[j + npl].set_yticks([])
                # for spine in axs[j + npl].spines.values():
                #     spine.set_visible(False)
                
            
            else:
                # axs[j+npl].plot(c,linestyle='-',color=cmap(j))
                sns.heatmap(c.transpose(), ax=axs[j+npl-1],vmin=8,vmax=vmax,cmap='Greens',cbar=False,yticklabels='',xticklabels='')
                
    #--- Seq Logo ---
    # axs[0] is the seq logo axs[-1] is just the sequence in grey
    cc=[0.5, 0.5, 0.5]
    refcolors={'A': cc,'T': cc, 'C': cc, 'G': cc}
    

    if (doubleseq):
        slend=sout.shape[2]
        slen=int(slend/2)
        
        # need to add the forward and reverse strand contributions 
        temp=sout[:,:,slen:slend,:]
        temp=sequence.revcomp(temp[0,:,:,0])
        temp=np.reshape(temp,(1,4,temp.shape[1],1))
        sout_combined=sout[:,:,0:slen,:]+temp


        #handle clip region.  Clip should be a range
        if clip is not None:
            sout_combined=sout_combined[:,:,clip,:]

        
        util.plot_seq_logo(sout_combined, ax=axs[0], title="", **kwargs)
        util.plot_seq_logo(abs(np.sign(sout_combined)), colors=refcolors, ax=axs[-1], title="", **kwargs)
        
        
    else:
        #handle clip region.  Clip should be a range
        if clip is not None:
            sout=sout[:,:,clip,:]

        
        util.plot_seq_logo(sout, ax=axs[0], title="", **kwargs)
        util.plot_seq_logo(abs(np.sign(sout)), colors=refcolors, ax=axs[-1], title="", **kwargs)

    # format the title
    if (len(y)==1):
        if show_title:
            axs[0].set_title("Position=[%d, %d], NormalizedPeak Height = %0.3f"%(pos[0],pos[1],y),fontsize=fs)
    else:
        if show_title:
            axs[0].set_title("Position=[%d, %d], Normalized Peak Height = %0.2f"%(pos[0],pos[1],np.mean(y)))
    

    axs[0].spines['bottom'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)

    
    axs[-1].spines['top'].set_visible(False)
    axs[-1].spines['right'].set_visible(False)
    axs[-1].spines['left'].set_visible(False)
    axs[-1].set_yticks([])

    if kwargs.get('show_pos',0)==0:
        axs[0].get_xaxis().set_ticks([])
        axs[-1].spines['bottom'].set_visible(False)


    
                
    return

#-----------------------
def exportSeqResponseGV(fname,model,X,y,seq_start,seq_stop,seq_strand,th):
    # plot of model predictions and disection on a given sequence(s)
    # X is a tensor of shape (nseqs,4,slen,1)
    # inds is an array of indices into nseqs
    
    inds=np.array([i for i,v in enumerate(y) if v >th])
    print(len(inds))

    sinds=np.argsort(-y[inds])
    inds=inds[sinds]


    #% #open the gff file  
    f=createGFFFile(fname)

    
    for i in inds:
    
        print(i)
        print(y[i])

        x0=np.reshape(X[i,:,:,:],(1,4,X.shape[2],1))
        
        # DS,PSmut,PS,sout,mfit=disectSingleSeqResponse(model,x0,y[i],i)
        out_dict=disectSingleSeqResponse(model,x0,y[i],i)
        
        PS=out_dict['ps']
        DS=out_dict['ds']
        PS=out_dict['ps']
        sout=out_dict['sout']
        mfit=out_dict['mfit']
    
    
        #% write the full length sequence region feature
        # pdb.set_trace()
        writeGFFFile(f,'cnn_seq','seq_%d_%f'%(i,PS),list([seq_start[0][i]]),list([seq_stop[0][i]]),[0],list(seq_strand[i][0]))
        
        #% Write out the critical bases
        
        #find all the critical bases
        ind_bases=np.array([i for i,v in enumerate(DS) if v >0.001])
        for jj in ind_bases:
            li= [i for i,v in enumerate(sout[0,:,jj,0]) if v >0]
            l=sequence.letters[li[0]]
            writeGFFFile(f,'pos_base','pos_%s_%d_%d_%f'%(l,i,jj,DS[jj]),list([seq_start[0][i]+jj]),list([seq_start[0][i]+jj]),[DS[jj]],list(seq_strand[i][0]))
            
        ind_bases=np.array([i for i,v in enumerate(DS) if v <-0.001])
        for jj in ind_bases:
            li= [i for i,v in enumerate(sout[0,:,jj,0]) if v <0]
            l=sequence.letters[li[0]]
            writeGFFFile(f,'neg_base','pos_%s_%d_%d_%f'%(l,i,jj,DS[jj]),list([seq_start[0][i]+jj]),list([seq_start[0][i]+jj]),[DS[jj]],list(seq_strand[i][0]))
        
        # the motif hits
        for j in range(len(mfit)):
            offset=math.floor(mfit[j].shape[1]/2)
            c=getMotifActivation(mfit[j],x0)
            ind_c=np.array([i for i,v in enumerate(c) if v >0])
            
            for jj in ind_c:
                # pdb.set_trace()
                writeGFFFile(f,'kernal_%d'%(j),'kernal_%d_%d_%d_%f'%(i,j,jj,c[jj]),[seq_start[0][i]+jj-offset],[seq_start[0][i]+jj-offset+mfit[j].shape[1]],[c[jj]],['+'])

    
    #% close the gff file
    f.close()
    return

#-----------------------
def exportWigFile(fname,val,winsize,stepsize=1,startpos=1):
    # write the val to a simple wig file and convert it to a TDF
    # val is currently only a vector one number per position which will be exported as for,rev, and total coverage
    # the first position is startpos
    # and each subsequent position is +stepsize
    
    # open file and print out header
    f = open(fname, "w")
    f.write('track type=wiggle_0 graphType=bar name=testwig\n')
    f.write('variableStep chrom=U00096\t\n')
    pos=startpos
    for i in range(len(val)):
        # pdb.set_trace()
        f.write('%d\t%f\t%f\t%d\n' %(int(pos+winsize/2),val[i],val[i],val[i]))
        pos=pos+stepsize
    f.close()
    

#-----------------------
def exportTDFFile(fname,val,winsize,stepsize=1,startpos=1):
    # write the val to a simple wig file AND convert it to a TDF, THEN REMOVE WIG
    # val is currently only a vector one number per position which will be exported as for,rev, and total coverage
    # the first position is startpos
    # and each subsequent position is +stepsize
    
    # open file and print out header
    f = open(fname, "w")
    f.write('track type=wiggle_0 graphType=bar name=testwig\n')
    f.write('variableStep chrom=U00096\t\n')
    pos=startpos
    for i in range(len(val)):
        # pdb.set_trace()
        f.write('%d\t%f\t%f\t%d\n' %(int(pos+winsize/2),val[i],val[i],val[i]))
        pos=pos+stepsize
    f.close()
    
    # now convert to a TDF
    IGV.toTDF(fname)
    
    # now delete the wig file
    os.system('rm %s'%fname)

#-----------------------
def createGFFFile(fname):
    # open file and print out header
    f = open(fname, "w")
    f.write('##gff-version 3\n')
    f.write('#chromossome\tsource\ttype\tstart\tend\tscore\tstrand\tphase\tnotes\n')

    return f

#-----------------------
def writeGFFFile(f,ftype,id,start_pos,stop_pos,score,strand):
    # Chromosome is for ecoli by default
    # ftype is a string with the feature type
    # start, stop, score, are lists of numbers
    # strand is a list of '+'/'-'
 
    for i in range(len(start_pos)):
        # pdb.set_trace()
        f.write('%s\t%s\t%s\t%d\t%d\t%f\t%s\t.\tID=%s\n' %('U00096',ftype,ftype,start_pos[i],stop_pos[i],score[i],strand[i],id))
    
    
    return


#-----------------------
def disectMultiSeqResponse(model,X,win=0):
    # (DS)=disectMultiSeqResponse(model,X)
    # plot of model predictions and disection on a given sequence
    # X is a tensor of shape (numseq,4,slen,1)
    
    
    DSall=calcBaseContributionMulti(model,X,win=win)
        
    return DSall

#-----------------------
def disectSingleSeqResponse(model,msize,x0,y,i):
    # plot of model predictions and disection on a given sequence
    # x0 is a tensor of shape (1,4,slen,1)

    (mfit,mfitc,biases)=getModelMotifs(model)

    DS,PSmut,PS,sout=calcBaseContribution(model,x0,show_neg=1)
    
    out={}
    out['ds']=DS
    out['psmut']=PSmut
    out['ps']=PS
    out['sout']=sout
    out['mfit']=mfit
    
    return out

#-----------------------
def getMotifsActivationGenome(model,**kwargs):
    # calculate the activation of motif m on genome
    
    biases=[]
    if 'biases' in kwargs:
        biases=kwargs.get('biases')
    
    (mfit,mfitc,biases)=getModelMotifs(model)
    genome=sequence.load_genome_matfile()
    genome=np.reshape(genome,(1,4,genome.shape[1],1))
    
    clist=[]
    for j in range(len(mfit)):
        if 'cmin' in kwargs:
            cmin=kwargs.get('cmin')
        else:
            cmin=coverage.minEnergy(mfit[j])
        
        if (biases==[]):
            clist.append(getMotifActivation(mfit[j],genome,init=cmin))
        else:
            clist.append(getMotifActivation(mfit[j],genome,init=cmin, bias=biases[j]))
    
    return clist


#-----------------------
def getMotifWeightedSeqContribution(model,s,do_doublseq=0,kernel_ind=None,**kwargs):
    '''At every seq position, calculate the sum of the w*seq*motif_activation (exp) summed over every motif hit that overlaps that position  
    every position will overlap mlen motif hits except those at the end of the sequences  
    s is assumed to be shape (1,4,slen,1)  
    
    Returns a dictionary with keys
    
    sout - a weighted one-hot encoding of shape (1,4,slen,1)
        where at each position, only the base at that position is non-zero
        but the actual value of that non-zero entry is the weight contribution
        
    mfit - the matrix
    
    if kernel_ind is not None then only use the indicated kernel dimension
    
    cc - TBD
    
    '''
    
    (mfit,mfitc,biases)=getModelMotifs(model)
    
    if kernel_ind is not None:
        mfit=[mfit[kernel_ind]]
        mfitc=[mfitc[kernel_ind]]
        biases=[biases[kernel_ind]]
    
    # (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=model_create.parseModelName(model.name)
    
    # used to keep track of the weighted nucleotides
    ss_sum=np.reshape(copy.deepcopy(s),(4,s.shape[2])).astype(float)
    if (do_doublseq):
        ss_sum=ss_sum[:,0:int(ss_sum.shape[1]/2)]
    
    
    for m in mfit:
        ss=np.reshape(copy.deepcopy(s),(4,s.shape[2]))
        c=coverage.matConvolve(m,ss,**kwargs)
        
        c=np.exp(c)
        
        # c[offset]=> c for a motif hit that starts at position 0 - so covers 0 to mlen-1
        offset=math.floor(m.shape[1]/2)
        
        cc=np.zeros(c.shape)
        # at every position in c starting at offset and going until slen-offset-1 
        for j in range(offset,len(c)-offset):
           
            # look at all positions covered by a hit here
            for jj in range(j-offset,j-offset+m.shape[1]):
                # print(jj) # the position on the seq
                # print(jj-(j-offset)) # the position on the motif of this position on the seq for the hit at c[j]
                
                # sum up w[]*s[] (the right one) * c[j]
                temp=c[j]*sum(ss[:,jj]*m[:,jj-(j-offset)])
                cc[jj]=cc[jj]+temp
                
    
        slend=cc.shape[0]
        slen=int(slend/2)
    
        
        if (do_doublseq):
            # need to add up both halves after reving the second half
            forw=cc[0:slen]
            rev=cc[range(slend-1,slen-1,-1)]
            cc=forw+rev
            
        
        for i in range(0,ss_sum.shape[1]):

            ss_sum[:,i]=ss_sum[:,i]*cc[i] 
    
    
    ss_sum=np.reshape(ss_sum,(1,4,ss_sum.shape[1],1))
    out={}
    out['cc']=cc
    out['sout']=ss_sum
    out['mfit']=mfit
    

    return out


#-----------------------
def getMotifActivation(m,s,**kwargs):
    '''calculate the activation of motif m on seq s  
    this is just the convolution of m on s followed by exponentiation  
    s is assumed to be shape (1,4,slen,1)  
    m is assumed to be shape (4,mlen)  
    if bias is provided in kwargs, then bias added before exp   
    '''
    
    ss=np.reshape(s,(4,s.shape[2]))
    c=coverage.matConvolve(m,ss,**kwargs)
    
    if 'bias' in kwargs:
        c=c+kwargs.get('bias')
    
    c=np.exp(c)
    
    return c

#-----------------------
def getKernelInfo(model,layer_name='conv'):
    """returns the number and size of kernels from the layer named "conv"
    # (nkerns,ksize)=getKernelInfo(model)
    TODO - move to model_disect"""

    l=model.get_layer(layer_name)
    lw=l.weights[0]
    nkerns=lw.shape[3]    
    ksize=lw.shape[1]

    return nkerns,ksize

#-----------------------
def getModelMotifs(model,layer_name='conv'):
    """returns the motif models from the convolution layer of model
    lnum is index into model.weights
    ksize is kernal/modif length
    (mfit,mfitc,biases)=getModelMotifs(model)
    TODO - move to model_disect"""
    
    l=model.get_layer(layer_name)
    allbfit=l.weights[0]
    ksize=allbfit.shape[1]
    
    if len(l.weights)>1:
        biases=l.weights[1].numpy()
    else:
        biases=np.zeros((1,))
    
    # print(allbfit.shape)
    mfitc=[]
    mfit=[]
    for i in range(allbfit.shape[3]):
        
        b=(allbfit[:,:,:,i])
        b=np.reshape(b,(4*ksize,1))
        
        m=sequence.deflatten(b)
        mfit.append(m)
        
        mc=sequence.revcomp(m)
        mfitc.append(mc)
    
    
    return mfit,mfitc,biases

def exportModelMotifJSON(model):
    '''Export a model motif an bias as a JSON string'''
    
    (mfit,mfitc,biases)=getModelMotifs(model)
    wm_df=pd.DataFrame(mfit[0])
    wm_df.index=sequence.letters
    
    d={}
    d['weight_matrix']=wm_df.to_dict(orient='index')
    d['bias']=float(biases[0])
    
    json_str=json.dumps(d,indent=4)
    
    return json_str

def importModelMotifJSON(fname):
    '''import a model wm and bias from json produced by
    exportModelMotifJSON
    
    Return a weight matrix as numpy.ndarray and bias as numpy.float32
    
    wm is shape (4, ksize,1,1)
    bias is shape (1,)
    
    
    '''
    with open(fname) as f:
        data = json.load(f)
    
    # --- Bias ---
    bias = np.array(data['bias'], dtype=np.float32).reshape(1)   # shape (1,)
    
    # --- Weight matrix ---
    wm_df = pd.DataFrame.from_dict(data['weight_matrix'], orient='index')
    wm = wm_df.to_numpy(dtype=np.float32)   # e.g. shape (4,25)
    
    # reshape to (1,4,25,1)
    wm = wm.reshape(wm.shape[0], wm.shape[1], 1, 1)
        
    
    return wm, bias
    

#-----------------------
def calcBaseContribution(model,s,**kwargs):
# Motivated by Aliphani 2015
# model is a keras model
# s is expected to be a 4 dim tensor w/shape = [1,4,slen,1]

    
    # Run model on native sequence to get P(S) = PS
    PS=model(s).numpy()
    PSmut=np.zeros((s.shape[2]))
    DS=PSmut.copy()
    # sout=s.copy()
    sout=s.astype(float)
    
    maxmut=PS.clip
    if 'show_neg' in kwargs:
        if kwargs.get('show_neg')==1:
            maxmut=1

    
    
    #For every position
    for i in range(s.shape[2]):
        smut=s.copy()
        
        # remove the base at this position
        smut[:,:,i,:]=np.zeros(smut[:,:,0,:].shape)
        
        #Run the model on the modified seq
        
        #Determine the P(Sij) PSmut[j,i] - i is position, j= the base selected
        # util.plot_seq_logo(smut)
        PSmut[i]=model(smut).numpy()
        
        # The sensitivity DS[i,j] 
        # This is SMALLER if a base causes the score to DECREASE
        DS[i]=1-PSmut[i].clip(min=0,max=maxmut)/PS.clip(max=1) #%%*np.max((0,PS,PSmut[j,i]))
   
        # pdb.set_trace()
   
        sout[:,:,i,:]=sout[:,:,i,:]*DS[i]
    
    
    return DS,PSmut,PS,sout

#-----------------------
def calcBaseContributionMulti(model,s,win=0,**kwargs):
# Motivated by Aliphani 2015
# model is a keras model
# s is expected to be a 4 dim tensor w/shape = [nseq,4,slen,1]
# if win>0 then +/-win bases on either side of central base are also zeroed
#      so win=2 means that 5 bp are zeroed
# faster version for multiple sequences that only returns the DS saliency score
    
    # Run model on native sequence to get P(S) = PS
    PS=model(s).numpy()
    DS=np.zeros((s.shape[0],s.shape[2])) # number of seqs by slen
    
    maxmut=PS.clip(max=1)
    if 'show_neg' in kwargs:
        if kwargs.get('show_neg')==1:
            maxmut=1

    
    
    #For every position
    for i in range(s.shape[2]):
        smut=s.copy()
        
        # remove the base at this position(s)
        for ii in range(max(0,i-win),min(i+win,s.shape[2])):
            smut[:,:,ii,:]=np.zeros(smut[:,:,0,:].shape)
        
        #Run the model on the modified seq
        
        #Determine the P(Sij) PSmut[j,i] - i is position, j= the base selected
        # util.plot_seq_logo(smut)
        PSmut=model(smut).numpy()

        # The sensitivity DS[i,j] 
        # This is SMALLER if a base causes the score to DECREASE
        ds=1-PSmut.clip(min=0,max=maxmut)/PS 
        ds=np.reshape(ds,(ds.shape[0],)) 
        DS[:,i]=ds
        
    
    return DS

#-----------------------
def calcMutationMap(model,s):
# Motivated by Aliphani 2015
# model is a keras model
# s is expected to be a 4 dim tensor w/shape = [1,4,slen,1]

    
    # Run model on native sequence to get P(S) = PS
    PS=model(s).numpy()
    PSmut=np.zeros((4,s.shape[2]))
    DS=PSmut.copy()
    
    #For every position
    for i in range(s.shape[2]):
        smut=s.copy()
        
        #For all 4 nucleotides
        for j in range(4):
            #modify the sequence
            smut[:,:,i,:]=np.zeros(smut[:,:,0,:].shape)
            smut[:,j,i,:]=1
        
            #Run the model on the modified seq
            
            #Determine the P(Sij) PSmut[j,i] - i is position, j= the base selected
            # util.plot_seq_logo(smut)
            PSmut[j,i]=model(smut).numpy()
            
            # The sensitivity DS[i,j] 
            # This is SMALLER if a base causes the score to DECREASE
            DS[j,i]=PSmut[j,i]/PS #%%*np.max((0,PS,PSmut[j,i]))
   
    
    return DS,PSmut,PS

#-----------------------
def createSeqTileSet(seq,tilelen,stepsize=1,**kwargs):
    '''create an Tensor Array of tiles of length tilelen over a sequence
    move each tile by stepsize
    The output will be shape (ntiles,4,tilelen,1)
    e.g. a set of ntiles tiles of 4xtilelen
    ntiles is determined by how many steps can fit in seqlen
    
    If doubleseq==1
    then each tile is rv and concat
    so the output will be shape (ntiles,4,2*tilelen,1)
    
    gpos return is the start position of each tile
    '''
    
    ntiles=seq.shape[1]-(tilelen-1)
    ntiles=int(np.ceil(ntiles/stepsize))
    print(ntiles)
    
    X=np.zeros((ntiles,4,tilelen))
    
    start_pos=0
    pos=[]
    for j in range(ntiles):
        stop_pos=start_pos+tilelen
        # print(start_pos,stop_pos)
        
        
        s=seq[:,start_pos:stop_pos]
        X[j,:,:]=s
    
        pos.append(start_pos)
        start_pos=start_pos+stepsize
    
    # need to check to see if we are making a doublseq tile set
    # each seq RC and concatenated with itself
    if 'doubleseq' in kwargs:
        if kwargs.get('doubleseq')==1:
            # pdb.set_trace()
            X=sequence.concatenate_revcomp(X)        

    # need to reshape as a tensor
    slen=X.shape[2]
    X=np.reshape(X,(ntiles,4,slen,1))

    pos=np.array(pos)
    
    return X,pos

#-----------------------
def loadMatlabData(fname):
    
    data=scipy.io.loadmat(fname)
    cov=data['data']['cov'][0][0][0]
    seq=data['data']['seqmatrix'][0][0]
    seq=reshapeMatSeq(seq)
    
    # index of first random sequence
    ifirstneg=int(data['data']['ifirstneg'][0][0]-1)
    
    
    #positions of sequences
    seq_start=data['data']['start'][0][0]
    seq_stop=data['data']['stop'][0][0]
    seq_strand=data['data']['strand'][0][0][0]

    
    
    return cov,seq,seq_start,seq_stop,seq_strand,ifirstneg,data



#-----------------------
def reshapeMatSeq(matseq):

    s=matseq    
    
    seq = np.array([e.tolist() for e in s.flatten()]).reshape(s.shape[1],4,-1)    

    return seq



# #-----------------------
# def concatenate_revcomp(sequences):
#     #input is shape nseq, 4, slen
#     #output is shape nseqm 4, 2*slen
#     out = np.concatenate((sequences,sequence.revcomp_multi(sequences)),axis=2)
#     return out


#-----------------------
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr, spearmanr

def print_accuracy(y_true,y_pred):
    #inputs are coverage values and model predictions
    #Requires Installation of SKLearn to work
    r2 = r2_score(y_true,y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
  
    pearson = pearsonr(y_true,y_pred)
    spearman = spearmanr(y_true,y_pred)
    
    print('Mean Absolute Error: %f' % (mae))
    print('Mean Squared Error: %f' % (mse))
    print('Pearson Correlation: %f' % (pearson[0]))
    print('Spearman Correlation: %f (p = %f)' % (spearman.correlation,spearman.pvalue))
    print('R2 Score: %f' % (r2))
    
    return mae,mse,r2,pearson[0],spearman.correlation,spearman.pvalue



#-----------------------
def trainingDataSubset(X,y,start_ind,stop_ind):
    # given an X,y training set,generate a subset from index start_ind to stop_ind

    X2=X[start_ind:stop_ind,:,:,:]
    y2=y[start_ind:stop_ind]
    
    return (X2,y2)

#-----------------------
def getNonPermIndices(circ_perm,ifirstneg,dlength):
    '''Returns indices into a data of dlength long
    given ifirstneg - the index of the first neg data
    and circ_perm - the number of circ perms added to pos data
    so returns
    
    [0:ifirstneg:circ_perm] + [ifirsneg:dlength-1]'''
    
    inds = list(range(0,ifirstneg,circ_perm+1))+list(range(ifirstneg,dlength))
    return inds

def createCircPermIndices(inds,circperm=2):
    '''Given an np vector (N,) of indices for the positive
    samples without circ perm, return the corresponding circ 
    perm indices.
    
    For any index x, this is y = [(circperm+1)*x,(circperm+1)*x+1,(circperm+1)*x+2]
    
    So if circperm==2 (defalt value)
    And inds=[0,2]
    
    Then returns
    
    [0,1,2,6,7,8]'''
    
    temp=inds
    temp2=np.repeat(temp*(circperm+1),circperm+1)
    temp3=temp2+np.tile([0, 1, 2], len(inds))
    
    return temp3

#-----------------------
def addCircPerm(seq,cov,seq_start,seq_stop,ifirstneg,shift):
    """add circpermuted sequences to the positive data
    for each seq, we permuate +/- shift
    permuted sequences are added after each sequence
    so original sequences would be 0,1,2,etc
    after augmentation it would be 0,0+,0-,1,1+.1-,etc...
    same for coverage"""


    # the positive sequence and coverages 
    seqp=seq[0:ifirstneg,:]
    covp=cov[0:ifirstneg]
    
    # circ perm seqs
    seqcpP=sequence.circ_permute_seqs(seqp, shift)
    seqcpN=sequence.circ_permute_seqs(seqp, -shift)
    
    
    # init output data with new sizes
    ifirstneg_new=3*(ifirstneg)
    newlen=seq.shape[0]+2*(ifirstneg)
    seq_new=np.zeros(shape=(newlen,4,seq.shape[2]))
    seq_start_new=np.zeros(shape=(1,newlen))
    seq_stop_new=np.zeros(shape=(1,newlen))
    if (len(cov.shape)==1):
        cov_new=np.zeros(shape=(newlen,))
    else:
        cov_new=np.zeros(shape=(newlen,cov.shape[1]))

    
    # interleave pos seqs and cov into new seq and cov
    for i in range(0,ifirstneg_new,3):
        ii=int(i/3)
        seq_new[i,:,:]=seq[ii,:,:].copy()
        seq_new[i+1,:,:]=seqcpP[ii,:,:].copy()
        seq_new[i+2,:,:]=seqcpN[ii,:,:].copy()
        
        cov_new[i]=cov[ii].copy()
        cov_new[i+1]=cov[ii].copy()
        cov_new[i+2]=cov[ii].copy()
                
        seq_start_new[0,i]=seq_start[0,ii].copy()
        seq_start_new[0,i+1]=seq_start[0,ii].copy()
        seq_start_new[0,i+2]=seq_start[0,ii].copy()
        
        seq_stop_new[0,i]=seq_stop[0,ii].copy()
        seq_stop_new[0,i+1]=seq_stop[0,ii].copy()
        seq_stop_new[0,i+2]=seq_stop[0,ii].copy()
        
        
        # print(i,ii)
        
    # copy all the negative seqs and covs into new seq and cov
    for i in range(ifirstneg,seq.shape[0]):
        ii=i+2*(ifirstneg)
        
        seq_new[ii,:,:]=seq[i,:,:].copy()
        cov_new[ii]=cov[i].copy()
        seq_start_new[0,ii]=seq_start[0,i].copy()
        seq_stop_new[0,ii]=seq_stop_new[0,i].copy()
        
        # print(ii,i)
    
        
    seq_start_new=seq_start_new.astype(int)
    seq_stop_new=seq_stop_new.astype(int)
    
    # pdb.set_trace()
        
    return seq_new,cov_new,seq_start_new,seq_stop_new,ifirstneg_new

#-----------------------
def processExperiment(data,exp_num,maxrandsamps=10000,mode='independent',double_seq=1,length_seq_side=250,logy=0, data_sources=None, **kwargs):
    """Main code for generating training data - returns an exp_data object
    TODO This should be moved to seqcovdb and renamed load_training_data"""
    # data is an object of class SeqCov

    fimo_neg=0
    if ('fimo_neg' in kwargs):
        fimo_neg=kwargs.get('fimo_neg')

    fimo_non_neg=0
    if ('fimo_non_neg' in kwargs):
        fimo_non_neg=kwargs.get('fimo_non_neg')
    
    real_cov = kwargs.get('real_cov', 0)

    wig_runs, wig_file, genome_mat = None, None, None
    if data_sources != None:
        wig_runs   = data_sources.get('wig_runs',   None)
        wig_file   = data_sources.get('wig_file',   None)
        genome_mat = data_sources.get('genome_mat', None)
        

    datainfo=data.get_info()

    # Load genomewide coverage for this experiment and mask it as necessary for the promoter
    if type(exp_num)==list:
        gcov=[]
        gcov_unmasked = []
        print('exp_num', exp_num)
        for e in exp_num:
            g=data.load_gw_cov(e, wig_runs=wig_runs, wig_file=wig_file)
            gcov_unmasked.append(g)
            
            # use masks to mask coverage here
            prom=datainfo['Promoter'][e]
            mod=util.prom2mod(prom)
            (masks)=browser_util.getBrowserMasks(data.tf_name,mod,'chip', data_sources=data_sources)
           # print('masks, ', (masks))
            for mask in masks:
                #print(type(g[mask[0]:mask[1]])) #Commented out by Keith
                g = np.array(g)# Added by Keith For FileDataType works for both
                g[mask[0]:mask[1]]=0
        
            gcov.append(g)
        
        gcov=np.array(gcov).transpose()
        gcov_unmasked_means = np.mean(np.array(gcov_unmasked).transpose(), axis=0)
        
    else:
        gcov=data.load_gw_cov(exp_num, wig_runs=wig_runs, wig_file=wig_file)
        gcov_unmasked_means = np.mean(gcov, axis=0)
        
        # use masks to mask coverage here
        prom=datainfo['Promoter'][exp_num]
        mod=util.prom2mod(prom)
        (masks)=browser_util.getBrowserMasks(data.tf_name,mod,'chip', data_sources=data_sources)
        for mask in masks:
            gcov[mask[0]:mask[1]]=0

    # Load experiment
    (cov,seq,seq_start,seq_stop,ifirstneg)=data.load_experiment(exp_num,mode,nnegative = maxrandsamps, 
                                                                length_seq_side=length_seq_side, 
                                                                fimo_neg=fimo_neg,fimo_non_neg=fimo_non_neg, 
                                                                real_cov=real_cov, gcov=gcov, 
                                                                gcov_unmasked_means=gcov_unmasked_means, 
                                                                genome_mat=genome_mat)

    # circ permuted pos seqs
    addcircperm=0
    if ('addcircperm' in kwargs):
        addcircperm=kwargs.get('addcircperm')
    if (addcircperm>0):
        (seq,cov,seq_start,seq_stop,ifirstneg)=addCircPerm(seq,cov,seq_start,seq_stop,ifirstneg,addcircperm)


    # motif size and number of samples
    msize=seq.shape[2]
    nsamps=seq.shape[0]
    
    # seq are the original sequences, slen are the lengths of these
    # X is the set of sequences for training, xslen are the lengths of these
    # process double_seq (revconcat each seq to itself) if necessary
    # otherwise X=seq
    s=seq
    slen=seq.shape[2]

    if double_seq==1:
        #rc and concat seqs
    
        ss=sequence.concatenate_revcomp(seq)
        sslen=ss.shape[2]
        # reshape input
        X=np.reshape(ss,(nsamps,4,sslen,1))
        xslen=sslen
    else:
        X=np.reshape(s,(nsamps,4,slen,1))
        xslen=slen
    
    # process the target coverages
    y2=cov
    if (logy):
        # #TESTING LOG COV
        if not real_cov:
            y2[ifirstneg:len(y2)]=1
        y=y2/np.amax(y2)
        # y=np.log10(y2*10)
        # pdb.set_trace()
    else:
        #rescale y to be [+/-baseline,1]
        # baseline=np.median(y2[ifirstneg:len(y2)])
        # y2=y2-baseline
        if not real_cov:
            y2[ifirstneg:len(y2)]=0  # Necessary if points already set to 0 in seqcovdb?
        if (len(y2.shape)>1):
            y=y2/np.max(y2,axis=0)
        else:
            y=y2/np.amax(y2)

    exp_data= {}
    exp_data['cov']=cov
    exp_data['seq']=seq
    exp_data['seq_start']=seq_start
    exp_data['seq_stop']=seq_stop
    exp_data['ifirstneg']=ifirstneg
    exp_data['slen']=slen
    exp_data['X']=X
    exp_data['xslen']=xslen
    exp_data['y']=y
    
    exp_data['gcov']=gcov
    exp_data['circ_perm']=addcircperm
    exp_data['run_id']=data.get_info()['run_id'][exp_num]
    exp_data['sample_id']=data.get_info()['sample_id'][exp_num]
        
    return exp_data
    

#-----------------------
def concatData(Xlist,ylist):
    # usage: (X,y)=tf_util.concatData((X1,X2,...),(y1,y2,...))
    
    X=np.concatenate(Xlist)
    y=np.concatenate(ylist)
    
    return X,y



#-----------------------
def getDataWeights(y,ifirstneg,scale=20):
    """Create weights to scale positive training data"""
    w = np.ones(shape=(len(y),))
    
    w[0:ifirstneg]=1/y[0:ifirstneg] * scale
    
    
    return w

#-----------------------
def splitPosNegData(X,y,ifirstneg):
    # X is shape (nsamps,4,slen,1)
    # y is shape (nsamps,:)
    
    X_pos=[]
    X_neg=[]
    y_pos=[]
    y_neg=[]
    
    X_pos=X[0:ifirstneg,:,:,:]
    y_pos=y[0:ifirstneg]
    
    
    X_neg=X[ifirstneg:len(y),:,:,:]
    y_neg=y[ifirstneg:len(y)]
    
    
    return X_pos,X_neg,y_pos,y_neg
    

#-----------------------
def load_data(path,maxrandsamps,revcomp=True):
    #DEPRECATED - NEED TO USE SEQCOV AND TF_UTIL.PROCESS EXPERIMENT
    #Load in the mat file
    (cov,seq,seq_start,seq_stop,seq_strand,ifirstneg,data)=loadMatlabData(path)


    # motif size
    msize=seq.shape[2]
    slen=seq.shape[2]


    # only use the first maxrandsamps random seqs for now
    lastseq=ifirstneg+maxrandsamps
    seq=seq[0:lastseq,:]
    cov=cov[0:lastseq]
    seq_start=seq_start[:,0:lastseq]
    seq_stop=seq_stop[:,0:lastseq]

    nsamps=seq.shape[0]
    y2=cov
    s=seq

    #rescale y to be [0,1]
    baseline=np.mean(y2[ifirstneg:len(y2)])
    y2=y2-baseline
    y=y2/np.amax(y2)
    
    
    # reshape input
    X=np.reshape(s,(nsamps,4,msize,1))
    #Line for adding the concatenated reverse complement sequences
    if revcomp:
        X = sequence.concatenate_revcomp(X)
    #convert to tensor object
    X = tf.constant(value=X, name = 'X', dtype=tf.float32)
    
    return X,y,s,msize,slen,cov,seq,seq_start,seq_stop,seq_strand,ifirstneg,data

#-----------------------
def getNumKernels(model):
    """Return the number of kernels in the conv layer
    TODO - move to model_disect"""
    
    l=model.get_layer('conv')
    nkerns=l.get_config().get('filters')
    
    return nkerns





#-----------------------
def genome_prediction(model,stepsize=10,**kwargs):
    ''' Model prediction on ecoli genome 
    (gpred,slen,gset,gpos)=genome_prediction(model,stepsize,**kwargs)
    
    calls createSeqTileSet to create sequence tiling of the genomome
    
    gset is tiling sequences - shape (ntiles,4,tilelen,1) e.g. a set of ntiles tiles of 4xtilelen
    gpos is the middle position of each tile
    '''
    
    data_sources = kwargs.get('data_sources', None)
    
    genome_mat = data_sources.get('genome_mat', None) if data_sources else None
            
    if genome_mat:
        GENOMEFILE = CONFIG.data_dir + genome_mat
    else:
        GENOMEFILE = None
    
    #%load the ecoli genome
    genome=sequence.load_genome_matfile(fname=GENOMEFILE)
    
    # get the expected sequence length from the model
    slen=model.input_shape[2] #The length of the actual sequence on the Genome
    xslen=slen  # The length of a sequence the model expects]
    
    # if we are working with doubleseq, this length is havlved
    if 'doubleseq' in kwargs:
        if kwargs.get('doubleseq')==1:
            slen=int(xslen/2) #The actual sequence is 1/2 the concatenated double sequence
    
    #% create genome wide tiling path if not optionally passed in
    if 'gset' in kwargs:
        gset=kwargs.get('gset')
        gpos=kwargs.get('gpos')
    else:
        (gset,gpos)= createSeqTileSet(genome, slen,stepsize=stepsize,**kwargs)
    print(gset.shape)
    
    # pdb.set_trace()
    
    
    #% Predict on genome wide tiling path
    gpred=model(gset)
    gpred=np.reshape(gpred,(gset.shape[0],gpred.shape[-1]))
    
    plotfig=1;
    if 'plotfig' in kwargs:
        plotfig=kwargs.get('plotfig')
        
    if (plotfig==1):
        if (gpred.shape[1]==1):
            fig,axt=plt.subplots(gpred.shape[1],1,figsize=(8,11))
            axs=[]
            axs.append(axt)
        else:
            fig,axs=plt.subplots(gpred.shape[1],1,figsize=(8,11))
            
        plt.subplots_adjust(hspace=0.6)
        
        for i in range(gpred.shape[1]):
            axs[i].plot(np.arange(0,genome.shape[1]-slen+1,stepsize),gpred[:,i]/np.max(np.abs(gpred[:,i])),'.')
            axs[i].axhline(y=0, color='k', linestyle='-')
            axs[i].set_ylabel('Normalized Output')
            axs[i].set_title('Output %d'%i)
        
        axs[-1].set_xlabel('Genome Position')
        
        if 'title' in kwargs:
            fig.suptitle(kwargs.get('title'))    
        
        plt.show()
        
    
    return (gpred,slen,gset,gpos)
   
#-----------------------
def genomeTileAve(val,pos,winsize):
    #val is one number per genome position
    # calculates the ave of val over window size centered on each pos
    
    aveval=np.zeros((pos.shape[0],))
    
    for i in range(pos.shape[0]):
        aveval[i]=np.mean(val[pos[i]-winsize:pos[i]+winsize,])
    
    aveval[np.isnan(aveval)] = 0
    return aveval
    
#-----------------------
def genomeTileMax(val,pos,winsize):
    #val is one number per genome position
    # calculates the max of val over window size centered on each pos
    
    aveval=np.zeros((pos.shape[0],))
    
    for i in range(pos.shape[0]):
        if len(val[pos[i]-winsize:pos[i]+winsize,]>0):
            aveval[i]=np.max(val[pos[i]-winsize:pos[i]+winsize,])
    
    aveval[np.isnan(aveval)] = 0
    return aveval

#-----------------------
def gc_pred(genome_path,model_name,stepsize,doubleseq=1,plot=True):
    #Load the model
    model = model_create.loadModel(model_name)
    #%load the ecoli genome
    genome=sequence.load_genome_matfile(genome_path)
    
    # # get the expected sequence length from the model
    slen=model.input_shape[2] #The length of the actual sequence on the Genome
    xslen=slen  # The length of a sequence the model expects]
    
    # # if we are working with doubleseq, this length is havlved
    if doubleseq == 1:
        slen=int(xslen/2) #The actual sequence is 1/2 the concatenated double sequence
    
    # #% create genome wide tiling path
    gset= createSeqTileSet(genome, slen,stepsize=stepsize,doubleseq = doubleseq)

    
    convs = model_disect.getConvModel(model)



    k_num = getNumKernels(model)
    #predict the output of the conv layer on the whole genome
    preds = convs(gset)
    preds = tf.reshape(preds,shape=(preds.shape[0],k_num))
    
    # gc_content = sequence.calc_gc(g)
    if doubleseq == 1:
        gc_content = sequence.calc_gc(gset[:, :slen, :, 0])
        
    else:
        gc_content = sequence.calc_gc(gset[:, :, :, 0])
    #Get Kernel Scores on genome-wide tiling path
    k_num = getNumKernels(model)
    corr_save = []
    for num in range(k_num):
        correlation = np.corrcoef(preds[:,num],gc_content)
        corr_save.append(correlation)
     
        
    fmap_max=np.max(preds[:,0])
    fmap_min=np.min(preds[:,0]) 
    if plot:
        

        plt.figure(figsize=(5,14))
        plt.tight_layout()
        # plt.subplots_adjust(wspace=1.2)
        for num in range(k_num):
            fmap_max=np.max(preds[:,num])
            fmap_min=np.min(preds[:,num]) 
            norm_val = max(abs(fmap_min),abs(fmap_max))
            
            plt.subplot(k_num,1,num+1)
            plt.scatter(gc_content,(preds[:,num] / norm_val))
            plt.ylim([-1,1])
            plt.xlabel('GC Content')
            plt.ylabel('Kernel %d' %(num))
            plt.suptitle(model_name)
    return (convs,gpred,slen,gset,preds,gc_content,corr_save)

#-----------------------   
def roll_sequence(seq,shift_val=1,rev_comp=True):

    #seq is shape s 4, sequence_len, 1
    if rev_comp == True or rev_comp == 1:
        seq[:,:int(seq.shape[2] / 2),:] = np.roll(seq[:,:int(seq.shape[2] / 2),:],shift=shift_val,axis=2)
    else:
        seq[:,:,:,:] = np.roll(seq[:,:,:,:],shift = shift_val,axis = 2)
    return seq

#-----------------------    
def val_split(X,y,plot=False,augment=None,shift_val=1):
    #augment takes values train, val, or None
    # print(X.shape)
    y_labels = np.empty(shape=(y.shape[0],),dtype='object')
    y_labels[:] = 'background'
    y_labels[np.where(y > 0.01)] = 'low'
    y_labels[np.where(y > 0.2)] = 'medium'
    y_labels[np.where(y > 0.7)] = 'high'

    #Get the counts for each label
    high_count = sum(y_labels == 'high')
    med_count = sum(y_labels == 'medium')
    low_count = sum(y_labels == 'low')
    background_count = sum(y_labels == 'background')
   
    #Create the empty vector to store the values, size is based on which augmentation method is employed
    if augment is None:
        #Take 1/3 of the highs, 1/4 of the mediums, 1/6 of the lows, and 1/3 background
        val_dim = int(high_count / 3) + int(med_count / 4) + int(low_count / 6) + int(background_count / 4)
        #The rest belong in the training set
        train_dim = (high_count + med_count + low_count + background_count) - val_dim
        
        val_set_X = np.zeros(shape=(val_dim,X.shape[1],X.shape[2],X.shape[3]))
        train_set_X = np.zeros(shape=(train_dim,X.shape[1],X.shape[2],X.shape[3]))
        val_set_y = np.zeros(shape=(val_dim,))
        train_set_y = np.zeros(shape=(train_dim,))
        
    elif augment == 'train':
        val_dim = int(high_count / 3) + int(med_count / 4) + int(low_count / 6) + int(background_count / 4)
        #Need to add extra space for the augmented values, one is removed and 2 are replaced
        train_dim = (high_count + med_count + low_count + background_count) + val_dim
        
        val_set_X = np.zeros(shape=(val_dim,X.shape[1],X.shape[2],X.shape[3]))
        train_set_X = np.zeros(shape=(train_dim,X.shape[1],X.shape[2],X.shape[3]))
        val_set_y = np.zeros(shape=(val_dim,))
        train_set_y = np.zeros(shape=(train_dim,))
        
    elif augment == 'val':
        #Two values augmented values added to val
        val_dim = (int(high_count / 3) + int(med_count / 4) + int(low_count / 6) + int(background_count / 4)) * 2
        train_dim = int((high_count + med_count + low_count + background_count) + (val_dim / 2))
        
        val_set_X = np.zeros(shape=(val_dim,X.shape[1],X.shape[2],X.shape[3]))
        train_set_X = np.zeros(shape=(train_dim,X.shape[1],X.shape[2],X.shape[3]))
        val_set_y = np.zeros(shape=(val_dim,))
        train_set_y = np.zeros(shape=(train_dim,))
        
        
    #Populate the training and validation sets
    train_idx = 0
    val_idx = 0
    x_idx = 0
    for i in range(1,high_count+1):
        if i % 3 == 0:
            if augment is None:
                val_set_y[val_idx] = y[val_idx + train_idx]
                val_set_X[val_idx,:,:,:] = X[val_idx + train_idx,:,:,:]
                val_idx += 1
                
            elif augment == 'train':
                #move one value from x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_X[val_idx,:,:,:] = X[x_idx]
                #put two augmented versions of X into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_y[train_idx + 1] = y[x_idx]
                
                train_set_X[train_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                train_set_X[train_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                x_idx += 1
                val_idx += 1
                train_idx += 2
                
            elif augment == 'val':
                #Move two augmented versions of x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_y[val_idx + 1] = y[x_idx]
                
                val_set_X[val_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                val_set_X[val_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                #Move X original into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_X[train_idx,:,:,:] = X[x_idx]
                
                x_idx += 1
                val_idx += 2
                train_idx +=1 

        else:
            train_set_y[train_idx] = y[x_idx]
            train_set_X[train_idx,:,:,:] = X[x_idx,:,:,:]
            train_idx += 1
            x_idx +=1
        
    for i in range(1,med_count+1):
        if i % 4 == 0:
            if augment is None:
                val_set_y[val_idx] = y[val_idx + train_idx]
                val_set_X[val_idx,:,:,:] = X[val_idx + train_idx,:,:,:]
                val_idx += 1
                
            elif augment == 'train':
                #move one value from x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_X[val_idx,:,:,:] = X[x_idx]
                #put two augmented versions of X into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_y[train_idx + 1] = y[x_idx]
                
                train_set_X[train_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                train_set_X[train_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                x_idx += 1
                val_idx += 1
                train_idx += 2
                
            elif augment == 'val':
                #Move two augmented versions of x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_y[val_idx + 1] = y[x_idx]
                
                val_set_X[val_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                val_set_X[val_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                #Move X original into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_X[train_idx,:,:,:] = X[x_idx]
                
                x_idx += 1
                val_idx += 2
                train_idx +=1 

        else:
            train_set_y[train_idx] = y[x_idx]
            train_set_X[train_idx,:,:,:] = X[x_idx,:,:,:]
            train_idx += 1
            x_idx += 1
        
    for i in range(1,low_count+1):
        if i % 6 == 0:
            if augment is None:
                val_set_y[val_idx] = y[x_idx]
                val_set_X[val_idx,:,:,:] = X[x_idx,:,:,:]
                val_idx += 1
                x_idx += 1
                
            elif augment == 'train':
                #move one value from x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_X[val_idx,:,:,:] = X[x_idx]
                #put two augmented versions of X into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_y[train_idx + 1] = y[x_idx]
                
                train_set_X[train_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                train_set_X[train_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                x_idx += 1
                val_idx += 1
                train_idx += 2
                
            elif augment == 'val':
                #Move two augmented versions of x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_y[val_idx + 1] = y[x_idx]
                
                val_set_X[val_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                val_set_X[val_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                #Move X original into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_X[train_idx,:,:,:] = X[x_idx]
                
                x_idx += 1
                val_idx += 2
                train_idx +=1 

        else:
            train_set_y[train_idx] = y[x_idx]
            train_set_X[train_idx,:,:,:] = X[x_idx,:,:,:]
            train_idx += 1
            x_idx += 1
        
    for i in range(1,background_count+1):
        if i % 4 == 0:
            if augment is None:
                val_set_y[val_idx] = y[val_idx + train_idx]
                val_set_X[val_idx,:,:,:] = X[val_idx + train_idx,:,:,:]
                val_idx += 1
                
            elif augment == 'train':
                #move one value from x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_X[val_idx,:,:,:] = X[x_idx]
                #put two augmented versions of X into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_y[train_idx + 1] = y[x_idx]
                
                train_set_X[train_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                train_set_X[train_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                x_idx += 1
                val_idx += 1
                train_idx += 2
                
            elif augment == 'val':
                #Move two augmented versions of x to the validation set
                val_set_y[val_idx] = y[x_idx]
                val_set_y[val_idx + 1] = y[x_idx]
                
                val_set_X[val_idx,:,:,:] = roll_sequence(X[x_idx,:,:,:],shift_val,rev_comp=True)
                val_set_X[val_idx + 1,:,:,:] = roll_sequence(X[x_idx,:,:,:],-shift_val,rev_comp=True)
                
                #Move X original into the training set
                train_set_y[train_idx] = y[x_idx]
                train_set_X[train_idx,:,:,:] = X[x_idx]
                
                x_idx += 1
                val_idx += 2
                train_idx +=1 

        else:
            train_set_y[train_idx] = y[x_idx]
            train_set_X[train_idx,:,:,:] = X[x_idx,:,:,:]
            train_idx += 1
            x_idx += 1
    if plot:
        plt.figure()
        plt.suptitle('%s Augment Method Split'%augment)
        plt.subplot(1,2,1)
        plt.scatter(np.arange(1,train_set_y.shape[0]+1),train_set_y,color='r')
        plt.ylim([0,1])
        plt.title('Training Set Coverage')
        plt.subplot(1,2,2)
        plt.scatter(np.arange(1,val_set_y.shape[0]+1),val_set_y,color='r')
        plt.title('Validation Set Coverage')
        plt.ylim([0,1])
        
        
    return train_set_X,val_set_X,train_set_y,val_set_y  
    
#-----------------------
def get_dna_color_for_energy_plot(dna_name, tf_name, genomic_tag = "EC_Ref"):
    """
    Helper function for color coding DNAs in energy scatterplots
        First: if TF name isn't in DNA name, it's a nonspecific site, thus gray
        Next: it's a specific site and genomic_tag (EC_Ref in the case of ecoli) is in the DNA name, it's green as a specific genomic sequence
        Finally: it's a specific site and not a genomic sequence, color it orange as a designed sequence
    """
    if tf_name not in dna_name:
        return (163/255, 163/255, 163/255)
    elif genomic_tag in dna_name:
        return (25/255, 201/255, 56/255)
    else:
        return (255/255, 124/255, 0/255)

#-----------------------
def get_dna_edge_color_for_energy_plot(dna_name, tf_name, dub_sites=['allR_EC_Ref_3', 'allR_EC_Ref_5', 'glnG_EC_Ref_1', 'glnG_EC_Ref_3', 'ulaR_EC_Ref_1']):
    """
    Helper function for getting the edge color of DNAs in energy scatterplots
        dub_sites (double-binding sequences - sequences with > 1 binding site in the seq) have a black border
        if it's not a double-binding sequence, there's no border
    dub_sites defaults to allR genomic references 3 & 5 as well as glnG genomic reference 3
        provide a list of multi-site sequences for other datasets
    """
    if dna_name in dub_sites and tf_name in dna_name:
        return 'black'
    else:
        return 'none'

#-----------------------
def load_energy_data(mode, tf, eval_seq_paths, version, prediction_base = None, bli_model_name = '1exp_full', **kwargs):
    """
    Loads BLI energy results & energy predictions and parses them into a dataframe

        Uses ecoliDB to get energy data from bli.tf_fit_kds (could use any DB connector since BLI energy data is in its own schema - could write a BLI-specific connector too).
        Requires a dictionary of predictions (results of eval_seq.py) that allow Eapp predictions for each DNA to be added to dataframe
            Keys allow prediction to be identified and values are prediction files
            Optionally provide prediction_base, will be joined to dictionary values, otherwise values must specify the full path to the file
        Runs linear regression on each prediction vs energy, appends prediction results to dataframe
        Also returns a dataframe of statistics from the linear regression (e.g. R^2, MSE)

    Returns energy_df, regression_df

    """
    if 'genomic_tag' in kwargs:
        genomic_tag = kwargs.get('genomic_tag')
    else:
        genomic_tag = 'EC_Ref'

    keyvals = {
        'nodes':('nnodes', -1),
        'ksize':('m', 5),
        'peaks':('peaks', -1)
    }
    prediction_dict = {}
    # Parse eval_seq_paths for predictions of this TF
    for file in eval_seq_paths:
        # Paths look like <seq_file_name>.fa_<tf>_<tf>_<filter patterns>.txt
        # Need to get the #peaks and convert # to an int
        if version is not None and version not in file:
            continue
        if tf in file:
            if mode is None:
                prediction_dict[tf] = file
            elif mode in keyvals:
                modeltoks = os.path.splitext(os.path.splitext(file)[0])[1].split('_')
                eval_tok = int(modeltoks[keyvals[mode][1]].replace(keyvals[mode][0], ''))
                prediction_dict[eval_tok] = file
            elif mode == 'exps':
                modeltoks = os.path.splitext(file)[0].split('_')
                subsettok = modeltoks[-1]
                prediction_dict[subsettok] = file


    # Gather energy data to plot alongside model dissection plots
    if len(prediction_dict) > 0:
        # Create list of mse_data which will become regression_df
        mse_data = []

        # Get energies from database
        db = ecoliDB()
        qry = f'SELECT dna_name, REPLACE(dna_name, " ", "_") AS dna_id, energy FROM bli.tf_fit_kds WHERE tf_name = "{tf}" AND model_name = "{bli_model_name}";'
        energy_df = db.runQuery(qry)
        energy_df.columns = ['dna_name', 'dna_id', 'energy']
        db.close()

        # For each prediction path, read data & append Eapp prediction to e_df
        for pred_key, pred_path in prediction_dict.items():
            if prediction_base is not None:
                pred_path_full = os.path.join(prediction_base, pred_path)
            else:
                pred_path_full = pred_path
            pred_col_name = f"boltzNet_prediction_{pred_key}"
            tmp_df = pd.read_csv(pred_path_full, sep='\t', skiprows=1)
            tmp_df = tmp_df.rename(columns={'ID':'dna_id', 'Eapp':pred_col_name})
            bn_df = tmp_df[['dna_id', pred_col_name]]
            energy_df = pd.merge(energy_df, bn_df, on='dna_id')

            linreg = LinearRegression()
            X_bn = energy_df[[pred_col_name]].values.reshape(-1,1)
            y = energy_df['energy'].values

            # Handle edge case where predictions may not have been possible (basically when kernel width > seq length)
            if X_bn[0][0] == '-inf ':
                continue

            linreg.fit(X_bn, y)

            energy_df[f'{pred_col_name}_linreg_energy'] = linreg.predict(X_bn)
            energy_df[f'{pred_col_name}_residual'] = energy_df['energy'] - energy_df[f'{pred_col_name}_linreg_energy']
            energy_df[f'{pred_col_name}_residual_z'] = (energy_df[f'{pred_col_name}_residual'] - energy_df[f'{pred_col_name}_residual'].mean()) / energy_df[f'{pred_col_name}_residual'].std()

            mse = mean_squared_error(y, energy_df[f'{pred_col_name}_linreg_energy'])
            r2 = linreg.score(X_bn, y)

            mse_data.append(
                {
                    'tf': tf,
                    'model': pred_col_name,
                    'mse': mse,
                    'coef': linreg.coef_[0],
                    'intercept': linreg.intercept_,
                    'rsquare': r2,
                }
            )

        regression_df = pd.DataFrame(mse_data)
        energy_df['shape'] = energy_df['dna_id'].apply(lambda x: '^' if genomic_tag in x else 'o')
        energy_df['color'] = energy_df['dna_id'].apply(get_dna_color_for_energy_plot, tf_name=tf, genomic_tag=genomic_tag)
        energy_df['edgecolor'] = energy_df['dna_id'].apply(get_dna_edge_color_for_energy_plot, tf_name = tf)
        energy_data = {
            'energy_df': energy_df,
            'regression_df': regression_df,
        }
    else:
        energy_data = None
    
    return energy_data