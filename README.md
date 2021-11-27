
# Lambda_Scatter_Gather

Instructions to deploy in an AWS account: 

1) sam build
2) sam deploy -g 
	2a) follow steps and input unique names for the 4 s3 buckets (ie. input3609) (appending last 4 digits of your phone number or something similar to "input" "raw" "processed" and "destination" respectivly should work nicely. Avoid upercase or special characters, or else the template will fail in deployment 

3) once your template has successfully deployed, add a sample .csv file into the "inputXXXX" bucket to test the geocoding capabilities. You can monitor the other buckets as well as the lambda functions to see the parallel processing take place in real time. Your output can be found in the "destination" bucket.

