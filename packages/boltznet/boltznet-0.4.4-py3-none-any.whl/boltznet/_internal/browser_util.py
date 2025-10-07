#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for using Browser to create TF browsers

@author: jgalag
"""
#Only print differences in getBRowserMask KK

from . import CONFIG
from .browser import Browser
import numpy as np
from os.path import exists
from .factory import Factory



# import matplotlib.pyplot as plt

# from dna_features_viewer import BiopythonTranslator
# from bokeh.plotting import figure, show
# from bokeh.layouts import gridplot, column
# from bokeh.models import Span, Text, LabelSet,ColumnDataSource,Range1d,WheelZoomTool

# from dna_features_viewer import GraphicFeature, GraphicRecord,BiopythonTranslator

# from Bio import SeqIO
# import sequence
# import tf_util
# import util
# import os
# import itertools

dataroot=CONFIG.server_data_root
memeroot=CONFIG.server_meme_root

# These are definitions of regions to mask since they are known artifacts
# pBAD artifacts = pbad_regions
araC_region=np.array([70000,71360])
leuL_region=np.array([83400,84400])
araJ_region=np.array([412000,413000])
# cyoA_region=np.array([451400,452400])
cspE_region=np.array([656800,657800])
lnt_region=np.array([689000,689400])
nagE_region=np.array([703500,704000])
chiP_region=np.array([707700,708700])
sucC_region=np.array([765500,766500])
# glnH_region=np.array([847600,849000])
mntS_region=np.array([852500,853300])
# ompF_region=np.array([986800,988000])
ssuE_region=np.array([997200,998200])
ompA_region=np.array([1019000,1020500])
dhaR_region=np.array([1250600,1251600])
dhaR_region=np.array([1250700,1251200])
ydcL_region=np.array([1502800,1504400])
yddM_region=np.array([1552500,1553000])
ydeO_region=np.array([1582300,1582900])
hipB_region=np.array([1592000,1593000])
uxaB_region=np.array([1610200,1611400])
yoaL_region=np.array([1901200,1902300])
cspC_region=np.array([1907400,1908600])
araF_region=np.array([1986000,1987000])
ugd_region=np.array([2099400,2101200])
intZ_region=np.array([2559600,2561200])
yffQ_region=np.array([2563000,2564500])
yqcC_region=np.array([2923900,2925000])
lysA_region=np.array([2978800,2979200])
yqeF_region=np.array([2984000,2984500])
srrS_region=np.array([3055600,3056600])
yggI_region=np.array([3087500,3089000])
yghF_region=np.array([3119000,3119800])
ribB_region=np.array([3184000,3185500])
cspA_region=np.array([3719600,3720400])
yiaT_region=np.array([3742300,3743000])
glmSU_region=np.array([3914500,3916000])
ilvXL_region=np.array([3949400,3951400])
ilvC_region=np.array([3957600,3958600])
aslB_region=np.array([3982000,3983000])
mobB_region=np.array([4040000,4041000])
glnA_region=np.array([4057800,4058800])
birA_region=np.array([4171500,4172000])
murB_region=np.array([4171500,4172050])
yjaA_region=np.array([4212850,4213250])
fimB_region=np.array([4539500,4540700])

# kbaZ_region=np.array([3278300,3279300])
# yraH_region=np.array([3281400,3282300])

pbad_regions =[araC_region,	araF_region,	araJ_region,	aslB_region,	birA_region,	
                chiP_region,	cspA_region,	cspC_region,	cspE_region,	
                dhaR_region,	dhaR_region,	fimB_region,	glmSU_region,	
                glnA_region,		hipB_region,	ilvC_region,	ilvXL_region,	
                intZ_region, leuL_region,	lnt_region,	lysA_region,	
                mntS_region,	mobB_region,	murB_region,	nagE_region,	ompA_region,	
                ribB_region,	srrS_region,	ssuE_region,	sucC_region,	ugd_region,	
                uxaB_region,	ydcL_region,	yddM_region,	ydeO_region,	yffQ_region,	
                yggI_region,	yghF_region,	yiaT_region,	yjaA_region,	yoaL_region,	
                yqcC_region,	yqeF_region] 

#FOR NOW ONLY USING A SUBSET OF THE MASKS FOR THE MOST COMMON ARTIFACTS
# pbad_regions = [araC_region, murB_region, mobB_region, yjaA_region,dhaR_region,glnA_region]

# Lac artifacts = lacI_region
lacI_region=[np.array([365500,367600])]

# NagC artifacts = nagC_regions
nagC1_region=np.array([1792,2084])
nagC2_region=np.array([702894,704338])
nagC3_region=np.array([707643,708608])
nagC4_region=np.array([1582233,1583171])
nagC5_region=np.array([1821447,1822024])
nagC6_region=np.array([1853252,1853933])
nagC7_region=np.array([2970954,2971343])
nagC8_region=np.array([3087544,3088523])
nagC9_region=np.array([3118979,3119693])
nagC10_region=np.array([3915026,3915637])
nagC11_region=np.array([4539724,4540633])
nagC12_region=np.array([4640049,4641198])

nagC_regions=[nagC1_region,	nagC2_region,	nagC3_region,	nagC4_region,	
              nagC5_region,	nagC6_region,	nagC7_region,	nagC8_region,	
              nagC9_region,	nagC10_region,	nagC11_region,	nagC12_region]

#Ribosomal Regions/ncRNA/tRNA = ncRNA_regions
# kgtP_ribosomal=np.array([2725746,2731595])
alaWX_region=np.array([2517400,2519200])
aspU_region=np.array([223408,229166])
# aspU_region=np.array([228650,229000])
glmY_region=np.array([2690800,2691800])
leuV_region=np.array([4603000,4606700])
metV_region=np.array([2930100,2931000])
metY_region=np.array([3317600,3319200])
proK_region=np.array([3707400,3708900])
ryhB_region=np.array([3580600,3583000])
serT_region=np.array([1031700,1032200])
serV_region=np.array([2726000,2726500])
thrW_region=np.array([262600,263600])
yhdZ_ribosomal=np.array([3423200,3429235])
yieP_ribosomal=np.array([3941327,3947127])

ncRNA_regions=[alaWX_region,	aspU_region,	glmY_region,	leuV_region,	metV_region,
               metY_region,	proK_region,	ryhB_region,	serT_region,	serV_region,	
               thrW_region,	yhdZ_ribosomal,	yieP_ribosomal]

# Combining the lists for each type of promoter
# NEED TO BREAK THIS OUT BY PROMOTER AT SOME POINT
chip_inducible_masks =  pbad_regions + lacI_region + ncRNA_regions + nagC_regions
chip_native_masks = lacI_region + ncRNA_regions + nagC_regions


def browserTF(tf,fwidth=14,region=[],ylims=[],showplot=1,table_tag=None,tracks=None,labels=None, data_sources: dict = None):
    ''' Create, save, and launch browser on all chip experiments for an Ecoli TF
        
        Arguments:  
            tf: tf symbol  
            fwidth: width of plot (default 14)  
            region: [start,end] of genomic region to plot - []=default=whole genome  
            ylims: ylimits on sample track - [] default is autofit  
            showplot: whether to save and show plot (1=default) or just save  
            tracks: a list that is a subset of ['known','samples','called','fimo']  
        
    '''
    chiponly=1 #TODO implement support for RNAseq
    data_sources = {} if not data_sources else data_sources
    if (temp := data_sources.get('server_data_root', None)):
        dataroot = temp
    
    
    #GET TF CHIP SEQ DATA FROM DB
    #NEED TO ADD SUPPORT RNASEQ
    # db=ecoliDB()
    factory = Factory()
    dat_obj = factory.create(data_sources.get('data_sources_type', 'ecoliDB'), data_sources=data_sources)
    
    if (chiponly==1):
        # exps_CS=db.getTFChipExperiments(tf,table_tag=table_tag)
        exps_CS = dat_obj.get_exp_info(tf=tf,table_tag=table_tag)

    # EARLY RETURN IF NO EXPERIMENTS TO PLOT    
    if (len(exps_CS)==0):
        print('No experiments to plot - skipping this TF\n')
        return
    
    # check to see if region is passed as a gene name str
    if isinstance(region,str):
        region=getRegionFromGene(region, data_sources=data_sources)
        print('Opening browser on region %d - %d'%(region[0],region[1]))
    
    
    # the temp filename for the bokeh html
    if (region==[]):
        html='%s_genome'%(tf)
    else:
        html='%s_%d_%d'%(tf,region[0],region[1])
    
    # initialize browser
    print('\nInitializing browser.........\n')        
    browser=Browser(region=region,fwidth=fwidth,filename=html, data_sources=data_sources)

    
    # load samples
    if (tracks is None or 'samples' in tracks):
        print('\nLoading sample files\n')    
        for n,row in exps_CS.iterrows():
            run=row[0]
            samp=row[1]
            mod=row[2]
            print ('\nAdding %i %s %s %s\n'%(n,run,samp,mod))
            
            #RIGHT NOW ONLY SUPPORTING CHIP
            (masks)=getBrowserMasks(tf,mod,'chip')
            
            if labels is None:
                track_title=''
            else:
                track_title=labels[n]
                
            browser.loadSampleTrack(run,samp,ylims,masks=masks,title=track_title)

    # load known sites
    if (tracks is None or 'known' in tracks):

        known_binding_file='%s/runs/known_binding/%s_regulondb_binding.gff'%(dataroot,tf)
        if (exists(known_binding_file)):
            print('\nLoading known binding sites hits\n')
            browser.loadGFFFile(known_binding_file,title='Known Sites')  

    # load called sites if any
    if (tracks is None or 'called' in tracks):
        print('\nLoading Called Peaks\n')    
        # called_peaks=db.getTFCalledPeaks(tf)
        called_peaks = dat_obj.get_called_peaks(tf=tf)
    
        if (len(called_peaks)>0):
            called_peaks=called_peaks.astype(int)
    
            starts=called_peaks['start'].tolist()
            ends=called_peaks['stop'].tolist()
            labels=called_peaks['index'].tolist()
            labels=list(map(str,labels))
            browser.loadGenericFeatures(starts=starts,ends=ends,labels=labels,title='Called Peaks')
        
  

    # # load fimo
    if (tracks is None or 'fimo' in tracks):
        print('\nLoading fimo hits\n')
        browser.loadFimoFile(tf)    

    #---------Rendering---------------
    if (showplot==1):
        print('\nRendering browser.........\n')
        browser.show()   
    else:
        print('\nSaving browser html.........\n')
        browser.save()       
    
    # db.close()
    factory.close()
    
    return browser



#-------------------------------------    
def getRegionFromGene(gene,window=10000, data_sources: dict = None):
    '''Get the region [start,end] from an Ecoli gene synmbol'''
    data_sources = {} if not data_sources else data_sources
    
    # db=ecoliDB()
    factory = Factory()
    dat_obj = factory.create(data_sources.get('data_sources_type', 'ecoliDB'), data_sources=data_sources)
    
    # region=np.array(db.getTFLocation(gene))[0]
    region = np.array(dat_obj.get_tf_loc(tf=gene))[0]
    
    region[0]=np.min(region[0]-window,0)
    region[1]=region[1]+window
    
    # db.close()
    factory.close()
    
    return region

#-------------------------------------    
def createAllTFBrowserHTMLS(overwrite=0, data_sources: dict = None):
    '''Create browswers for all Ecoli TFs with ChiP'''
    data_sources = {} if not data_sources else data_sources
    
    # db=ecoliDB()
    factory = Factory()
    dat_obj = factory.create(data_sources.get('data_sources_type', 'ecoliDB'), data_sources=data_sources)

    # tfs=db.getTFsWithChIP()
    tfs = dat_obj.get_tf_with_chip()  # TODO: Doesn't currently exist for darpa_biosensor...
    
    
    for tf in tfs.TF:
        print('Creating browser html for %s'%tf)
        if (exists('%s/%s_genome.html'%(CONFIG.browser_dir,tf)) and overwrite==0):
            print('HTML for %s exists!'%tf)
        else:
            browserTF(tf,showplot=0, data_sources=data_sources)
    
    factory.close()
 
#-------------------------------------    
def getBrowserMasks(tf,mod,exptype="chip", data_sources = None):
    '''Get browser masks based on:  
    TF  = string with tf symbol  
    mode = "inducible", or "native"    
    exptype = "chip"  is only exptype supported and is default
    '''
    data_sources = {} if not data_sources else data_sources
    
    # NEED TO UPDATE THIS TO BE SPECIFIC FOR PROMOTERS
    masks=[]
    if(exptype=='chip'):
        if (mod=='inducible'):  # (darpa_biosensor has only in vitro)
            # factory = Factory()
            # masks=chip_inducible_masks
            # masks=chip_native_masks
                        
            # db=ecoliDB(data_sources=data_sources)
            factory = Factory()
            dat_obj = factory.create(data_sources)
            
            # (tf_loc)=db.getTFLocation(tf)
            (tf_loc) = dat_obj.getTFLocation(tf=tf)

            # db.close()
            factory.close()
            tf_mask=np.array(tf_loc)[0]
            tf_mask[0]=tf_mask[0]-20
            tf_mask[1]=tf_mask[1]+20
            
            masks = [tf_mask] + chip_inducible_masks
        
        if (mod=='native'):
            masks=chip_native_masks

        
    return masks
    
