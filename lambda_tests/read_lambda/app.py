import boto3
import pickle
import json




s3_client = boto3.client("s3")

# # S3_BUCKET = 'BUCKET_NAME'
# # S3_PREFIX = 'BUCKET_PREFIX'

# s3 = boto3.client('s3')
# parkerslambdatest
# file_for_s3_bucket.txt


temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='NN_model.bin')
nea_nei_model = pickle.loads(
    temp_response['Body'].read()
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='TfidfVectorizer.bin')
tfidf_vectorizer = pickle.loads(
    temp_response['Body'].read()
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='training_set_list.json')
tfidf_vectorizer_training_set = json.load(
    temp_response['Body']#.read().decode('utf-8')
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='mesh.json')
mesh_dict = json.load(
    temp_response['Body']#.read().decode('utf-8')
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='ncbi.json')
ncbi_dict = json.load(
    temp_response['Body']#.read().decode('utf-8')
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='genes_human.json')
genes_human = json.load(
    temp_response['Body']#.read().decode('utf-8')
)
temp_response = s3_client.get_object(Bucket='parkerslambdatest', Key='customer_added.json')
customer_added = json.load(
    temp_response['Body']#.read().decode('utf-8')
)

total_node_id_dict={**mesh_dict,**ncbi_dict,**genes_human}




def handler(event, context):
    '''
    expects input like

    {
        "freetext_string": "neoplasms",
        "number_of_neighbors": 20
    }
    '''

    temp=json.loads(event['body'])

    #this is a list because thats what the tfidf, or maybe NN model expects
    #my_freetext_string_list=list(event['body']['freetext_string'])
    #number_of_neighbors_to_return=event['body']['number_of_neighbors']
    
    my_freetext_string_list=list(temp['freetext_string'])
    number_of_neighbors_to_return=temp['number_of_neighbors']

    my_test_strings_vector=tfidf_vectorizer.transform([my_freetext_string_list])
    _,kn_ind=nea_nei_model.kneighbors(my_test_strings_vector,number_of_neighbors_to_return)
    
    total_results=list()
    for element in kn_ind[0]:
        total_results.append(
            (
                tfidf_vectorizer_training_set[element],
                total_node_id_dict[
                    tfidf_vectorizer_training_set[element]
                ]
            )
        )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(total_results)
    }