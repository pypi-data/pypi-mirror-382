#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 14:57:57 2025

@author: avanc
"""

import pandas as pd
import os
from .base_data_type import base_data_type
import glob


def create_data_sources(tf, file_paths):
    """
    constructs a  data_sources dict dynamically--used to initialize a FileDataType object.
    
    params:
    - base_path (str): base directory where the user's data files are located.
    - file_names (dict, optional): dictionary mapping logical dataset keys (ex anything with 'unionPeaks', 'passingChipExperiments' in the file name) 
        to exact filenames or filename patterns (ex "unionPeaks*.csv"). If a pattern is 
        provided, the first match is used.
    - genome_mat (str, optional): path to genome mat file.
    - fasta_file (str, optional): path to FASTA file.
    -wig_runs (str, optional): Path to wig runs
    -wig_file (str, optional): Path to wig file to include in the data source dictionary.
    
    Note:
code allows a little flexibility in how data files are specified.
If filenames folow these naming patterns (like 'unionPeaks*.csv'), the function 
will detect using glob. If filenames dont follow patterns, the 
user must explicitly specify them directly in the config file or command-line overrides.
best thing is to just put in config.

    return:
    - dict: a dictionary of file paths that exist 
    """
    
    default_names = {
        "unionPeaks": "unionPeaks*.csv",
        "unionPeaksExpCoverage": "unionPeaksExpCoverage*.csv",
        "individualExpCoverage": "individualExpCoverage*.csv",
        "passingChipExperiments": "passingChipExperiments*.csv"
    }
    
    base_path=file_paths['file_path']
    genome_mat = file_paths['genome_mat']
    file_names = file_paths['file_names']
    wig_runs=file_paths['wig_runs']
    wig_file=file_paths['wig_file']
    
    # if file_names is None:
    #     file_names = {}
    #     for key, pattern in default_names.items():
    #         matches = glob.glob(os.path.join(base_path, pattern))
    #         if matches:
    #             file_names[key] = os.path.basename(matches[0]) 
    
    #pull out filenames
    resolved_files = {}   
    for key, name_or_pattern in file_names.items():
        if '*' in name_or_pattern:
            matches = glob.glob(os.path.join(base_path, name_or_pattern))
            if matches:
                resolved_files[key] = os.path.basename(matches[0])
                print(f"[INFO] Resolved pattern for {key}: {resolved_files[key]}")
            else:
                print(f"[WARN] No match found for pattern: {name_or_pattern}")
        else:
            resolved_files[key] = name_or_pattern

    print("debug resolved files", resolved_files)


    # if genome_mat is None:
    #     mat_files = glob.glob(os.path.join(base_path, "*.mat"))
    #     genome_mat = mat_files[0] if mat_files else None

    # if fasta_file is None:
    #     fa_files = glob.glob(os.path.join(base_path, "*.fa")) + glob.glob(os.path.join(base_path, "*.fasta"))
    #     fasta_file = fa_files[0] if fa_files else None

    data_sources = {
        key: os.path.join(base_path, file_name) for key, file_name in resolved_files.items()
    }   
    
    data_sources.update({
        'data_sources_id': 'file',   
        'data_sources_type': 'fileDataType',  
        'wig_runs': wig_runs,
        'wig_file': wig_file,
        'genome_mat': genome_mat,
        # 'genome_fa': fasta_file
    })
    
    return data_sources

class FileDataType(base_data_type):
    
    """
    subclass for handling transcription factor data from local files (ex CSV).
    """
    def __init__(self, data_sources: dict = None):
        super().__init__(data_sources)
        
        self.files = data_sources
        
    
    def load_csv(self, file_key):
        """
        load a CSV file.
        """
        #pdb.set_trace()
        file_path = self.files.get(file_key)
        #print('load_csv file path:', file_path)
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
            
        res=pd.read_csv(file_path)
        
        return res
    
    def getUnionPeaks(self, tf, table_tag=''):
        """
        Get rank_ind, peak_ind, pos, start, stop, max_fe  
        from a CSV file storing union peaks, also orders by rankid.
        """
        # load CSV file for union peaks
        df = self.load_csv("unionPeaks")

        # filter the DF by te TF like edcR
        df_filtered = df[df["tf"] == tf][["rank_ind", "peak_ind", "pos", "start", "stop", "max_fe"]]

        # sort by rank_ind
        df_filtered = df_filtered.sort_values(by="rank_ind")
        df_filtered = df_filtered.reset_index(drop=True)

        return df_filtered
    
    def getUnionExpCoverageTF(self,tf,run_id,sample_id,table_tag=''):
        '''Get rank_ind,pos,start,stop,abs(fold_enrichment)   
        from union_peaks_view<tag>  
        for peaks matching tf symbol, run_id, and sample_id  
        order by rank_ind  
        '''
        #df = self.load_csv("unionPeaksExpCoverage")
        df_chip = self.load_csv("passingChipExperiments")
        df_union = self.load_csv("unionPeaks")
        indiv_df = self.load_csv("individualExpCoverage")
        print("Columns in df_union:", df_union.columns.tolist())
       
        
        indiv_filtered = indiv_df[
            (indiv_df["tf_symbol"] == tf) &
            (indiv_df["run_id"] == run_id) &
            (indiv_df["sample_id"] == sample_id)
        ]
        if "center_pos" in indiv_filtered.columns and "pos" not in indiv_filtered.columns:
            indiv_filtered = indiv_filtered.rename(columns={"center_pos": "pos"})
        print("columns in indiv_filtered:", indiv_filtered.columns.tolist())
        #print('shape: ', indiv_filtered.shape)
        if sample_id in df_union.columns:
            print(f"[wide format] using column '{sample_id}' from unionPeaks")
        
            df_union_sample = df_union[["peak_ind", "rank_ind", "pos", "start", "stop", sample_id]].copy()
            df_union_sample = df_union_sample.rename(columns={sample_id: "fold_enrichment"})
            
            print("df_union_sample keys:", df_union_sample["peak_ind"].nunique())
            print("indiv_filtered keys:", indiv_filtered["peak_ind"].nunique())
            #merged = pd.merge(df_union_sample, indiv_filtered, on=["peak_ind", "pos", "start", "stop"], how="inner")
            merged = pd.merge(df_union_sample, indiv_filtered, on=["peak_ind"], how="left")
            #merged = pd.merge(df_union_sample, indiv_filtered, on=["peak_ind"], how="inner")
            # norm column names for wide format after left merge
            if "pos_x" in merged.columns:
                merged = merged.rename(columns={
                    "pos_x": "pos",
                    "start_x": "start",
                    "stop_x": "stop"
                })
        
        else:
            print("[long format] merging full unionPeaks")
            merged = pd.merge(df_union, indiv_filtered, on=["peak_ind", "pos", "start", "stop"], how="inner")
        
            # Rename rank_ind from union if needed
            if "rank_ind_x" in merged.columns:
                merged = merged.rename(columns={"rank_ind_x": "rank_ind"})
        
       # merged = pd.merge(df_union, indiv_filtered, on=["peak_ind", "pos", "start", "stop"], how="inner")
        # if "rank_ind_x" in merged.columns:
        #     merged = merged.rename(columns={"rank_ind_x": "rank_ind"})
        if "fe" in merged.columns and "fold_enrichment" in merged.columns:
            merged = merged.drop(columns=["fe"])
        
        # Handle fold_enrichment/fe name
        if "fold_enrichment" in merged.columns:
            fe_col = "fold_enrichment"
        elif "fe" in merged.columns:
            fe_col = "fe"
        else:
            raise KeyError("not 'fe' nor 'fold_enrichment' found in merged columns")
        merged = merged.rename(columns={"fold_enrichment": "fe"})
        merged["fe"] = merged["fe"].fillna(0)
       

        #print("merged columns:", merged.columns.tolist())
        
        df_filtered = merged[["rank_ind", "pos", "start", "stop", "fe"]]
        df_filtered = df_filtered.sort_values(by="rank_ind", ascending=True)
        df_filtered = df_filtered.reset_index(drop=True) #added 3/25
        #print('table tag is', table_tag)
        #print("Final df columns:", df_filtered.columns.tolist())
        print('the filtered df: ', df_filtered.head())
        return df_filtered   
         
    
    def getIndividualExpCoverageTF(self,tf,run_id,sample_id,th,table_tag=''):
        '''Get peak_ind,center_pos,start,stop,abs(fold_enrichment)    
        from indiv_cov_table<tag>  
        for peaks matching tf symbol, run_id, and sample_id  
        and fold_enrichment>th  
        order by abs(fold_enrichment)   
        '''

        df = self.load_csv("individualExpCoverage")
        
        if 'pos' in df.columns and 'center_pos' not in df.columns:
                df = df.rename(columns={'pos': 'center_pos'})
        if 'fold_enrichment' not in df.columns and 'fe' in df.columns:
            df = df.rename(columns={'fe': 'fold_enrichment'})
        
        df_filtered = df[
        (df["tf_symbol"] == tf) & 
        (df["run_id"] == run_id) & 
        (df["sample_id"] == sample_id) & 
        (df["fold_enrichment"] > th)][['peak_ind', 'center_pos', 'start', 'stop', 'fold_enrichment']]
        
        #order by abs(fold_enrichment)
        df_filtered = df_filtered.sort_values(by="fold_enrichment", key=abs, ascending=False)

    # rename columns to match DB return format
        df_filtered = df_filtered.rename(columns={
            'center_pos': 'pos',
            'fold_enrichment': 'fe'
        })
        df_filtered = df_filtered.reset_index(drop=True) #added 3/25
        
        return df_filtered    
    
    def getTFChipExperiments(self,tf,table_tag=''):
        '''Get run_id,sample_id, modification, promoter,num_peaks,max_exp_fe  
        from the passing_chip_table<tag>  
        for a tf symbol  
        order by modification
        '''
        
        df = self.load_csv("passingChipExperiments")
        
        df_filtered = df[df["tf_symbol"] == tf][['run_id','sample_id','modification','Promoter','num_peaks','max_fe']]
        df_filtered = df_filtered.sort_values(by="modification", ascending=True)
        
        return df_filtered   
    def getTFLocation(self, tf):
        '''Estimate [start, stop] location of a TF by checking its union peaks'''
        df_union = self.load_csv("unionPeaks")
        
        tf_peaks = df_union[df_union["tf"] == tf]
        
        if tf_peaks.empty:
            print(f"warning: no union peaks found for TF {tf}")
            return None
    
        start = tf_peaks["start"].min()
        stop = tf_peaks["stop"].max()
        data = {
            'start': [122092],
            'stop': [122856]
            }
        df = pd.DataFrame(data)
        
        return df
    
    def getTFsWithUnionPeaks(self,num_peaks_th=0, max_fe_th=2,filterpat=''):
      '''Get TF, num_peak, max_fe for 
      a tf symbol aving num_peaks>num_peaks_th   
      and max_fe>max_fe_th 
      from unionPeaks .csv file
      
      Filtering is done by giving a list of tfs to exclude
      '''
      df_union = self.load_csv("unionPeaks")
      
      unique_tfs = df_union['tf'].unique()
      tf_list = []
      max_fe = []
      num_peaks=[]
      
 
      
      for tf in unique_tfs:
          tf_ind = df_union.index[df_union ['tf'] == tf].tolist()
          num_peak = len(tf_ind)
          df_tf = df_union.iloc[tf_ind]
          max_fe_in = max(df_tf['max_fe'])
          
          
          if max_fe_in>max_fe_th:
              if num_peak>num_peaks_th:
                  if tf not in filterpat:
                  
                      tf_list.append(tf)
                      max_fe.append(max_fe_in)
                      num_peaks.append(num_peak)
          
      
      out_df_cols = ['TF','num_peaks','max_fe']
      out_df = pd.DataFrame(columns=out_df_cols)
      out_df['TF'] = tf_list
      out_df['num_peaks'] = num_peaks
      out_df['max_fe'] = max_fe
          
      
      return out_df
    
# assume a user will pass in exps all for one tf
# in the future we could allow one obj of filedata type to encompass multiple tfs
        


        
        