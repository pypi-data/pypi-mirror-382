# -*- coding: utf-8 -*-
"""
Base class for a generic data source for information about TFs, peaks, etc

"""
import pandas as pd
import importlib



#-------------------------------------------------------------
#%% base_data_type OBJECTS
#-------------------------------------------------------------

class base_data_type():
    """
    Base class for a generic data source for information about TFs, peaks, etc

    """
    def __init__(self, data_sources: dict = None):
        
        # save the dataSourceConfig dictionary
        self.dataSourceConfig=data_sources
        
    def get(self,key,default=None):
        '''Return an entry from the data source config'''
        return self.dataSourceConfig.get(key,default)
    
    def getTFKnownPeaks(self,tf=None):
        ''' 
        Return known peaks for a TF ordered by start
        Returns symbol,start,stop 
        
        if TF is None then return all peaks for all TFs
        '''
        
        pass
        
        
    def getTFChipExperiments(self,tf,table_tag=''):
        '''Get run_id,sample_id, modification, promoter,num_peaks,max_exp_fe  
        '''
        
        pass
        
    
    def getTFCalledPeaks(self,tf):
        '''
        These are the union of all peaks for a tf  
        returns rank_ind,start,stop from union peaks table
        where symbol = tf  
        rank_ind is the rank of the peak by height  
        start and stop are the positions of the peak   
        '''
    
        pass
    
    def getTFLocation(self,tf):
        '''Get the location of a gene [start,stop] by tf symbol string'''        
        pass
    
    def getTFExperiments(self,tf):
        '''Get [run_id,sample_id] for all experiments  
        '''        
        
        pass
                

    def getUnionPeaks(self,tf,table_tag=''):
        '''
        Get rank_ind,peak_ind,pos,start,stop, max_fe  for all union peaks
        '''
        
        pass  

    def getTFsWithUnionPeaks(self,num_peaks_th,max_fe_th,filterpat=None,rsq_th=None,rsq_train_th=None, data_sources: dict = None):
        '''Get TF, num_peaks, max_fe  
        for a tf symbol having num_peaks>num_peaks_th   
        and max_fe>max_fe_th   
        
        if filterpat regexp is given, then filter out TFs with 
        model names matching the filterpat in ecoli_project_analysis.modelStats_view (or equivalent in other schema) 
        and whose models pass rsq_th and rsq_train_th  
        this is useful for getting TFs that still need models         
        '''
        pass  

    def getUnionExpCoverageTF(self,tf,run_id,sample_id,table_tag=''):
        '''Get rank_ind,pos,start,stop,abs(fold_enrichment)   
        from union_peaks_view<tag>  
        for peaks matching tf symbol, run_id, and sample_id  
        order by rank_ind  
        '''
        
        pass       

    def getIndividualExpCoverageTF(self,tf,run_id,sample_id,th,table_tag=''):
        '''Get peak_ind,center_pos,start,stop,abs(fold_enrichment)    
        from indiv_cov_table<tag>  
        for peaks matching tf symbol, run_id, and sample_id  
        and fold_enrichment>th  
        order by abs(fold_enrichment)   
        '''

        pass
    
    
