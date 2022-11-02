import networkx as nx
import metagenompy
import numpy as np
from collections.abc import Iterable

class NXParserNCBI:

    def __init__(self):
        self.ncbi_nx=metagenompy.generate_taxonomy_network(auto_download=False)

if __name__=="__main__":
    my_NXParserNCBI=NXParserNCBI()
    
