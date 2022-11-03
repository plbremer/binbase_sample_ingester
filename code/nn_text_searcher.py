from nltk.util import trigrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import json
import os
import time
import pickle

class NNTextSearcher:

    def __init__(self,json_base_address):
        temp_file_address_list=os.listdir(json_base_address)
        #print(temp_file_list)
        temp_file_list=list()
        for temp_file in temp_file_address_list:
            with open(json_base_address+temp_file,'r') as file_path:
                temp_file_list.append(json.load(file_path))

        self.total_node_id_dict=dict()
        for temp_dict in temp_file_list:
            self.total_node_id_dict.update(temp_dict)

    def create_tfidf_matrix(self):
        self.training_set=[element.lower() for element in self.total_node_id_dict.keys()]
        self.TfidfVectorizer=TfidfVectorizer(
            analyzer=trigrams,
            #max_df=1,
            #min_df=0.001
        )
        self.tfidf_matrix=self.TfidfVectorizer.fit_transform(self.training_set)


    def create_NN_model(self):
        self.NN_model=NearestNeighbors(
            n_neighbors=100,
            n_jobs=5,
            metric='cosine'
        )
        self.NN_model.fit(self.tfidf_matrix)


if __name__ =="__main__":
    my_NNTextSearcher=NNTextSearcher('../intermediate_results/attribute_node_id_pairs/')
    print(len(my_NNTextSearcher.total_node_id_dict))
    my_NNTextSearcher.create_tfidf_matrix()
    my_NNTextSearcher.create_NN_model()


    with open('../intermediate_results/models_and_matrices_webapp/TfidfVectorizer.bin','wb') as fp:
        pickle.dump(my_NNTextSearcher.TfidfVectorizer, fp)

    with open('../intermediate_results/models_and_matrices_webapp/TfidfVectorizer.bin','wb') as fp:
        pickle.dump(my_NNTextSearcher.TfidfVectorizer, fp)

    start=time.time()
    my_test_string_list=['utero']
    my_test_strings_vector=my_NNTextSearcher.TfidfVectorizer.transform(my_test_string_list)
    kn_dist,kn_ind=my_NNTextSearcher.NN_model.kneighbors(my_test_strings_vector,100)
    end=time.time()
    print(end-start)
    for location in kn_ind[0]:
        print(my_NNTextSearcher.training_set[location])
    
