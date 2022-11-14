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
        with open('../../intermediate_results/models_and_matrices_webapp/training_set_list.json','r') as my_file:
            self.tfidf_vectorizer_training_set=json.load(my_file)

    def read_in_models(self):
        self.tfidf_vectorizer=pickle.load(open('../../intermediate_results/models_and_matrices_webapp/TfidfVectorizer.bin','rb'))
        self.nea_nei_model=pickle.load(open('../../intermediate_results/models_and_matrices_webapp/NN_model.bin','rb'))

    def get_node_property_matrix(self):
        '''
        should be in api

        !!!!
        needs to be redone in light of label ALL_NODE_LABEL
        !!!!

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
        #print(unique_nodeLabel_set)
        self.property_dict={element:list() for element in unique_nodeLabel_set}
        for temp_record in results_list:
            self.property_dict[temp_record[1][0]].append(temp_record[2])
        pprint(self.property_dict)

    def get_node_labels_for_string(self,temp_string,temp_driver):
        '''
        the point of this is to get all of the node labels, etc for a given text string
        basically, it helps populat the short list (so that 'plasma' appears as Plasma-MESH_NODE)

        we actually should get the node type from the app.... because the nodes have various "identifying" properties
        
        #or we could change it so that all of the NODELABELS have the same "name/id" and then we index on those...
        #call it something like "identifying name" or some such

        can get the mesh

        shold be in api
        '''

        # <id>	3
        # id	D03.633.100.221
        # mesh_id	D03.633.100.221
        # mesh_label	Benzoxazoles

        # <id>	56136
        # id	6
        # ncbi_id	6
        # rank	genus
        # scientific_name Azorhizobium

        results_list=list()
        #driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
        query=f'''match (n) where n.id='{temp_string}' return n limit 5'''
        #with driver.session() as my_session:
        with temp_driver.session() as my_session:
            my_results=my_session.run(query)
            for element in my_results:
                results_list.append(element)
        #driver.close()
        #pprint(results_list)
        return results_list

    def generate_nodes_from_freetext_string(self,freetext_string):
        my_test_strings_vector=self.tfidf_vectorizer.transform([freetext_string])
        _,kn_ind=self.nea_nei_model.kneighbors(my_test_strings_vector,2)
        total_results=list()
        print(kn_ind)
        for element in kn_ind[0]:
            print(self.tfidf_vectorizer_training_set[element])
            total_results.append(
                (
                    self.tfidf_vectorizer_training_set[element],
                    self.total_node_id_dict[
                        self.tfidf_vectorizer_training_set[element]
                    ]
                )
            )
        #print(total_results)
        return total_results

    def node_to_json(self,neo4j_node):
        '''
        Convert a neo4j node object into json/dict
        :param neo4j_node:
        :return: node in json/dict format
        '''

        json_version = {}
        for items in neo4j_node.items():
            json_version[items[0]] = items[1]

        return json_version

    def construct_smart_node_selection_options(self,graph_db_record,string_node_id_pair):
        '''
        putting "humans" into the taxonomy thing did not work out well. it returns "human" and "humans" one is a species and one is a genus
        there needs to be more detail so that people chosoe the righ thing
        '''
        #print(graph_db_record.labels)
        
        
        #print(graph_db_record)
        this_nodes_properties=self.node_to_json(graph_db_record[0])
        #print(type(graph_db_record))
        #print(type(graph_db_record[0]))
        #print(graph_db_record[0].items())
        #print(graph_db_record.get('node'))
        #print(self.node_to_json(graph_db_record[0]))
        #print(graph_db_record.get('properties'))
        #print(graph_db_record.labels)
        print('-'*50)
        if 'NCBI_NODE' in graph_db_record[0].labels:
            #print('ncbi node')
            #print(graph_db_record.get('properties'))
            total_string=f'{this_nodes_properties["scientific_name"]} - NCBI Node - Rank: {this_nodes_properties["rank"]}'
            #print(total_string)
        elif 'MESH_NODE' in graph_db_record[0].labels:
            print('mesh node')
            total_string=f'{this_nodes_properties["mesh_label"]} - MeSH Node'
            print(total_string)
        else:
            print('other type of node')
        return total_string
        #pass

    def get_all_node_labels(self):
        '''
        should be in api
        '''
        driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
        query='''call db.labels()'''
        results_list=list()
        with driver.session() as my_session:
            my_results=my_session.run(query)
        #print(dir(my_results))
        #print(my_results._summary)
            for element in my_results:
                results_list.append(element)
        driver.close()
        #pprint(results_list)
        # property_dict={
        #     element.nodeLabels[0]:
        # }
        
        label_set=set()
        for temp_record in results_list:
            label_set.add(temp_record[0])
        # #print(unique_nodeLabel_set)
        # self.property_dict={element:list() for element in unique_nodeLabel_set}
        # for temp_record in results_list:
        #     self.property_dict[temp_record[1][0]].append(temp_record[2])
        # pprint(self.property_dict)
        #print(label_set)
        return label_set

    def get_all_edge_labels(self):
        '''
        should be in api
        '''
        driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
        query='''call db.relationshipTypes()'''
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
        
        label_set=set()
        for temp_record in results_list:
            label_set.add(temp_record[0])
        # #print(unique_nodeLabel_set)
        # self.property_dict={element:list() for element in unique_nodeLabel_set}
        # for temp_record in results_list:
        #     self.property_dict[temp_record[1][0]].append(temp_record[2])
        # pprint(self.property_dict)
        print(label_set)
        return label_set



if __name__=="__main__":
    my_FrontendHelper=FrontendHelper()
    # my_FrontendHelper.read_in_freetext_jsons('../../intermediate_results/attribute_node_id_pairs/')
    # my_FrontendHelper.read_in_models()
    # my_FrontendHelper.read_in_training_set()
    # my_test_string_list=['utero']
    # my_test_strings_vector=my_FrontendHelper.tfidf_vectorizer.transform(my_test_string_list)
    # kn_dist,kn_ind=my_FrontendHelper.nea_nei_model.kneighbors(my_test_strings_vector,100)
    # for location in kn_ind[0]:
    #     print(my_FrontendHelper.tfidf_vectorizer_training_set[location])
    # my_FrontendHelper.get_node_property_matrix()
    # my_FrontendHelper.get_all_node_labels()
    my_FrontendHelper.get_all_edge_labels()
