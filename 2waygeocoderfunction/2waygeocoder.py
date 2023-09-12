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
        data = pd.read_csv(response.get("Body")).dropna(thresh=1)
        data = data.rename(columns=str.title)
        columns = data.columns
        Countries = []
        Points = []
        Latitude = []
        Longitude = []
        Labels = []
        AddressNumbers = []
        Streets = []
        Regions = []
        SubRegions = []
        Municipalities = []
        Neighborhoods = []
        PostalCodes = []
        Relevances = []
        Interpolates = []
        Categories = []
        ###########################
        #     ReverseGeocoder     #
        ###########################
        if "Latitude" and "Longitude" in columns:
            for index, row in data.iterrows():
                try:
                    json_response = ""
                    response = location.search_place_index_for_position(
                        IndexName=location_index,
                        Position=[row.Longitude, row.Latitude])
                    json_response = response["Results"]
                except:
                    print("API Response Error")
                try:
                    CountryCode = (json_response[0]["Place"]["Country"])
                    Countries.append(CountryCode)
                except:
                    Countries.append("")
                try:
                    PostalCode = (json_response[0]["Place"]["PostalCode"])
                    PostalCodes.append(PostalCode)
                except:
                    PostalCodes.append("")
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Points.append("")
                    Longitude.append("")
                    Latitude.append("")
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append("")
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    AddressNumber = (json_response[0]["Place"]["AddressNumber"])
                    AddressNumbers.append(AddressNumber)
                except:
                    AddressNumbers.append("")
                try:
                    Street = (json_response[0]["Place"]["Street"])
                    Streets.append(Street)
                except:
                    Streets.append("")
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append("")
                except:
                    Municipalities.append("")
                try:
                    Neighborhood = (json_response[0]["Place"]["Neighborhood"])
                    Neighborhoods.append(Neighborhood)
                except:
                    Neighborhoods.append("")
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append("")
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append("")
                try:
                    Interpolate = (json_response[0]["Place"]["Interpolated"])
                    Interpolates.append(Interpolate)
                except:
                    Interpolates.append("")
                    print("Error: Interpolated unavailable for given input in row", (len(Points)) + 1)
                try:
                    Category = (json_response[0]["Place"]["Categories"])
                    Categories.append(Category)
                except:
                    Categories.append("")
                    print("Error: Categories unavailable for given input in row", (len(Points)) + 1)
    
            data["Label"] = Labels
            data["Points"] = Points
            #data["Latitude"] = Latitude
            #data["Longitude"] = Longitude
            data["AddressNumber"] = AddressNumbers
            data["Street"] = Streets
            data["Municipality"] = Municipalities
            data["Neighborhood"] = Neighborhoods
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
            data["PostalCode"] = PostalCodes
            data["CountryCode"] = Countries
            data["Interpolated"] = Interpolates
            data["Categories"] = Categories
        #########################################################
        #     Geocoder  (for different possible column labels)  #
        #########################################################
        elif "Address" and "City" and "State" and "Zip" in columns:
            for index, row in data.iterrows():
                try:
                    json_response = ""
                    if 'Country' in columns and pd.isna(row.Country) == False:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= str(row.Address) + str(row.City) + "," + str(row.State) + "," + str(row.Zip),
                            FilterCountries=[str(row.Country)])
                    else:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= str(row.Address) + str(row.City) + "," + str(row.State) + "," + str(row.Zip))
                    json_response = response["Results"]
                    print(json_response)
                except:
                    print("API Response Error")
                try:
                    CountryCode = (json_response[0]["Place"]["Country"])
                    Countries.append(CountryCode)
                except:
                    Countries.append("")
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Points.append("")
                    Longitude.append("")
                    Latitude.append("")
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append("")
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    AddressNumber = (json_response[0]["Place"]["AddressNumber"])
                    AddressNumbers.append(AddressNumber)
                except:
                    AddressNumbers.append("")
                try:
                    Street = (json_response[0]["Place"]["Street"])
                    Streets.append(Street)
                except:
                    Streets.append("")
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                         Municipality = (json_response[0]["Place"]["Municipality"])
                         Municipalities.append(Municipality)
                    else:
                         Municipalities.append("")
                except:
                     Municipalities.append("")
                try:
                    Neighborhood = (json_response[0]["Place"]["Neighborhood"])
                    Neighborhoods.append(Neighborhood)
                except:
                    Neighborhoods.append("")
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append("")
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append("")
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
                try:
                    PostalCode = (json_response[0]["Place"]["PostalCode"])
                    PostalCodes.append(PostalCode)
                except:
                    PostalCodes.append("")
                try:
                    Relevance = (json_response[0]["Relevance"])
                    Relevances.append(Relevance)
                except:
                    Relevances.append("")
                    print("Error: Relevance unavailable for given input in row", (len(Points)) + 1)
                try:
                    Interpolate = (json_response[0]["Place"]["Interpolated"])
                    Interpolates.append(Interpolate)
                except:
                    Interpolates.append("")
                    print("Error: Interpolated unavailable for given input in row", (len(Points)) + 1)
                try:
                    Category = (json_response[0]["Place"]["Categories"])
                    Categories.append(Category)
                except:
                    Categories.append("")
                    print("Error: Categories unavailable for given input in row", (len(Points)) + 1)
    
            data["Relevance"] = Relevances
            data["Label"] = Labels
            # data["Points"] = Points
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["AddressNumber"] = AddressNumbers
            data["Street"] = Streets
            data["Municipality"] = Municipalities
            data["Neighborhood"] = Neighborhoods
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
            data["PostalCode"] = PostalCodes
            data["CountryCode"] = Countries
            data["Interpolated"] = Interpolates
            data["Categories"] = Categories
        elif "Street" and "City" and "State" in columns:
            for index, row in data.iterrows():
                try:
                    json_response = ""
                    if 'Country' in columns and pd.isna(row.Country) == False:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= str(row.Street) + row.City + "," + row.State,
                            FilterCountries=[str(row.Country)])
                    else:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= str(row.Street) + row.City + "," + row.State)
                    json_response = response["Results"]
                    print(json_response)
                except:
                    print("API Response Error")
                try:
                    CountryCode = (json_response[0]["Place"]["Country"])
                    Countries.append(CountryCode)
                except:
                    Countries.append("")
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Points.append("")
                    Longitude.append("")
                    Latitude.append("")
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append("")
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    Street = (json_response[0]["Place"]["Street"])
                    Streets.append(Street)
                except:
                    Streets.append("")
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append("")
                except:
                    Municipalities.append("")
                try:
                    Neighborhood = (json_response[0]["Place"]["Neighborhood"])
                    Neighborhoods.append(Neighborhood)
                except:
                    Neighborhoods.append("")
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append("")
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append("")
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
                try:
                    PostalCode = (json_response[0]["Place"]["PostalCode"])
                    PostalCodes.append(PostalCode)
                except:
                    PostalCodes.append("")
                try:
                    Relevance = (json_response[0]["Relevance"])
                    Relevances.append(Relevance)
                except:
                    Relevances.append("")
                    print("Error: Relevance unavailable for given input in row", (len(Points)) + 1)
                try:
                    Interpolate = (json_response[0]["Place"]["Interpolated"])
                    Interpolates.append(Interpolate)
                except:
                    Interpolates.append("")
                    print("Error: Interpolated unavailable for given input in row", (len(Points)) + 1)
                try:
                    Category = (json_response[0]["Place"]["Categories"])
                    Categories.append(Category)
                except:
                    Categories.append("")
                    print("Error: Categories unavailable for given input in row", (len(Points)) + 1)
    
            data["Relevance"] = Relevances
            data["Label"] = Labels
            # data["Points"] = Points
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["Street"] = Streets
            data["Municipality"] = Municipalities
            data["Neighborhood"] = Neighborhoods
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
            data["PostalCode"] = PostalCodes
            data["CountryCode"] = Countries
            data["Interpolated"] = Interpolates
            data["Categories"] = Categories
        elif "City" and "State" in columns:
            for index, row in data.iterrows():
                try:
                    json_response = ""
                    if 'Country' in columns and pd.isna(row.Country) == False:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= row.City +","+ row.State,
                            FilterCountries=[str(row.Country)])
                    else:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= row.City +","+ row.State)
                    json_response = response["Results"]
                    print(json_response)
                    print(index)
                except:
                    print("API Response Error")
                try:
                    CountryCode = (json_response[0]["Place"]["Country"])
                    Countries.append(CountryCode)
                except:
                    Countries.append("")
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Points.append("")
                    Longitude.append("")
                    Latitude.append("")
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append("")
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append("")
                except:
                    Municipalities.append("")
                try:
                    Neighborhood = (json_response[0]["Place"]["Neighborhood"])
                    Neighborhoods.append(Neighborhood)
                except:
                    Neighborhoods.append("")
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append("")
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append("")
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
                try:
                    PostalCode = (json_response[0]["Place"]["PostalCode"])
                    PostalCodes.append(PostalCode)
                except:
                    PostalCodes.append("")
                try:
                    Relevance = (json_response[0]["Relevance"])
                    Relevances.append(Relevance)
                except:
                    Relevances.append("")
                    print("Error: Relevance unavailable for given input in row", (len(Points)) + 1)
                try:
                    Interpolate = (json_response[0]["Place"]["Interpolated"])
                    Interpolates.append(Interpolate)
                except:
                    Interpolates.append("")
                    print("Error: Interpolated unavailable for given input in row", (len(Points)) + 1)
                try:
                    Category = (json_response[0]["Place"]["Categories"])
                    Categories.append(Category)
                except:
                    Categories.append("")
                    print("Error: Categories unavailable for given input in row", (len(Points)) + 1)
    
            data["Relevance"] = Relevances
            data["Label"] = Labels
            # data["Points"] = Points
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["Street"] = Streets
            data["Municipality"] = Municipalities
            data["Neighborhood"] = Neighborhoods
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
            data["PostalCode"] = PostalCodes
            data["CountryCode"] = Countries
            data["Interpolated"] = Interpolates
            data["Categories"] = Categories
        elif "Addressline" in columns:
            for index, row in data.iterrows():
                try:
                    json_response = ""
                    if 'Country' in columns and pd.isna(row.Country) == False:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= row.Addressline,
                            FilterCountries=[str(row.Country)])
                    else:
                        response = location.search_place_index_for_text(
                            IndexName=location_index,
                            Text= row.Addressline)
                    json_response = response["Results"]
                    if (len(json_response) == 0):
                        print (f"Error: No results for record {index} {row.Addressline}")
                        Countries.append("")
                        Points.append("")
                        Longitude.append("")
                        Latitude.append("")
                        Labels.append("")
                        AddressNumbers.append("")
                        Streets.append("")
                        Municipalities.append("")
                        Regions.append("")
                        SubRegions.append("")
                        PostalCodes.append("")
                        Relevances.append("")
                        Interpolates.append("")
                        Categories.append("")
                        continue
                    else:
                        print(f"Results for {index} {len(json_response)} {json_response}")
                except:
                    print("API Response Error")
                try:
                    CountryCode = (json_response[0]["Place"]["Country"])
                    Countries.append(CountryCode)
                except:
                    Countries.append("")
                try:
                    Point = (json_response[0]["Place"]["Geometry"]["Point"])
                    Points.append(Point)
                except:
                    Points.append("")
                try:
                    Longitude.append(Point[0])
                    Latitude.append(Point[1])
                except:
                    Longitude.append("")
                    Latitude.append("")
                    print("Error: Lat/Lon unavailable for given input in row", (len(Points)) + 1)
                try:
                    Label = (json_response[0]["Place"]["Label"])
                    Labels.append(Label)
                except:
                    Labels.append("")
                    print("Error: Address unavailable for given input in row", (len(Points)) + 1)
                try:
                    AddressNumber = (json_response[0]["Place"]["AddressNumber"])
                    AddressNumbers.append(AddressNumber)
                except:
                    AddressNumbers.append("")
                try:
                    Street = (json_response[0]["Place"]["Street"])
                    Streets.append(Street)
                except:
                    Streets.append("")
                try:
                    if "Municipality" in (json_response[0]["Place"]):
                        Municipality = (json_response[0]["Place"]["Municipality"])
                        Municipalities.append(Municipality)
                    else:
                        Municipalities.append("")
                except:
                    Municipalities.append("")
                try:
                    Neighborhood = (json_response[0]["Place"]["Neighborhood"])
                    Neighborhoods.append(Neighborhood)
                except:
                    Neighborhoods.append("")
                try:
                    Region = (json_response[0]["Place"]["Region"])
                    Regions.append(Region)
                except:
                    Regions.append("")
                    print("Error: Region unavailable for given input in row", (len(Points)) + 1)
                try:
                    SubRegion = (json_response[0]["Place"]["SubRegion"])
                    SubRegions.append(SubRegion)
                except:
                    SubRegions.append("")
                    print("Error: SubRegion unavailable for given input in row", (len(Points)) + 1)
                try:
                    PostalCode = (json_response[0]["Place"]["PostalCode"])
                    PostalCodes.append(PostalCode)
                except:
                    PostalCodes.append("")
                try:
                    Relevance = (json_response[0]["Relevance"])
                    Relevances.append(Relevance)
                except:
                    Relevances.append("")
                    print("Error: Relevance unavailable for given input in row", (len(Points)) + 1)
                try:
                    Interpolate = (json_response[0]["Place"]["Interpolated"])
                    Interpolates.append(Interpolate)
                except:
                    Interpolates.append("")
                    print("Error: Interpolated unavailable for given input in row", (len(Points)) + 1)
                try:
                    Category = (json_response[0]["Place"]["Categories"])
                    Categories.append(Category)
                except:
                    Categories.append("")
                    print("Error: Categories unavailable for given input in row", (len(Points)) + 1)
    
            data["Relevance"] = Relevances
            data["Label"] = Labels
            # data["Points"] = Points
            data["Latitude"] = Latitude
            data["Longitude"] = Longitude
            data["AddressNumber"] = AddressNumbers
            data["Street"] = Streets
            data["Municipality"] = Municipalities
            data["Neighborhood"] = Neighborhoods
            data["Region"] = Regions
            data["SubRegion"] = SubRegions
            data["PostalCode"] = PostalCodes
            data["CountryCode"] = Countries
            data["Interpolated"] = Interpolates
            data["Categories"] = Categories
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
