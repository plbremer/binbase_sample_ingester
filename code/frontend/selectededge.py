from frontend_helper import *
from neo4j import GraphDatabase

driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))

class SelectedEdge:

    #creatin an object was overkill, especially in light o fthe fact that we have to jsonify everything