from pprint import pprint
import json
import pickle
import os
from neo4j import GraphDatabase



class FrontendHelper:

    def __init__(self):
        pass

    def read_in_freetext_jsons(self,json_base_address):
        temp_file_address_list=os.listdir(json_base_address)
        #print(temp_file_list)
        temp_file_address_list.sort()
        temp_file_list=list()
        for temp_file in temp_file_address_list:
            with open(json_base_address+temp_file,'r') as file_path:
                temp_file_list.append(json.load(file_path))

        self.total_node_id_dict=dict()
        for temp_dict in temp_file_list:
            self.total_node_id_dict.update(temp_dict)
        
        
        # with open('../intermediate_results/attribute_node_id_pairs/mesh.json','r') as my_file:
        #     mesh_string_node_pairs=json.load(my_file)
        # with open('../intermediate_results/attribute_node_id_pairs/ncbi.json','r') as my_file:
        #     ncbi_string_node_pairs=json.load(my_file)
        # self.string_node_pairs=mesh_string_node_pairs
        # self.string_node_pairs.update(ncbi_string_node_pairs)    

    def read_in_training_set(self):
        with open('../intermediate_results/models_and_matrices_webapp/training_set_list.json','r') as my_file:
            self.tfidf_vectorizer_training_set=json.load(my_file)

    def read_in_models(self):
        self.tfidf_vectorizer=pickle.load(open('../intermediate_results/models_and_matrices_webapp/TfidfVectorizer.bin','rb'))
        self.nea_nei_model=pickle.load(open('../intermediate_results/models_and_matrices_webapp/NN_model.bin','rb'))

    def get_node_property_matrix(self):
        '''
        should be in api
        '''
        driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
        query='''call db.schema.nodeTypeProperties()'''
        results_list=list()
        with driver.session() as my_session:
            my_results=my_session.run(query)
        #print(dir(my_results))
        #print(my_results._summary)
            for element in my_results:
                results_list.append(element)
        driver.close()
        pprint(results_list)
        # property_dict={
        #     element.nodeLabels[0]:
        # }
        
        unique_nodeLabel_set=set()
        for temp_record in results_list:
            unique_nodeLabel_set.add(temp_record[1][0])
        print(unique_nodeLabel_set)
        self.property_dict={element:list() for element in unique_nodeLabel_set}
        for temp_record in results_list:
            self.property_dict[temp_record[1][0]].append(temp_record[2])
        pprint(self.property_dict)

    def get_node_labels_for_string(self):
        '''
        the point of this is to get all of the node labels, etc for a given text string
        basically, it helps populat the short list (so that 'plasma' appears as Plasma-MESH_NODE)
        '''

if __name__=="__main__":
    my_FrontendHelper=FrontendHelper()
    # my_FrontendHelper.read_in_freetext_jsons('../intermediate_results/attribute_node_id_pairs/')
    # my_FrontendHelper.read_in_models()
    # my_FrontendHelper.read_in_training_set()
    # my_test_string_list=['utero']
    # my_test_strings_vector=my_FrontendHelper.tfidf_vectorizer.transform(my_test_string_list)
    # kn_dist,kn_ind=my_FrontendHelper.nea_nei_model.kneighbors(my_test_strings_vector,100)
    # for location in kn_ind[0]:
    #     print(my_FrontendHelper.tfidf_vectorizer_training_set[location])
    my_FrontendHelper.get_node_property_matrix()