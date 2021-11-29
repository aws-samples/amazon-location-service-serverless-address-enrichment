# Serverless Address Validation with Amazon Location Service

This repository contains a SAM tempalte and code for deploying a Serverless Address Validation pipeline using S3, Lambda, and Amazon Location Service.

## Highlevel Architecture
<img width="891" alt="Architecture" src="https://user-images.githubusercontent.com/73195085/141511303-9475720d-778d-4fd6-9305-3c2acdf00484.png">

  1.	The *Scatter* Lambda function takes a data set from the S3 bucket labeled *input* and breaks it into equal sized shards. 
  2.	The *Process* Lambda function takes each shard from the *pre-processed* bucket and performs Address Validation in parallel calling the [Amazon Location Service Places API](https://docs.aws.amazon.com/location-places/latest/APIReference/Welcome.html)
  3.	The *Gather* Lambda function takes each shard from the *post-processed* bucket and appends them into a complete dataset with additional address information.


## Deploying the Project
### 1. Deploy SAM application 

To use the SAM CLI, you need the following tools:

 - SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)


## Testing the Application

Sample dataset for goecoding: City of Hartford, CT Business Listing Dataset
 - https://catalog.data.gov/dataset/city-of-hartford-business-listing

Sample dataset for reverse-geocoding: NYPD Shooting Incident Data (Historic) Dataset
 - https://catalog.data.gov/dataset/nypd-shooting-incident-data-historic


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
>>>>>>> 9d32564376548b4c5634f637754be3ba5fef0e39

