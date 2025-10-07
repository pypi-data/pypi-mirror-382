#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:48:01 2025

@author: kolak

OBJECT INTERFACE

seqPredict is a class for objects that take one or more models and enables prediction of 
those models on n sets of sequences of arbitrary length and analyse the results.  Basic usage:
    
    sp=seqPredict(model_name_list)
    sp.load_seqs(peak_seqs)
    sp.plotSeqResponse()


See scripts/scratch_predict.py for more example code

FUNCTIONAL INTERFACE

See predict_predict_tf_mdoel.py for running information: Not Active Yet

Toolbox for making predictions for sequences and analyzing those predictions. To use this module, a data object
must be created. Valid data objects are present in PredictionDT.py. Main function is makePrediction(models, data_obj,summary)
which makes predictions for all sequences and models provided. All results are written to a .csv file.

Results include:
    
    -Prediction Affinites for sequences (Overall, Best FRsum)
    -Greatest Correlating models for each group of sequences against a provided comparison metric (Overall, Best FRsum)
    -rGeatest Correlating models for each group of sequences against mutual information for each group of sequences (Positional, Convolutional)

Contains:
    
        -Utility functions
        - Model predictions
        -Prediction analyses
        -Stats for predictions (correlations and mode)
        -figures (scatter least squares)

exp is expirament name or sequence file name depending on data object
"""



from . import CONFIG
import os


import pandas as pd
import numpy as np


from .model_disect import  getAllLayerOutputs, getLayerOutput
from . import sequence
from . import model_predict_create
from . import tf_util
from . import genomes


# from scipy import stats
import matplotlib.pyplot as plt
from scipy.stats import rankdata
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from BCBio.GFF import GFF3Writer



from . import model_create
from . import model_disect
# import model_predict_models
from . import util
import random
import tensorflow as tf
import gc



from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import ScalarFormatter

import re

from dna_features_viewer import GraphicRecord, GraphicFeature



#-------------------------------------------------------------
#%% OBJECT INTERFACE
#-------------------------------------------------------------

class baseSeqPredict:
    '''A base class for derived seqPredict object.
    
    Contains private methods for creating a prediction model from a set of input models
    and for doing certain core analyses such as ranking
    
    But does not have any actual public methods for loading sequences.  Those must be
    instatiated in derived classes.  But does have a private __load_seqs__ to load sequences
    into the right variables for downstream analysis.
    
    TODOs
    - add function to plot statistics over pronmoters
    - support for stacked models
    
    '''
    
    
    def __init__(self, model_name_list=None, model_location=CONFIG.model_json_dir):
        """Constructor that takes a list of models tf names
        and an optional location for these models
        
        If not location given, defaults to CONFIG.model_dir
        
        if model_name_list is None, the get a model for all TFs by
        loading all TF models with getAllModelNames
          
        """
        
        self.model_names=model_name_list # redundant with tf_list but keeping just in case
        self.model_location=model_location
        
        # Retrieve all weight matrices for given list of tf names
        # or all matrices if model_name
        self.weight_dict,self.tf_list=model_create.loadModelWeightJsons(model_name_list,model_location)    
        
        self.ntfs=len(self.tf_list)
        
        
        # the input sequence "slots" - set in load_seqs
        self.seqs=None # one-hot encoded format (nseqs,4,seqlen)
        self.seqpos=None
        self.nseqs=0
        self.seqnames=None
        self.concat_seqs=None # one-hot encoded format (nseqs,4,2*seqlen,1)
        self.seqlen=None
        
        # annotations
        self.annots={}
        self.default_seqid='default' # the default seqid for assigning annots to all seqs
        
        
        # the prediction model - set when __create__ is run 
        self.predict_model=None # the prediction model
        self.predict_model_params=None # the prediction model params object
        self.layers=None # the names of the output layers of the model
        
        ### the prediction results from running the prediction model of the input sequences
        # the basic model layers
        self.conv=None      
        self.FRSumConv=None
        self.fmap=None  
        
        self.fmapRanks=None # ranked fmaps (nseqs,ntfs)
        self.fmapPercentile=None  #normalized fmap so that fmap <=1 and mean=0 (nseqs,ntfs)
         
        # the prediction on both fwd and rev strand after conv and exp
        self.conv2D,self.conv2DPos = (None, None)
        
        # the sum of the predictions on both strands in windows of kernel size
        self.ksize=None # the kernel size
        self.winSum=None
        self.winSumMax=None # max binding site in each seq for each tf  (nseqs,ntfs)
        self.winSumRanks=None # ranked max winsums (nseqs,ntfs)
        self.winSumPercentile=None # normalized (nseqs,ntfs)
        
        
    
    def __get_seqinds_by_patterns__(self,pattern_list):
        '''Get the indices of all sequences that contain any pattern in pattern list
        Preserves order of indices associated with order in pattern list'''
        
        inds=[]
        for pat in pattern_list:
            inds.extend([ind for ind,name in enumerate(self.seqnames) if pat in name ])
        return inds
    
    def __load_seqs__(self,seqs,seqpos=None, seqnames=None):
        '''Load a set of sequences in one-hot encoded format
        This should be a numpy array of shape
        
        (nseqs,4,seqlen)
        
        The seqs are stored and the concatenated sequences are automatically created and stored too - this is handy
        
        '''
        
        self.seqs=seqs # (shape nseqs,4,seqlen)
        self.seqpos=seqpos # list of [start,stop] for the seqs
        self.seqnames=seqnames
        self.seqlen=self.seqs.shape[2]
        self.nseqs=self.seqs.shape[0]
        
        
        # note the need to add the last axis of dim 1
        self.concat_seqs=sequence.concatenate_revcomp(self.seqs)
        self.concat_seqs=np.expand_dims(self.concat_seqs,axis=-1)
        self.concat_seqlen=self.concat_seqs.shape[2]
    
    
    def __get_annots_in_range__(self,seqid_list,pos,type_list=None,name_list=None):
        '''Return a dataframe of annotations from self.annots
        that overlap the range start->stop and are associated with
        the first seqid from seqid list where we get a match
        
        e.g.
        __get_annots_in_range__(['bob','default'],[1,100])
        
        if type_list is given then only return feature types given
        if name_list is given, only return featurs with names in that list
        
        '''
        
        # Try each seqid in list and return when you have first match 
        # of seqid - might still be an empty df
        for seqid in seqid_list:        
            df= self.annots.get(seqid,None)
            if df is None:
                continue
                        
            mask = (df["start"] < pos[1]) & (df["stop"] > pos[0])
            result = df[mask]
            
            if type_list is not None:
                mask = (result["type"].isin(type_list))
                result = result[mask]

            if name_list is not None:
                mask = (result["name"].isin(name_list))
                result = result[mask]

            if len(result)==0:
                return None
            else:
                return result
    
        # if we are here, then not entries in annot to any seqid in list
        return None
        
    def __load_annot_gff__(self,gff_file):
        '''Loads a gff file into a dictionary seqid=>df
        where each df has fields
        type,ID,name,symbol,start,stop,strand
        
        Note that symbol is set to name for internal use
        but exporting does not export the symbol
        
        '''
        
        annot_dict=util.load_annot_gff(gff_file)
        
        self.annots=annot_dict
        return
        
    def __export_annot_gff__(self,ddf,filename):
        ''' Given a dictionary of 
        seqid => dataframe 
        where each df has fields
        type, ID, name, start, stop, strand, source
        
        all assumed to come from seqid key
        
        export to gff filename
        '''
        
        strand_map = {"+": 1, "-": -1, ".": 0, None: 0}
        
        seqrecs=[]
        for seqid,df in ddf.items():
            
            # create this seq record
            rec = SeqRecord(Seq(''), id=seqid, description="")
            
            # add the records
            for _, row in df.iterrows():
                feat = SeqFeature(
                    FeatureLocation(
                        int(row["start"]) - 1,  # Biopython uses 0-based, half-open
                        int(row["stop"]),
                        strand=strand_map.get(row["strand"], 0)
                    ),
                    type=row["type"],
                    qualifiers={
                        "ID": [str(row["ID"])],
                        "Name": [str(row["name"])],
                        "source": [str(row["source"])],
                    }
                )
                rec.features.append(feat)
                    
        
            # add to list of seq records
            seqrecs.append(rec)
    
            # write the gff
            with open(filename, "w") as out_handle:
                writer = GFF3Writer()
                writer.write(seqrecs, out_handle)
                        
    
    
    def __export_seqs_to_fasta__(self,filename):
        '''Export loaded sequences to a fasta file
        
        Files headers have the format
        
        ><seqname> (start=<seqpos_start>, end=<seqpos_end>)
        
        And if seqname has spaces, the spaces are replaced with underscores
        
        '''
        
        # convert one-hot back to sequences
        seqs=sequence.onehot2str_multi(self.seqs)
        
        records = [ SeqRecord(Seq(s), id=seqid.replace(" ", "_"), description='(start=%i, end=%i)'%seqpos) for (s,seqid,seqpos) in zip(seqs,self.seqnames,self.seqpos)]

        with open(filename, "w") as output_handle:
            
            SeqIO.write(records, output_handle, "fasta")        

        pass

    def __load_seqs_from_fasta__(self, seqfile):
        ''' Internal command to load a set of sequences from a file in one line per seq format
        All sequences must be the same length and the correct length for the model  
        
        Headers are expected to have the form
        
        >seqname description
        
        And if description contains the following text
         
        (start=<seqpos_start>, end=<seqpos_end>)
        
        then seqpos is parsed out
        
        '''
            
        seq_dict=util.load_seqs_from_fasta(seqfile)
        
        seqlist=[seq_dict[k]['onehot'] for k in seq_dict]
        seqpos=[seq_dict[k]['pos'] for k in seq_dict]
        seqids=list(seq_dict.keys())
        
            
        seqs = np.stack(seqlist) #one hot encoding
        
        if len(seqpos)==0:
            seqpos=None
        
        self.__load_seqs__(seqs,seqpos=seqpos, seqnames=seqids)

        return

    def __get_topN_seqs__(self,seq_inds=None, tf_names=None,maxN=None,perc_th=0.2,mode='full_sequence', savefilename=None):
        '''given the seq indices, return the names of tfs that for 
        which the TF scores above perc_th
        
        Limit to the tf names in tf_names if given
        
        If seq_inds is None, return for all sequences
        
        Returns a dataframe with columns ['ind','seq_name','num_tfs','tfs','percentiles','ranks']
        
        If savefilename is not None, the save the df to savefilename where the
        list of tfs becomes a ; seperated string.  
        
        modes:
            'max_binding_site' = winSum
            'full_sequence' = fmap
        '''
        
        # get list of tf indices or all if tf_names is None
        tf_inds=self.getTFIndByName(tf_names)
        
        # Get the correct scores
        valid_modes=['max_binding_site','full_sequence']
        assert mode in valid_modes, 'Mode must be one of %s'%valid_modes
        if mode=='max_binding_site':
            perc=self.winSumPercentile[:,tf_inds]
            ranks=self.winSumRanks[:,tf_inds]
        elif mode=='full_sequence':
            perc = self.fmapPercentile[:,tf_inds]
            ranks= self.fmapRanks[:,tf_inds]
            
        if seq_inds is None:
            seq_inds=list(range(len(self.seqs)))
            
        df=pd.DataFrame(columns=['ind','seq_name','num_tfs','tfs','percentiles','ranks'])
        for ind in seq_inds:
            seq_name=self.seqnames[ind]
            indices = np.where(perc[ind,:] >= perc_th)[0] # this also indices tf_inds

            # sort on descending percentiled/normalized scores
            indices = indices[np.argsort(perc[ind, indices])]
            indices=indices[::-1]
            
            if maxN is not None:
                indices=indices[:maxN]
                
            tf_names=[self.tf_list[tf_inds[i]] for i in indices]
            percentiles=[perc[ind,i] for i in indices]
            ranklist=[ranks[ind,i] for i in indices]
            
            
            
            df.loc[len(df)] = {"ind":ind, "seq_name": seq_name, "num_tfs": len(tf_names),"tfs":tf_names,
                               "percentiles":percentiles,'ranks':ranklist}
                    
        if savefilename is not None:
            df_temp=df.copy()
            df_temp["tfs"] = df_temp["tfs"].apply(lambda x: ";".join(map(str, x)))
            df_temp["percentiles"] = df_temp["percentiles"].apply(lambda x: ";".join(map(str, x)))

            print("Saving %s..."%savefilename)
            df_temp.to_csv(savefilename, index=False)

        
        return df

    def __analyze_seqs__(self):
        '''Perform various analyzes of the results of the promoter wide prediction
        This includes percentiling (normalizing the scores to max) the promoters for each TF'''
        
        
        # get percentiled data for each TF
        
        ##################
        # winSum - this is looking at the best score in a biding site window in the genome
        # 'max_binding_site' mode
        self.winSumMax = np.max(self.winSum,axis=(1)) # max over every position of each sequence => (Nseqs,ntfs)
        ranks = np.apply_along_axis(rankdata, 0, self.winSumMax, method='average') # max is max rank
        self.winSumRanks=self.winSumMax.shape[0] - ranks +1 # need to covert so that 1 is max rank
        self.winSumRanks=self.winSumRanks.astype(int) # the rank of each promoter for each tf
       
        tfmean=self.winSumMax.mean(axis=0)
        temp=self.winSumMax-tfmean
        self.winSumPercentile=temp/temp.max(axis=0) # for each TF, the mean is zero and the max is 1, so 0.2 is 20% of the distance from mean to max
        
        # tfmax=x_flat.max(axis=0)
        # self.winSumPercentile=x_flat/tfmax # the percentile of the max score
        
        ##################
        #fmap - sum exp scores over entire sequence - 'full_sequence' mode 
        x_flat = self.fmap.numpy()
        ranks = np.apply_along_axis(rankdata, 0, x_flat, method='average')
        self.fmapRanks=x_flat.shape[0] - ranks +1
        self.fmapRanks=self.fmapRanks.astype(int)

        tfmean=x_flat.mean(axis=0)
        temp=x_flat-tfmean
        self.fmapPercentile=temp/temp.max(axis=0) # for each TF, the mean is zero and the max is 1, so 0.2 is 20% of the distance from mean to max
        # tfmax=x_flat.max(axis=0)
        # self.fmapPercentile=x_flat/tfmax
        
        return    

    def __predict__(self):
        '''Run a prediction on stored sequences 
            - and then runs predictions to retrieve and store each intermediate layer
            
            TODO
            - need to make sure new prediction models will work with model_disect.getLayerOutput
        '''
        
        assert self.predict_model is not None, 'Predict model must be created before calling __predict__'
        
        # run the predict model at each layer on the stored seqs
        layers = getLayerOutput(self.predict_model,self.concat_seqs,self.layers)
        self.conv=layers[0]
        self.FRSumConv=layers[1]
        self.fmap=layers[2]
        
        # the prediction on both fwd and rev strand after conv and exp
        self.conv2D,self.conv2DPos=model_disect.convReshape2D(self.predict_model,self.conv,pad=True) 
        
        # the sum of the predictions on both strands in windows
        (mfit,mfitc,biases)=tf_util.getModelMotifs(self.predict_model)
        self.ksize=mfit[0].shape[1]
        self.winSum=model_disect.calcWindowSum(self.conv2D,self.ksize)
        
        
    
    def __create_model__(self):
        ''' Creates a prediction model based on the length of the sequences that have
        been imported to the object
        
        Right now just a non-stacked model - and only one TF
        
        TODO - Support stacked model for multiple TFs
        
        '''
        
        # check to make sure that we have sequences - just an assert now - will handle more 
        # gracefully later
        assert self.concat_seqlen is not None, 'Sequences must be loaded before calling __create_model__'
        
        
        # build the stacked prediction model from the stacked weights in weigh_dict['conv']    
        self.predict_model, self.predict_model_params=model_predict_create.buildPredictionModelFromWeighs(self.weight_dict,self.concat_seqlen)
        self.layers=['conv','FRSumConv','pool']
        
        
    
    def __repr__(self):
        """Unambiguous representation used for debugging."""
        return f"{self.__class__.__name__}"

    def __str__(self):
        """User-friendly string representation."""
        return "seqPredict object"   
    
    def clearKeras(self):
        '''Clear keras backend
        '''
        tf.keras.backend.clear_session()  # reset state and free graph memory
        gc.collect()
        return
        
    
    def getTFIndByName(self,tf_name=None):
        '''get the index into a stacked model of a TF by tf name
        if there are duplicates, will return all hits
        if tf_name is None return a list of all tf indices'''
        
        if tf_name is None:
            inds=list(range(len(self.tf_list)))
        elif isinstance(tf_name,list):
            inds=[i for i,tf in enumerate(self.tf_list) if tf in tf_name]
        else:
            inds=[i for i,tf in enumerate(self.tf_list) if tf==tf_name]
        
        # return only the unique elements
        inds=list(set(inds))
        
        return inds
    
    def getPredictions(self):
        '''Returns a np array of predicions at each position on both
        strands of each sequence for all TFs
        
        The numpy array has shape
        
        (nseqs,2,seqlen,numtfs)
        - nseqs: number of sequences
        - 2: forward and reverse strands
        - seqlen: length of each sequence
        - numtf: number of tfs in the model
        
        At every position the value is the results of applying 
        the tf weight matrix centered at that position, adding the bias
        term, and the exponentiating the results'''
        
        return self.conv2D
    
    def getMaxBindingSiteScores(self):
        '''Returns an np array of the max binding site scores for each sequence for each TF
        
        Has shape of (nseqs, ntfs) where each entry is the 
        max bindins site score (proportional to the binding energy) of that TF to any
        location in the sequence
        
        Binding site scores are the sum of the exponentiated binding energies in windows
        of length(weigth_matrix) '''
        
        if self.fmap is not None:        
            return np.array(self.fmap)
        else:
            return None
    
        
    def getScores(self):
        '''Returns an np array of scores for each sequence for each TF
        
        Has shape of (nseqs, ntfs) where each entry is the 
        score (proportional to the binding energy) of that TF to that entire sequence
        
        Scores are the sum of the exponentiated binding energies at every 
        position across both strands'''
        
        if self.fmap is not None:        
            return np.array(self.fmap)
        else:
            return None
    
    def predictionRanking(self,mode = 0,rank_type = 0,layer = None,seq_inds = None,**kwargs):
        '''DEPRECATED Ranking Function that returns a numpy array of ranks of the best sequences for each model 
        or the best model for each sequence.
        
        mode: mode for ranking:
            mode 0: ranks based on max values or fmaps
            mode 1: ranks based on the fe of the max vs the sequence prediction mean
        
        rank_type:
            rank_type 0: ranks sequences for each model
            rank_type 1: ranks models for each sequence
        
        layer: layer or winSum for ranking
        seq_inds: sequence indexs for ranking
        
        '''


        if layer == 'conv':
            data = self.conv
            data = np.array(data).squeeze()
        elif layer == 'frsums':
            data = self.FRSumConv
            data = np.array(data).squeeze()
        elif layer == 'fmap':
            data = self.fmap
            data = np.array(data)
        else:
            data = self.winSum
                
        if seq_inds is None:
             data = data
        else:
            data = data[seq_inds]

                
        #Straight max for ranking
        if mode ==0:
            if layer != 'fmap':
                maxes = np.max(data,axis=1)
            else:
                maxes = data
                

            ranks = np.apply_along_axis(rankdata, rank_type, maxes, method='average')
            out_data = maxes.shape[rank_type] - ranks +1
            out_data = out_data.astype(int)
            
            
        #fe over sequence average    
        elif mode ==1:
            if layer == 'fmap':
                raise Exception('fmap not valid for mode = 1')
                
            averages = np.mean(data, axis = 1)
            maxes = np.max(data,axis=1)
            fe = maxes/averages

            ranks = np.apply_along_axis(rankdata, rank_type, fe, method='average')
            out_data = maxes.shape[rank_type] - ranks +1
            out_data = out_data.astype(int)       
            
        return out_data
   
    
    def plotSeqHeatmapSummary(self, inds=None, annots=None, seqposlist=None, mode=1, vmax=None, vmin=None, num_xtick=5):
        '''Plot a summary heatmap for the sequences in ind
        
        inds - indices of sequences
        annots - annotations (TODO) - must also provide seqpos in this case
        seqpos -the position of the sequence
        mode = (1) plot self.winSum (2) plot self.Conv2D
        vmax = array of vmax values 1 for each TF (default None means 200 (mode1) or 50(mode2), or max over seq)
        
        TODO
        - add fmap summary plot on right showing where this seq is on histogram of all seqs?
        - add vmax support
        - add seqpos support
        
        '''

        # calculate vmax over all sequences
        if vmax is None:
            if mode==1:
                vmax=np.max(self.winSum,axis=(0,1))
                vmin=np.min(self.winSum,axis=(0,1))
            if mode==2:
                vmax=np.max(self.conv2D,axis=(0,1,2))
                vmin=np.min(self.conv2D,axis=(0,1,2))
        
        for ii,ind in enumerate(inds):
            
            if self.seqnames is not None:
                title=self.seqnames[ind]
            else:
                title='Sequence %s'%ind
                
            if annots is not None:
                annot=annots[ii]
            else:
                annot=None
        
            if mode==1:
                tensor=self.winSum[ind] #(seqlen,ntfs)
                slen=tensor.shape[0]
                
            if mode==2:
                tensor = self.conv2D[ind]  # (2, slen, ntfs)
                slen=tensor.shape[1]
        
            if seqposlist is not None:
                seqpos=seqposlist[ii]
            elif self.seqpos is not None:
                seqpos=self.seqpos[ii]
            else:
                seqpos=[0,slen]
                
        
            # Create figure with two axes
            mosaic=[]
            height_ratios=[]
            if annots is not None:
                mosaic.append(['annot'])
                height_ratios.append(self.ntfs/5)
            mosaic.append(['heatmap'])
            height_ratios.append(3*self.ntfs)
            fig,ax=plt.subplot_mosaic(mosaic,figsize=(18,4*self.ntfs), gridspec_kw={'height_ratios': height_ratios},sharex=True, constrained_layout=True)
            # fig, ax = plt.subplots(figsize=(18,3*self.ntfs), layout='constrained')

            
            
            ######################
            # Heatmap
            offset = 0
            
            # in reverse order of TFs so A is at top and Z at bottom for all TF model
            for i in reversed(range(self.ntfs)):
                
                if mode==1:
                    vmax_i = vmax[i] # to make strong peaks stand out
                    vmin_i = vmin[i]
                                        
                    row_data = tensor[:, i]
                    cmap = 'Greys'
                    
                    
                    ax['heatmap'].imshow(
                        row_data[np.newaxis, :],  # shape (1, slen)
                        aspect='auto',
                        extent=[0, slen, offset, offset + 1],
                        cmap=cmap,
                        vmin=vmin_i,
                        vmax=vmax_i
                    )
                    offset += 1
                    
                    # Draw a horizontal line after each tf
                    ax['heatmap'].axhline(offset, color='black', linewidth=0.5)
                
                if mode==2:
                    
                    vmax_i = vmax[i] # to make strong peaks stand out
                    vmin_i = vmin[i]
                                    
                    # we want the fwd strand (0) on top and we are plotting from
                    # bottom to top (increasing offsets)
                    for j in [1,0]:  
                        row_data = tensor[j:j+1, :, i]
                        cmap = 'Greens' if j == 0 else 'Oranges'
                        
                        ax['heatmap'].imshow(
                            # row_data[np.newaxis, :],  # shape (1, 101)
                            row_data,
                            aspect='auto',
                            extent=[0, slen, offset, offset + 1],
                            cmap=cmap,
                            vmin=vmin_i,
                            vmax=vmax_i
                        )
                        offset += 1
            
                    # Draw a horizontal line *after* each pair
                    ax['heatmap'].axhline(offset, color='black', linewidth=0.5)
        
            
            if mode==1:
                ax['heatmap'].set_ylim(0, self.ntfs)
                
                yticks = np.arange(0.5, self.ntfs+0.5, 1)
                ax['heatmap'].set_yticks(yticks)
                yticklabels=['%s'%tf for tf in reversed(self.tf_list)]
                ax['heatmap'].set_yticklabels(yticklabels)
                
                if annots is not None:
                    ax['annot'].set_title('Kernel Window Sum Prediction for All TFs on %s'%title)
                
                
            if mode==2:
                # Add vertical lines at each xtick
                for x in range(0, self.conv2D.shape[2]+1):  # 0 to 101 inclusive
                    ax['heatmap'].axvline(x, color='gray', linewidth=0.2)
                
                ax['heatmap'].set_ylim(0, self.ntfs*2)
                yticks = np.arange(0.5, self.conv2D.shape[3]*2+0.5, 2)
                ax['heatmap'].set_yticks(yticks)
                yticklabels=['%s'%tf for tf in reversed(self.tf_list)]
                ax['heatmap'].set_yticklabels(yticklabels)
                
                if annots is not None:
                    ax['annot'].set_title('Prediction for All TFs on %s'%title)

            # Add yticklabels on the right
            ax_right = ax['heatmap'].twinx()
            ax_right.set_ylim(ax['heatmap'].get_ylim())  # Match limits
            ax_right.set_yticks(yticks)
            ax_right.set_yticklabels(yticklabels)
            ax_right.tick_params(axis='y', direction='in')  # Optional: inward ticks
        
            # xlabel and title do not depend on mode
            ax['heatmap'].set_xlim(0, slen)
            
            tickspacing=int(slen/num_xtick)
            ticks = np.arange(0, slen, tickspacing)
            labels = [str(seqpos[0]+t) for t in ticks]  # 1-based labels
            
            ax['heatmap'].set_xticks(ticks)
            ax['heatmap'].set_xticklabels(labels)
            ax['heatmap'].set_xlabel('Position')
            
            
            ######################
            # Annotations do last to xlim is set
            if annot is not None:
                plotAnnotationTrack(ax['annot'],annot,seqpos,ax['annot'].get_xlim(),ax['annot'].get_ylim())
            
    
    def plotSeqResponseByInds(self,inds=None, seqnames=None, annots=None, fig=None, tf_names=None, highlights=None, savefilename=None, title=None, maxN = 10, row_titles=None, dpi=300, perc_th=0.1, ranking_mode='full_sequence',annot_type_list=None, **kwargs):
        '''Do seqResponse plot(s) for the sequences indicated by the 
        list of indices
        
        annots is a list of annotations - one entry per ind - see plotAnnotationTrack
        highlights is a list of [seq,stop] - on entry per tf in tf_names
        
        annots and highlights are provide in native sequence coordinates as determined by
        self.seqpos
        
        if inds is None then plot all seqs - and annots is set to None to be safe
        since there is now way to be sure they will be the correct length
        
        title is an optional title for the entire figure - if None then the title is promoter name
        row_titles is an optional list of titles for each row - if None then title is TF name
        
        if savefilename is not None the we save each figure.  If only one figure then save
        as savefilename.png, otherwise save as savefilename_<ind>.png where for each ind in inds
        unless savefilename is a list, the we use the element of the list
        and we close the figure after saving
        
        
        tf_names is a list of tf_names that will be used to determine what members 
        of a stacked model will be plotted.
        
                
        '''
        #plot size parameters
        figheightperrow=3
        figwidth=18*.6

        no_title=True
        if title is not None:
            no_title=False

        
        if inds is None and seqnames is None:
            inds = list(range(0,self.nseqs))
        
        if inds is None and seqnames is not None:
            inds=[]
        
        if seqnames is not None:
            inds.extend(self.__get_seqinds_by_patterns__(seqnames))
            
        # get only unique indices in order
        unique_inds = []
        for x in inds:
            if x not in unique_inds:
                unique_inds.append(x)
        
        inds=unique_inds
                
        # if we are given tf names, find their indices
        tf_inds=[]
        if tf_names is not None:
            for tfn in tf_names:
                temp=self.getTFIndByName(tfn)
                if len(temp)==0:
                    raise Exception('Could not find tf %s'%tfn)
                tf_inds.append(temp[0])
            perc_th=-1e10 # if we provide TF names, then we do not filter on perc_th

        # get rankings of all TFs for each seq
        tfmap=self.__get_topN_seqs__(perc_th=perc_th, mode=ranking_mode)
    

        #outer loop over sequences
        ################################
        for ii,i in enumerate(inds):
            
            # if not explicit tf list then get to N ranked for this seq
            if tf_names is None:
                tf_inds=[]
                tfnames_i=tfmap.iloc[i]['tfs'][:maxN]
                
                for tfn in tfnames_i:
                    temp=self.getTFIndByName(tfn)
                    if len(temp)==0:
                        raise Exception('Could not find tf %s'%tfn)
                    tf_inds.append(temp[0])

            ################
            # if no tfs to plot, then continue to next sequence
            ################
            if len(tf_inds)==0:
                continue

            # get any annotations for this seq that were passed in as arguments
            if annots is not None:
                annot=annots[ii]
            #otherwise, see if we have loaded any for this sequence or default
            # or return none
            else:
                annot=self.__get_annots_in_range__([self.seqnames[i],self.default_seqid], self.seqpos[i],annot_type_list)

            ######################################
            # create a new plot for each sequence i 
            # if we have annot:
            # we create an extra subfigure at the top of the figure
            # and we plot the annotation track in this subfigure
            # and have plotSeqPredict just plot the rest (we set annot to None)
            ######################################
            nsubfigs=len(tf_inds)
            height_ratios=[1]*nsubfigs
            
            plot_annot=False
            ########################################
            # TODO - plotting the annotations in seperate subfig not working
            # It seems plotLogo is shifting the left axis in a way that is not easily tracked
            # so the annotation subplot is not lining up on the left
            # Need to debug more - but for now just plotting anntations with each TF
            ########################################
            # if annot is not None and len(annot)>0:
            #     nsubfigs=nsubfigs+1
            #     plot_annot=True  
            #     height_ratios=[0.7] + height_ratios

            #create the fig and subfigs - ignores any given fig for now
            fig=plt.figure(figsize=(figwidth,figheightperrow*len(tf_inds)), layout='constrained')
            
            subfigs=fig.subfigures(nsubfigs,hspace=0.01, height_ratios=height_ratios)
            if nsubfigs==1:
                subfigs=[subfigs]
                            
            # this is the suptitle for the entire figure
            if self.seqnames is not None and no_title:
                title=self.seqnames[i]
            fig.suptitle("%s"%title, fontsize=16,fontweight='bold', fontfamily='Helvetica')
            
            # inner loop over TFs - need to loop over an explicit list of indices
            ################################

            for tt,tf_ind in enumerate(tf_inds):

                # get the row title and set suptitle if nececceary            
                if row_titles is None:
                    tf_name=self.tf_list[tf_ind]
                    tfmap_ind=tfmap.iloc[i]['tfs'].index(tf_name)
                    per=tfmap.iloc[i]['percentiles'][tfmap_ind]
                    rnk=tfmap.iloc[i]['ranks'][tfmap_ind]

                    row_title='%s (score: %0.2f, rank: %i)'%(tf_name,per,rnk)
                else:
                    row_title=row_titles[tt]
            
                if plot_annot:
                    plotfig=subfigs[tt+1] # one tf per subfig after annot subfig
                else:
                    plotfig=subfigs[tt] # one tf per subfig starting with first subfig
            
                    
                # get the max and min conv values over all sequences for this TF
                vmax=np.max(self.winSum[:,:,tf_ind:tf_ind+1])
                vmin=np.min(self.winSum[:,:,tf_ind:tf_ind+1])
                
                # get the highlights for this tf and shift based on seqpos
                # the base class cannot know this.  Must be passed in from derived class call or pull from annots any features with type TF_binding_site
                tf_highlights = None
                if highlights is not None:
                    tf_highlights=highlights[tt] # the entry for this tf
                else:
                    df=self.__get_annots_in_range__([self.seqnames[i],self.default_seqid], self.seqpos[i],type_list=['TF_binding_site'],name_list=[self.tf_list[tf_ind]])
                    if df is not None:    
                        tf_highlights=[[start,stop] for start,stop in zip(df['start'],df['stop'])]


                ############################################
                # Call plotSeqPredict which designed to plot annot, seqlogo +highights, heatmap, baseseq
                # but we if we are plot_annot ourselves, then set annot to None
                # so the plotSeqPredict will only plot seqlogo, heatmap, baseseq
                # TODO - commented out until we can debug algnment issues
                #############################################
                # if plot_annot: 
                #     this_annot=None
                # else:
                #     this_annot=annot
                
                this_annot=annot
                axs=plotSeqPredict(self.conv[i:i+1,:,:,tf_ind:tf_ind+1],
                               self.seqs[i],self.predict_model,seqpos=self.seqpos[i],
                               vmax=vmax,vmin=vmin,fig=plotfig,annot=this_annot, 
                               kernel_ind=tf_ind,title=row_title,
                               highlights=tf_highlights,
                               return_axs=1,
                               **kwargs)
            
            # add the annotation track if necessary and sync xaxes with axes from plotSeqPredict
            # THIS DOES NOT WORK YET.  if you plot seqlogo, the annotation trak no longer lines up on left
            
            # if plot_annot:
            #     pass
            #     ax_annot=subfigs[0].add_subplot(1, 1, 1)

            #     plotAnnotationTrack(ax_annot,annot,self.seqpos[i],ax_annot,None)

            #     #sync annot with xaxes from plotSeqPredict
            #     all_axes = [ax_annot]+ list(axs.values())
            #     ref_ax = all_axes[-1] # the last axis from plotSeqPredict always has xticks and xticklabels
            #     for ax in all_axes[:-1]:
            #         if ax is ref_ax:
            #             continue
            #         # check if they already share
            #         if ref_ax not in ax.get_shared_x_axes().get_siblings(ax):
            #             ax.sharex(ref_ax)

            
            # add xlabel at bottom of entire figure
            fig.supxlabel('Genomic Position',fontfamily='Helvetica')
            
            # one plot per sequence with all TFs
            if savefilename is not None:
                if isinstance(savefilename,list): # we expect one string per plot
                    fname="%s.png"%(savefilename[ii])
                else:
                    fname="%s_%s.png"%(savefilename,self.seqnames[i])
                print("Saving %s at %i dpi..."%(fname,dpi))
                fig.savefig(fname, dpi=dpi)
                plt.close(fig)
            
        # enable shared zoom for interacive and only zoom on x
        else:
            all_axes = fig.get_axes()            
            base_ax = all_axes[0]  
            for ax in all_axes[1:]:
                ax._shared_axes["x"].join(base_ax, ax) 
            
    
        
class seqPredict(baseSeqPredict):
    '''An object that takes one or more model names, and provides
    an interface to make predictions with those models on sets
    of sequences of arbitrary length and analyse the results
    
    Plan for usage
    - Initialize with a list of model names
    - Load (or reload) some sequences 
        - these are stored and any results from prev seqs are removed
        - assumes one hot encoding
        - so assumes a matrix of appropriate shape
        - seq length assumed from this matrix
    - Run a prediction on these sequences (done automatically when seqs are loaded)
        - this builds an appropriate multi-TF model and stores it
        - and then runs prediction which sets all the layers appropriately
    - Analyze the results
        - basically pull the appropriate layers and do something (visualize, analyze, etc)
    '''
    
    def __init__(self, model_name_list=None, model_location=CONFIG.model_json_dir):
        """Constructor that takes a list of models names
        and an optional location for these models
        
        If not location given, defaults to CONFIG.model_dir
        
        """
        
        super().__init__(model_name_list,model_location)
        
        
    
    def __repr__(self):
        """Unambiguous representation used for debugging."""
        
        return self.__str__()

    def __str__(self):
        """User-friendly string representation."""
        
        mnames = [m for m in self.tf_list]
        
        s='%s object on %s models with %s loaded sequences'%(self.__class__.__name__,len(mnames),self.nseqs)
        
        return s
    
    def load_annot_gff(self,filename,default_seqid='default'):
        '''Load annotations from a gff
        
        Annotations are associated with specific sequences through their seqid
        If seq is default_seqid then the annotation will be applied to all sequences
        that do not have have any specific entries
        
        E.g. if the gff has entries
        
        bob	.	gene	190	255	.	+	.	ID=0;Name=thrL
        bob	.	gene	337	2799	.	+	.	ID=1;Name=thrA
        default	.	gene	2801	3733	.	+	.	ID=2;Name=thrB
        default	.	gene	3734	5020	.	+	.	ID=3;Name=thrC
        default	.	gene	5234	5530	.	+	.	ID=4;Name=yaaX
        default	.	gene	5683	6459	.	-	.	ID=5;Name=yaaA


        then the sequence bob will use the first two rows as the only annotations
        and every other seqeunce will use the rest of the rows but not the rows 
        with bob
        
        This way you can load annotations for certain specific sequences
        and/or load annotations for all sequences (if they all come from same genome for example)
        
        '''
        
        self.__load_annot_gff__(filename)
        for k,v in self.annots.items():
            print('Loaded %i annots for sequence %s...'%(len(v),k))
            
        self.default_seqid=default_seqid
    
    def export_fasta(self,filename):
        '''Export loaded sequences to fasta file
        Files headers have the format
        
        ><seqname> (start=<seqpos_start>, end=<seqpos_end>)
        
        And if seqname has spaces, the spaces are replaced with underscores
        '''
        
        self.__export_seqs_to_fasta__(filename)
        print("Exported %i loaded sequences to fasta file %s..."%(self.nseqs,filename))
        
        
    def load_fasta(self,filename):
        '''Load sequences from fasta file
        
        All sequences must be the same length and the correct length for the model  
        
        Headers are expected to have the form
        
        >seqname description
        
        And if description contains the following text
         
        (start=<seqpos_start>, end=<seqpos_end>)
        
        then seqpos is parsed out
        
        Then prediction is run on these sequences by calling self.__predict__
        
        '''
        self.__load_seqs_from_fasta__(filename)
        print('Loaded %i sequences from fasta file %s'%(self.nseqs,filename))

        # creat the predict model - will fail if no seqs stored
        self.__create_model__()
        
        # run predictions and store layers of predict model
        print('Running predictions on %i sequences of length %i'%(self.nseqs,self.seqlen))
        self.__predict__()
        
        print("Analyzing prediction results...")
        self.__analyze_seqs__()
        

    
    def load_seqs(self,seqs,seqpos=None):
        '''Load a set of sequences in one-hot encoded format
        This should be a numpy array of shape
        
        (nseqs,4,seqlen)
        
        The seqs are stored and the concatenated sequences are automatically created and stored too
        
        Then prediction is run on these sequences by calling self.__predict__
        '''
        
        # load sequences into correct attributes for downstream methods
        seqnames=['Sequence %s'%i for i in range(seqs.shape[0])]
        self.__load_seqs__(seqs,seqpos,seqnames)         
        
        # creat the predict model - will fail if no seqs stored
        self.__create_model__()
        
        # run predictions and store layers of predict model
        print('Running predictions on %i sequences of length %i'%(self.nseqs,self.seqlen))
        self.__predict__()
        
        print("Analyzing prediction results...")
        self.__analyze_seqs__()
        
    

class baseGenomePredict(baseSeqPredict):
    '''An abstract base class for predicting on genomes

    Loads the full genome and does a prediction on the full genome
    Derived classes can then add additional functionality like predicting
    on all promoters or arbitrary regions
    '''    
    
    def __init__(self, model_name_list=None, model_location=CONFIG.model_json_dir,genome='ecoli'):
        '''Derived constructor that instantiates the genomes.  
        
        For the genome argument, two options are supported
        genome='ecoli' loads the ecoli genome from the database
        genome={'fasta':faname,'gff':gffname} loades from a fasta/gff file combo
        genome={'gb':genbank_file} loads from genbank file
        
        '''
        
        super().__init__(model_name_list, model_location)
        
        # create the correct genome object
        if isinstance(genome,str):
            assert genome=='ecoli', 'Only supporting ecoli genome for now'
        
            # load genome object and annotations
            # right now only supporting  ecoli
            self.genome=genomes.ecoliGenome()
            
            
        elif isinstance(genome,dict):
            if len(genome.keys())==2:
                required_keys = {"fasta", "gff"}
                if not required_keys.issubset(genome):
                   raise Exception('genome dictionary must have keys %s'%required_keys)
                    
                self.genome=genomes.fileGenome(fasta_file=genome['fasta'],
                                               gff_file=genome['gff'])
            elif len(genome.keys())==1:
                required_keys = {"gb"}
                if not required_keys.issubset(genome):
                   raise Exception('genome dictionary must have keys %s'%required_keys)
                    
                self.genome=genomes.fileGenome(genbank_file=genome['gb'])
                
            else:
                raise Exception('Received unexpected genome dictionary argument')
            
            
        else:
            raise Exception('genome argument must be a string or dictionary')

        # get info from genome object        
        self.annots=self.genome.annots
        self.genes=self.genome.getGenes()
        self.known_sites=self.genome.getTFKnownPeaks()
        
        
        # these are the attributes to store the results of the genome wide prediction
        # these are separate from the attributes for storing sequences common to all
        # derived classes of baseSeqPredict but still uses the same self.predict_model
        self.full_conv=None # first two layers of predict model on genome
        self.fullFRSumConv=None
        
        self.fullConv2D = None
        self.fullConv2DPos = None
        
        # the sum of the predictions on both strands in self.ksize windows at each position
        self.fullWinSum=None
        
        # Percentiled fullWinSum by making the average value 0 and the top value 1
        self.fullWinSumMean = None # shape (1,1,ntfs) 
        self.fullWinSumCenteredMax=None   # shape (1,1,ntfs)
        self.fullWinSumPercentile=None  # (fullWinSum - fullWinSumMean)/fullWinSumCenteredMax
        
        # run the genome wide prediction        
        self.__genomewidePredict__()
        
    
    def getAnnotsInRegion(self,start,stop):
        '''Return a data frame of genes that overlap the region start-stop'''
    
        overlapping = self.annots[(self.annots['start'] <= stop) & (self.annots['stop'] >= start)]
        
        return overlapping
    
    def plotSeqHeatmapSummary(self, inds=None, annots=None, seqposlist=None, mode=1, vmax=None, vmin=None):
        '''Plot heatmap on loaded region - at this level of inheritance we add
        the calculation of vmin and vmax over genome but we still do not have loaded
        sequences
        
        mode = (1) plot self.winSum (2) plot self.Conv2D
        
        '''
                
        # get vmin and vmax over genome
        if vmin is None:
            if mode==1:
                vmin=np.min(self.fullWinSum,axis=(0,1))
            if mode==2:
                vmin=np.min(self.fullConv2D,axis=(0,1))
                
                
        if vmax is None:
            if mode==1:
                vmax=np.max(self.fullWinSum,axis=(0,1))
            if mode==2:
                vmax=np.max(self.fullConv2D,axis=(0,1))


                
        super().plotSeqHeatmapSummary(inds,annots=annots, seqposlist=seqposlist, mode=mode, vmax=vmax,vmin=vmin)
        
    def exportGenomePredictions(self,dirname):
        '''#%% Export the full genome predictions for each TF - one file per TF
        
        dirname is the full path to a directory (that must exist)
        
        '''
        
        # check to see if dirname exists and make it if not
        os.makedirs(dirname, exist_ok=True)
        
        # gpp2.fullConv2D.shape => (2, 4641652, 124) = (f,r, pos, tf)
        data = self.fullConv2D
        
        # loop through each TF
        for tf_ind,tf_name in enumerate(self.tf_list):
            
            fname="%s/%s.csv"%(dirname,tf_name)
            print('Saving %s...'%fname)
            
            slice_ = data[:, :, tf_ind]   # shape (2, 4641652)
            # Transpose to shape (4641652, 2) so each row = one index
            slice_T = slice_.T

            # Build DataFrame
            df = pd.DataFrame(slice_T, columns=["forward", "reverse"])
            df.insert(0, "pos", np.arange(slice_T.shape[0]))
            
            # Save as CSV
            df.to_csv(fname, index=False, float_format="%.3g")

    def exportAnnotGFF(self,filename,seqid=None):
        '''Export annotations to a gff
        
        Right now just handles genes and known sites
        
        Option seqid is the seqid used for each entry.  If None 
        then use the genome accession of the genome object
        
        All entries will have the same seqid
        '''
        
        # get the seqid for all entries
        if seqid is None:
            seqid = self.genome.accession
            
        # # get a dataframe annotations with fields
        # # seqid, type, ID, name, start, stop, strand,source
        # # first genes
        # df1 = self.genes.copy()
        # df1 = df1.rename(columns={"symbol": "name"})
        # df1["ID"] = df1.index
        # df1["source"] = '.'
        
        # # now known sites
        # df2 = self.known_sites.copy()
        # df2 = df2.rename(columns={"tf": "name"})
        # df2["ID"] = df2.index
        # df2["source"] = '.'
        
        # # now concat dfs
        # df = pd.concat([df1, df2], ignore_index=True)
        
        # ddf={seqid:df}
        ddf={seqid:self.genome.annots}
        
        self.__export_annot_gff__(ddf, filename)
        print('Exported genome annotation and known sites to %s with seqid %s...'%(filename,seqid))
        
        
    def __genomewidePredict__(self):
        '''Perform a prediction on the whole genome and save results in attributes'''
        
        # get the full genome
        ss=self.genome.getSubseq(extra_dim_end=True,concat=True)
        ss_len=ss.shape[2]
        
         
        print('Building genomewide prediction model...')
        self.predict_model, self.predict_model_params=model_predict_create.buildPredictionModelFromWeighs(self.weight_dict,ss_len)
        self.layers=['conv','FRSumConv','pool']
        
        # only interested in the conv and FRSum layer for now
        print("Performing genomewide prediction...")
        layers=['conv','FRSumConv']
        layers = getLayerOutput(self.predict_model,ss,layers)
        self.full_conv=layers[0].numpy()
        self.fullFRSumConv=layers[1].numpy()
        
        # now reshape the conv layer to 2D by unconcatinating
        # forward and reverse strands
        #############
        # TODO conv2d and winsum should realy be calculated using the TF model!!!!
        ############
        print("Analyzing genomewide prediction results...")
        conv2D,pos=model_disect.convReshape2D(self.predict_model,self.full_conv)
        self.fullConv2D = np.squeeze(conv2D)
        self.fullConv2DPos = pos
                
        # the sum of the predictions on both strands in kernel size windows at each position
        (mfit,mfitc,biases)=tf_util.getModelMotifs(self.predict_model)
        self.ksize=mfit[0].shape[1]
        self.fullWinSum=model_disect.calcWindowSum(conv2D,self.ksize)
        
        # now lets percentile the fullWinSum by making the average value 0 and the top value 
        self.fullWinSumMean=self.fullWinSum.mean(axis=1, keepdims=1) # shape (1,1,ntfs)
        centered=self.fullWinSum-self.fullWinSumMean
        
        self.fullWinSumCenteredMax=centered.max(axis=1, keepdims=True)  # shape (1,1,ntfs)
        self.fullWinSumPercentile=centered/self.fullWinSumCenteredMax
        
        return
        
    
   

class genomePredict(baseGenomePredict):
    '''An object that takes one or more model names, and provides
    an interface to make predictions with those models on regions of a genome
    and on all promoter regions (TU start regions)

    constructor defaults to th ecoli genome built from the lab database
    but also accepts file arguments for fasta/gff 
    
    works with objects derived from the genome object in genomes.py'''
    
    
    def __init__(self, model_name_list=None, model_location=CONFIG.model_json_dir,genome='ecoli'):
        '''Derived constructor that instantiates the genomes.  ONly accepts
        genome='ecoli' (default) for now'''
        
        super().__init__(model_name_list, model_location, genome)
        
    def __repr__(self):
        """Unambiguous representation used for debugging."""
        
        return self.__str__()

    def __str__(self):
        """User-friendly string representation."""
        
        mnames = [m for m in self.tf_list]
        
        s='%s object on genome %s on %s models'%(self.__class__.__name__,self.genome.name, len(mnames))
        
        return s
    
    
    def loadRegion(self,start=None,stop=None):
        '''Load a region, build a model, and run prediction
        
        If start not given then start will be 1
        If stop not given then stop will be the end of the genome'''
        
        if start is None:
            start=1
        if stop is None:
            stop=self.genome.len

        MAXREGION=10000
        assert stop-start+1 < MAXREGION, 'Region must be less than %s'%MAXREGION
        
        # load the appropriate sequence region
        seqs=self.genome.getSubseq(start,stop)
        seqtitle='%s Genome (%s - %s)'%(self.genome.name.capitalize(),start,stop)
        
        
        self.__load_seqs__(seqs,[[start,stop]],[seqtitle])
        
        # create a model for this seqlen
        self.__create_model__()
        
        # run prediction
        self.__predict__()
        
        return
    
    def plotSeqHeatmapSummary(self, inds=None, annots=None, seqposlist=None, mode=1, vmax=None, vmin=None):
        '''Plot heatmap on loaded region with annotations'''
        
        # get the annotations
        [start,stop]=self.seqpos[0]
        annots=self.getGenesInRegion(start, stop)
        annots=[annots]
        
        
        super().plotSeqHeatmapSummary([0],annots=annots, seqposlist=self.seqpos, mode=mode, vmax=vmax,vmin=vmin)
        
        
    def rankTFsInRegion(self,tf_names=None):
        '''Given the region loaded and the predictions on those regions
        Rank each TF by fullWinSum:
       
        - take the max WinSum for each TF in this region
        - subtract fullWinSumMean to get centered values
        - divide centered values by fullWinSumCenteredMax to get normalized values
        - rank list of TFs by their normalized values
        
        Returns a dataframe with columns [tf_inds, tf, percentile]
        that lists the ranked tfs
       
        '''
        
        if self.winSum is None:
            raise Exception('Must load a region first')
        
        # get the max winsum in this region for all tfs
        max_in_region=self.winSum.max(axis=1,keepdims=1) # shape (1,1,ntf)
        
        # normalize
        max_in_region_centered=max_in_region-self.fullWinSumMean
        normalized=np.squeeze(max_in_region_centered/self.fullWinSumCenteredMax) # shape (ntfs,)
        
        # get the list of inds that sorts normalized in decending order
        tf_inds_sorted=np.argsort(normalized)
        tf_inds_sorted=tf_inds_sorted[::-1] # flip to get descending order
        
        # get all the return values sorted
        tf_names_sorted =[self.tf_list[i] for i in tf_inds_sorted]
        normalized_sorted = [normalized[i] for i in tf_inds_sorted]
        
        df=pd.DataFrame({'tf_inds':tf_inds_sorted,'tf':tf_names_sorted,'percentile':normalized_sorted})
        
        return df
    
    def plotRegionSeqResponse(self, tf_names=None, savefilename=None,maxN=5,**kwargs):
        '''Plot the seqResponse for the loaded region of the genome
        
        If start not given then start will be 1
        If stop not given then stop will be the end of the genome
        
        If tf_names is None, the plot only maxN TFs ranked by rankTFsInRegion()
        
        But right now restricted to only support regions less that
        MAXREGION=10000 length
        
        '''
        
        # get the tfs
        if tf_names is not None:
            tf_inds=[]
            for tf in tf_names:
                temp=self.getTFIndByName(tf)
                if len(temp)==0:
                    raise Exception('Could not find tf %s'%tf)
                tf_inds.append(temp[0])
        else:
            df=self.rankTFsInRegion()
            tf_inds=df.nlargest(maxN, "percentile")["tf_inds"].tolist()
        
        # set up the figure
        if ('fig' in kwargs):
            fig=kwargs.pop('fig') # not we are poping not getting
        else:
            fig=plt.figure(figsize=(28,3*len(tf_inds)), layout='constrained')
            subfigs=fig.subfigures(len(tf_inds),hspace=0.01)
            if len(tf_inds)==1:
                subfigs=[subfigs]
        
        # get the seqposition and names
        [start,stop]=self.seqpos[0]
        seqtitle=self.seqnames[0]
        
        # get annotations for this region
        annots=self.getAnnotsInRegion(start, stop)
        
        
        # loop over tfs - one row per tf
        for tt,tf_ind in enumerate(tf_inds):
            
            # get any known peaks for this TF
            tf_name=self.tf_list[tf_ind]
            highlights = self.known_sites.loc[self.known_sites['tf'] == tf_name, ['start', 'stop']].values.tolist()
            
            row_title='%s %s'%(self.tf_list[tf_ind],seqtitle)
            
            # get the max and min conv values over the full genome to scale heatmaps
            vmax=np.max(self.full_conv[:,:,:,tf_ind:tf_ind+1])
            vmin=np.min(self.full_conv[:,:,:,tf_ind:tf_ind+1])
            
            # generate the plot
            plotSeqPredict(self.conv[0:1,:,:,tf_ind:tf_ind+1],self.seqs[0],self.predict_model,seqpos=self.seqpos[0],
                           vmax=vmax,vmin=vmin,fig=subfigs[tt],title=row_title, 
                           kernel_ind=tf_ind,annot=annots, highlights=highlights, **kwargs)
            
        if savefilename is not None:
            fname="%s.png"%savefilename
            print("Saving %s..."%fname)
            fig.savefig(fname)
            plt.close(fig)
        
        return


class genomePromoterPredict(baseGenomePredict):
    '''An object that takes one or more model names, and provides
    an interface to make predictions on all promoter regions of a genome (TU start regions)

    constructor defaults to th ecoli genome but building it to be extensible
    to other genomes
    
    works with objects derived from the genome object in genomes.py'''

    def __init__(self, model_name_list=None, upstream_margin=1000, downstream_margin=400,
                 model_location=CONFIG.model_json_dir,genome='ecoli'):
        '''Derived constructor that instantiates the genomes.  ONly accepts
        genome='ecoli' (default) for now'''
        
        super().__init__(model_name_list, model_location, genome)
                
        self.upstream_margin=upstream_margin
        self.downstream_margin = downstream_margin
        
        
        self.__load_promoters__()
        
    def __repr__(self):
        """Unambiguous representation used for debugging."""
        
        return self.__str__()

    def __str__(self):
        """User-friendly string representation."""
        
        mnames = [m for m in self.tf_list]
        
        s='%s object on genome %s on %s models with %s loaded promoters (upstream %ibp, downstream %ibp)'%(self.__class__.__name__, self.genome.name, len(mnames),
                                                                                                       self.nseqs,self.upstream_margin,self.downstream_margin)
        
        return s
    
    
    def __load_promoters__(self):
        '''Load all promoter regions defined as windows around the start
        of unique TU start genes
        
        Each "promoter" region goes from 
        start-upstream/downstream_margin to stop+upstream/downstream_margin 
        where upstream/downstream depends on the strand
        
        Note that each start gene can belong to multiple TUs'''
        
        upstream_margin=self.upstream_margin
        downstream_margin=self.downstream_margin
    
        ########################################
        # get the table of TU start positions
        print('Getting TU information...')
        ecolidb=ecoliDB()
        self.promoters=ecolidb.getTUGeneStarts()
        ecolidb.close()
            
        # add columns for the start and stop 
        self.promoters['promoter_start']=self.promoters.apply(lambda row: row['tu_start']-upstream_margin if row['strand']=='+' else row['tu_start']-downstream_margin, axis=1)

        self.promoters['promoter_stop']=self.promoters.apply(lambda row: row['tu_start']+downstream_margin if row['strand']=='+' else row['tu_start']+upstream_margin, axis=1)

        # make sure regions are within 1 and length of genome and shift the region up or down as necessary to keep the length
        # this should only apply to the first and last
        ind = self.promoters.index[self.promoters['promoter_start'] < 1].to_list()
        for i in ind:
            shift = -self.promoters.loc[i, 'promoter_start'] + 1
            self.promoters.loc[i, 'promoter_start'] += shift
            self.promoters.loc[i, 'promoter_stop'] += shift

        ind = self.promoters.index[self.promoters['promoter_stop'] > self.genome.len].to_list()
        for i in ind:
            shift = self.genome.len-self.promoters.loc[i, 'promoter_stop'] + 1
            self.promoters.loc[i, 'promoter_start'] -= shift
            self.promoters.loc[i, 'promoter_stop'] -= shift

        self.promoters['promoter_length']=self.promoters['promoter_stop']-self.promoters['promoter_start']+1

        ########################################        
        # now get the actual subsequences
        print('Getting %s promoter sequences...'%len(self.promoters))

        starts=self.promoters['promoter_start'].to_list()
        stops=self.promoters['promoter_stop'].to_list()
        seqs=self.genome.getMultSubseqs(starts,stops,concat=False, extra_dim_end=False)
        
        ########################################
        # now lets load the sequences into object
        seqpos=list(zip(starts,stops))
        seqnames=self.promoters['tu_names']
        self.__load_seqs__(seqs,seqpos,seqnames) 
               
        ########################################
        # now run predction on whole set and analzye results
        print("Running prediction on promoters...")
        self.__create_model__()
        self.__predict__()    
        self.__analyzePromoters__()
        
        
    def __analyzePromoters__(self):
        '''Perform various analyzes of the results of the promoter wide prediction
        This includes percentiling (normalizing the scores to max) the promoters for each TF'''
        
        print("Analyzing promoter prediction results...")
        self.__analyze_seqs__()        
        
        return
        
        
    def getTFNamesForPromotersByPerc(self,prom_inds=None, tf_names=None,perc_th=0.2,mode=1, savefilename=None):
        '''given a promoter indices, return the names of tfs that for 
        which the TF scores above perc_th
        
        Limit to the tf names in tf_names if given
        
        If prom_inds is None, return for all promoters
        
        Returns a dataframe with columns ['ind','tu_name','num_tfs','tfs','percentiles','ranks']
        
        If savefilename is not None, the save the df to savefilename where the
        list of tfs becomes a ; seperated string.  
        
        modes:
            1 = winSum
            2 = fmap
        '''
                
        # get list of tf indices or all if tf_names is None
        tf_inds=self.getTFIndByName(tf_names)
        
        # Get the correct scores
        if mode==1:
            perc=self.winSumPercentile[:,tf_inds]
            ranks=self.winSumRanks[:,tf_inds]
        if mode==2:
            perc = self.fmapPercentile[:,tf_inds]
            ranks= self.fmapRanks[:,tf_inds]
            
        if prom_inds is None:
            prom_inds=list(range(len(self.promoters)))
            
        df=pd.DataFrame(columns=['ind','tu_name','num_tfs','tfs','percentiles','ranks'])
        for ind in prom_inds:
            tu_name=self.promoters.loc[ind]['tu_names']
            indices = np.where(perc[ind,:] >= perc_th)[0] # this also indices tf_inds
            indices = indices[np.argsort(ranks[ind, indices])]
                                    
            tf_names=[self.tf_list[tf_inds[i]] for i in indices]
            percentiles=[perc[ind,i] for i in indices]
            ranklist=[ranks[ind,i] for i in indices]
            
            df.loc[len(df)] = {"ind":ind, "tu_name": tu_name, "num_tfs": len(tf_names),"tfs":tf_names,
                               "percentiles":percentiles,'ranks':ranklist}
        
        if savefilename is not None:
            df_temp=df.copy()
            df_temp["tfs"] = df_temp["tfs"].apply(lambda x: ";".join(map(str, x)))
            df_temp["percentiles"] = df_temp["percentiles"].apply(lambda x: ";".join(map(str, x)))

            print("Saving %s..."%savefilename)
            df_temp.to_csv(savefilename, index=False)
        
        return df
            
    def exportPromotersFasta(self,filename):
        '''Export the promoter sequences as a fasta file'''
        
        self.__export_seqs_to_fasta__(filename)
        print('Exported %i sequences to fasta file %s'%(self.nseqs,filename))
        
        
    def getPromoterInfoByGene(self,gene_list):
        '''Get the indices and dataframe rows for promoters that contain any of the genes
        in gene_list
        
        returns inds,matches
        
        inds = the indices
        matches = dataframe of rows with TU information
        '''
                
        # Get matching rows
        pattern = '|'.join(map(re.escape, gene_list))
        matches = self.promoters[self.promoters['tu_names'].str.contains(pattern, case=False,na=False)]
        
        # Get their indices
        inds = matches.index.tolist()
        
        return inds, matches
    
    def plotSeqHeatmapSummary(self, inds=None, annots=None, seqposlist=None, mode=1, vmax=None, vmin=None):
        '''Plot heatmap on loaded region with annotations'''
        
        # get the annotations for these regions
        annots=[]
        seqposlist=[]
        for ind in inds:
            prom=self.promoters.loc[ind]
            genes=self.getGenesInRegion(prom['promoter_start'], prom['promoter_stop'])
            annots.append(genes)
            seqposlist.append(self.seqpos[ind])
                    
        super().plotSeqHeatmapSummary(inds=inds,annots=annots,
                                      seqposlist=seqposlist,mode=mode,
                                      vmax=vmax, vmin=vmin)
    
    def plotSeqResponseByInds(self,inds=None, fig=None, tf_names=None,savefilename=None,perc_th=0.1,mode=1, maxN=10, **kwargs):
        '''Calculates the annotations in promoters given by the indices in ind
        and then calls base class plotSeqResponseByInds
        
        if tf_names is not given, then for each sequence, get the TFs where the TF
        scores in the top perc_th for that TF limited to the top MaxN tfs by percentile
        
        if savefilename is given, save images and not show
        savefilename is the filename prefix that will be used for each save appended
        with the promoter tu name(s)
        e.g.
        savefilename="../promoter_" => 
            ../promoter_pdhR,pdhR-aceE-aceF-lpd.png
            ../promoter_ung.png
            etc...
            
        mode is passed to getTFNamesForPromotersByPerc to determine how to decide what TFs to plot
            
        We eventually call plotSeqPredict with plots seqlogos and heatmaps, the latter from self.conv 
        for each selected promoter
        '''
        
        # Basically gathers information about the TUs in inds and then loops
        # through each promoter and calls baseSeqPredict.plotSeqResponseByInds
        # on that sequence/promoter to do the plotting
        # Also figures out what TFs to plot for each promoter if this is not given
        
        # get the annotations and promoter/TU names for these regions
        annots=[]
        prom_names=[]
        
        # if none inds then do all promoters
        if inds is None:
            inds=range(self.nseqs)
            
        # get the promoters/prom names, genes in each region, 
        for ind in inds:
            prom=self.promoters.loc[ind]
            genes=self.getAnnotsInRegion(prom['promoter_start'], prom['promoter_stop'])
            annots.append(genes)
            prom_names.append(prom['tu_names'])
        
        # get the percentiled data if we need to auto select TFs
        if tf_names is not None:
            perc_th=-1e10 # if we provide TF names, then we do not filter on perc_th
        tfmap=self.getTFNamesForPromotersByPerc(perc_th=perc_th, mode=mode)
        
                        
        # iterate over sequences in case we want to do different things for each sequence
        # like plot different TFs
        for ii,i in enumerate(inds):
            
            print('Generating plot for %s...'%prom_names[ii])
        
            # if tf_names is None, get the TFs that score above perc for this seq
            # and order them by score
            perc=tfmap.loc[i]['percentiles']
            rank=tfmap.loc[i]['ranks']

            if tf_names is None:
                tf_names_i=tfmap.loc[i]['tfs']
            
                # take top MaxN only
                tf_names_i=tf_names_i[:maxN]
                perc=perc[:maxN]
                rank=rank[:maxN]

            else:
                tf_names_i=tf_names
                
                tf_inds=[self.getTFIndByName(n)[0] for n in tf_names_i]
                perc=[perc[ind] for ind in tf_inds]
                rank=[rank[ind] for ind in tf_inds]
        
            
            if len(tf_names_i)==0:
                print('No TFs above percentile for %s'%prom_names[ii])
                continue
            
            # get the row-titles for the plots to come these are tf name and info in parentheses
            row_titles=['%s (percentile %0.2f, rank %i)'%(tfn,p,r) for tfn,p,r in zip(tf_names_i,perc,rank)]
            
            # get the highlight regions for the tfs in tf_names_i
            highlights=[]
            for tfn in tf_names_i:
                hl = self.known_sites.loc[self.known_sites['tf'] == tfn, ['start', 'stop']].values.tolist()
                highlights.append(hl)
            
            # create the filename for this plot
            fnames=None
            if savefilename is not None:
                fname="%s%s"%(savefilename,prom_names[ii])
                fnames=[fname]
            
            thisannot=[annots[ii]]
            super().plotSeqResponseByInds([i],annots=thisannot, tf_names=tf_names_i, highlights=highlights, 
                                          savefilename=fnames,row_titles=row_titles,**kwargs)
            
        
    
    def plotSeqResponseByGene(self,gene_list, fig=None, tf_names=None, savefilename=None,maxN=10,**kwargs):
        '''Plot seq response for promoters that contain tany of 
        the genes in the gene list
        
        '''
        
        inds,tuinfo=self.getPromoterInfoByGene(gene_list)
        
        self.plotSeqResponseByInds(inds, tf_names=tf_names, savefilename=savefilename, maxN=maxN, **kwargs)
        
        return inds,tuinfo
        

    #-------------------------------------------------------------
    #%% FIGURES
    #-------------------------------------------------------------

def plotSeqPredict(conv,seq, model,seqpos=None,fig=None,heatmap=True,seqlogo=True,baseseq=True,
                   vmax=None,vmin=0,highlights=None, annot=None, title=None, xlabel=None, kernel_ind=0, num_xtick=5,
                   highlight_bases = None, extra_heatmaps_data = None,colors = None, **kwargs):
    '''Plot a heatmap and seqlogo with optional highlighted regions and annotations
    
    Inputs
    - conv - the convolution layer for a sequence
    - seq - the actual input sequence
    - seqpos - the [start, stop] position of the sequence
    - model - the trained prediction model (supports stacked) - the predictions are pulled directly from this
    
    Options
    - heatmap (default true) - draw heatmap or not
    - vmax, vmin - scale ranges for imshow heatmap for conv (default None)
    - seqlogo (default true) - draw seqlogo or not
    - highlight - list of [start,stop] regions to highlight in cyan
    - baseseq (default true) - plot the sequence 
    - annot - dataframe of annotatoins, expects symbol,strand, start, stop cols
    - fig - optional handle for figure on which to plot
    - kernel_ind is the optional index for a kernel in a stacked model (default 0 which should work with any model)
    - num_xtick = number of xticks evenly spaces (default 5)
    -highlight_bases: a binary list with a 1 or 0 at each position (1 = highlight)

    Add Extra Heatmaps Info:
        Arguments:
            -extra_heatmaps_data: a list of list of data that you wish to plot
        Optional(kwargs):
            -extra_mmin(list): Minimum valueS for heatmapS
            -extra_mmax(list): Maximum ValueS for heatapS
            -extra_heat_names(list): y-lables
            
            FOR OPTIONAL ARGS, PASS NONE IN NOT NEEDED POSITIONS

    
    annots and highlights are provide in native sequence coordinates as determined by
    seqpos
    
    hightlights are passed plot_seq_logo
    
    Replaces tf_util.plotSingleSeqResponse for general prediction use.  A cleaner interface tailored
    for general preciction as opposed to BoltzNet training validation
    
    For fastest testing and use set seqlogo and baseseq to False since drawing all the bases
    takes a longer time
    
    TODOs 
    - add highlights support
     
    
    '''

    # NB: all plots is done with xlims from 0 to seqlen.  annots and highlights and any other
    # seq based coordinates get translated according to seqpos 


    ###############################    
    # layout the figure based on options
    ###############################    
    mosaic=[]
    height_ratios=[]
    if annot is not None:
        mosaic.append(['annot'])
        height_ratios.append(3)    
    if seqlogo:
        mosaic.append(['seqlogo'])
        height_ratios.append(2)
    if extra_heatmaps_data is not None:
        for x in range(len(extra_heatmaps_data)):
            mosaic.append(['ex_heat_%s' % x])
            height_ratios.append(0.75)
    if heatmap:
        mosaic.append(['fwd'])
        mosaic.append(['rev'])
        height_ratios.extend((0.75,0.75))
    if baseseq:
        mosaic.append(['seq'])
        height_ratios.append(0.25)
  
        
    # future support for stacked
    nstacked=1            
        
    if (fig):
        axs=fig.subplot_mosaic(mosaic, gridspec_kw={'height_ratios': height_ratios},sharex=True)
    else:
        fig,axs=plt.subplot_mosaic(mosaic,figsize=[22,5*nstacked], gridspec_kw={'height_ratios': height_ratios},sharex=True)

    
    
    seqlen=seq.shape[1]

    ###############################
    # do the plots based on options
    ###############################
    
    if annot is not None:
        
        plotAnnotationTrack(axs['annot'],annot,seqpos,axs['annot'].get_xlim(),axs['annot'].get_ylim())
        
    
    if seqlogo:
        
        # create revcomp version of seq
        seqexpanded=np.expand_dims(seq, axis=0)
        doubleseq=sequence.concatenate_revcomp(seqexpanded)
        doubleseq=np.expand_dims(doubleseq, axis=-1) # need to make (1,4,slen,1)
        
        # get representation of base contributions where sout will be
        # a weighted one-hot encoding of shape (1,4,slen,1)
        # where at each position, only the base at that position is non-zero
        # but the actual value of that non-zero entry is the weight contribution
        out_dict=tf_util.getMotifWeightedSeqContribution(model,doubleseq,kernel_ind=kernel_ind)
        sout=out_dict['sout']
        
        # need to add the forward and reverse strand contributions 
        slend=sout.shape[2]
        slen=int(slend/2)
        temp=sout[:,:,slen:slend,:]
        temp=sequence.revcomp(temp[0,:,:,0])
        temp=np.reshape(temp,(1,4,temp.shape[1],1))
        sout_combined=sout[:,:,0:slen,:]+temp
        

        # translate hightlights to 0,seqlen coordinates
        shifted_highlights=None
        if highlights is not None:
            shifted_highlights=[[x-seqpos[0],y-seqpos[0]] for [x,y] in highlights] 

        # the actual plot        
        util.plot_seq_logo(sout_combined, ax=axs['seqlogo'], title=title, 
                           fs=12,fontweight='bold',fontfamily='Helvetica',highlightRegion=shifted_highlights, **kwargs)
        
        axs['seqlogo'].spines['bottom'].set_visible(False)
        axs['seqlogo'].spines['top'].set_visible(False)
        axs['seqlogo'].spines['right'].set_visible(False)
        
        
        
        
    if extra_heatmaps_data is not None:
        for x in range(len(extra_heatmaps_data)):
            
            if colors is None:
                colors = ['Blues','Reds','Greens','Yellows']
            
            extra_mmin_1 = kwargs.get('extra_mmin',None)[x]
            extra_mmax_1 = kwargs.get('extra_mmax',None)[x]
            extra_heat_names_1 = kwargs.get('extra_heat_names',None)[x]
            addHeatMap(axs,x, extra_heatmaps_data[x], colors[x],
                       extra_mmin_1=extra_mmin_1,extra_mmax_1=extra_mmax_1, 
                       extra_heat_names_1=extra_heat_names_1,**kwargs)
        
        
        
    if heatmap:
        # Results pulled directly from conv layer as a conv2D tensor
        
        # convert conv layer to 2d with seperate fwd and rev dims
        conv2D,pos=model_disect.convReshape2D(model,conv,pad=True)        
        conv2D=np.squeeze(conv2D)
        if vmax is None:
            vmax=np.max(conv2D)
        if vmin is None:
            vmin=np.min(conv2D)
        
        
        # plot the heatmaps with imshow
        axs['fwd'].imshow(conv2D[0:1],aspect='auto',vmin=vmin,vmax=vmax,cmap='Greens',origin='upper') 
        axs['rev'].imshow(conv2D[1:],aspect='auto',vmin=vmin,vmax=vmax,cmap='Oranges',origin='upper') 
        
        axs['fwd'].set_yticks([])
        axs['rev'].set_yticks([])
        
        # need to add position ticks if not baseseq
        if baseseq==False:
            tickspacing=int(seqlen/num_xtick)
            xpositions=np.arange(0,seqlen,tickspacing)
            axs['rev'].set_xticks(xpositions)
            if seqpos is None:
                axs['rev'].set_xticklabels(xpositions+1,rotation=0)
            else:
                axs['rev'].set_xticklabels(xpositions+seqpos[0],rotation=0)   
                
        # add the title here if no seqlogo
        if not seqlogo:
            axs['fwd'].set_title(title)
    
    
    if baseseq:
        cc=[0.5, 0.5, 0.5]
        refcolors={'A': cc,'T': cc, 'C': cc, 'G': cc,}
        
        seqexpanded=np.expand_dims(np.expand_dims(seq, axis=0), axis=-1) # need to make (1,4,slen,1)
        util.plot_seq_logo(seqexpanded, colors=refcolors, ax=axs['seq'], title="", highlight_bases = highlight_bases ,**kwargs)
        axs['seq'].set_yticks([])
        axs['seq'].spines['top'].set_visible(False)
        axs['seq'].spines['right'].set_visible(False)
        axs['seq'].spines['left'].set_visible(False)
        axs['seq'].spines['bottom'].set_visible(False)
        
        # xtick position labels

            
        tickspacing=int(seqlen/num_xtick)
        xpositions=np.arange(0,seqlen,tickspacing)
        axs['seq'].set_xticks(xpositions)
        if seqpos is None:
            axs['seq'].set_xticklabels(xpositions+1,rotation=0)
        else:
            
            axs['seq'].set_xticklabels(xpositions+seqpos[0],rotation=0)
        
    if xlabel is not None:
        fig.supxlabel(xlabel,fontfamily='Helvetica')
        
    if kwargs.get('return_fig'):
        return fig
    
    elif kwargs.get('return_axs'):
        return axs
    else:

        return


def plotAnnotationTrack(ax, annot, seqpos, xlim, ylim, fontsize=8):
    """
    Draw one annotation track for the genomic window [seqpos[0], seqpos[1]].

    annot  : DataFrame with columns ['type','strand','start','stop','symbol'] (global coords)
    seqpos : tuple (win_start, win_end) in GLOBAL genome coordinates (inclusive)
    xlim   : IGNORED for computation (we set xlim locally to the window length)
    ylim   : kept for API compatibility (not required by dna_features_viewer)
    """

    # Ensure ScalarFormatter so dna_features_viewer’s initialize_ax won’t choke
    ax.xaxis.set_major_formatter(ScalarFormatter())  # avoids the FuncFormatter error
    
    # set ylims so features are more centered vertically
    ax.set_ylim((-1,1))

    feat_col_map = {
        "genes": "lightblue",
        "gene": "lightblue",
        "CDS": "blue",
        "TF_binding_site": "plum",
        "promoter": "lime",
        "tRNA": "gold",
        "region": 'lightgray',
        'mobile_genetic_element': 'yellow',
        'ncRNA': 'cyan', 
        'exon': 'lightsteelblue',
        'rRNA': 'indianred', 
        'pseudogene': 'darkgray', 
        'sequence_feature': 'tomato',
    }
    default_col = "lightblue"

    #window bookkeeping (GLOBAL -> LOCAL)
    win_start, win_end = int(seqpos[0]), int(seqpos[1])
    win_len = int(win_end - win_start + 1)               # local coordinates will be 1..win_len
    x_lim_local = (1, win_len)

    features = []
    for _, a in annot.iterrows():
        # Global bounds, ensure start < end regardless of strand
        g0 = int(min(a["start"], a["stop"]))
        g1 = int(max(a["start"], a["stop"]))

        # Skip if outside the window
        if g1 < win_start or g0 > win_end:
            continue

        # Clip to window and convert to LOCAL (1-based) coordinates
        s_local = max(g0, win_start) - win_start + 1
        e_local = min(g1, win_end)   - win_start + 1

        # Strand mapping
        s = a.get("strand", ".")
        strand = +1 if s == "+" else (-1 if s == "-" else None)

        features.append(
            GraphicFeature(
                start=s_local,
                end=e_local,
                strand=strand,                        # +1, -1 -> arrows; None -> rectangle
                color=feat_col_map.get(a["type"], default_col),
                label=str(a.get("symbol", "")),
                fontdict={'fontsize':fontsize}
            )
        )

    # Build a record in LOCAL coordinates (1..win_len)
    record = GraphicRecord(
        sequence_length=win_len,
        features=features,
        first_index=1,                                  # show 1-based ticks if you enable a ruler
    )

    # Plot ONLY the features (no sequence line or ruler); use LOCAL x-limits
    # NEED THE RULER below to be able to sync axes with other plots.  e.g. with_ruler=True
    record.plot(ax=ax, with_ruler=True, draw_line=False, x_lim=x_lim_local)
    ax.set_xlim(*x_lim_local)                           # keep the axis consistent
    
    
    
    return ax
 
def addHeatMap(axs,plot_ind, data, color,**kwargs):
    '''Adds Addtional Heatmap for plotSeqPredict(),
    Mandatory:
        -axs: Plot
        -plot_ind: Index of addtional heatmap
        -data: Data
        -color: Color scheme for plot
    
    Optional:
        -extra_mmin: Minimum value for heatmap
        -extra_mmax: Maximum Value for heatap
        -extra_heat_names: y-lables
    '''
    
    if kwargs.get('extra_mmin_1',None)is not None:
        mmin = kwargs.get('extra_mmin_1')
    else:
        mmin = np.min(data)
    if kwargs.get('extra_mmax_1',None)is not None:
        mmax =  kwargs.get('extra_mmax_1')
    else:
        mmax = np.max(data)

    data = np.atleast_2d(data) 
    
    
    axs['ex_heat_%s' %plot_ind].imshow(data,aspect='auto',vmin=mmin,vmax=mmax,cmap=color,origin='upper')
    
    if kwargs.get('extra_heat_names_1',None) is not None:
        try:
            x = kwargs.get('extra_heat_names_1')
            if isinstance(x, list):
                axs['ex_heat_%s' %plot_ind].set_yticks(np.arange(0,len(kwargs.get('extra_heat_names_1')),1)) 
            else:
                axs['ex_heat_%s' %plot_ind].set_yticks([0])
            axs['ex_heat_%s' %plot_ind].set_yticklabels(kwargs.get('extra_heat_names_1'),fontsize=8)
        except:
            pass
        
    return
    
    
def scatter(X,Y,xlabel,ylabel,title, leg_label='', norm=False, ls = True, show = True):
    '''Makes scatter plots with least squares fit'''
    color = (random.random(), random.random(), random.random())
    plt.figure()
    plt.rcParams.update({'font.size': 16})
    
    if norm is True:
        X = X/np.max(X)
        Y = Y/np.max(Y)
        xlabel = 'Normalized ' + xlabel
        ylabel = 'Normalized ' + ylabel
    

    if ls is True:
        Xls = X.reshape(-1,1)
        Yls = Y.reshape(-1,1)
            
        A = np.hstack([Xls, np.ones((len(Xls), 1))])
        xhat, residuals, rank, s = np.linalg.lstsq(A, Yls, rcond=None)     
        
        r = np.corrcoef(X, Y)[0, 1]

        lin = np.arange(0,np.max(X)+.5,.05)
        ls_line = xhat[1]+xhat[0]*lin

        plt.plot(lin,ls_line,c=color,label='LS Line: y = %sx +%s; r = %s' % (str(np.round(xhat[0],3)),str(np.round(xhat[1],3)),str(np.round(r,5))))

    
    plt.scatter(X,Y,c=color,label=leg_label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc = 'upper left')
    
    if show is True:
        plt.show()
    return plt




    #-------------------------------------------------------------
    #%% MODEL COMPARISON
    #-------------------------------------------------------------



def modelCompareOAff(model_1, model_2, seqs, tf_name = '',  layer_number_1 = None, layer_number_2 = None):
    '''Compares the overall affinity scores of two models
    on the same data by generatng a scatter plot for each of the models overall afinty score pedictions. 
    Seqs should be encoaded sequences (not concatenated)
    The models must have the same input sequence length and match the length of sequences in input dataset

    Params:
        model_1
        model_2
        seqs
        layer for comparison model 1(Stacked model)
        layer for comparison model 2(Stacked model)
        
        Generates Scatter plot'''
    
    #Prep Seqs
    X=np.reshape(seqs,(len(seqs[:,0,0]),4,len(seqs[0,0,:]),1))
    data = sequence.concatenate_revcomp(X)
    
    #make prediction on pooling layer
    layer_outputs_old = np.array(getLayerOutput(model_1,data,["pool"]))
    layer_outputs_new = np.array(getLayerOutput(model_2,data,["pool"]))

    #Extract requested model layer
    if layer_number_1 is not None:
        layer_outputs_old  = layer_outputs_old[:,:,layer_number_1]
    if layer_number_2 is not None:
        layer_outputs_new  = layer_outputs_new[:,:,layer_number_2]
    
   
    
    fmaps_old = layer_outputs_old.flatten()
    fmaps_new = layer_outputs_new.flatten()
        
    x = np.arange(0,6,1)
    
    plt.scatter(fmaps_old,fmaps_new,c='blue',label='Overall Affinity Score')
    plt.plot(x,x,c='black')
    plt.xlabel('New Model Overall Affinity')
    plt.ylabel('Old model Overall Affinity')
    plt.title('Scatter for Overall Affinity %s' % tf_name)
    plt.legend(loc = 'upper left')
    plt.show()
        
    return


    
def modelCompareCov(old_model, new_model,seqs):
    '''Compares the coverage of two models
    on the same data. The models must have the same 
    input sequence length and match the length of sequences in input dataset.
    
    Generates matrix of True or False values
    
    modelCompareCov(model_1, mdoel_2,data_name,data_dir=CONFIG.model_dir)'''
    #Prep Seqs
    X=np.reshape(seqs,(len(seqs[:,0,0]),4,len(seqs[0,0,:]),1))
    data = sequence.concatenate_revcomp(X)
    
    old_pred = old_model.predict(data)
    new_pred = new_model.predict(data)
    
    print('Does the new model output match the old one: %s' % np.equal(old_pred,new_pred))
    
    return
    
    
