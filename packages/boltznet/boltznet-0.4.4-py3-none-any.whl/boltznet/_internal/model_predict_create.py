#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 15:46:54 2025

@author: kolak


Module for building new models for sequences of any length using parameters and weights extracted from 
previously trained models.

To build a prediction model run the script build_predict_tf_models.py in bin folder

Main function is buildPredictionModels(model_list, seq_len,stop_layer), which takes a list of models, a
sequence length, and a stop_layer (build partial models) as the main inputs. New models are then constructed  
for the new sequence length using the extracted weights and biases from the convolution and neural network layers.
The stop_layer input enables the construction of partial models.

Tools include:
    
    -loading models from multiple places (folder or best E. coli models)
    -building full or partial models using extracted weights for sequences of any length
    -model checking and identification
    
"""

from . import CONFIG

from .model_create import loadModel, saveModel,loadModelParams, saveModelParams, create_model

import numpy as np
    #-------------------------------------------------------------
    #%% LOAD MODELS FROM DIFFERENT DATA SOURCES
    #------------------------------------------------------------



    # TODO make best models names work currrently split betwen two folders doing try loop for now
def loadBestEcoliModels(tf_list):
       '''Load all or some of the best E. coli models based on an 
       input list of tf names. To load all of the models, the input should be 'All'.
       Loads the models from best_models on the Galagan server using a list generated 
       from getBestEcoliModels() in ecoliDB.py.
           
           (models, valid_model_names) = loadBestEcoliModels(tf_list)

       '''
       if tf_list[0] == 'All':
           tf_list = None
       
       #Stf_list = [tf_list]
       models = []
       valid_model_names = []
       db=ecoliDB()
       df=db.getBestModels()
       db.close()

       if tf_list is not None:
           for tf_tf in tf_list:
              loc = df[df['tf'].str.contains(tf_tf, regex=True)]
              ind = loc.index.tolist()
              ind = int(ind[0])
              try:
                  models.append(loadModel(df.at[ind,'model'],path='%s/downstream_files/analysis/best_models' % CONFIG.server_data_root))
                  valid_model_names.append(df.at[ind,'model'])
              except:
                  print('Could not load model for %s' % tf_tf)
       else:
           model_names = df['model'].tolist()
           for model_name in model_names:
               try:
                   models.append(loadModel(model_name,path='%s/downstream_files/analysis/best_models' % CONFIG.server_data_root))
                   valid_model_names.append(model_name)
               except:
                   try:
                       models.append(loadModel(df.at[ind,'model'],path='%s/downstream_files/analysis/best_models_11_10_23' % CONFIG.server_data_root))
                       valid_model_names.append(df.at[ind,'model'])
                   except:
                       print('Could not load %s' % model_name)
       return models, valid_model_names
    


    #-------------------------------------------------------------
    #%% PREDCTION MODEL BUILDING 
    #-------------------------------------------------------------


def modifyModelName_SeqLength(model_name,seq_len, kstack, tag):
    '''Generates a new name for the prediction model. Takes the sequence 
    length for the new model and replaces the number for the one in the old model name
    after "slen".
        
        new_model_name = modifyModelName_seqLength(old_model_name,seq_length)'''  

    ind = model_name.index('slen')
    len_seq_num = len(str(int(seq_len/2)))
    
    if kstack == 0:
        new_name = model_name[:(ind+4)] + str(int(seq_len/2)) + model_name[(ind+4+len_seq_num):] 
    elif 'ConvStack' in model_name:
        new_name = model_name[:(ind+4)] + str(int(seq_len/2)) + model_name[(ind+4+len_seq_num):]  + '_' + tag
    else:
        new_name = 'ConvStack' + model_name[4:(ind+4)] + str(int(seq_len/2)) + model_name[(ind+4+len_seq_num):]  + '_' + tag 
    
    return new_name
    

def buildPredictionModelFromWeighs(weight_dict,seq_len):
    ''' Builds a stacked prediction model from the stacked weights in weight_dict["conv"]
    for sequences of seq_len
    
    
    '''


    # The params for this new model
    model_params={ 'pool': 'ave', 'conv_kreg': None,'conv_actreg': None, 'conv_biasreg': None}
    weights=weight_dict['conv']
    model_params['nkerns'] = weights['weights'].shape[3]
    model_params['ksize']  = weights['weights'].shape[1]
    model_params['xslen']  = seq_len
    model_params['kstack'] = 1
    
    stop_layer=2
    
    # build model from saved weight dict
    predict_model = create_model('prediction_model',model_params, stop_layer = stop_layer, 
                                                  initialize_Weights_from_Dict = True, 
                                                  weight_dict=weight_dict, kstack = 1)
    
    return predict_model,model_params


def buildPredictionModels(model_list, seq_len,stop_layer=2, load_dir=CONFIG.model_dir,tag = '', kstack = 0, save_files=True):
    '''Builds new models for sequences of any length using parameters and 
    weights extracted from the convolution and NN layers of previous models. 
    Has the ability to build reduced versions of the old_model using the 
    stop_layer feature.Returns a list of new models and their new names.
    
    stop_layer:
        
        0 = conv only 
        1 = conv + FRSumus
        2 = conv+ FRSumus + pool 
        3 = full model
    
        Signature
        new_models = buildPredictionModels(model_list, seq_len,stop_layer)
        
        Returns
        new_models - list of new tensorflow models
        new_model_params - list of new param objects
        
        kstack = 1 for stacked model, 0 otherwise
    '''
        
        
    new_model_params = []
    new_models =[]
    model_count = len(model_list)
    b = False
        
    print('Building and Saving Prediction Models')
    
    #cycle through all models in the list
    for old_model in model_list:
        
        new_model_name = modifyModelName_SeqLength(old_model.name,seq_len,kstack, tag)
        
        #Sets parameters for model building 
        model_params, model_options = loadModelParams(old_model.name, path = load_dir)
        if model_params.get('kstack',None) is None and kstack == 1:
            model_params['nkerns'] = model_count
            model_params['kstack'] = model_params['nkerns']
        elif model_params.get('kstack',None) is not None:
            model_params['nkerns'] = model_params['kstack']
            model_params['kstack'] = model_params['nkerns']
            
        model_params['xslen'] = seq_len
        model_params['extra_tag'] = tag
        
        #Model bulding function
        if kstack == 0:
            new_model = create_model(new_model_name,model_params, stop_layer = stop_layer, old_model = [old_model], initialize_Weights = True, kstack = kstack)
        else:
            new_model = create_model(new_model_name,model_params, stop_layer = stop_layer, old_model = model_list, initialize_Weights = True, kstack = kstack)
            b = True
            model_name = []
            
            #Adds kernel order to the model parameters if not already present
            for model in model_list:
                model_name.append(model.name)
            if 'ConvStack' not in model_name:        
                model_params['kernel_order'] = model_name
            
        
        
        new_models.append(new_model)
        new_model_params.append(model_params)
        
        if save_files:
            saveModelParams(new_model.name,model_params, model_options)
            saveModel(new_model)
        
        #If a stack model was built break the for loop as all models in the list were used to construct one model
        if b ==True:
            break
        #checkWeights_MP(model,new_model)
        
    return new_models, new_model_params
    
  

    #-------------------------------------------------------------
    #%% MODEL VALIDATION AND IDENTIFICATION
    #------------------------------------------------------------- 
    

def checkWeights(old_model, new_model):
    '''Check if the weight matrix and bias terms are equal between the two models for the 
    convolution layer.'''
    
    l_old=old_model.get_layer('conv')#double check this
    kernel_weights_old = l_old.get_weights()[0]
    bias_weight_old = l_old.get_weights()[1]
    l_new=new_model.get_layer('conv')#double check this
    kernel_weights_new = l_new.get_weights()[0]
    bias_weight_new = l_new.get_weights()[1]
    print('Bias weight Match: %s' % np.array_equal(bias_weight_new,bias_weight_old))
    print('Kernel weight Match: %s' % np.array_equal(kernel_weights_old,kernel_weights_new))

    return


def isStackedModel(model):
    '''
    Determines if the model is a Convstack model or not by checking the biases in 
    the Conv2D layer. Returns True if the model is a stacked model.
    Returns False if the model is not a stacked model.
    '''
    l = model.get_layer('conv')
    biases = l.get_weights()[1]
    if len(biases) > 1:
        return True
    else:
        return False
    
def getLayerList(model, path = CONFIG.model_dir):
    '''Takes a model and returns a list of the models used to make the given model'''
    model_params, _ = loadModelParams(model.name, path = path)
    if model_params.get('kernel_order',None) is None:
        return model.name
    else:
        return model_params['kernel_order']
    
    
    

    
    
    
    