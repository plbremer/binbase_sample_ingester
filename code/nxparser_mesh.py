import networkx as nx
from collections import defaultdict

class NXParserMesh:

    def __init__(self):
        self.mesh_nx=nx.DiGraph()

    def readMeSH(self,fin):
        """
        Given a file-like object, generates MeSH objects, i.e.
        dictionaries with a list of values for each qualifier.
        Example: {"MH": ["Acetylcysteine"]}
        """
        currentEntry = None
        for line in fin:
            line = line.strip()
            if not line:
                continue
            # Handle new record. MeSH explicitly marks this
            if line == "*NEWRECORD":
                # Yiel old entry, initialize new one
                if currentEntry:
                    yield currentEntry
                currentEntry = defaultdict(list)
                continue
            # Line example: "MH = Acetylcysteine"
            key, _, value = line.partition(" = ")
            # Append to value list
            currentEntry[key].append(value)
        # If there is a non-empty entry left, yield it
        if currentEntry:
            yield currentEntry
    
    def add_nodepath_and_label_to_endnode_to_mesh_networkx(self,temp_mesh_entry):
        '''
        We receive a networkx label and a single mesh entry
        we split the MN into multiple labels
        we split each label into a list of perpetually growing strings (A01, A01.032, A01.032,047)
        we add the "word label" at the end from teh MH
        '''

        #MN and MH are 'attributes' in the ascii text file
        #MN is all paths
        #MH is the end node
        nodepath_string_path_list=temp_mesh_entry['MN']
        
        #confirm that we are adding the right label always because there is only one
        if (len(temp_mesh_entry['MH']))>1:
            print(temp_mesh_entry['MH'])
            hold=input('found an entry with multiple labels')
        end_node_label=temp_mesh_entry['MH'][0]


        for temp_string_path in nodepath_string_path_list:
            node_path_elements=temp_string_path.split('.')
            node_paths=list()

            for i in range(0,len(node_path_elements)):
                node_paths.append('.'.join(node_path_elements[0:i+1]))

            #if 'A11' in node_paths:
                nx.add_path(self.mesh_nx,node_paths)
            self.mesh_nx.nodes[node_paths[-1]]['mesh_label']=end_node_label

    def get_current_headnodes(self):
        number_string_list=['01','02','03','04','05','06','07','08','09']+[str(i) for i in range(10,51)]
        possible_headnodes_list=list()
        for i in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
            for j in [str(i) for i in number_string_list]:
                possible_headnodes_list.append(i+j)
        self.current_headnodes=[element for element in possible_headnodes_list if (element in self.mesh_nx)] 
              
    def make_mesh_nx(self,mesh_file_address):
        with open(mesh_file_address, "r") as infile:
            # readMeSH() yields MeSH objects, i.e. dictionaries
            for entry in self.readMeSH(infile):
                self.add_nodepath_and_label_to_endnode_to_mesh_networkx(entry)

        self.get_current_headnodes()
        self.complete_top_of_nx()
        self.remove_mesh_subgraphs(['B'])

    def complete_top_of_nx(self):
        category_headnodes={
            'A':'Anatomy',
            'B':'Organisms',
            'C':'Diseases',
            'D':'Chemicals and Drugs',
            'E':'Analytical, Diagnostic and Therapeutic Techniques, and Equipment',
            'F':'Psychiatry and Psychology',
            'G':'Phenomena and Processes',
            'H':'Disciplines and Occupations',
            'I':'Anthropology, Education, Sociology, and Social Phenomena',
            'J':'Technology, Industry, and Agriculture',
            'K':'Humanities',
            'L':'Information Science',
            'M':'Named Groups',
            'N':'Health Care',
            'V':'Publication Characteristics',
            'Z':'Geographicals'
        }
        #add the category headnodes
        for element in category_headnodes.keys():
            self.mesh_nx.add_node(element,mesh_label=category_headnodes[element])

        #connect the original headnodes to the category headnodes
        temp_edges=list()
        for element in self.current_headnodes:
            temp_edges.append(
                (element[0],element)
            )
        #print(temp_edges)
        self.mesh_nx.add_edges_from(temp_edges)

        #add the true headnode
        self.mesh_nx.add_node('root',mesh_label='root')

        #connect the category headnoes to the true headnode
        temp_edges=[('root',element) for element in self.current_headnodes]
        self.mesh_nx.add_edges_from(temp_edges)

    def remove_mesh_subgraphs(self,headnodes_to_remove):
        for temp_headnode in headnodes_to_remove:
            nodes_to_remove=[
                element for element in self.mesh_nx.nodes if temp_headnode in element
            ]
        self.mesh_nx.remove_nodes_from(nodes_to_remove)



if __name__=="__main__":
    my_NXParser=NXParserMesh()
    my_NXParser.make_mesh_nx('../resources/mesh_ascii_2021.txt')
    print(my_NXParser.mesh_nx.nodes)

    ### need to save these nx to file