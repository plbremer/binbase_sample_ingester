import json
import networkx as nx
from collections.abc import Iterable


class NodeIDDictParser:

    def __init__(self,file_path,attributes):
        self.input_nx=nx.read_gpickle(file_path)
        self.attributes_that_differentiate_node_id=attributes

    #def define_attributes_to_maintain(self,attributes):

    def flatten(self,xs):
        '''
        given a list of elements (can contain arbitrarily nested lists)
        creates a generator? of flattned elements
        warning: strings will become lists of char
        '''
        for x in xs:
            if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                yield from self.flatten(x)
            else:
                yield x

    def create_one_values_to_node_id_dict(self,temp_node):
        '''
        This takes a single node and returns a dict
        where the keys (probably many) are the nested values of the node
        and the value for each key is the node ID
        '''
        one_node_id_dict=dict()
        #we make scientific name the endpoint so that it works like the mesh hierarchies
        #scientific_name=self.input_nx.nodes[temp_node][temp_attribute]
        for temp_attribute in self.attributes_that_differentiate_node_id:
            #print(temp_attribute)
            if temp_attribute not in self.input_nx.nodes[temp_node].keys():
                continue
            elif isinstance(self.input_nx.nodes[temp_node][temp_attribute],str):
                #print(total_ncbi_networkx.nodes[temp_node][temp_attribute])
                one_node_id_dict[self.input_nx.nodes[temp_node][temp_attribute]]=[temp_node]
            else:
                #print(set(flatten(total_ncbi_networkx.nodes[temp_node][temp_attribute])))
                temp_dict={
                    element:[temp_node] for element in set(self.flatten(self.input_nx.nodes[temp_node][temp_attribute]))
                }
                one_node_id_dict.update(temp_dict)
        return one_node_id_dict

    def create_all_attribute_to_node_id_dict(self):
        '''
        takes an entire networkx and features that help to differentiate nodes
        returns a dict of {attribute:node_id}
        '''
        self.total_feature_node_id_dict=dict()
        for i,temp_node in enumerate(self.input_nx.nodes):
            small_dict_to_add=self.create_one_values_to_node_id_dict(temp_node)
            for temp_key in small_dict_to_add.keys():
                try:
                    self.total_feature_node_id_dict[temp_key]=self.total_feature_node_id_dict[temp_key]+small_dict_to_add[temp_key]
                except KeyError:
                    self.total_feature_node_id_dict[temp_key]=small_dict_to_add[temp_key]
            # what we had before. this basically erased all but the last entry for any particular node, so like, "Liver Neoplasms" had only one entry
            # self.total_feature_node_id_dict.update(
            #     #self.create_one_values_to_node_id_dict(temp_node)
            # )

if __name__ == "__main__":
    my_NodeIDDictParser=NodeIDDictParser('../intermediate_results/nxs/ncbi_nx.bin',{'common_name','genbank_common_name','scientific_name'})
    #'../resources/mesh_ascii_2021.txt'
    my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
    with open('../intermediate_results/attribute_node_id_pairs/ncbi.json', 'w') as fp:
        json.dump(my_NodeIDDictParser.total_feature_node_id_dict, fp,indent=4)

    my_NodeIDDictParser=NodeIDDictParser('../intermediate_results/nxs/mesh_nx.bin',{'mesh_label','common_name'})
    #'../resources/mesh_ascii_2021.txt'
    my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
    with open('../intermediate_results/attribute_node_id_pairs/mesh.json', 'w') as fp:
        json.dump(my_NodeIDDictParser.total_feature_node_id_dict, fp,indent=4)
