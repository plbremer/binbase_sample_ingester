import pandas as pd
import json

class GeneTSVParser:
    
    def __init__(self,file_path):
        self.gene_panda=pd.read_csv(file_path,sep='\t')


    def create_attribute_to_node_id_from_panda(self):
        '''
        we assume that 'Symbol' and 'Description' are what we need to complete this
        '''
        symbol_mapping=dict(zip(self.gene_panda['Symbol'].tolist(),self.gene_panda['NCBI GeneID'].tolist()))
        description_mapping=dict(zip(self.gene_panda['Description'].tolist(),self.gene_panda['NCBI GeneID'].tolist()))
        self.total_feature_node_id_dict={**symbol_mapping,**description_mapping}


if __name__=="__main__":
    my_GeneTSVParser=GeneTSVParser('/home/rictuar/coding_projects/fiehn_work/binbase_sample_ingester/resources/ncbi_genes_human.tsv')
    my_GeneTSVParser.create_attribute_to_node_id_from_panda()
    with open('../intermediate_results/attribute_node_id_pairs/genes_human.json', 'w') as fp:
        json.dump(my_GeneTSVParser.total_feature_node_id_dict, fp,indent=4)   