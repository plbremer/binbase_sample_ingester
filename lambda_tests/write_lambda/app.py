from nltk.util import trigrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import boto3
import pickle
import json




s3_client = boto3.client("s3")

#read jsons and new values
#jsons
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='training_set_list.json')
tfidf_vectorizer_training_set = json.load(
    temp_response['Body']#.read().decode('utf-8')
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='customer_added.json')
customer_added = json.load(
    temp_response['Body']#.read().decode('utf-8')
)



def handler(event, context):




    #new values - make as a dict in case we want to encapuslate the "column" that the value came from in the excel file
    customer_added_values_keys=list(event['customer_added_values'].keys())

    #increase customer_added json with whatever is fresh
    customer_added.update(event['customer_added_values'])
    #increase training list by whatever is fresh
    augmented_tfidf_vectorizer_training_set=tfidf_vectorizer_training_set+customer_added_values_keys
    

    #train new  models
    my_TfidfVectorizer=TfidfVectorizer(
            analyzer=trigrams,
        )
    tfidf_matrix=my_TfidfVectorizer.fit_transform(augmented_tfidf_vectorizer_training_set)
    NN_model=NearestNeighbors(
        n_neighbors=40,
        n_jobs=-1,
        metric='cosine'
    )
    NN_model.fit(tfidf_matrix)


    #push models, json, and training list to s3
    #customer added json
    s3_client.put_object(
        Bucket='parkerslambdatest',
        Key='customer_added.json',
        Body=json.dumps(customer_added).encode('utf-8')
    )
    #training set
    s3_client.put_object(
        Bucket='parkerslambdatest',
        Key='training_set_list.json',
        Body=json.dumps(tfidf_vectorizer_training_set).encode('utf-8')
    )    
    #models
    s3_client.put_object(
        Bucket='parkerslambdatest',
        Key='NN_model.bin',
        Body=pickle.dumps(NN_model)
    )
    s3_client.put_object(
        Bucket='parkerslambdatest',
        Key='TfidfVectorizer.bin',
        Body=pickle.dumps(my_TfidfVectorizer)
    )



    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': 'did the dang thing'
    }

# if __name__=="__main__":
#     handler(
#         {
#             "customer_added_values":{
#                 "soil": "species"
#             }
#         },
#         'nothing'
#     )