#  Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import pandas as pd
import boto3
import io
import os

###  This function is triggered when a file with suffix _LAST.csv
###  is input into the "processed" bucket. This function then takes
###  all of the shards from the "processed" bucket and pieces them t
###  together to create a complete processed data set. Then this function 
###  writes that dataset to a "destination" bucket

s3_client = boto3.client('s3')
destination_bucket = os.environ.get('DESTINATION_BUCKET')
def lambda_handler(event, context):
    #Get all the objects in the bucket
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    #Identify the name of the most recent object uploaded to the bucket
    all = response['Contents']
    latest = max(all, key=lambda x: x['LastModified'])
    latest_object_name = (latest['Key'])
 
    #Get all the shards that share the same prefix (file name)
    response_1 = s3_client.list_objects_v2(Bucket=bucket_name, Prefix= latest_object_name[:-12])['Contents']
    
    #Create a list of all the shards
    list_of_shards = []
    count = 0
    for i in response_1:
        record = response_1[count]['Key']
        list_of_shards.append(record)
        count += 1
    
    #Create the data frame (final_doc) using the first shard
    final_doc = pd.DataFrame()
    first_object_response = response_2 = s3_client.get_object(Bucket=bucket_name, Key=list_of_shards[0])
    final_doc = pd.read_csv((first_object_response.get("Body")))
    count_2 = 1
    length=len(list_of_shards)
    

    #Write a new file (final_doc) by iterating through the list of files in the bucekt
    for i in list_of_shards[1:length]:
        response_2 = s3_client.get_object(Bucket=bucket_name, Key=i)
        data_1 = pd.read_csv((response_2.get("Body")))
        data_1 = data_1.dropna(thresh=1)
        #print(titanic_data)
        final_doc = pd.concat([final_doc, data_1])
        count_2 +=1
    
    
    #Put new File back to S3
    with io.StringIO() as csv_buffer:
        final_doc.to_csv(csv_buffer, index=False)
        response_3 = s3_client.put_object(
            Bucket=destination_bucket, Key="processed_data"+"/"+latest_object_name[:-15]+"/"+"PROCESSED_DATA_"+latest_object_name[:-15]+".csv", Body=csv_buffer.getvalue()
        )
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")

