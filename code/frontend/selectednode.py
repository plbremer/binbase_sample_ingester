from frontend_helper import *
from neo4j import GraphDatabase

driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))

class SelectedNode:

    def __init__(self,node_name,existing_node,node_name_and_ids):
        print(node_name)
        print(existing_node)
        print(node_name_and_ids)
        self.existing_node=existing_node
        #the MeSH hierarchy has many nodes with the same name. we must connect to all the gneeric nodes. using a single id wont work
        if existing_node=='existing_node':
            self.generic_node_ids_to_connect_to=node_name_and_ids[node_name]
            self.node_name=node_name
        #FrontendHelper.
        # elif existing_node=='new_node':
        #     self.generic_node_ids_to_connect_to=


    def update_name(self,label_value):
        self.node_label=label_value