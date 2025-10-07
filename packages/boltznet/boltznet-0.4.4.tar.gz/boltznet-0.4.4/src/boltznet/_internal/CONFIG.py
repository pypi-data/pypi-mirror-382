#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file that can be modified for each user
Primarily to indicate locations of files etc

@author: jgalag
"""

# SERVER LOCATIONS

server_data_root = '/Volumes/eng_research_galagan/seqdata/projects/ecoli'
'''Mounted server location of seqdata/projects/ecoli'''
server_projects_root = '/Volumes/eng_research_galagan/seqdata/projects/'
'''Mounted server location of seqdata/projects/'''

server_meme_root = '%s/downstream_files/analysis/meme' % server_data_root
'''Mounted server location of meme analysis directory'''

boltznet_comparison_server='/Volumes/eng_research_galagan/seqdata/projects/boltzNetComparisons/'

new_regulon_dir='/Volumes/eng_research_galagan/seqdata/projects/ecoli/downstream_files/analysis/known_motifs/Regulon-v12-confirmed'
'''Location of regulonDB meme file'''


# LOCAL PLACES

model_dir = '/Users/jgalag/Dropbox/Python/CNNModels/models'
'''Location for models'''

model_json_dir = '%s/json'%model_dir
'''Location for model json files'''


bokeh_temp_dir = '/Users/jgalag/Dropbox/Python/CNNModels/bokeh_temp'
'''Temp dir for browsers'''

browser_dir = '/Users/jgalag/Dropbox/Python/CNNModels/browsers'
'''Standard location for TF genome browsers and model browsers'''

data_dir = '/Users/jgalag/Dropbox/Python/CNNModels/source/datafiles'
'''Location of datafiles including genome files and geneview files'''

# figpath='/Users/jgalag/Dropbox/Projects/Papers/Ecoli Papers/Model Paper/resub'
figpath='/Users/jgalag/Dropbox/Projects/Papers/Ecoli Papers/Boltznet/NatureFormat/Nat Comm Files/Final Submission/figures'

file_dir = '/Users/jgalag/Dropbox/Python/CNNModels/input_files'
'''Loction of Files for import and export'''

source_dir ='/Users/jgalag/Dropbox/Python/CNNModels/source'
'''Location of source folder'''
