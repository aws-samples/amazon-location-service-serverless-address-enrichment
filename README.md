# Serverless Address Validation with Amazon Location Service

This repository contains a SAM tempalte and code for deploying a Serverless Address Validation pipeline using S3, Lambda, and Amazon Location Service.

## Highlevel Architecture
![Screen Shot 2021-12-09 at 12 08 50 PM](https://user-images.githubusercontent.com/73195085/145862737-42331c9c-ccee-4553-b915-6bb27bb39a30.png)



  1.	The *Scatter* Lambda function takes a data set from the S3 bucket labeled *input* and breaks it into equal sized shards. 
  2.	The *Process* Lambda function takes each shard from the *pre-processed* bucket and performs Address Validation in parallel calling the [Amazon Location Service Places API](https://docs.aws.amazon.com/location-places/latest/APIReference/Welcome.html)
  3.	The *Gather* Lambda function takes each shard from the *post-processed* bucket and appends them into a complete dataset with additional address information.


## Deploying the Project
### Prerequistes:

To use the SAM CLI, you need the following tools:
  - [AWS account](https://aws.amazon.com/free/?trk=ps_a134p000003yBfsAAE&trkCampaign=acq_paid_search_brand&sc_channel=ps&sc_campaign=acquisition_US&sc_publisher=google&sc_category=core&sc_country=US&sc_geo=NAMER&sc_outcome=acq&sc_detail=%2Baws%20%2Baccount&sc_content=Account_bmm&sc_segment=438195700994&sc_medium=ACQ-P%7CPS-GO%7CBrand%7CDesktop%7CSU%7CAWS%7CCore%7CUS%7CEN%7CText&s_kwcid=AL!4422!3!438195700994!b!!g!!%2Baws%20%2Baccount&ef_id=Cj0KCQjwsuP5BRCoARIsAPtX_wEmxImXtbdvL3n4ntAafj32KMc_sXL9Z-o8FyXVQzPk7w__h2FMje0aAhOFEALw_wcB:G:s&s_kwcid=AL!4422!3!438195700994!b!!g!!%2Baws%20%2Baccount&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) 
  - AWS SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
  - Python 3.9 or later - [download the latest of version of python](https://www.python.org/downloads/) 
  - An [AWS Identity and Access Managment](https://aws.amazon.com/iam/) role with appropriate access

### This Sample Includes: 
  - *template.yaml*: Contains the AWS SAM template that defines you applications AWS resources, which includes a Place Index for Amazon Location Service
  - *scatterfunction/*: Contains the Lambda handler logic behind the scatter function and its requirements 
  - *2waygeocoderfunction/*: Contains the Lambda handler logic for the processor function which calls the Amazon Location Service Places API to perform address   validation
  - *gatherfunction/*: Contains the Lambda handler logic for the gather function which appends all of processed data into a complete dataset

### Deploy Sam-App:
1. Use `git clone https://github.com/aws-samples/amazon-location-service-serverless-address-validation` to clone the repository to your environment where AWS SAM and python are installed.
2. Use ``cd ~/environment/amazon-location-service-serverless-address-validation``to change into the project directory containing the template.yaml file SAM uses to build your application. 
3. Use ``sam build`` to build your application using SAM. You should see 
4. Use `sam deploy --guided` to deploy the application to your AWS account. 
5. Input names for the application parameters. Provide a globally unique name for your s3 buckets such as input-YOUR NAME or input-AWS::ACCOUNTID. See below for an example.
  ![image](https://user-images.githubusercontent.com/73195085/145865103-2677a8e0-8c9c-4a0a-8ae0-db11a3831a59.png)







## Testing the Application

Sample dataset for GeoCoding: City of Hartford, CT Business Listing Dataset
 - https://catalog.data.gov/dataset/city-of-hartford-business-listing

Sample dataset for Reverse-GeoCoding: NYPD Shooting Incident Data (Historic) Dataset
 - https://catalog.data.gov/dataset/nypd-shooting-incident-data-historic


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
>>>>>>> 9d32564376548b4c5634f637754be3ba5fef0e39

