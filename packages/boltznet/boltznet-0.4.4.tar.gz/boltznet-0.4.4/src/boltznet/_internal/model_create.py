#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for creating models that includes:
    - Model naming
    - Model creation
    - Model saving and loading
    - Model initialization
    - Model training (single process)
    - Model training (multiprocess)
    - Model cross validation (soon to be moved to its own module)

@author: jgalag
"""

import os
from os.path import exists
import fnmatch
import tensorflow.keras as keras
import tensorflow as tf
from tensorflow.keras import layers, activations
from tensorflow.keras.optimizers import Adam

import time
import matplotlib.pyplot as plt
import numpy as np
import re
from sklearn.model_selection import KFold
import pandas as pd
from datetime import datetime
import pickle
import multiprocessing
import setproctitle


from . import CONFIG
from . import model_disect

try: 
    from seqcovdb import SeqCovDB
except:
    pass
    
from .factory import Factory

from . import util
from . import tf_util
import importlib
# from tf_models import TFModels


model_stats_table_name = 'ecoli_project_analysis.modelStats'

#-------------------------------------------------------------
#%% MODEL CONFIG
#-------------------------------------------------------------
def loadModelConfig(version=''):
    '''Load model_params and model_build_options
    from the model_configs subdir from the corresponding CONFIG_MODEL_BUILD file.
    If version is '' the load from CONFIG_MODEL_BUILD
    Otherwise load from CONFIG_MODEL_BUILD_v#'''

    module_name='model_configs.CONFIG_MODEL_BUILD'    
    if version:
        module_name='%s_%s'%(module_name,version)
    
    print('Using configs from %s'%module_name)
    config_module = importlib.import_module(module_name)
            
    model_params = getattr(config_module,'model_params')
    model_build_options = getattr(config_module,'model_build_options')
    
    return model_params,model_build_options


def loadModelConfigFileInfo(version='vfile'):
    '''Load model_params and model_build_options
    from the model_configs subdir from the corresponding CONFIG_MODEL_BUILD file.
    If version is '' the load from CONFIG_MODEL_BUILD
    Otherwise load from CONFIG_MODEL_BUILD_v#'''

    module_name='model_configs.CONFIG_MODEL_BUILD'    
    if version:
        module_name='%s_%s'%(module_name,version)
    
    print('Load file inforamtion from %s'%module_name)
    config_module = importlib.import_module(module_name)
            
    file_paths = getattr(config_module,'file_paths')
    
    return file_paths



#-------------------------------------------------------------
#%% MODEL NAMING
#-------------------------------------------------------------
# -----------------------
def createModelName(tf_name, model_params, **kwargs):
    """Create a model name from the tf_name and the model params"""
    
    model_tag = ''

    model_tag = '%s_%s' % (model_tag, model_params['nnact'])

    model_tag = '%s_%s' % (model_tag, model_params['final_layer'])

    if model_params['doubleseq'] == 1:
        model_tag = '%s_%s' % (model_tag, 'doubleseq')

    model_tag = '%s_slen%s' % (model_tag, model_params['length_seq_side'] * 2 + 1)
    
    if 'data_sources_id' in kwargs:
        data_sources_id = kwargs.get('data_sources_id', '')
        if data_sources_id and data_sources_id != 'ecoli':
            model_tag += ('_' + str(data_sources_id))

    if (model_params['model_tag'] != ''):
        model_tag = '%s_%s' % (model_tag, model_params['model_tag'])

    # only add extr tag if it is in model_params and not None
    extra_tag=model_params.get('extra_tag',None)
    if extra_tag != None:
        model_tag='%s_%s'%(model_tag,extra_tag)

    exp_num = 0
    if 'exp_num' in kwargs:
        exp_num = kwargs.get('exp_num')

    nkerns = model_params['nkerns']
    ksize = model_params['ksize']
    if (type(exp_num) == str):
        model_name = '%s_%s_%dk_%dm%s' % (tf_name, exp_num, nkerns, ksize, model_tag)
    else:
        model_name = '%s_%d_%dk_%dm%s' % (tf_name, exp_num, nkerns, ksize, model_tag)

    return model_name

# -----------------------
def parseModelName(model_name):
    """Parse model name into individual parameters
    TODO - need to phase out reliance on this - will not work well outside lab context
    TODO - Better to load params for already build models - need to add tf_name to params
    
    Returns the following:
        
    tf_name, exp_num, nkerns, ksize, nnact, final_layer, model_tag, doubleseq, slen
    
    Note the the tag is sort of a catchall bucket for information.  It has the format
    of "_" seperated tokens.  And it is also parsed for doubleseq and slen
    
    You can add arbitrary information to the tag by adding more '_' seperated tokens
    NO CODE SHOULD DEPEND ON THE ORDER OF THE INFORMATION IN THE TAG

    Example:
        'pdhR_A_1k_25m_leakyrelu_linear_doubleseq_slen101_ecoli_v40'

        model_create.parseModelName(model.name)
        Out[6]: 
        ('pdhR',
         'A',
         1,
         25,
         'leakyrelu',
         'linear',
         'doubleseq_slen101_ecoli_v40',
         1,
         101)
    
    """
    # (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=parseModelName(model)

    parts = model_name.split('_')

    # some basic checks to make sure the model name is correct
    if len(parts) < 6:
        print('*******%s does not conform to expected format********\n' % model_name)
        return [], [], [], [], [], [], [], []
    if (not parts[1].isnumeric() and parts[1] != 'A'):
        if (not parts[2].isnumeric()):
            print('*******%s does not conform to expected format********\n' % model_name)
            return [], [], [], [], [], [], [], []

    if (parts[1].isnumeric() or parts[1] == 'A'):
        tf_name = parts[0]
        if (parts[1] == 'A'):
            exp_num = 'A'
        else:
            exp_num = int(parts[1])
        nkerns = int(parts[2].split('k')[0])
        ksize = int(parts[3].split('m')[0])
        nnact = parts[4]
        final_layer = parts[5]
        if len(parts) > 7:
            model_tag = "_".join(parts[6:])
        else:
            model_tag = parts[6]

    else:  # assume that tf_name is [tf]_[tag]
        tf_name = '%s_%s' % (parts[0], parts[1])
        exp_num = int(parts[2])
        nkerns = int(parts[3].split('k')[0])
        ksize = int(parts[4].split('m')[0])
        nnact = parts[5]
        final_layer = parts[6]
        if (len(parts) > 8):
            model_tag = "_".join(parts[7:])
        else:
            model_tag = parts[7]

    doubleseq = 0
    if ('doubleseq' in model_tag):
        doubleseq = 1

    slen = 501
    if ('slen' in model_tag):
        slen = int(re.findall(r'slen(\d+)', model_tag)[0])

    # print('model_tag: ', model_tag)
    return (tf_name, exp_num, nkerns, ksize, nnact, final_layer, model_tag, doubleseq, slen)

#-----------------------
def getModelParams(model):
    """Parses model params from model name
    TODO - this needs to be phased out - only used in crossvalModel"""

    (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=parseModelName(model.name)

    # # get the expected sequence length from the model
    slen=model.input_shape[2] #The length of the actual sequence on the Genome
    xslen=slen  # The length of a sequence the model expects]

    # # if we are working with doubleseq, this length is havlved
    if doubleseq == 1:
        slen=int(xslen/2) #The actual sequence is 1/2 the concatenated double sequence

    return(model.name,tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen,xslen)



#-------------------------------------------------------------
#%% MODEL CREATION
#-------------------------------------------------------------
def create_model(model_name,model_params,**kwargs):
    """Create a model based on params in model_params and
    assign it the given name and compile it. Also builds prediction models.
    Required arguments for prediction model include kwargs['initialize_Weights']
    and kwargs['stop_layer']"""
    
    if kwargs.get('stop_layer',None) is None:
        kwargs['stop_layer'] = 4
        kwargs['initialize_Weights'] = False
        kwargs['kstack'] = 0
        
        
    model = tf.keras.Sequential(name=model_name)
    
    addConvLayers(model,model_params,**kwargs)
    
    if kwargs.get('stop_layer') >2 and kwargs.get('kstack') == 0:
        addNNLayers(model,model_params,**kwargs)
        
    #kwargs for initializing a model from a weight_dict
    if 'initialize_Weights_from_Dict' in kwargs and kwargs['initialize_Weights_from_Dict'] is True:
        set_Conv2d_Weights(kwargs['weight_dict'], model, model_params)
        if kwargs.get('stop_layer') >2 and kwargs.get('kstack') == 0:
            set_NN_Weights(kwargs['weight_dict'], model)
    
    
    # kwargs for initializing new model from (list of) old models
    if 'initialize_Weights' in kwargs and kwargs['initialize_Weights'] is True:
        set_Conv2d_WeightsFromModels(kwargs['old_model'], model, model_params)
        if kwargs.get('stop_layer') >2 and kwargs.get('kstack') == 0:
            set_NN_WeightsFromModels(kwargs['old_model'], model)
            
    
    compileModel(model,**kwargs)

    # model.summary()

    return model


# -----------------------
def addConvLayers(model, model_params, **kwargs):
    """Add convolutional layer to model"""
    nkerns = model_params['nkerns']
    ksize = model_params['ksize']
    xslen = model_params['xslen']
    pool = model_params['pool']
    
    conv_use_bias = model_params.get('conv_bias',True)

    # model.add(layers.Dropout(0.01, input_shape=(4,xslen,1)))
    
    

    # regularization params for conv2d
    kreg = model_params['conv_kreg']
    actreg = model_params['conv_actreg']
    biasreg = model_params['conv_biasreg']

    if pool=='exp':
        conv_activation=activations.linear
    else:
        # this works best
        conv_activation=activations.exponential
    

    model.add(layers.Conv2D(nkerns, input_shape=(4, xslen, 1), kernel_size=(4, ksize),
                            kernel_regularizer=tf.keras.regularizers.l1(l=kreg),
                            activity_regularizer=tf.keras.regularizers.l1(l=actreg),
                            bias_regularizer=tf.keras.regularizers.l1(l=biasreg),
                            kernel_initializer=tf.keras.initializers.HeUniform(), activation=conv_activation,
                            use_bias=conv_use_bias, name='conv'))

    # Sum the corresponding positions on the forward and reverse strand
    dfr = int((xslen - ksize + 1) / 2)  # distance between forward and reverse seqs after first kernel
    
    if kwargs.get('stop_layer') >0:
        
        FRSumConv = layers.DepthwiseConv2D(kernel_size=(1, 2), depth_multiplier=1, dilation_rate=(1, dfr), # changed for model stcking, if not backwrds compatable add if statement for kstack
                                           trainable=False, depthwise_initializer=keras.initializers.Ones(),activation=activations.linear, 
                                           use_bias=False,name='FRSumConv')
        #old model layer
        # FRSumConv = layers.Conv2D(nkerns, kernel_size=(1, 2), dilation_rate=(1, dfr), trainable=False,  
        #                           kernel_initializer=keras.initializers.Ones(), activation=activations.linear, 
        #                           use_bias=False, name='FRSumConv') 
        model.add(FRSumConv)

    
    if kwargs.get('stop_layer') >1:
        # ave pooling works best, pooling with max or exp() does not seem to work 
        if pool == 'ave':
            model.add(layers.GlobalAveragePooling2D(name='pool'))
        if pool == 'max':
            model.add(layers.GlobalMaxPooling2D(name='pool'))
        if pool == 'exp':
            exp_pool = layers.Conv2D(1, kernel_size=(1, dfr), trainable=False,
                                  kernel_initializer=keras.initializers.Ones(), activation=activations.exponential,
                                  use_bias=True, name='exp_pool')
            model.add(exp_pool)
        # model.add(layers.BatchNormalization(name='batch_norm'))

    return


# -----------------------
def addNNLayers(model, model_params, **kwargs):
    """Add fully connected neural net to model"""
    nnact = model_params['nnact']
    final_layer = model_params['final_layer']
    nnodes = model_params['nn_nnodes']
    nlayers = model_params['nn_nlayers']

    kreg = model_params['nn_kreg']
    actreg = model_params['nn_actreg']
    biasreg = model_params['nn_biasreg']

    nnodes_final = model_params['nnodes_final']

    act = getActivation(nnact)

    # input layer
    model.add(layers.Dense(nnodes, activation=act, use_bias=True, kernel_regularizer=tf.keras.regularizers.l1(l=kreg),
                           activity_regularizer=tf.keras.regularizers.l1(l=actreg),
                           bias_regularizer=tf.keras.regularizers.l1(l=biasreg), name='nn_in'))

    # intermediate layers
    for i in range(0, nlayers - 1):
        model.add(
            layers.Dense(nnodes, activation=act, use_bias=True, kernel_regularizer=tf.keras.regularizers.l1(l=kreg),
                         activity_regularizer=tf.keras.regularizers.l1(l=actreg),
                         bias_regularizer=tf.keras.regularizers.l1(l=biasreg)))

    # final layer
    final_act = getActivation(final_layer)
    model.add(layers.Dense(nnodes_final, activation=final_act, use_bias=True,
                           kernel_regularizer=tf.keras.regularizers.l1(l=kreg),
                           activity_regularizer=tf.keras.regularizers.l1(l=actreg),
                           bias_regularizer=tf.keras.regularizers.l1(l=biasreg), name='nn_out'))

    return


# -----------------------
def compileModel(model, **kwargs):
    """Compile model with:
    - Exponential decay on learning rate
    - Adam optimizer
    - MSE error function"""

    # adaptive learning rate
    initial_learning_rate = 0.01
    if 'initial_learning_rate' in kwargs:
        initial_learning_rate = kwargs.get('initial_learning_rate')

    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate,
        decay_steps=10000,  # this is the number of batches
        decay_rate=0.5,
        staircase=True)

    model.compile(Adam(learning_rate=lr_schedule), loss=tf.keras.losses.MeanSquaredError())

    return

#-----------------------
def getActivation(nnact):
    """Given a string for nnact - returns corresponding TF activation object
    Supported nnact are {relu,linear,swish,tanh,softplus,softsign,sigmoid,leakyrelu"""

    if (nnact=='relu'):
        act=activations.relu
    elif (nnact=='linear'):
        act=activations.linear
    elif (nnact=='swish'):
        act=activations.swish
    elif (nnact=='tanh'):
        act=activations.tanh
    elif (nnact=='softplus'):
        act=activations.softplus
    elif (nnact=='softsign'):
        act=activations.softsign
    elif (nnact=='sigmoid'):
        act=activations.sigmoid    
    elif (nnact=='leakyrelu'):
        act=keras.layers.LeakyReLU()    
    
    return act

#-------------------------------------------------------------
#%% MODEL INITIALIZATION
#-------------------------------------------------------------

def loadModelWeightJsons(tf_list=None,json_dir=CONFIG.model_json_dir):
    '''Load a weight dictionary from the jsons in json_dir
    
    The weight dict will have a key = "conv"
    and this entry will point to 
    { weights: tensor(4,ksize,1,nkerns), biases: tensor(nkerns,)}
    
    If tf_list is given, it must be a list of tf names that correspond
    to <tf_name>_wm_bias.json in the json_dir
    
    If tf_list is None, then load all files <tf_name>_wm_bias.json from json_dir
    
    '''
    
    
    # get a list of all TFs
    if tf_list is None:
        tf_list = [
            fname.replace("_wm_bias.json", "")
            for fname in sorted(os.listdir(json_dir))
            if fname.endswith("_wm_bias.json")
        ]
    
    for i,tf_name in enumerate(tf_list):
        fpath="%s/%s_wm_bias.json"%(json_dir,tf_name)
        
        try:
            w,b=tf_util.importModelMotifJSON(fpath)
        except:
            raise Exception("No json file %s found for TF %s" %(fpath, tf_name))
            
        if i==0:
            weights=w
            biases=b
        else:
            weights=np.concatenate([weights,w],axis=3)
            biases=np.concatenate([biases,b],axis=0)
    weight_dict={}
    weight_dict['conv'] = {'weights': weights, 'biases': biases} 
    
    return weight_dict, tf_list

def set_NN_WeightsFromModels(old_model, new_model):
    '''Initialize NN weights and biases on a new model using weights 
    extracted from an older model. '''

    old_model = old_model[0]
    weight_dict = {}
    
    #Collects NN weights
    for layer in new_model.layers:
        if isinstance(layer, tf.keras.layers.Dense) and (layer.name.startswith("nn_in") or layer.name.startswith("nn_out") or "dense" in layer.name):
            weights = layer.get_weights()
            if weights:  
                weight_dict[layer.name] = {'weights': weights[0], 'biases': weights[1]}
    
    set_NN_Weights(weight_dict, new_model)
    
    return


def set_NN_Weights(weight_dict, new_model):
    '''Initialize NN weights and biases on a new model using weights 
    in weight_dict.
    
    The keys of weight_dict are layer names and each layer points to a
    dictionary with keys weights and biases
    
    '''
    
    #Initializes NN weights
    for layer in new_model.layers:
        if layer.name in weight_dict:
            weights = weight_dict[layer.name]
            if isinstance(weights, dict):  
                layer.set_weights([weights['weights'], weights['biases']])
            else:
                layer.set_weights(weights) 

    return


def set_Conv2d_WeightsFromModels(old_model_list, new_model,model_params):
    '''Initialize conv weights and biases on a new model using weights 
    extracted from an older model. 
    set_Conv2d_weights(old_model,new_model, model_params)'''

    # Collect Conv2D weights from new_model
    weight_dict = extractLayerWeights(old_model_list,new_model,model_params) 
    
    # given the weight dictionary - set the weights
    set_Conv2d_Weights(weight_dict, new_model,model_params)
    
    return

def set_Conv2d_Weights(weight_dict, new_model,model_params):
    '''Initialize conv weights and biases on a new model using weights 
    in the weight_dict
    
    weight_dict must have an entry
    weight_dict['conv'] ={ weights: tensor(4,ksize,1,nkerns), biases: tensor(nkerns,)}
    
    '''
    
    # Assign weights to old_model's matching Conv2D layers
    for layer in new_model.layers:
        if isinstance(layer, tf.keras.layers.Conv2D) and layer.name in weight_dict:
            weights = weight_dict[layer.name]
            layer.set_weights([weights['weights'], weights['biases']])
            
    return


def extractConvWeights(model_list):
    '''Extract conv weights and biases from the models in old_model_list
    and return in dictionary with key "conv"
    
    Assumes all models have kernels of the same size
    
    weight_dict=extractConvWeights(old_model_list)
    
    '''
    weight_dict = {}    
    count = 0
    
    for model in model_list:
        for layer in model.layers:
            if isinstance(layer, tf.keras.layers.Conv2D) and layer.name == 'conv':
                l=model.get_layer('conv')
                kernel_weights = l.get_weights()[0]
                bias_weight = l.get_weights()[1]
    
                if count==0:
                    weights=kernel_weights
                    biases=bias_weight
                else:
                    weights=np.concatenate([weights,kernel_weights],axis=3)
                    biases=np.concatenate([biases,bias_weight],axis=0)
                    
                count = count+1
                
    weight_dict['conv'] = {'weights': weights, 'biases': biases} 
    
    

    return weight_dict    

def extractLayerWeights(old_model_list,new_model, model_params):
    '''Extracts the weights and biases from the "conv" layer for a list of models and 
    stores them in a dictionary. Returns a dictionary of the weights and biases for all models.'''

    old_kernel_size = old_model_list[0].get_layer('conv').get_weights()[1].shape
    old_model =old_model_list[0]

    new_kernel_size = new_model.get_layer('conv').get_weights()[1].shape

    weight_dict = {}
    
    #If the old model kernel size matches the new kernel size directly use the extracted weights
    if old_kernel_size == new_kernel_size:
        for layer in old_model.layers:
            if isinstance(layer, tf.keras.layers.Conv2D) and layer.name == 'conv':
                l=old_model.get_layer('conv')
                kernel_weights = l.get_weights()[0]
                bias_weight = l.get_weights()[1]
                weight_dict[layer.name] = {'weights': kernel_weights, 'biases': bias_weight}
    
    #If the kernel sizes do not match, extract the weights an biases from each model in the list in order/.
    else:
        weights = np.zeros((4, model_params['ksize'], 1, new_kernel_size[0]))
        biases = np.zeros(new_kernel_size)
        count = 0
        
        for model in old_model_list:
            for layer in model.layers:
                if isinstance(layer, tf.keras.layers.Conv2D) and layer.name == 'conv':
                    l=model.get_layer('conv')
                    kernel_weights = l.get_weights()[0]
                    bias_weight = l.get_weights()[1]
                    weights[:,:,0,count] = kernel_weights[:,:,0,0]
                    biases[count] = bias_weight
                    count = count+1
        weight_dict['conv'] = {'weights': weights, 'biases': biases} 
        
    return weight_dict
    
#-------------------------------------------------------------
#%% MODEL SAVING AND LOADING
#-------------------------------------------------------------

#--------------------------------
def getValidModels(tf_name,path=CONFIG.model_dir):
    """Returns a list of valid models for a TF where a valid model is one whose name
    can be succesfully parsed"""
    model_names=[]
    tf_names=[]
    exp_nums=[]
    nkernels=[]
    ksizes=[]
    nnacts=[]
    final_layers=[]
    tags=[]
    doubleseqs=[]
    models=np.array(fnmatch.filter(os.listdir(path), '%s*.model'%tf_name)).T

    for model in models:
        (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=parseModelName(model)
        if (tf_name !=[]):
            model_names.append(model)
            tf_names.append(tf_name)
            exp_nums.append(exp_num)
            nkernels.append(nkerns)
            ksizes.append(ksize)
            nnacts.append(nnact)
            final_layers.append(final_layer)
            tags.append(model_tag)
            doubleseqs.append(doubleseq)
            
    return model_names,tf_names,exp_nums,nkernels,ksizes,nnacts,final_layers,tags,doubleseqs    


# -----------------------
def saveModel(model, path=CONFIG.model_dir, model_name=None):
    """Save the model as path/model_name.model"""
    if (model_name is None):
        model_name = model.name

    filename = '%s/%s.model' % (path, model_name)
    print(filename)

    model.save(filename)

    return  filename

# -----------------------
def loadModel(model_name, path=CONFIG.model_dir):
    """Load a model"""
    filename = '%s/%s.model' % (path, model_name)
    print(filename)

    model = tf.keras.models.load_model(filename)
    print(model.summary())

    return model

# -----------------------
def loadModelList(names,path=CONFIG.model_dir):
    '''Load a list of models from a local file directory. 
    Takes a file and a path that has a default to model_dir and 
    returns a list of models and model names that were able to be 
    successfully loaded. 
    (models, valid_model_names) = loadModelList(names,path = CONFIG.model_dir)
    
    
    Raises exception if model not found
    ''' 
    
    models = []
    valid_model_names = []
    #names = [names]
    
    for name in names:
        try:
            print('Loading %s' % name)
            models.append(loadModel(name,path=path))
            valid_model_names.append(name)
        except:
            raise Exception('Unable to load %s' %name )
        
    return models , valid_model_names 


# -----------------------
def loadAllModelsDir(directory):
    '''Loads all models from a given directory and returns all of the ones 
    that were able to be successfully loaded.
    (models, valid_model_names) = loadAllModels(directory) '''
    fold_names = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    model_names = []
    for name in fold_names:
        if name[-6:] =='.model':
            model_names.append(name[:-6])
    if model_names == []:
        print('No valid model could  be loaded')
        return None
    else:
        
        models , valid_model_names = loadModelList(model_names,directory)
        return models , valid_model_names
    
# -----------------------
def saveModelTrainingData(model, exp_data, path=CONFIG.model_dir, model_name=None):
    """Save model training data (exp_data) as a pickle path/<model_name>.training_data.pickle"""
    if (model_name is None):
        model_name = model.name

    filename = '%s/%s.training_data.pickle' % (path, model_name)
    print(filename)

    f = open(filename, 'wb')
    pickle.dump(exp_data, f)
    f.close()

    return

# -----------------------
def loadModelTrainingData(model_name, path=CONFIG.model_dir):
    """Loads model training data - returns dictionary exp_data"""
    filename = '%s/%s.training_data.pickle' % (path, model_name)
    print('Loading data from %s' % filename)

    if (os.path.exists(filename)):
        f = open(filename, 'rb')
        exp_data = pickle.load(f)
        f.close()

        return exp_data
    else:
        return None


# -----------------------
def saveModelCVData(df, path=CONFIG.model_dir):
    """Save model cv data as a pickle path/<df.name>.cvvdata.pickle"""
    # expects a dataframe whose name is the model name
    filename = '%s/%s.cvdata.pickle' % (path, df.name)
    # print(filename)

    f = open(filename, 'wb')
    pickle.dump(df, f)
    f.close()

    return


# -----------------------
def loadModelCVData(model_name, path=CONFIG.model_dir):
    """Load model cv data - returns a dataframe"""
    filename = '%s/%s.cvdata.pickle' % (path, model_name)

    if (not exists(filename)):
        return pd.DataFrame({})

    f = open(filename, 'rb')
    df = pickle.load(f)
    f.close()

    return df


# -----------------------
def saveModelParams(model_name, params, options, path=CONFIG.model_dir):
    """Save model params as pickle path/<model_name>.params.pickle"""
    filename = '%s/%s.params.pickle' % (path, model_name)
    # print(filename)

    f = open(filename, 'wb')
    pickle.dump((params, options), f)
    f.close()

    return


# -----------------------
def loadModelParams(model_name, path=CONFIG.model_dir):
    """Loads model params from an existing model pickle file - return a list of (params,options)"""
    filename = '%s/%s.params.pickle' % (path, model_name)

    if (not exists(filename)):
        return []

    f = open(filename, 'rb')
    l = pickle.load(f)
    f.close()

    return l


# -----------------------
def modelExists(model_name, path=CONFIG.model_dir):
    """checks to see if a model exists by the same name"""
    # checks to see if model exists and returns 1 if so, 0 if not
    filename = '%s/%s.model' % (path, model_name)

    return os.path.exists(filename)



# -----------------------
def loadModelAndData(model_name, tf_name, exp_num, maxrandsamps=10000, mode='independent', path=CONFIG.model_dir,
                     maskgcov=1, length_seq_side=250, **kwargs):
    """Load both a model and associated training data
    Returns tuple (model,exp_data)"""

    model = loadModel(model_name, path)
    
    data_sources = kwargs.get('data_sources', None)

    # get the length of the input sequence for this model - need that for processExperiment below
    # get the expected sequence length from the model
    (tf_name, exp_num, nkerns, ksize, nnact, final_layer, model_tag, doubleseq, slen) = parseModelName(model.name)

    slen = model.input_shape[2]  # The length of the actual sequence on the Genome
    if (doubleseq == 1):
        length_seq_side = int(((slen - 1) / 2) / 2)
    else:
        length_seq_side = int((slen - 1) / 2)  # The length of a sequence the model expects]


    # % Load training data (this needs to try to load the data first)
    exp_data = loadModelTrainingData(model_name, path=path)

    # TODO THIS is lab specific - need to remove - here just for backwards compat for older models
    if (exp_data is None):
        data = SeqCovDB(tf_name, data_sources=data_sources)
        df = data.get_info()

        # % Load and Process Experiment
        (exp_data) = tf_util.processExperiment(data, exp_num, maxrandsamps, mode=mode, length_seq_side=length_seq_side,
                                               **kwargs)


    # Load genomewide coverage for this experiment and mask it as necessary for the promoter
    # gcov=data.load_gw_cov(exp_num)
    # gcov = exp_data['gcov']

    # # use masks to mask coverage here
    # if (maskgcov):
    #     prom=df['Promoter'][exp_num]
    #     mod=util.prom2mod(prom)
    #     (masks)=browser_util.getBrowserMasks(tf_name,mod,'chip')
    #     for mask in masks:
    #         gcov[mask[0]:mask[1]]=0

    # exp_data['gcov']=gcov

    return model, exp_data


#-----------------------
def uploadModelStats(model,exp_data,overwrite=1, data_sources = None):
    """ upload stats of model predition on genome as well as model attributes like nkerns,ksizem,etc
    see model_stats_table_name abovve
    TODO - lab specific - needs to be moved to another module - model_outputs"""
        
    print ('----- Uploading model stats ------\n')

    #parse the model name
    (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=parseModelName(model.name)    


    #stats on training data
    yhat=model(exp_data['X'])
    if (len(yhat.shape)==1):
        yhat=np.reshape(yhat,(exp_data['X'].shape[0],1))
    
    (stats_train)=util.cov2accuracy(exp_data['y'],yhat)

    # get stats of genome wide comparison of pred vs true coverage
    ( stats,gc,gp,gpred,gpos,gcov,gcov_tile,gset)=genome_prediction_comparison(model)

    # --------- END OF BLOCK THAT SHOULD BE MOVED -------

    #open database connection
    # db=ecoliDB()
    factory = Factory()
    dat_obj = factory.create(data_sources)
    
    #--- Accuracy stats ---- 
    if (overwrite):
        q='delete from %s where model_name="%s"'%(model_stats_table_name,model.name)
        dat_obj.runQuery(q)
        dat_obj.runQuery('commit')

    # get timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    # do the insert (*****this overwrites any current data for now*****)
    if (len(exp_data['run_id'])==1):
        d=(model_stats_table_name,model.name,stats_train['sens'],stats_train['spec'],stats_train['rsq'],stats['sens'],stats['spec'],stats['rsq'],stats['auc'],nkerns,ksize,tf_name,slen,exp_data['run_id'],exp_data['sample_id'],timestamp)
    else:
        d=(model_stats_table_name,model.name,stats_train['sens'],stats_train['spec'],stats_train['rsq'],stats['sens'],stats['spec'],stats['rsq'],stats['auc'],nkerns,ksize,tf_name,slen,'All','All',timestamp)
    
    q='insert into %s (model_name,sens_train,spec_train,rsq_train,sens,spec,rsq,auc,nkerns,ksize,tf,slen,run_id,sample_id,create_time) values("%s",%f,%f,%f,%f,%f,%f,%f,%d,%d,"%s",%d,"%s","%s","%s")'%d
    print(q)
    dat_obj.runQuery(q)
    dat_obj.runQuery('commit')

    
    #close the connection on the db object
    dat_obj.close()
    
  

    return    


#-------------------------------------------------------------
#%% MODEL TRAINING
#-------------------------------------------------------------
def train_model(model,X,y,ifirstneg,seq,pat=200,plotfreq=100,epochs=3000,batch_size=256,verbose=0,showplots=1,validate=False,val_X=None,val_y=None,**kwargs):
    """Base function for training a model
    Required parameters are:
        model - a tensorflow model
        X - a tensor with onehot training sequences: shape=(Nseqs,4,modified_seqlen,1)
        y - a matrix with one column per output head and on row per sequence in X - shape = (Nseqs,Noutputs)
        ifirstneg - the index of the first negative training sample
        seq - onehot tensor of raw training sequences - shape=(Nseqs,4,seqlen)
    Returns tuple of 
        model
        hist_p - training histogram generated by model.fit
        minl - minimum loss function value
    TODO - need to refactor input to take exp_data dict instead of indiv input data X,y,ifirstneg,seq"""
    
    weights=False
    if 'weight_data' in kwargs:
        weights=kwargs.get('weight_data')
    
    callbacks=[]
    
    # TODO support validation split and early stoppoing on val_loss
    if (validate):
        stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=pat, restore_best_weights=True)
    else:
        stopping = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=pat, restore_best_weights=True)
    
    callbacks.append(stopping)

    if verbose==3:
        verbose=2
    else:
        perfcallback=PerformanceCallback(X,y,ifirstneg,plotfreq,seq,showplots)
        callbacks.append(perfcallback)

    
    # hist_p = model.fit(X, y, validation_split=0.25, epochs=3000, batch_size=10, verbose=1,callbacks=[stopping,perfcallback])
    if validate:
        hist_p = model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=verbose,callbacks=callbacks,validation_split=0.2)
    else:
        if (weights):
            w = tf_util.getDataWeights(y,ifirstneg)
            hist_p = model.fit(X, y, sample_weight=w, epochs=epochs, batch_size=batch_size, verbose=verbose,callbacks=callbacks,)
        else:
            hist_p = model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=verbose,callbacks=callbacks,)
        
    
    #plot training history
    if showplots==1:
        minl=tf_util.plotFitHist(hist_p)
        print(minl)
    else:
        # minl=tf_util.getMinLossFromHist(hist_p.history['loss'])
        minl=tf_util.getMinLossFromHist(hist_p)
        

    return (model,hist_p,minl)

#-----------------------
def preTrainModel(model_name,pretrain_tries,model_params,exp_data,rsq_break_th=0.86,validate=False,showplot=1,pat=100,epochs=2000,**kwargs):
    """Pretrain a model by fiting it to mostly positive data - do this multiple times, and choose best model to return based on min loss
    Returns 
        minl - loss function of best model
        model - the best model
        max_rsq - the rsq of best model with respect to actual data"""
    # creates pretrain_tries number of models and selects the best one to return (best based on rsq with actual)
    
    negscale=2
    if 'negscale' in kwargs:
        negscale=kwargs.get('negscale')+1
    
    X=exp_data['X']
    y=exp_data['y']
    ifirstneg=exp_data['ifirstneg']
    seq=exp_data['seq']
    
    minl=1
    tries=0
    last_rsq=0
    pretrain_models=[]
    pretrain_rsq=[]
    pretrain_minl=[]
    
    while (tries<pretrain_tries and last_rsq<rsq_break_th):
    
        util.flush_print('Start pretrain try %d for %s' % (tries, model_name))
        
        
        # clear the session from any previous models
        tf.keras.backend.clear_session()
        
        # --- CREATE THE MODEL ---
        model_params['xslen']=exp_data['xslen']
        model=create_model(model_name,model_params)    
        pretrain_models.append(model)
        
    
        #create pretrain data set
        (X2,y2)=tf_util.trainingDataSubset(X,y,0,ifirstneg*negscale)

        # train the model
        (model,hist_p,minl)=train_model(model,X2,y2,ifirstneg,seq,verbose=3,showplots=0,pat=pat,epochs=epochs,validate=validate,**kwargs)

        if len(y.shape)==1:
            yhat=np.reshape(model(exp_data['X']),(exp_data['X'].shape[0],1))
        else:
            yhat=np.reshape(model(X),(X.shape[0],y.shape[1]))
            
        (stats)=util.cov2accuracy(exp_data['y'],yhat)
        pretrain_rsq.append(stats['rsq'][0])
        pretrain_minl.append(minl)
        last_rsq=stats['rsq'][0]
        
        util.flush_print('Finished pretrain try %d for %s' % (tries, model_name))
        
        
        if (showplot):
            util.plot_y_vs_yhat(exp_data['y'], yhat, firstneg=exp_data['ifirstneg'], title='Pretrain %d %s Rsq=%0.4f' % (tries, model.name, stats['rsq']))
            plt.show()
            mit_pfm,ns=tf_util.plotModelPFM(model,exp_data['seq'],0.5,title='%s pretrain %d'%(model.name,tries),heatmap=0,numseqs=exp_data['ifirstneg'])
            plt.show()

        tries=tries+1

    #-- SELECT BEST OF THE PRETRAINED MODELS TO FULLY TRAIN ----
    # best_pretrain_model=np.argmax(pretrain_rsq)
    best_pretrain_model=np.argmin(pretrain_minl)
    model=pretrain_models[best_pretrain_model]
        
    max_rsq=pretrain_rsq[best_pretrain_model]
    
    # clear the session to release resources
    tf.keras.backend.clear_session()
    
    util.flush_print('Returning from pretrain for %s after %d tries' % (model_name, tries))
    
    
    return minl,model,max_rsq

#-----------------------
def trainSaveModel(model,exp_data,model_path,epochs=3000,pat=100,validate=False,create_browser=1,save_PFMS=0,upload_stats=0,showplot=1, data_sources= None):
    """Train a model and then save output data
    Returns a tuple:
        stats - accuracy stats on genome
        stats_train - accuracy stats on training set
    TODO - lab specific, needs refactoring - should be moved to model_autotrain"""
    
    X=exp_data['X']
    y=exp_data['y']
    ifirstneg=exp_data['ifirstneg']
    seq=exp_data['seq']
    
    #% Train the model
    # TODO - add validation_split support
    (model,hist_p,minl)=train_model(model,X,y,ifirstneg,seq,epochs=epochs,verbose=3,showplots=0,pat=pat,validate=validate)
    
    #% Save the model model_name.model and save the exp_data
    saveModel(model)
    saveModelTrainingData(model,exp_data)

    # get accuracy stats
    if (len(y.shape)==1):
        yhat=np.reshape(model(exp_data['X']),(exp_data['X'].shape[0],1))
    else:
        yhat=np.reshape(model(X),(X.shape[0],y.shape[1]))

    
    
    (stats_train)=util.cov2accuracy(exp_data['y'],yhat)
    (stats,gc,gp,gpred,gpos,gcov,gcov_tile,gset)=genome_prediction_comparison(model,exp_data=exp_data, data_sources=data_sources)


    if (showplot):


        util.plot_y_vs_yhat(exp_data['y'], yhat, firstneg=exp_data['ifirstneg'], title='%s Rsq=%0.2f' % (model.name, stats_train['rsq']))

        util.plot_y_vs_yhat(gc, gp, firstneg=0, title='%s (RS=%0.3f)' % (model.name, stats['rsq']))
        
        plt.show()

    
    
    # # Save the kernels and PFMs as [model.name]_PFMs.PNG
    if (save_PFMS and showplot):
        tf_util.plotModelPFM(model,seq,0.5,title=model.name,savefile=model.name,numseqs=ifirstneg,showplot=showplot)
        tf_util.plotModelKernels(model,savefile=model.name)
        plt.show()

    #% Create a browser on this model - A BIG HACK but alas 
    if (create_browser):    
        tf_models=TFModels.TFModels('',path='models',filterpat='*%s*'%model.name)
        tf_models.browse_genome_model([0], fwidth=14, region=[], showkernels=1, showsaliency=1, showplot=0, title=model.name, data_sources=data_sources)

    #-- UPLOADING MODEL STATS INCLUDING CV STATS--- 
    data_source_id = data_sources.get('data_sources_id', None) if data_sources else None
    if data_source_id == None or data_source_id == 'ecoli':
        if (upload_stats):
            uploadModelStats(model,exp_data, data_sources=data_sources)
    else:
        print('Does not appear to be ecoli data; skipping upload for now')  # TODO: CK: Change once darpa/TB schemas created
    
    
    
    return stats,stats_train




#-------------------------------------------------------------
#%% MODEL TRAINING MULTIPROCESS
#-------------------------------------------------------------

#-----------------------
def preTrainModelMPProcess(model_num,mp_args):
    """Process used for multiprocess pretraining"""
    # we have a task we can perform
    print(model_num)
    # pdb.set_trace()
    
    model_name=mp_args['model_name']
    model_params=mp_args['model_params']
    exp_data=mp_args['exp_data']
    showplot=mp_args['showplot']
    pretrain_epochs=mp_args['epochs']
    validate=mp_args['validate']
    negscale=mp_args['negscale']
    
    setproctitle.setproctitle('%s python pretraining process'%model_name)
    
    minl,model,max_rsq = preTrainModel(model_name,1,model_params,exp_data,showplot=showplot,epochs=pretrain_epochs,validate=validate,negscale=negscale)
    minl=minl[0]

    
    d={}
    d['minl']=minl
    d['model']=model
    d['rsq']=max_rsq

    print(model.name)
    print(max_rsq)
    
    return d

#-----------------------
class preTrainModelMPResults:
    """Class to save multiprocess pretraining results"""
    
    def __init__(self,model_name):
        self.results=[]
        self.numdone=0
        self.model_name=model_name
    
    def preTrainModelMPCallback(self,result):
    
        self.results.append(result)
        self.numdone=self.numdone+1
  
        print("GOT RESULT {}".format(result))
        util.flush_print("%s NUMBER DONE = %d (rsq=%0.2f minl=%0.6f)" % (self.model_name, self.numdone, result['rsq'], result['minl']))
        
        return

#-----------------------
def preTrainModelMP(args):
    """MULTIPROCESS version of preTrainModel - calls preTrainModel"""
    
    util.flush_print('Pretraining MP - %s' % args['model_name'])
    
    
    
    results=[]
    while (results==[]): # in case no process returns we go again
    
        # create the processing pool
        # pool = multiprocessing.Pool(args['num_procs'])
        pool = multiprocessing.Pool(maxtasksperchild=1)

        # add the processes to the pool
        results_obj=preTrainModelMPResults(args['model_name'])
        _ = [pool.apply_async(preTrainModelMPProcess, args=(x,args), callback=results_obj.preTrainModelMPCallback) for x in range(args['pretrain_tries'])]
        pool.close()
    
        timeout=max(100,int(args['epochs']*1.5)) # total time we will wait for all processes
        last_timeout=100 # time to wait since last result was received
    
        start_time=time.time()
        last_done=0
        last_time=None
        while 1:
            now=time.time()
            
            if (results_obj.numdone>last_done):
                last_done=results_obj.numdone
                last_time=time.time()
            
            if (results_obj.numdone==args['pretrain_tries'] or now-start_time>timeout or (last_time is not None and now-last_time>last_timeout)):
                pool.terminate()
                break
            time.sleep(0.3)
    
        results=results_obj.results
            
    util.flush_print('Done with mp processes %s' % args['model_name'])
    
    # pdb.set_trace()
    
    # review results and return best model and stats (minl,model,max_rsq)
    all_rsq=[]
    all_models=[]
    all_minl=[]
    for d in results:
        all_rsq.append(d['rsq'])
        all_models.append(d['model'])
        all_minl.append(d['minl'])
        
    best_model_ind=np.argmax(all_rsq)
    # best_model_ind=np.argmin(all_minl)
    
    util.flush_print('Best model is %d' % best_model_ind)
    
    max_rsq=all_rsq[best_model_ind]
    model=all_models[best_model_ind]
    minl=[all_minl[best_model_ind]]
    
    # pdb.set_trace()

    return minl,model,max_rsq


#-------------------------------------------------------------
#%% MODEL CROSS VALIDATION
#-------------------------------------------------------------# def crossvalModel(model,data,model_params,model_options,k=70,pretrain_th=1e-3,showplot=0, k2=-1,skip=0,savestats=1):
def crossvalModel(model,k=70,pretrain_th=1e-3,showplot=0, k2=-1,skip=0,savestats=0,pretrain_mp=0,save_cvmodels=0,**kwargs):
    """Cross validate a model
    TODO - work completely with saved exp_data"""
    # k is the split fold
    # k2 is the number of splits - if k2==-1 then k2=k
    
    util.flush_print('Crossvalidating %s' % model.name)
    
    
    if (k2==-1):
        k2=k
        
    model_name=model.name
    
    # create the model_params object for a single model
    (single_model_params,model_options)=loadModelParams(model_name)
    pretrain_tries=model_options['pretrain_tries']

    # Load the full training data 
    exp_data=loadModelTrainingData(model_name,path=CONFIG.model_dir)
    if (exp_data is None):
        raise ValueError("Could not load training data")
        
    if (len(exp_data['run_id'])>1):
        run_id='A'
        sample_id='A'
    else:
        run_id=exp_data['run_id']
        sample_id=exp_data['sample_id']


    # get the full model predictions
    ny=1
    if len(exp_data['y'].shape)>1:
        ny=exp_data['y'].shape[1]
    yhat_full=np.reshape(model(exp_data['X']),(exp_data['X'].shape[0],ny))
    yposmin=exp_data['y'][exp_data['ifirstneg']-1]
    
    (nnlay,cnnlay)=model_disect.getSubModels(model)
    fmap_full=cnnlay(exp_data['X'])

    
    i=-1
    cvstats=[] # empty list of lists
    for xtrain,ytrain,ifirstneg_train,xtest,ytest,ifirstneg_test,itest in balanceKfold(exp_data['X'],exp_data['y'],exp_data['ifirstneg'],k,skip=skip,gsize=model_options['addcircperm']+1):
                
        #only perform cv on samples where the full model predicted a positive hit in at least one output
        if (yhat_full[itest,:]>yposmin).any():
            
            i=i+1
            

            # print(itest,ytest[0],yhat_full[itest],yposmin)
            
            # # create the cv training data dictionary for preTrainModel
            cv_exp_data={}
            cv_exp_data['seq']=exp_data['seq']
            cv_exp_data['X']=xtrain
            cv_exp_data['y']=ytrain
            cv_exp_data['ifirstneg']=ifirstneg_train
            cv_exp_data['xslen']=exp_data['xslen']
            
            
            #this is going to be the filename for the cv model
            # check to see if it exists and skip with a message if so
            mname='cv%d_%s'%(i,model.name)

            if modelExists(mname):
                util.flush_print("%s already exists! Skipping"%mname)
                continue
            else:
                util.flush_print('Starting CV on %s sample %d' % (model.name, i))
            
            
            # # #pretrain
            if (pretrain_mp==0):
                print('Single Process Pretraining')
                minl,cvmodel,max_rsq = preTrainModel(model_name,pretrain_tries,single_model_params,
                                                     cv_exp_data,epochs=model_options['pretrain_epochs'],
                                                     validate=False,negscale=model_options['pretrain_negscale'],showplot=showplot)
                minl=minl[0]
                # print(minl)
            else:
                mp_args={}
                mp_args['model_name']=model_name
                mp_args['num_procs']=pretrain_mp
                mp_args['pretrain_tries']=pretrain_tries
                mp_args['model_params']=single_model_params
                mp_args['exp_data']=cv_exp_data
                mp_args['showplot']=showplot
                mp_args['epochs']=model_options['pretrain_epochs']
                mp_args['validate']=False
                mp_args['negscale']=model_options['pretrain_negscale']
                
                
                minl,cvmodel,max_rsq = preTrainModelMP(mp_args)
                
                
                minl=minl[0]
                print(minl)
            
        
            #% Train the cvmodel
            util.flush_print('Training model - %s' % mname)
            

            (cvmodel,hist_p,minl)=train_model(cvmodel,xtrain,ytrain,ifirstneg_train,exp_data['seq'], epochs=model_options['train_epochs'],verbose=3,showplots=0,pat=200,validate=False)
            
            # save this model if desired
            if (save_cvmodels):
                
                saveModel(cvmodel,model_name=mname)
                saveModelTrainingData(cvmodel,cv_exp_data,model_name=mname)
                saveModelParams(mname,single_model_params,model_options)
                
            # calc some stats/results on the trained cvmodel
            # TODO we are bypassing crossvalStats - neeeds to be updated for hydra and it got very messy 
            # (stats_train,yhat_test,yhat,y,fmaphat_test,fmaphat)=crossvalStats(cvmodel,exp_data['X'],exp_data['y'],exp_data['ifirstneg'],xtrain,ytrain,ifirstneg_train,itest,i,exp_data['seq'],showplot=0)
            print(itest)
            
            #get stats on just training set
            X=exp_data['X']
            y=exp_data['y']
            ifirstneg=exp_data['ifirstneg']
            ny=1
            if len(y.shape)>1:
                ny=y.shape[1]
            yhat_cv_train=np.reshape(cvmodel(xtrain),(xtrain.shape[0],ny))
            (stats_train)=util.cov2accuracy(ytrain,yhat_cv_train,th=y[ifirstneg-1])        

            # the prediction of cv model on full data set
            # the test data point will be point itest[0]
            yhat_cv_full=np.reshape(cvmodel(X),(X.shape[0],ny))
            
            # the fmap of cv model of full data set
            # the test data point will be point itest[0]
            (nnlay,cnnlay)=model_disect.getSubModels(cvmodel)
            fmap_cv_full=cnnlay(X)
            
            # save key stats results
            cvstats.append((stats_train['sens'],stats_train['spec'],stats_train['rsq'],
                            itest[0], # the cv test data point index
                            y[itest[0]], # the actual y value(s) for the test point
                            yhat_cv_full[itest[0]], # the cv model predicted y values for test point
                            fmap_full[itest[0]], # the full model fmap for the test point
                            fmap_cv_full[itest[0]])) # the cv model fmap for the test point
    
            if ('pdb' in kwargs and kwargs.get('pdb')):
                pdb.set_trace()
            
            util.flush_print('Done with CV on %s sample %d' % (model.name, i))
            
            
        #stop if we have done enough number of splits    
        if (i>=k2):
            break
    
    util.flush_print('Done with CV on %s' % model.name)
    df = pd.DataFrame(cvstats, columns =['SensTrain', 'SpecTrain', 'RsqTrain', 'TestIndex','YTestTrue','YTestPred','FMAP_Full','FMAP_test'], dtype = float)
    df.name=model.name
    df.run_id=run_id
    df.sample_id=sample_id

    pd.options.display.width = 0
    print(df)
    
    if (savestats):
        #pickle stats here
        saveModelCVData(df)
        
    return df
    

# def crossvalStats(cvmodel,model,X,y,ifirstneg,xtest,ytest,ifirstneg_test,xtrain,ytrain,ifirstneg_train,i,seq,label='', showplot=0, showkernels=0):
def crossvalStats(cvmodel,X,y,ifirstneg,xtrain,ytrain,ifirstneg_train,itest,i,seq,label='', showplot=0, showkernels=0):
    """Calculate cross validation stats"""
    
    # thresholds for stats are the lowest true peak
    ny=1
    if len(y.shape)>1:
        ny=y.shape[1]
    yhat_train=np.reshape(cvmodel(xtrain),(xtrain.shape[0],ny))
    (stats_train)=util.cov2accuracy(ytrain,yhat_train,th=y[ifirstneg-1])        

    print(itest)
    yhat=np.reshape(cvmodel(X),(X.shape[0],ny))
    yhat_test=yhat[itest]
    ytest=y[itest]
    yposmin=y[ifirstneg-1]
    
    (nnlay,cnnlay)=model_disect.getSubModels(cvmodel)
    fmaphat=cnnlay(X)
    fmaphat_test=fmaphat[itest]
    
    
    return stats_train,yhat_test,yhat,y,fmaphat_test,fmaphat




def balanceKfold(X,y,ifirstneg,k,skip=0,gsize=1):
    """ TODO - NEEDS REFACTORING INTO SEPERATE FUNCTIONS
    
    A generator function that ....
    
    THE WAY THIS WORKS CURRENTLY IS LEAVE ONE OUT
    - CALLS leaveOneOutKfold TO GET THE INDICES FOR THE DATA TO LEAVE OUT (AND KEEP)
    - USE THESE INDICES ON POS DATA ONLY
    - ALWAYS INCLUDE ALL NEGATIVE DATA IN THE TRAINING
    
    BUT THE COMMENTED CODE BELOW CAN ALSO DO KFOLD ON THE NEGATIVE TO SPLIT 
    NEGATIVE BETWEEN TEST AND TRAIN
    
    
    
    
    returns kfold for training/tersting
    the data are first split into the peaks and non peaks
    then each subset are kfolded and each kfold concatenated together
    so each final kfold will have a kfold of peaks, and kfold of non
    if k> then the total number of peak, k will be set to number of peaks
    gize accomodates circ permuation - it is the size of groups of peaks that are all the same peak, but circ perm.  
    It is assumed that the first peak of every group is the primary (e.g. peak zero is the real uncirc perm strongest peak)"""
    
    # first split the trainin set into pos (peaks) and neg (non peaks)
    X_pos,X_neg,y_pos,y_neg=tf_util.splitPosNegData(X,y,ifirstneg)
    
    # kf1 = KFold(n_splits=min(k,len(y_pos)), shuffle=True)
    kf1 = leaveOneOutKfold(X_pos,min(k,len(y_pos)-skip),skip=skip,gsize=gsize)
    
    kf2 = KFold(n_splits=min(k,len(y_neg)-skip), shuffle=True)
    

    for ((t1,t2),(t3,t4)) in zip(kf1,kf2.split(X_neg)):
        # pdb.set_trace()
        # print(t2) #number of peaks in test set
        
        
        
        xptrain=X_pos[t1,:,:,:]
        xptest=X_pos[t2,:,:,:]
        yptrain=y_pos[t1]
        yptest=y_pos[t2]
        
        # xntrain=X_neg[t3,:,:,:]
        # xntest=X_neg[t4,:,:,:]
        # yntrain=y_neg[t3]
        # yntest=y_neg[t4]

        # xtrain = np.concatenate((xptrain,xntrain))
        # ytrain = np.concatenate((yptrain,yntrain))

        xtrain = np.concatenate((xptrain,X_neg))
        ytrain = np.concatenate((yptrain,y_neg))

        # xtest = np.concatenate((xptest,xntest))
        # ytest = np.concatenate((yptest,yntest))

        xtest = np.concatenate((xptest,X_neg))
        ytest = np.concatenate((yptest,y_neg))


        ifirstneg_train=len(t1)
        ifirstneg_test=len(t2)
        
        # print(len(t1),len(t2),len(t3),len(t4),ifirstneg_train,ifirstneg_test)
        
        #print(xtrain.shape,ytrain.shape,xtest.shape,ytest.shape)
        
        yield xtrain,ytrain,ifirstneg_train,xtest,ytest,ifirstneg_test,t2
        
    
    return

def leaveOneOutKfold(X,k,skip=0,gsize=1):
    """given indices from X.shape[0], returns two sets of indices (t1,t2)
    t2 - is the index of a single data point to leave out for testing
    t1 - is the rest
    t1 and t2 ar arrays
    indices for t2 are taken starting from first element to the kth element
    k must be <= to the number of data points in data
    if skip >0 then skip those number of elements before starting to return t2 (and t1)
    gize accomodates circ permuation - it is the size of groups of peaks that are all the same peak, but circ perm.  
    It is assumed that the first peak of every group is the primary (e.g. peak zero is the real uncirc perm strongest peak)"""

    
    if k+skip>X.shape[0]:
        raise Exception('K+skip (%d) must be less than the X.shape[0] %d'%(k+skip,X.shape[0]))
        
    allind=set(range(X.shape[0]))
    
    
    for i in range(skip*gsize,k+(skip*gsize),gsize):
        t2=np.array([i])
        t1=np.array(list(allind.difference(range(i,i+gsize))))
        yield (t1,t2)
    
    
    
    return

def plotTestTrainOverlay(yhat_train,ytrain,ifirstneg_train,yhat_test,ytest,yposmin,**kwargs):
    """Plot test and training data on one plot - used for CV
    TODO Should be moved to a module for CV"""
    
    if 'ax' in kwargs:
        ax=kwargs.get('ax')
    else:
        fig, ax = plt.subplots(1,1)    
    
    # last_test=len(ytest)-1
    last_train=len(ytrain)-1
    ms=14
    lw=2

    
    ax.plot(ytrain,yhat_train,'ro',fillstyle='none',)
    
    # the positive test data is always the first point (index=0) in ytest/yhat_test
    if (yhat_test[0]<yposmin).any():  #TODO need to test this on hydra models
        ax.plot(ytest[0,:],yhat_test[0,:],'ro',markersize=ms, lw=lw,fillstyle='none')
    else:
        ax.plot(ytest[0,:],yhat_test[0,:],'ro',markersize=ms, lw=lw)
    
    # ax.plot(ytest[1:last_test],yhat_test[1:last_test],'bs',markersize=ms)
    
    ax.plot(ytrain[ifirstneg_train:last_train,:],yhat_train[ifirstneg_train:last_train,:],'ko',fillstyle='none',)


    ax.plot([0,1.05], [0,1.05], c="black")
    ax.set_xlabel('Actual')
    ax.set_ylabel('Predicted')
    ax.set_ylim([None,1.05])
    ax.set_xlim([None,1.05])
    
    if 'title' in kwargs:
        tit=kwargs.get('title')
        ax.set_title(tit,fontsize=15)
    
#--------------------------------
#%%  UTILITY FUNCTIONS
#--------------------------------

#-----------------------
def genome_prediction_comparison(model,stepsize=10,ws=10,th=0.1,pred_ave_win=0,exp_data=None, data_sources=None):

    """Compare model prediction to genome coverage maxing over windows of ws
    Returns:
        
        # smoothed data - max over ws avoids the issue that chipseq peaks are spread out, so that a window
        # can have coverage but not the actual peak which means that we predict 0 correctly, but the coverage is
        # not zero. Since peaks can be quite broad, we look for max a ws window of tiles
        # In effect, gp and gc compare predictions on ws*stepsize windows
        # BOTTOM LINE - the prediction is actually spatially correct, it is the true coverage that is smeared
        # but we need to filter both to get correct lengths for comparison
        stats - fit between gc and gp
        gc - smoothed genome coverage on gset - ave over pred_ave_win (none by default), then max over ws
        gp - smoothed prediction of genome coverage on gset
        
        # raw data on genome tiling path
        gpred - prediction of model on gset ave over pred_ave_win
        gpos - middle position of each tile of gset
        gcov - the coverage from experimental data - NOT gset
        gcov_tile - true coverage on gset
        gset - the sequences that form a tiling set along genome
    """
    #data_sources = {} if not data_sources else data_sources
    
    #parse the model name
    (tf_name,exp_num,nkerns,ksize,nnact,final_layer,model_tag,doubleseq,slen)=parseModelName(model.name)    
    if (exp_data==None):
        exp_data=loadModelTrainingData(model.name)
    
    # this get the prediction on the genome
    (gpred,model_slen,gset,gpos)=tf_util.genome_prediction(model,stepsize,plotfig=0,doubleseq=doubleseq, data_sources=data_sources)
    gpos=gpos+int(model_slen/2)
    gcov=exp_data['gcov']
    
    
    # ave the gpred over window 
    if (pred_ave_win>0):
        gpred=util.window_ave(gpred, pred_ave_win, stepsize=1)

    # this gets the true coverage at the positions of the prediction
    if (len(gcov.shape)==1):
        gcov_tile=tf_util.genomeTileAve(gcov,gpos,5)
        gcov_tile=gcov_tile-np.mean(gcov_tile)
        gcov_tile=gcov_tile/np.max(gcov_tile)
        
    else:
        # not efficient - need to fix
        temp=[]
        for ii in range(gcov.shape[1]):
            temp.append(tf_util.genomeTileAve(gcov[:,ii],gpos,5))
        gcov_tile=np.array(temp).transpose()
        gcov_tile=gcov_tile-np.mean(gcov_tile,axis=0)
        gcov_tile=gcov_tile/np.max(gcov_tile,axis=0)
            

    # this does a max over windows on both prediction and true 
    # it is necessary to correct for smear on true, but done on pred to get correct lenghts for prediction
    gp=util.window_max(gpred, ws)
    gc=util.window_max(gcov_tile, ws)
    
    # calculate accuracy between prediction and true - SHOULD MAKE THIS A FUNCTION IN TF_UTIL (args: model,stepsize,ws,th)
    # that performs the three blocks of code above and then calls util.cov2accuracy
    (stats)=util.cov2accuracy(gc,gp,th=th)
    
    return stats,gc,gp,gpred,gpos,gcov,gcov_tile,gset
#--------------------------------
#%%  CALLBACKS DURLING LEARNING
#--------------------------------

class PerformanceCallback(keras.callbacks.Callback):
    """
    Callback to plot the learning curves of the model during training.
    """
    def __init__(self, x,y,ifirstneg,nepochs,seq,plot_kernels=1):
        self.x=x
        self.y=y
        self.nepochs=nepochs
        self.ifirstneg=ifirstneg
        self.seq=seq
        self.plot_kernels=plot_kernels

    def on_epoch_end(self, epoch, logs={}):

        if (epoch%20==0):
            print('Epoch %d --- Loss %e'%(epoch,logs.get("loss")))
            if logs.get("val_loss") is not None:
                print('Epoch %d --- Val Loss %e'%(epoch,logs.get("val_loss")))  
        
        if (epoch%self.nepochs==0):
            
            if self.plot_kernels==1:
                tf_util.plotModelKernels(self.model)
            
                mit_pfm,ns=tf_util.plotModelPFM(self.model,self.seq,0.5,title=self.model.name,numseqs=self.ifirstneg)
                plt.show()
            
            yhat=np.reshape(self.model(self.x),(self.x.shape[0],1))
            plotYvsYhat(self.y, yhat,firstneg=self.ifirstneg,title='epoch_%d (loss=%.5E)(%s)'%(epoch,logs.get("loss"),self.model.name))
            
