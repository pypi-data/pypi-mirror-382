# -*- coding: utf-8 -*-
"""

Two classes

- boltznet_tf: a factory class for creating objects of boltznet_tf_model
- boltznet_tf_model: a model for one or more TFs that allow predictions on arbitrary sequences

Example usage:
    
from boltznet import boltznet_tf

# create a tfmodel on all TFs that have been loaded into the package cache
tfmodel=boltznet_tf.create()

# load sequences from fasta file and run predictions
fa_name='/Users/jgalag/Dropbox/Python/CNNModels/source/promoters.fa'
y=tfmodel(fastafile=fa_name)

# load annotations for the sequences
gff_name='/Users/jgalag/Dropbox/Python/CNNModels/source/ecoli.gff'
tfmodel.loadGff(gff_name)

# Plot the predictions for a uniques sequence by sequence index or sequence name patterns
# Below will plot sequence number 76 as well as any sequences that contain chaC or pdhR in the 
# name.  But will not plot the same sequence twice
tfmodel.plotPrediction(inds=[76],seqnames=['chaC','pdhR'],model_names=None,seqlogo=False,baseseq=False, maxN=3, savefilename=None)

"""

__all__ = ["boltznet_tf_model", "create"]


# No top level imports unless we want them to be exposed
# in the boltznet_tf namespace through dir

###################################
# The boltznet tf model class
###################################

class boltznet_tf_model():
    ''' The primary interface for predicting binding sites for one or more TFs on an arbitrary 
    set of sequences
    
    '''

    # lazy import to hide these modules from the user at the top 
    # but will stil be seen in dir(boltznet_tf.boltznet_tf_model)
    # import test_module

    
    def __init__(self,tf_list=None):
        # lazy import to keep top level namespace clean
        from ._internal import model_predict
        
        cache_dir=__cache_dir__()

        if tf_list is None:
            tf_list=__get_all_cached_models__()

        self.sp=model_predict.seqPredict(tf_list,model_location=cache_dir)
        self.tf_list=tf_list
        
    def get_model_list(self):
        '''Returns a list of TF names included in this model'''
    
        return self.tf_list
    
    def loadGff(self,gff_file,default_seqid='default'):
        '''Load annotations for sequences from GFF file
        
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
        
        self.sp.load_annot_gff(gff_file,default_seqid=default_seqid)
    
    def predict(self,fastafile=None, seqdict=None):
        """Load sequences and run predictions
        
        y=tfmodel.predict(fastafile=filename)
        
        Sequences can be provide as either
        - fastafile - this must be a path to a fasta file
        - seqdict - TBD
        Only one can be provided
        
        Returns a np array of predicions at each position on both
        strands of each sequence for all TFs
        
        The numpy array has shape
        
        (nseqs,2,seqlen,numtfs)
        - nseqs: number of sequences
        - 2: forward and reverse strands
        - seqlen: length of each sequence
        - numtf: number of models
        
        models are ordered in the same order as provided by
        tfmodel.getModelList()
        
        At every position the value is the results of applying 
        the model weight matrix centered at that position, adding the bias
        term, and the exponentiating the results
        
        """
        
        ### Load sequences and run predictions
        if fastafile is not None and seqdict is not None:
            raise Exception('Only one of fastafile or seqdict can be provided to predict()')
            
        if fastafile is not None:
            self.__load_fasta__(fastafile)
    
        # get the results of the predictions and return
        return self.sp.getPredictions()
    
    def getSeqNames(self):
        '''Return the sequence names that have been loaded'''
        
        return self.sp.seqnames
    
    def getPredictions(self):
        '''Return the predictions from the last predict() run as described in that function'''
        
        return self.sp.getPredictions()
    
    def getMaxBindingSiteScores(self):
        '''Returns an np array of the max binding site scores for each sequence for each TF
        
        Has shape of (nseqs, ntfs) where each entry is the 
        max bindins site score (proportional to the binding energy) of that TF to any
        location in the sequence
        
        Binding site scores are the sum of the exponentiated binding energies in windows
        of length(weigth_matrix) '''
        
        return self.sp.getMaxBindingSiteScores()
    
    def getScores(self):
        '''
        Returns an np array of scores for each sequence for each TF
        
        Has shape of (nseqs, ntfs) where each entry is the 
        score (proportional to the binding energy) of that TF to that entire sequence
        
        Scores are the sum of the exponentiated binding energies at every 
        position across both strands
        '''
        
        return self.sp.getScores()
    
    def plotPrediction(self,inds=None,seqnames=None, model_names=None,seqlogo=True,baseseq=True, savefilename=None, ranking_mode='full_sequence', maxN=10, **kwargs):
        '''Generate a plot of model predictions for the given sequences
        and model names
        
        Sequences can be selected in two ways:
            - inds: a list of indices into the list of sequences loaded
            - seqnames: a list of strings that will be used to retrieve any 
                        sequences that whose seqid contains the string
                        
        If both inds and seqnames are provide, both sets of sequences will be plotted
        
        If the same sequence is selected more than once, it will only be plotted once
        
        Other arguments
        - seqlogo: True to plot the sequence logo for each TF (default True)
        - baseseq: True to plot the sequence (default True)
        - MaxN: the maximum number of models to plot for any sequence if model_names is None (default 10)
        - savefilename: if given, will save plots as savefilename_<seqid>.png instead of plotting
        
        - ranking_mode: one of two strings to determine how sequences are ranked for each model
            "full_sequence": TFs ranked by summing exp(wm+bias) over every position on both strands
            "max_binding_site": sum exp(wm+bias) in ln(wm) windows over seq and take max 
        
        '''
        
        
        self.sp.plotSeqResponseByInds(inds=inds,seqnames=seqnames,tf_names=model_names,
                                      seqlogo=seqlogo,baseseq=baseseq,
                                      ranking_mode=ranking_mode,
                                      savefilename=savefilename,maxN=maxN, **kwargs)
    
    def __call__(self,fastafile=None, seqdict=None):
        '''Callable interface that calls self.predict()'''
        
        return self.predict(fastafile, seqdict)
        
    
    def __load_fasta__(self,filename):
        """Load sequences from a fasta file and run prediction
        All sequences must be the same length 
        
        Headers are expected to have the form
        
        >seqname description
        
        And if description contains the following text
         
        (start=<start>, end=<end>)
        
        then start and end are parsed out as the coordinates of the sequence
        
        once sequences are loaded, the model is run on the sequences automatically
        
        """
        
        self.sp.load_fasta(filename)
    
    def __repr__(self):
        """Unambiguous representation used for debugging."""
        
        return self.__str__()

    def __str__(self):
        """User-friendly string representation."""
        
        s='%s object on %s models with %s loaded sequences'%(self.__class__.__name__,
                                                             len(self.tf_list),self.sp.nseqs)
        
        return s



###################################
# package functions to create tf model objects
# and handle any caching of weight matrices and/or
# retrieval from boltznet website
    
def create(tf_list=None):
    
    tfmodel=boltznet_tf_model(tf_list)
    return tfmodel

def __download_model__(cache_dir,tf_name):
    '''Downloads a specific model by name and stores in
    __cache_dir__
    
    Raises an exception if the model did not download
    
    '''
    import requests,os

    JSON_PATH='https://boltznet.bu.edu/static/data/models'
    JSON_SUFFIX='_wm_bias.json'
    

    fname='%s%s'%(tf_name,JSON_SUFFIX)
    url='%s/%s'%(JSON_PATH,fname)

    try:
        response = requests.get(url)
        response.raise_for_status()  # raises an error if status != 200

        # Save content to file
        local_path = os.path.join(cache_dir, fname)

        with open(local_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded {fname} → {cache_dir}")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download {url}: {e}")
        
        

def __download_all_models__():
    '''Retrieve all model jsons from the boltznet.bu.edu website
    and store them in __cache_dir__
    
    '''
    import requests
    
    ###############################
    #### get the list of valid TFs
    TF_LIST_URL='https://boltznet.bu.edu/static/data/tf_list.txt'
    
    response = requests.get(TF_LIST_URL)
    response.raise_for_status()  # raise an error if download failed
    
    # Split by lines, strip whitespace, and store in a list
    tf_list = [line.strip() for line in response.text.splitlines() if line.strip()]
    
    ###############################
    #### get the cache dir
    cache_dir=__cache_dir__()
    
    
    ###############################
    #### try to download each json file but catch any exceptions
    #### keep a list of tfs that are downloaded
    downloaded_tfs=[]
    for tf_name in tf_list:
        try:
            __download_model__(cache_dir, tf_name)
        except Exception as e:
            print('**Warning: could not download model for %s**'%tf_name)
            continue
        downloaded_tfs.append(tf_name)
    
    ###############################
    #### save the tf_list as a text file in the cache dir
    fname='%s/tf_list.txt'%cache_dir
    print('Saving list of tf models -> %s'%fname)
    with open(fname, "w") as f:
        for tf_name in downloaded_tfs:
            f.write(tf_name + "\n")
    
    
    return
    
def __get_all_cached_models__():
    '''Return a list of all tfs with model jsons downloaded'''
    
    ###############################
    #### get the cache dir
    cache_dir=__cache_dir__()
    
    ###############################
    #### load tf_list.txt from this dir 
    fname='%s/tf_list.txt'%cache_dir
    with open(fname, "r", encoding="utf-8") as f:
        tf_list = [line.strip() for line in f if line.strip()]
    
    return tf_list

def __cache_dir__():
    '''Return the location of the cache dir where json files are
    stored.  Can be overriden with the environment variable
    BOLTZNET_CACHE_DIR
    '''
    
    import os
    from pathlib import Path
    from platformdirs import user_cache_dir 
    
    APP = "boltznet"
    
    override = os.getenv("BOLTZNET_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    d = Path(user_cache_dir(APP))
    d.mkdir(parents=True, exist_ok=True)
    return d
    


