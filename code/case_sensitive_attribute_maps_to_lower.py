import json
import os
from collections import Counter

def convert_ontologies(input_directory,output_directory,strategy):

    for temp_ont_address in os.listdir(input_directory):
        #read it in
        with open(input_directory+temp_ont_address,'r') as temp_input_file:
            temp_ont=json.load(temp_input_file)

        output_dict=dict()

        if strategy=='keep_last_encountered':
            for temp_key in temp_ont:
                output_dict[temp_key.lower()]=temp_ont[temp_key]

        with open(output_directory+temp_ont_address,'w') as temp_output_file:
            json.dump(output_dict,temp_output_file,indent=4)


if __name__=="__main__":

    strategy='keep_last_encountered'
    input_directory='../intermediate_results/attribute_node_id_pairs/'
    output_directory='../intermediate_results/attribute_node_id_pairs_lowercase/'

    convert_ontologies(input_directory,output_directory,strategy)