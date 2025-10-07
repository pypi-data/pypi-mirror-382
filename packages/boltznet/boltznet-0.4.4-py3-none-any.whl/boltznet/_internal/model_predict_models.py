#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module with functions to retrieve models available for building prediction
models.  

The lab version of this module retrieves information from the database.
But when we release code, we can swap this module out with one that loads from
files that included as part of the release

TODO - create a function that loads a prebuild model for all TFs as well as the 
information about the TFs and genome vmaxs for all TFs



@author: jgalag
"""

from . import CONFIG
import os
from . import model_create

SERVER_MODEL_LOCATION ='https://boltznet.bu.edu/static/data/models/'
'''base url to retrieve models and params files from boltznet server'''


# -----------------------
def getAllModelNames(local_dir = False):
    '''Function to return a dataframe with inforamation for all models that have
    been built and can be used for prediction model building.  The df includes columns:
    
    - tf (the tf symbol)
    _ model (the model_name)
    
    
    Right now this is ecoli models only, but this could be extended to other sets
    in which case we could add annother column to the df for the set label
    
    '''
    if local_dir == False:
        db=ecoliDB()
        df=db.getBestModels()
        db.close()
        assert df['tf'].is_unique, "Duplicate tf names in list of tfs and models!"
    else:
        path = CONFIG.model_dir
        model_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        df = []
        for name in model_names:
            df.append(name[:-6])
    
    return df


def getModelFromServer(model_name,server_location=SERVER_MODEL_LOCATION, local_model_location=CONFIG.model_dir):
    '''Retrieve a model and associated pickle files from from the server
    
    TODO - need to load he pickle files to the server - right now only models
    are uploaded
    
    '''
    pass

# -----------------------
def getTFModels(tf_name_list=None, all_model_names=None, model_location=CONFIG.model_dir):
    '''Function that retrieves a model and params for the TFs in tf_name_list
    Returns an exception if any tf_name does not have a model
    
    First checks locally, and then downloads from SERVER_MODEL_LOCATION if not local
    
    all_model_names is the return from getAllModelNames().  If None, then call getAllModelNames for this info.  I
    
    tf name matching is case insensitive
    
    if tf_name_list is None then get all TF models
    
    TODO - add support for downloading files from server
    
    returns 
    model_list - list of models
    param_list - list of param objects
    '''
    
    # get all the models if necessary
    if all_model_names is None:
        all_model_names=getAllModelNames()

    if tf_name_list==None:
        tf_name_list=all_model_names['tf'].to_list()
    

    # find the (first) entry for tf_name - assumes no duplicates
    model_names=[]
    model_list=[]
    params_list=[]
    for tf_name in tf_name_list:
        
        row = all_model_names[all_model_names['tf'].str.lower() == tf_name.lower()]
        if row.empty:
            raise Exception('Could not find a model for %s' %tf_name)
        
        model_name=row['model'].iloc[0]
        tf_name=row['tf'].iloc[0]
        
        # check to see if it exists and and if not, download from server and unzip
        if not modelExists(model_name):
            # load from server TODO
            pass
        
        # add model name and tf_name to list
        model_names.append(model_name)
        
    # load all models and params
    for mname in model_names:
        model=model_create.loadModel(mname,model_location)
        model_list.append(model)
        params=model_create.loadModelParams(mname,model_location) # returns tuple of model_params, model_options
        params_list.append(params)
             
    
    # and return lists
    return model_list,params_list
    
    

# -----------------------
def modelExists(model_name, path=CONFIG.model_dir):
    """checks to see if a model exists by the same name"""
    # checks to see if model exists and returns 1 if so, 0 if not
    filename = '%s/%s.model' % (path, model_name)

    return os.path.exists(filename)
