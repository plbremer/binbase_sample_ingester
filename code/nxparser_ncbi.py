import networkx as nx
import metagenompy
import numpy as np
from collections.abc import Iterable

class NXParserNCBI:

    def __init__(self):
        self.ncbi_nx=metagenompy.generate_taxonomy_network(auto_download=False)

    def construct_graphml_for_neo4j(self):
        #based on
        #https://stackoverflow.com/questions/65973902/which-elements-from-networkx-graph-might-become-labels-at-neo4j-graph
        for temp_node in self.ncbi_nx.nodes:
            self.ncbi_nx.nodes[temp_node]['labels']=':NCBI_NODE:ALL_NODE_LABEL'
            for attribute in ['acronym','includes','authority','synonym','genbank_acronym','equivalent_name','type_material','genbank_synonym','common_name','blast_name','in-part','genbank_common_name']:
                try:
                    del self.ncbi_nx.nodes[temp_node][attribute]
                except KeyError:
                    continue
            #self.ncbi_nx.nodes[temp_node]['ncbi_id']=temp_node
        for temp_edge in self.ncbi_nx.edges:
            self.ncbi_nx.edges[temp_edge]['label']='PARENT_OF'


if __name__=="__main__":
    my_NXParserNCBI=NXParserNCBI()
    nx.write_gpickle(my_NXParserNCBI.ncbi_nx,'../intermediate_results/nxs/ncbi_nx.bin')

    my_NXParserNCBI.construct_graphml_for_neo4j()
    nx.write_graphml(my_NXParserNCBI.ncbi_nx, '../intermediate_results/graphmls/ncbi_graphml.graphml', named_key_ids=True)
    ### need to save these nx to file
