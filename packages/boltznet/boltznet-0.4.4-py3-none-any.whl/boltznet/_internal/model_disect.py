#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for disecting models

@author: jamesgalagan
"""

from . import tf_util
from . import util
from . import model_create
import matplotlib.pyplot as plt
import numpy as np
from . import sequence
from . import coverage
from mpl_toolkits import mplot3d
from sklearn.decomposition import PCA
import tensorflow as tf
import keras
from matplotlib.patches import FancyArrowPatch
from scipy.ndimage import uniform_filter1d



#%% Code for interpreting models biophysically and associcated plots
lac_operators=[(15.3,'O1'),(13.9,'O2')]
lac_max=15.3
lac_min=13.9


def get_genome_biophysics(model,slp=1,offset=0,energy_mode=0,winavesize=30, stepsize=50, data_sources=None):
    '''Generates a tiling path along the genome and then 
    calls get_seq_biophysics to get dictionary of biophysic values
    then adds the following values to the dictionary
    
    # values for genome comparison
    gp
    gc
    stats # linefit btw gc and gp
    
    
    '''
    data_sources = {} if not data_sources else data_sources
    
    # genome prediction path
    # gset is the set of sequences that form a tiling path along genome
    # gpred is the prediction on that tiling path
    # gp and gc are corrected for chipseq smear - see genome_prediction_comparison
    (stats, gc, gp, gpred, gpos, gcov, gcov_tile,
     gset) = model_create.genome_prediction_comparison(model,stepsize=stepsize,ws=winavesize, data_sources=data_sources)
    
    # # val is the NEGATIVE energy relative to solution typically
    # # pb,energy,yhat,layers= get_seq_pbinding(model,gset,slp=slp,offset=offset, mode=energy_mode)
    # retval = get_seq_pbinding(model,gset,slp=slp,offset=offset, mode=energy_mode)
    
    # energy=retval['energy']
    
    # pos=[i*50/1e6 for i in range(0,len(energy))]    
    # retval['pos']=pos
    

    retval=get_seq_biophysics(model,gset,slp=slp,offset=offset, energy_mode=energy_mode)
    retval['gc']=gc
    retval['gp']=gp
    retval['stats']=stats
    retval['gpos']=gpos
    
    return retval
    # return pb,energy,pos,yhat,gp,gc,stats,layers


def get_seq_biophysics(model,X,slp=1,offset=0,energy_mode=3):
    '''For sequences in X return a dictionary with values:
    pbinding
    energy
    pos
    yhat
    
    # the output of every layer of the network are also included
    # see getAllLayerOutputs
    
    based on slp, offset, and energy_mode
    calls get_seq_pbinding
    '''
    
    # val is the NEGATIVE energy relative to solution typically
    # pb,energy,yhat,layers= get_seq_pbinding(model,gset,slp=slp,offset=offset, mode=energy_mode)
    retval = get_seq_pbinding(model,X,slp=slp,offset=offset, mode=energy_mode)
    
    energy=retval['energy']
    
    pos=[i*50/1e6 for i in range(0,len(energy))]    
    retval['pos']=pos
    
    return retval
    # return pb,energy,pos,yhat,gp,gc,stats,layers


def get_seq_pbinding(model,X,slp=1,offset=0, mode=0):
    '''Calls get_seq_energy with slp, offset and mode to get energies
    Then calculates pbinding relative to the strongest binding site in X
    for sequence in X
    
    So pbinding(best_seq)=1
    every other seq is has 0<= pbinding < 1
    
    returns pbinding,energy, yhat 
    
    Pbinding is given by 
    
    P=C1/(C1+exp(dE)) = 1/(1+C2 exp(dE)) 
    for some C2=1/C1 for some C1 that is a function of #TF molecules
    and stronger dE is more negative
    We assume 
    - C1 << exp(dE)
    - that C2 exp(dE) >> 1 
    (which might fall apart near dE=0)
    
    Then
    P = 1/(C2 exp(dE))) = C1 exp(-dE)
    
    And if Pmax = 1 = C1 exp(-dEmax)
    
    Then Pother/Pmax=C1 exp(-dEother)/C1 exp(-dEmax) 
    
    Pother = exp(-dEother)/exp(-dEmax) = exp(dEmax - dEother) 
    
    '''
    
    
    # this is the NEGATIVE energy relative to solution typically
    # energy,yhat,layers= get_seq_energy(model,X,slp=slp,offset=offset, mode=mode)
    retval = get_seq_energy(model,X,slp=slp,offset=offset, mode=mode)
    
    energy=retval['energy']
    maxval=np.max(energy)
    pb=np.exp(energy-maxval)
    
    retval['pbinding']=pb
    
    return retval
    
    


def get_seq_energy(model,X,slp=1,offset=0, mode=0):
    ''' Given a model and input sequences, 
    calculate the sum of the boltzman energies of each sequence
    using the slope and offset parameters
    
    modes are different ways of calulating a single approximiate binding energy that we get from BLI
    mode 0: val = slp*np.log(convs) + offset # take the log of the sum of the bolztman energies
    mode 1: val = slp*np.log(max_frsum) + offset # take the log of maximum binding energy off the sequence
    mode 2: val = slp*(MAX_E) + offset # where sum e is the sum of the energies over the sequence (not exponentiated)
    
    This returns the NEGATIVE energy as part of a dictionary with the results
    of getAllLayerOutputs
    The energy is dict['energy']
    
    '''  
    
    # get the output of the intermediate layers
    retval=getAllLayerOutputs(model,X)
    
    yhat=retval['yhats']
    fmaps_gen=retval['fmaps']
    frsums_gen=retval['frsums']
    conv=retval['convs']
    maxe=retval['maxe']

    
    # these are different ways of potentially calculating the effective energy 
    # of a sequence - mode 0 is the correct way for most general sequences
    if mode==0:
        sum_convs=np.sum(conv,axis=1)
        eapp=np.log(sum_convs)
        energy=slp*eapp+offset
    elif mode==1:
        en11=np.max(frsums_gen,axis=1)
        energy=slp*np.log(en11)+offset
        energy=np.reshape(energy,(energy.shape[0],1))
    elif mode==2:
        energy=slp*(maxe)+offset
    elif mode==3:
        sum_convs=np.sum(conv,axis=1)
        eapp=np.log(sum_convs)
        (mfit,mfitc,biases)=tf_util.getModelMotifs(model)
        energy=eapp*np.exp(-biases)
        energy=slp*energy+offset
            


    if (len(energy.shape)==1):
        energy=np.reshape(energy,(energy.shape[0],1))
    
    retval['energy']=energy
     
    return retval


def genome_plot(ax,val,pos,ylabel,title,fs=12,tick_font=9,bottom=None,c=None,showave=0,avemode=1,ylabel2=None,arrows=None,arrow_col='k',xlabel='Genome Position (Mb)',**kwargs):
    '''Helper function for plotting values on the genome with pub ready formatting
    Plot val vs pos on ax
    fs = fontsize
    bottom is the bottom ylim of the plot
    if showave == 1 then draw a line at the average value of val and add second y axis with 
      tick values relative to this average
      ylabel2 is the label for this second axis
    '''

    ax.plot(pos,val,c=c)
        
    ax.set_ylabel(ylabel,fontsize=fs,weight='normal')
    ax.set_title(title,fontsize=fs)
    ax.tick_params(axis="both", labelsize=int(fs*0.8))    

    
    # plot the genome average line
    if showave:
        mval=np.nanmean(val)
        
        ax.axhline(mval,c='k')
        ax.text(min(pos)+(max(pos)-min(pos))*.01,mval,'%0.2f'%mval,c='k',fontsize=int(fs*.8),va='bottom',ha='left')
        yl=ax.get_ylim()
        yt1=ax.get_yticks()
        
        ax2=ax.twinx()
        ax2.set_yticks(yt1)
        ax2.set_ylim(yl)
        yt2=ax2.get_yticks()

        if avemode==1:        
            ytl=['%0.1f'%(i-mval) for i in yt2]
        elif avemode==2:
            ytl=['%0.1f'%(i/mval) for i in yt2]
        else:
            raise Exception("unknown avemode")
            
        ax2.set_yticklabels(ytl)
        ax2.tick_params(axis="both", labelsize=int(fs*0.8)) 
        ax2.set_ylabel(ylabel2,fontsize=fs,weight='normal', rotation=-90,verticalalignment='bottom')

        ax2.spines[['bottom','top','left']].set_visible(False) #only want the right spine on this axis
        if ylabel2==None:
            ax2.spines[['right']].set_visible(False)
            ax2.set_yticks([])
            
      
    # pdb.set_trace()
    # show any arrow positions provided
    if arrows is not None:
        ylim=ax.get_ylim()
        for ar in arrows:
            ar=ar/1000000
            arrow = FancyArrowPatch((ar,ylim[1]), (ar, ylim[1]-1),arrowstyle='simple,tail_width=0.5,head_width=4,head_length=6',color=arrow_col)                     
            ax.add_patch(arrow)
    

    # the yaxis limit - 0 is the solution reference
    if bottom is not None:
        ax.set_ylim(bottom=bottom)
 
    # scaling the xlabels
    ax.autoscale(enable=True, axis='x', tight=True)    
    ax.set_xlabel(xlabel,fontsize=fs)
    ax.spines[['top','right']].set_visible(False)


def plot_genome_binding(ax,pb,pos,tf=None,version=None,ylabels=['Relative Affinity',None],title=None,scrams=None,showave=1,avemode=2,**kwargs):
    '''Plot pbinding relative to strongest binding site
    across the genome'''
          
    
    
    # GENOME ENERGY PLOT #    
    if title is not None:
        title=title
    elif tf is not None:
        title='%s %s'%(tf,version)
    else:
        title=None
        
    genome_plot(ax,pb,pos,title=title,ylabel=ylabels[0],ylabel2=ylabels[1],showave=showave,avemode=avemode,**kwargs)


def plot_genome_energy(ax,val,pos,tf=None,version=None,fs=12,tick_font=9,scrams=None,ylabels=None,title=None, showave=1,bottom=None,showlac=0,**kwargs):
    '''Plot Energy of binding across the genome with lac references and average genome energy line'''
        
    
    # GENOME ENERGY PLOT #
    if ylabels is None:
        ylabel='-$\\Delta\\epsilon$ vs Solution (k$_bT$)'
        ylabel2='-$\\Delta\\epsilon$ vs Genome (k$_bT$)'
    else:
        ylabel=ylabels[0]
        ylabel2=ylabels[1]
        
    if title is None:
        title='%s %s'%(tf,version)
        
    genome_plot(ax,val,pos,ylabel,title,showave=showave,ylabel2=ylabel2,fs=fs,tick_font=tick_font,**kwargs)
    
    
    
    # Lac operator lines
    if showlac:
        for v,l in lac_operators: 
            ax.axhline(v-lac_max+np.max(val),c='k',linestyle=':')
        ax.text(max(pos),np.max(val)-0.05,'Lac O1:O2 Delta',c='k',fontsize=fs,va='top',ha='right')
  

    # scrambled DNA measurements
    if scrams is not None:
        for scram in scrams:
            ax.axhline(-scram,c='y',linestyle='--')
        ax.text(max(pos),-np.max(scrams),'Scrambled DNAs',fontsize=fs,va='top',ha='right',c='y')
        
        

def plot_genome_coverage(ax,model,tf,version,slp,offset,exp_ind=[-2],energy_mode=0,scrams=None,nplots=1,bottom=0,**kwargs):
    '''Plot the coverage along the genome'''
        
    # genome prediction path
    (stats, gc, gp, gpred, gpos, gcov, gcov_tile,
     gset) = model_create.genome_prediction_comparison(model,stepsize=50)
    
    retval=get_seq_energy(model,gset,slp=slp,offset=offset, mode=energy_mode)
    val=retval['energy']
    yhat=retval['yhats']
    
    pos=[i*50/1e6 for i in range(0,len(val))]
        
    ylabel='Normalized Coverage'
    title='ChIP-Seq Coverage'
    genome_plot(ax,gcov_tile[:,exp_ind],pos,ylabel,title,c=plt.get_cmap()(0.4))
    



def plot_training_vs_energy(model,exp_data,slp,offset,energy_mode=3,fig=None,title=None,fs=12,**kwargs):
    '''Plot Coverage vs Energy relative given the 
    calibration values of slp and offset and energy_mode are used to calc energy using get_seq_energy
    
    ''' 
    
    X=exp_data['X']

    retval= get_seq_energy(model,X,slp=slp,offset=offset, mode=energy_mode)
    val=retval['energy']
    yhat=retval['yhats']

    pdb.set_trace()
    
    
    if fig is None:
        fig=plt.figure(figsize=(12,8))

    yplots=[None, yhat] #replace None with y if you want the bg real coverages 

    plot2DFMAP(model, val, yplots,title='',labels=list(exp_data['sample_id']),fig=fig,**kwargs)
    ax=fig.gca()
    ax.set_ylabel('Normalized Peak Coverage',fontsize=fs,weight='normal')
    ax.set_xlabel('-$\\Delta\\epsilon$ vs Solution (k$_b$T)',fontsize=fs,weight='normal')
    ax.tick_params(axis="both", labelsize=int(fs*0.8))    
    
    # Lac operator lines
    for v,l in lac_operators:
        v=v-lac_max+np.max(val)
        ax.axvline(v,c='k',linestyle=':')
    # ax.text((lac_min-lac_max)/2+np.max(val),ax.get_ylim()[0],'Lac O2:O1 Delta',fontsize=int(fs*.5),va='bottom',ha='center')

    if title is None:    
        ax.set_title('Coverage vs $\Delta\epsilon$ on Called Peaks',fontsize=fs,weight='bold')
    else:
        ax.set_title(title,fontsize=fs,weight='bold')
           

def plot_matrix(model,slp=1,offset=0,fs=12,tick_font=8,fig=None,ax=None,title=None,ylabel=None):
    '''Create a kernel map scaled by energy
    Energy is calculed using slp and offset determined by fits to BLI data
    '''

    (mfit,mfitc,biases)=tf_util.getModelMotifs(model)
    
    w=mfit[0]
    b=biases[0]
    wlen=w.shape[1]
    
    # bias distributed over matrix
    # scaling offset distributed over sequence
    c=(b/wlen) + (offset/(89))
   
    e=slp*(w+c)
    
    if fig is None and ax is None:
        fig=plt.figure(figsize=(12,8))
    
    if ax is None:
        ax=fig.subplots(1,1)
    
    util.plot_logo(e, ax=ax)
    
    if ylabel is not None:
        ax.set_ylabel(ylabel,fontsize=fs)
    else:
        ax.set_ylabel('-$\Delta\epsilon$ vs Solution (k$_b$T)',fontsize=fs,weight='normal')
    
    ax.set_xlabel('Position',fontsize=fs)
    
    if title is not None:
        ax.set_title(title,fontsize=fs)
    else:
        ax.set_title('Binding Energy Matrix',fontsize=fs)
    ax.tick_params(axis="both", labelsize=tick_font)    
    
    # ax.axhline(1.5,c='k',linestyle=':')
    # ax.axhline(-1.5,c='k',linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.text(0,-1.5,'Thermal Energy',fontsize=int(fs*.5),va='bottom',ha='left')

    


#%% Code for getting the output of sublayers
def getLayerOutput(model,X,layer_list):
    '''For each layer in the layer_list, return the output of that layer when
    the model is run on input X
    
    returns a list of outputs, one for each layer
    
    '''
    output_list=[]
    for layer_name in layer_list:
            
        intermediate_layer_model = keras.Model(inputs=model.input,
                                           outputs=model.get_layer(layer_name).output)
        fmap = intermediate_layer_model(X)

        output_list.append(fmap)
    
    return output_list
    
def getAllLayerOutputs(model,X,ind=None):
    '''For a model and input, get the following layer outputs and derivatives
    returns a dict of the following
    yhats = the full model output
    fmaps = the output of the pool layer
    frsums = the output of the FR sum layer
    convs = the output of the conv layer only
    maxe = the maximum energy - take the log of the conv layer and max
    sume = the sum energy - take the log of the conv layer and sum
    maxefr - the ave of the max on the forward strand + max on neg strand
    
    '''
    
    # get the output of the intermediate layers
    layers=['conv','FRSumConv','pool']
    layer_outputs=getLayerOutput(model,X,layers)
    
    retval={}
    
    retval['yhats']=model(X).numpy()

    retval['convs']=layer_outputs[0].numpy().squeeze()
    retval['frsums']=layer_outputs[1].numpy().squeeze()
    retval['fmaps']=layer_outputs[2].numpy().squeeze()
    
    en=np.log(retval['convs'])
    retval['maxe']=np.max(en,axis=1)
    retval['sume']=np.sum(en,axis=1)
    retval['avee']=np.mean(en,axis=1)
    
    
    seqlen=en.shape[1]
    retval['maxefr']=(np.max(en[:,0:int(seqlen/2)],axis=1)+np.max(en[:,:int(seqlen/2):-1],axis=1))/2
        
    return retval


def convReshape2D(model,conv,pad=True):
    '''For a doubleseq model (standard boltznet), takes the output of the conv layer
    which has both the forward and negative strand concatenated and thus is twice 
    the length (L) of the actual input seq minus a margin for the kernel size (M):
    
    [1, 1, 2*L-(M-1), 1]
    
    and converts it a 2D array with the forward strand and negative strand in 
    their own dims:
        
    [1,2,L-((M-1)/2),1]

    conv must be a numpy array and not a tensor

    if pad=True then pad the start of each dim with zeros so that the the output will
    be shape
    
    [1,2,L,1]

    Returns
    - conv2D - the 2D numpy array
    - pos =[start,stop] the positions of conv2D along the input sequence assuming that
    the original input sequence went from pos 1 to seq_len
    
    '''
    
    # get the kernel(s) from the model to check the length
    (mfit,mfitc,biases)=tf_util.getModelMotifs(model)
    mlen=mfit[0].shape[1]

    # work out the lengths of the layers and input seqs
    dlend=conv.shape[2]
    slen=int(dlend/2)
    seqlen=slen+int(mlen/2)
        
    fwd=conv[:,:,:slen,:]
    
    # get reverse strand and reverse it
    rev=conv[:,:,slen:,:]
    rev=rev[:,:,::-1,:]

    # now create the 2D array
    conv2D=np.concatenate((fwd,rev),axis=1)
    
    if pad:
        pad_width = [(0, 0),(0, 0), (int((mlen-1)/2), 0),(0, 0)]  # no pad on axis 3
        conv2D = np.pad(conv2D, pad_width=pad_width, mode='constant', 
                        constant_values=0)

        start=1
        stop=seqlen
    else:
        start=int((mlen-1)/2)+1
        stop=seqlen
    
    pos=[start,stop]
        

    assert pos[1]-pos[0]+1 == conv2D.shape[2], "Positions and shape of conv2D don't line up"
    

    return conv2D, pos
    

def calcWindowSum(conv2D, ksize: int):
    """
    Window-sum over both strands, centered ('same' length).
    Accepts:
      - (nseqs, 2, seqlen, ntfs)  -> sums strands -> (nseqs, seqlen, ntfs)
      - (2, seqlen, ntfs)         -> sums strands -> (1, seqlen, ntfs)
      - (nseqs, seqlen, ntfs)     -> used as-is

    Returns: (nseqs, seqlen, ntfs) window SUM (not average).
    """
    x = conv2D

    # Normalize to (nseqs, seqlen, ntfs) by summing the 2 strands if present
    if x.ndim == 4:           # (nseqs, 2, L, ntfs)
        summed = x.sum(axis=1)
    elif x.ndim == 3:
        # If first dim looks like the strand axis (2), sum it
        if x.shape[0] == 2 and (x.shape[1] >= 1024 or x.shape[1] > x.shape[0]):
            summed = x.sum(axis=0, keepdims=True)  # -> (1, L, ntfs)
        else:
            summed = x
    else:
        raise ValueError("conv2D must be 3D or 4D")

    # Ensure fast, compact dtype/layout (float32 halves bandwidth vs float64)
    summed = np.ascontiguousarray(summed, dtype=np.float32)
    nseqs, L, ntfs = summed.shape

    # Centered window of size ksize: pad left/right so output length stays L
    # Works for odd or even ksize (matches 'origin=0' behavior).
    left = ksize // 2
    right = ksize - 1 - left

    # Zero-padding along the sequence axis
    padded = np.pad(summed, ((0,0), (left, right), (0,0)), mode='constant')

    # Cumulative sum along sequence axis
    c = np.cumsum(padded, axis=1, dtype=np.float32)

    # Window sum via prefix differences: S[i] = C[i+k] - C[i]
    result = c[:, ksize:, :] - c[:, :-ksize, :]

    return result

def calcWindowSumOld(conv2D,ksize):
    '''REPLACED WITH FASTER VERSION ABOVE
    calculate a window sum over both strands of conv2d
    
    If conv2d is (nseqs, 2, seqlen, ntfs)
    
    then the we convolve 25 sum over dim=2 with padding to return as result
    of shape:
    
    (nseqs,seqlen, ntfs)
    
    where is position along seqlen is the sum of the window centered at that position'''
    
    # first sum along axis 1 (note that this means we can also pass in the FRSumConv and this work
    summed = conv2D.sum(axis=1) # gets us (nseqs,seqlen, ntfs)
    
    # mode='constant' with cval=0 gives adaptive averaging at edges
    avg = uniform_filter1d(summed, size=ksize, axis=1, mode='constant', cval=0.0)

    # Convert to sum by multiplying by window size
    result = avg * ksize
    
    return result
        

#%% Code for getting submodels 
def getSubModels(model,trainable=False,new_name=''):
    '''Return submodels for the conv-pool layers and the NN layers   
    returns (nnlay,cnnlay)   
    '''
    # Get CNN Submodel
    
    cnnlay=getConvModel(model,trainable,new_name)
    
    # Get NN submodel  
    nnlay=getNNModel(model,trainable,new_name)
    
    
    return (nnlay,cnnlay)


#------------------------
def getConvModel(model,trainable=False,new_name='',offset=0,last_layer='pool'):
    '''Get a model starting with offset layer through the layer indicated by the named last_layer   
    trainable is False by default
    new_name is name for new model ='' by default
    offset = 0 by default 
    last layer is 'pool' by default
    
    '''
    i=0
    for l in model.layers:
        if (l.name==last_layer):
            i=i+offset
            print(i)
            cnnlay=extract_layers(model,0,i,trainable,new_name)
        else:
            i=i+1
    
    
    return cnnlay

#------------------------
def getNNModel(model,trainable=False,new_name=''):
    '''Get a model starting with layer named 'nn_in' and ending with 
    the layer named 'nn_out' inclusive   
    trainable is False by default   
    new_name is name for new model ='' by default   
    
    '''
    
    i=0
    for l in model.layers:
        if (l.name=='nn_in'):
            i1=i
        if (l.name=='nn_out'):
            i2=i
        i=i+1
    
    print((i1,i2))
    nnlay=extract_layers(model,i1,i2,trainable,new_name)
    return nnlay


#-----------------------
# extract layers from a model to create a new model

def extract_layers(model, starting_layer_ix, ending_layer_ix,trainable=False,new_name=''):
  '''extract layers from a model to create a new model  
  '''
  
  if (new_name==''):
      new_name=model.name
    
  # create an empty model
  new_model = tf.keras.Sequential(name=new_name)
  
  # need to clone the original model otherwise the new model layers will be the same instances as original model
  main_model= tf.keras.models.clone_model(model)
  main_model.set_weights(model.get_weights())
  
  # get the input size from the layer prior to the starting layer if starting layer is >0
  if (starting_layer_ix>0):
      player=main_model.get_layer(index=starting_layer_ix-1)
      isize=player.input_shape
      print(isize)
  else:
      player=main_model.get_layer(index=0)
      isize=player.input_shape
      print(isize)

  for ix in range(starting_layer_ix, ending_layer_ix + 1):
    curr_layer = main_model.get_layer(index=ix)
 
    # set trainable status
    curr_layer.trainable=trainable
    
    # copy this layer over to the new model
    new_model.add(curr_layer)
  
    
    
  #build the model with the input shape
  new_model.build(input_shape=isize)
  
  new_model.summary() 
  
  return new_model
#%% 2D plots of fmap
def plot2DFMAP(model,fmap,ylist,msize=16,linewidth=2,fs=12,legend_font_size=8,tick_font=8,title='',fig=None,ax=None,**kwargs):
    '''ylist is a list of y vectors.  
    The first vector gets grey colored plot with msize/2 points
    Set the first vector to None if you want to avoid this
    
    The rest of the vector are plotted behind the rest of the elements
    each y in ylist can also be multicolumn
    '''
    
    #in case we get a 4d tensor
    fmap=np.reshape(fmap,(fmap.shape[0],fmap.shape[-1]))
    
    nkerns=tf_util.getNumKernels(model)
    
    if fig is None and ax is None:
        fig = plt.figure(figsize=(8,11))
        axs=fig.subplots(nkerns,1)
    elif ax is None:
        axs=fig.subplots(nkerns,1)
    else:
        axs=ax
            
    if 'colors' in kwargs:
        colors = kwargs.get('colors')
    else:
        colors = []
    
    if 'legend_up' in kwargs:
        legend_up = kwargs.get('legend_up')
    else:
        legend_up = False

    # Custom markers for primary points
    if 'markers' in kwargs:
        markers = kwargs.get('markers')
    else:
        markers = ['-o']

    markeredgewidth=kwargs.get('markeredgewidth',1)


    if nkerns==1:
        temp=axs
        axs=[]
        axs.append(temp)
    
    cmap = plt.get_cmap("tab10")
    # plt.subplots_adjust(hspace=0.9)
    
    # support for multiple kernels
    for knum in range(nkerns):
        
        for kk in (range(len(ylist))):
            y=ylist[kk]
            
            # the first element of ylist gets grey color and smaller points
            if (kk==0 and y is not None):
                if (len(y.shape)>1):
                    for ii in range(y.shape[1]):
                        axs[knum].plot(fmap[:,knum],y[:,ii],'.',ms=int(msize/2),linewidth=linewidth,color='#AAAAAA',markeredgewidth=markeredgewidth,linestyle='')
                else:
                    axs[knum].plot(fmap[:,knum],y,'.',ms=msize,linewidth=linewidth,color=cmap(knum),markeredgewidth=markeredgewidth,linestyle='')
            
            # all subsequent elements are considered primary and get default colors
            elif kk>0:
                
                if (len(y.shape)>1):
                    
                    if ('labels' in kwargs):
                        labels=kwargs.get('labels')
                    else:
                        labels = [str(i) for i in range(y.shape[0])]
                    
                    for ii in range(y.shape[1]):
                        ys=np.reshape(y[:,ii],(y.shape[0],))
                        sortind=np.argsort(ys)

                        if len(markers) > 1:
                            mk = markers[ii]
                        else:
                            mk = markers[0]

                        if len(colors) == 0:
                            axs[knum].plot(fmap[sortind,knum],y[sortind,ii],mk,
                                           linewidth=linewidth,ms=msize*.75,label=labels[ii],alpha=0.6,markeredgewidth=markeredgewidth)  
                        else:
                            axs[knum].plot(fmap[sortind,knum],y[sortind,ii],mk,
                                           linewidth=linewidth,ms=msize*.75,label=labels[ii],alpha=0.6,c=colors[ii],markeredgewidth=markeredgewidth)
                else:
                    ys=np.reshape(y,(y.shape[0],))
                    sortind=np.argsort(ys)

                    axs[knum].plot(fmap[sortind,knum],y[sortind],'-o',
                                   linewidth=linewidth,ms=msize*.75,color='#444444',markerfacecolor="#666666",markeredgewidth=markeredgewidth)

        if len(y.shape)>1 and legend_font_size>0:
            if legend_up:
                axs[knum].legend(fontsize=legend_font_size,frameon=False,ncol=2, loc='upper left', bbox_to_anchor = (0, 1))
            else:
                axs[knum].legend(fontsize=legend_font_size,frameon=False,ncol=2)
        
        if 'xlabel' in kwargs:
            axs[knum].set_xlabel(kwargs.get('xlabel'),fontsize=fs)
        else:
            axs[knum].set_xlabel('Kernel %d'%knum,fontsize=fs)
        
        if ('ylabel' in kwargs):
            axs[knum].set_ylabel(kwargs.get('ylabel'),fontsize=fs)
        else:
            axs[knum].set_ylabel('Output',fontsize=fs)
                        
        axs[knum].tick_params(axis='both', which='major', labelsize=tick_font)
        axs[knum].spines['top'].set_visible(False)
        axs[knum].spines['right'].set_visible(False)
        
        axs[knum].set_title(title)
        
        # if 'title' in kwargs:
        #     fig.suptitle(kwargs.get('title'),fontsize=fs,fontweight='bold')
        # else:
        #     fig.suptitle(model.name,fontsize=fs,fontweight='bold')

    return

# #%% 3d plots of feature map
def plot3DFMAP(model,fmap,y,msize=80,**kwargs):
    
    nkerns=tf_util.getNumKernels(model)
    
    pair=()
    if 'pair' in kwargs:
        pair=kwargs.get('pair')
    
    print(pair)

    #in case we get a 4d tensor
    fmap=np.reshape(fmap,(fmap.shape[0],fmap.shape[-1]))

    for k1 in range(nkerns):
        for k2 in range(k1,nkerns):
            if (not pair or (k1==pair[0] and k2==pair[1]) or (k2==pair[0] and k1==pair[1])):
                if 'fig' in kwargs:
                    fig=kwargs.get('fig')
                else:
                    fig = plt.figure()
                
                ax = fig.add_subplot(111)
                img=ax.scatter(fmap[:,k1],fmap[:,k2],c=y,s=msize,cmap=plt.get_cmap('hot').reversed(),vmin=0,vmax=1)
                fig.colorbar(img)
                ax.set_xlabel('Kernel %d'%k1)
                ax.set_ylabel('Kernel %d'%k2)
                
                ax.set_title(model.name)
                plt.show()
            
    return

# #%% 4d plots of feature map
def plot4DFMAP(model,fmap,y,msize=80,**kwargs):
    
    #in case we get a 4d tensor
    fmap=np.reshape(fmap,(fmap.shape[0],fmap.shape[-1]))
    
    nkerns=tf_util.getNumKernels(model)
    for k1 in range(nkerns):
        for k2 in range(k1+1,nkerns):
            for k3 in range(k2+1,nkerns):
                if (k2!=k1 and k3!=k1):
                    print('%d %d %d'%(k1,k2,k3))
                    
                    if 'fig' in kwargs:
                        fig=kwargs.get('fig')
                    else:
                        fig = plt.figure()
                        
                    ax = fig.add_subplot(111, projection='3d')
                    
                    img = ax.scatter(fmap[:,k1], fmap[:,k2], fmap[:,k3], s=msize,c=y, cmap=plt.get_cmap('hot').reversed(),vmin=0,vmax=1)
                    fig.colorbar(img)
                    ax.set_xlabel('Kernel %d'%k1)
                    ax.set_ylabel('Kernel %d'%k2)
                    ax.set_zlabel('Kernel %d'%k3)
                    ax.set_title(model.name)
                    plt.show()
                    
    return

#%% PCA input data by fmap using PCA
def PCAFmap(model,fmap,y,numpc=3,scale=1,msize=80,addlegend=1,**kwargs):

    #in case we get a 4d tensor
    fmap=np.reshape(fmap,(fmap.shape[0],fmap.shape[-1]))    

    pca = PCA(n_components=numpc)
    pc = pca.fit_transform(fmap)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    
    
    (nkerns,ksize)=tf_util.getKernelInfo(model)
    
    if 'fig' in kwargs:
        fig=kwargs.get('fig')
    else:
        fig = plt.figure()
    
    if 'title' in kwargs:
        title=kwargs.get('title')
    else:
        title=model.name
    
    if (numpc==3):
        ax = fig.add_subplot(111, projection='3d')
        
        img = ax.scatter(pc[:,0],pc[:,1],pc[:,2], s=msize, c=y, cmap=plt.get_cmap('hot').reversed(),vmin=0,vmax=1)
        
        for i in range(nkerns):
            lx=[0,loadings[i, 0]*20*scale]
            ly=[0,loadings[i, 1]*20*scale]
            lz=[0,loadings[i, 2]*20*scale]
            ax.plot3D(lx,ly,lz,linewidth=5,label='Kernel %d'%i)
            if (addlegend):
                ax.legend()
        
        fig.colorbar(img)
        ax.set_xlabel('PC %d'%1)
        ax.set_ylabel('PC %d'%2)
        ax.set_zlabel('PC %d'%3)
        ax.set_title(title)
        
    
        
            
    if (numpc==2):
        ax = fig.add_subplot(111)
        
        img = ax.scatter(pc[:,0],pc[:,1], s=msize, c=y, cmap=plt.get_cmap('hot').reversed(),vmin=0,vmax=1)

    
        for i in range(nkerns):
            lx=[0,loadings[i, 0]*20]
            ly=[0,loadings[i, 1]*20]
            ax.plot(lx,ly,linewidth=5,label='Kernel %d'%i)
            if (addlegend):
                ax.legend() 
            

        fig.colorbar(img)
        ax.set_xlabel('PC %d'%1)
        ax.set_ylabel('PC %d'%2)
        ax.set_title(title)
        

    plt.show()

    return

#%% GC Content
#-----------------------
def GCPredCorr(model,preds,gset,doubleseq=1,plot=1,**kwargs):
    
    xslen=gset.shape[2]
    if doubleseq == 1:
        slen=int(xslen/2) #The actual sequence is 1/2 the concatenated double sequence
        
    print(slen)
    # gc_content = sequence.calc_gc(g)
    if doubleseq == 1:
        gc_content = sequence.calc_gc(gset[:, :slen, :, 0])
        
    else:
        gc_content = sequence.calc_gc(gset[:, :, :, 0])
    
    #Get correlations
    k_num = tf_util.getNumKernels(model)
    corr_save = []
    for num in range(k_num):
        correlation = np.corrcoef(preds[:,num],gc_content)
        corr_save.append(correlation)
     
        
    fmap_max=np.max(preds[:,0])
    fmap_min=np.min(preds[:,0]) 
    if plot:
        
        cmap = plt.get_cmap("tab10")
        
        (nkerns,msize)=tf_util.getKernelInfo(model)
        if 'fig' in kwargs:
            fig=kwargs.get('fig')
            axs=fig.subplots(nkerns,1)
        else:
            fig = plt.figure(figsize=(8,11))
            axs=fig.subplots(nkerns,1)
        
        if (nkerns==1):
            temp=axs
            axs=[]
            axs.append(temp)
            axs=np.array(axs)
        
        # plt.subplots_adjust(wspace=1.2)
        for num in range(k_num):
            fmap_max=np.max(preds[:,num])
            fmap_min=np.min(preds[:,num]) 
            norm_val = max(abs(fmap_min),abs(fmap_max))
            if (norm_val==0):
                norm_val=1

            # plt.tight_layout()
            
            # plt.subplot(k_num,1,num+1)
            axs[num].scatter(gc_content,(preds[:,num] / norm_val),color=cmap(num))
            axs[num].set_ylim([fmap_min/norm_val,fmap_max/norm_val])
            axs[num].set_xlabel('GC Content')
            axs[num].set_ylabel('Kernel %d' %(num))
        
        
        if 'title' in kwargs:
            fig.suptitle(kwargs.get('title'))
        else:
            fig.suptitle(model.name)
    return (gc_content,corr_save)
    

#%% FMAP Scan

def FMAPScan(model,nsteps,scanfs,fixed_vals,fmap_max,fmap_min):
    
    (nnlay,cnnlay)=getSubModels(model)
    (nkerns,ksize)=tf_util.getKernelInfo(model)

    # calc the ranges over the two scanfs (scan features)
    fmax=[]
    fmin=[]
    fstep=[]

    for ii in range(nkerns):
        fmax.append(fmap_max[ii])
        fmin.append(fmap_min[ii])
        fstep.append((fmax[ii]-fmin[ii])/nsteps)


    for ii in range(nkerns):
        if fixed_vals[ii]>0:
            fixed_vals[ii]=fmax[ii]*fixed_vals[ii]
        if fixed_vals[ii]<0:
            fixed_vals[ii]=fmin[ii]*abs(fixed_vals[ii])
            

    fmap_syn=np.zeros((nsteps*nsteps,nkerns)) 
    icount=0   
    for i1 in np.arange(fmin[scanfs[0]],fmax[scanfs[0]],fstep[scanfs[0]]):
        for i2 in np.arange(fmin[scanfs[1]],fmax[scanfs[1]],fstep[scanfs[1]]):
            for pos in range(nkerns):
                if pos==scanfs[0]:
                    fmap_syn[icount,pos]=i1
                elif pos==scanfs[1]:    
                    fmap_syn[icount,pos]=i2
                else:
                    fmap_syn[icount,pos]=fixed_vals[pos]    
            icount+=1        

    print(fmap_syn)


    fmap_syn_out=nnlay(fmap_syn)
    print(fmap_syn_out)


    #% plot fmap scan

    fig=plt.figure(figsize=(15,11))

    ax = fig.add_subplot(111,projection ='3d')
    img=ax.scatter(fmap_syn[:,scanfs[0]],fmap_syn[:,scanfs[1]],fmap_syn_out,c=fmap_syn_out,cmap=plt.get_cmap('hot').reversed(),vmin=0,vmax=1)
    fig.colorbar(img)
    ax.set_xlabel('Kernel %d'%scanfs[0])
    ax.set_ylabel('Kernel %d'%scanfs[1])
    ax.set_zlabel('NN Output')
    ax.view_init(elev=15, azim=15)

    ax.set_title(model.name)
    plt.show()
    

def plot_energy_scatter(data, pred_col, fig = None, ax = None, tf = None, rsquared = None, show_legend = False, **kwargs):
    """
    Plot actual (BLI measured) energies vs model predictions

    data df requires at least 5 columns (pred_col - provided as second arg, energy, shape, color, edgecolor),
        the latter 3 are set by default in tf_util.load_energy_data
        but can be altered with:
            tf_util.get_dna_color_for_energy_plot for color
            tf_util.get_dna_edge_color_for_energy_plot for edge color (e.g. black for multi-site sequence or no edge otherwise)
            
    """
    if 'txt_size' in kwargs:
        txt_size = kwargs.get('txt_size')
    else:
        txt_size = 16

    if 'txt_weight' in kwargs:
        txt_weight = kwargs.get('txt_weight')
    else:
        txt_weight = 'normal'


    if 'scat_size' in kwargs:
        scat_size = kwargs.get('scat_size')
    else:
        scat_size = 200

    if 'leg_scat_size' in kwargs:
        leg_scat_size = kwargs.get('leg_scat_size')
    else:
        leg_scat_size = 20

    if 'leg_font_size' in kwargs:
        leg_font_size = kwargs.get('leg_font_size')
    else:
        leg_font_size = 8

    if 'show_kbt' in kwargs:
        show_kbt = kwargs.get('show_kbt')
    else:
        show_kbt = False

    if 'line_width' in kwargs:
        line_width = kwargs.get('line_width')
    else:
        line_width = 4

    x = data[[pred_col]]
    y = data[['energy']]
    y_pred = data[[f"{pred_col}_linreg_energy"]]

    if fig is None and ax is None:
        fig=plt.figure(figsize=(12,8))
    # At this point we have a fig no matter what


    if ax is None:
        pltax=fig.subplots(1,1)
    else:
        pltax = ax

    
    # Below this point we have an axis (pltax) to plot on
    pltax.plot(x.values, y_pred.values, color = 'black', linewidth=line_width, zorder=1)
    if show_kbt:
        xtmp = x.values.flatten()
        yptmp = y_pred.values.flatten()
        sortinds = np.argsort(xtmp)
        x_sorted = xtmp[sortinds]
        y_pred_sorted = yptmp[sortinds]

        x_min, x_max = x_sorted[0], x_sorted[-1]
        y_min_pred, y_max_pred = y_pred_sorted[0], y_pred_sorted[-1]
        
        pltax.plot([x_min, x_max], [y_min_pred - 1.5, y_max_pred - 1.5], color = 'gray', linewidth=line_width/2, zorder=1, linestyle='dashed')
        pltax.plot([x_min, x_max], [y_min_pred + 1.5, y_max_pred + 1.5], color = 'gray', linewidth=line_width/2, zorder=1, linestyle='dashed')
        
    for shape in data['shape'].unique():
        subset = data[data['shape'] == shape]

        pltax.scatter(
            x = subset[pred_col].values,
            y = subset['energy'].values,
            color = subset['color'].values,
            marker = shape,
            edgecolors = subset['edgecolor'].values,
            s = scat_size,
            linewidths = 2,
            zorder = 2

        )

    if rsquared is not None:
        pltax.text(0.1, 0.9, "Rsq = %0.2f"%rsquared,
                transform=pltax.transAxes,
                fontsize=txt_size,
                verticalalignment='top',
                horizontalalignment='left',
                fontweight=txt_weight,
                )
    
    if tf is not None:
        pltax.set_ylabel(f"{tf[0].upper()}{tf[1:]} $-\Delta\epsilon$")
    else:
        pltax.set_ylabel("$-\Delta\epsilon$")

    pltax.set_xlabel(f"Predicted $-\Delta\epsilon$")

    pltax.spines['top'].set_visible(False)
    pltax.spines['right'].set_visible(False)

    if show_legend:
        green_triangle = pltax.scatter([], [], color=(0.09803921568627451, 0.788235294117647, 0.2196078431372549), marker='^', linestyle='None', s=leg_scat_size, label='Genomic Sites')
        orange_circle = pltax.scatter([], [], color=(1.0, 0.48627450980392156, 0.0), marker='o', linestyle='None', s=leg_scat_size, label='Designed Sites')
        gray_triangle = pltax.scatter([], [], color=(0.6392156862745098, 0.6392156862745098, 0.6392156862745098), marker='^', linestyle='None', s=leg_scat_size, label='Nonspecific Genomic')
        gray_circle = pltax.scatter([], [], color=(0.6392156862745098, 0.6392156862745098, 0.6392156862745098), marker='o', linestyle='None', s=leg_scat_size, label='Nonspecific Designed')
        bold_triangle = pltax.scatter([], [], color=(1,1,1), marker='^', s=leg_scat_size, edgecolors='black', label='Multi-Site Sequence')

        
        if show_kbt:
            kbt_line = pltax.plot([], [], color='gray', linestyle='dashed', label='$\pm 1.5k_BT$')[0]
            leg_handles = [kbt_line, green_triangle, orange_circle, gray_triangle, gray_circle, bold_triangle]
        else:
            kbt_line = None
            leg_handles = [green_triangle, orange_circle, gray_triangle, gray_circle, bold_triangle]

        pltax.legend(
            handles=leg_handles, 
            fontsize=leg_font_size,
            loc='lower right',
            framealpha=1,
            edgecolor = 'black',
            )