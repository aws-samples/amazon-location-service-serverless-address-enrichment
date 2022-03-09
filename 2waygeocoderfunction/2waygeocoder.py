#  Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import boto3
import pandas as pd
import io
import os
import urllib.parse

###  This function takes a raw data shard from the "raw" bucket, 
###  uses AWS Locations to GeoCode/ReverseGeoCode based on the columns in the datasets, 
###  and puts the processed shard into a "processed" bucket.
s3_client = boto3.client('s3')
location = boto3.client('location')
destination_bucket = os.environ.get('PROCESSED_SHARDS_BUCKET')
location_index = os.environ.get('LOCATION_INDEX')

def lambda_handler(event, context):
    ################################################################
    #     Get Pre-Processed Shard from S3 via a triggered GET      #
    ################################################################
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    s3_file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8') 
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print(f"Successful S3 get_object response. Status - {status}")
        data = pd.read_csv(response.get("Body")).dropna(thresh=2)
        data = data.rename(columns=str.title)
        columns = data.columns
        Countries = []
        Points = []
        Latitude = []
        Longitude = []
        Labels = []
        Regions = []
        SubRegions = []
        Municipalities = []
        Zipcodes = []
        ###########################
        #     ReverseGeocoder     #
        ###########################
        if "Latitude" and "Longitude" in columns:
            for index, row in data.iterrows():
                try:
                    response = location.search_place_index_for_position(
                        IndexName=location_index,
                        Position=[row.Longitude, row.Latitude])
                    json_response = response["Results"]
                except:
                    print("API Response Error")
                try:
                    Country = (json_response[0]["Place"]["Country"])
                    Countries.append(Country)
                except:
                    Countries.append(0)
                try:
                    Zipcode = (json_response[0]["Place"]["PostalCode"])
                    Zipcodes.append(Zipcode)
                except:
                    Zipcodes.append(0)
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                except:
                    Points.append(0)
                try:
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Longitude.append(0)
                    Latitude.append(0)
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append(0)
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append(0)
                except:
                    Municipalities.append(0)
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append(0)
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append(0)
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
    
            data["Points"] = Points
            data["Country"] = Countries
            data["Zipcode"] = Zipcodes
            #data["Latitude"] = Latitude
            #data["Longitude"] = Longitude
            data["Label"] = Labels
            data["Municipality"] = Municipalities
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
        #########################################################
        #     Geocoder  (for different possible column labels)  #
        #########################################################
        elif "Address" in columns:
            for index, row in data.iterrows():
                 try:
                    response = location.search_place_index_for_text(
                        IndexName=location_index,
                        Text= str(row.Address) + row.City + "," + row.State)
                    json_response = response["Results"]
                    print(json_response)
                 except:
                    print("API Response Error")
                 try:
                    Country = (json_response[0]["Place"]["Country"])
                    Countries.append(Country)
                 except:
                    Countries.append(0)
                 try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                 except:
                    Points.append(0)
                 try:
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                 except:
                    Longitude.append(0)
                    Latitude.append(0)
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                 try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                 except:
                    Labels.append(0)
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                 try:
                    if "Municipality" in (json_response[0]["Place"]):
                         Municipality = (json_response[0]["Place"]["Municipality"])
                         Municipalities.append(Municipality)
                    else:
                         Municipalities.append(0)
                 except:
                     Municipalities.append(0)
                 try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                 except:
                    Regions.append(0)
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                 try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                 except:
                    SubRegions.append(0)
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
    
            data["Points"] = Points
            data["Country"] = Countries
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["Label"] = Labels
            data["Municipality"] = Municipalities
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
    
        elif "Street" in columns:
            for index, row in data.iterrows():
                try:
                    response = location.search_place_index_for_text(
                        IndexName=location_index,
                        Text= str(row.Street) + row.City + "," + row.State)
                    json_response = response["Results"]
                    print(json_response)
                except:
                    print("API Response Error")
                try:
                    Country = (json_response[0]["Place"]["Country"])
                    Countries.append(Country)
                except:
                    Countries.append(0)
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                except:
                    Points.append(0)
                try:
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Longitude.append(0)
                    Latitude.append(0)
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append(0)
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append(0)
                except:
                    Municipalities.append(0)
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append(0)
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append(0)
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
    
            data["Points"] = Points
            data["Country"] = Countries
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["Label"] = Labels
            data["Municipality"] = Municipalities
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
        elif "City" and "State" in columns:
            for index, row in data.iterrows():
                try:
                    response = location.search_place_index_for_text(
                        IndexName=location_index,
                        Text= row.City +","+ row.State)
                    json_response = response["Results"]
                    print(json_response)
                    print(index)
                except:
                    print("API Response Error")
                try:
                    Country = (json_response[0]["Place"]["Country"])
                    Countries.append(Country)
                except:
                    Countries.append(0)
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                except:
                    Points.append(0)
                try:
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Longitude.append(0)
                    Latitude.append(0)
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append(0)
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append(0)
                except:
                    Municipalities.append(0)
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append(0)
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append(0)
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
    
            data["Points"] = Points
            data["Country"] = Countries
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["Label"] = Labels
            data["Municipality"] = Municipalities
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
        ################################################## 
        #     Write processed shard to S3 via a PUT      #
        ##################################################
        with io.StringIO() as csv_buffer:
            data.to_csv(csv_buffer, index=False)
            response = s3_client.put_object(
                Bucket=destination_bucket, Key=s3_file_key, Body=csv_buffer.getvalue()
                )
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status == 200:
                print(f"Successful S3 put_object response. Status - {status}")
            else:
                print(f"Unsuccessful S3 put_object response. Status - {status}")
