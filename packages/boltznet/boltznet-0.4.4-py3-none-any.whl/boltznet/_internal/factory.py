# -*- coding: utf-8 -*-

"""
Created Mon March 31, 2024

Example usage:
factory = Factory()
dat_obj = factory.create(data_sources.get('data_sources_type', 'ecoliDB'), data_sources=data_sources)
tf_list = dat_obj.get_tf_list(data_sources=data_sources)  # get TF list
factory.close()

@author: christopherkrenz
"""




from .fileDataType import FileDataType #uncommented Keith


class Factory:
    
    #---------- Object Creation ----------#
    def __init__(self):
        
        self.data_object = None
        
        self.data_object_types = {
            'ecoliDB': ecoliDB,
            'darpaDB': darpaDB,
            'mtbDB': mtbDB,
            'fileDataType': FileDataType,
        }
            
        
    def create(self, dataSourceConfig, **kwargs):
        """
        Uses data_object_type to identify the appropriate object type and instantiates it
        """
        #pdb.set_trace()
        data_sources_type = dataSourceConfig.get('data_sources_type','ecoliDB') #Second term is an optional term that is returned if the fist one is not found
        dat_obj_type = self.data_object_types.get(data_sources_type, None)  # get object type
        if not dat_obj_type:  # if type was unrecognized...
            raise ValueError(f"Do not recognize {dat_obj_type} data structure (hint: valid example would be ecoliDB)")
        else:            
            self.data_object = dat_obj_type(data_sources=dataSourceConfig,**kwargs)  # else instantiate and return object

            return self.data_object
        
    
    #---------- Object Removal ----------#
    def close(self):
        """
        Empty function for now
        """
        pass
        
        
    def __del__(self):
        
        self.close()


