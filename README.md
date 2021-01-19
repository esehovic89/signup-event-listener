## Setup 

To deploy and run the code on AWS execute the commands below via aws cli tool.
Make sure your user has the necessary privileges to create the needed resources.


### Create an S3 bucket

Create an S3 bucket where the artifact will be uploaded 

`aws s3 mb s3://komoot-coding-challenge-sam`


### Package artifact and generate template
Navigate to the root of this project and execute the command below.

`aws cloudformation package --s3-bucket komoot-coding-challenge-sam --template-file template.yaml --output-template-file gen/generated-template.yaml`

### Create stack
After the artifact is succesfully uploaded to the S3 bucket, execute the following
command to create a CloudFormation stack and all the needed resources.
 
`aws cloudformation deploy --template-file gen/generated-template.yaml --stack-name CodingChallengeStack --capabilities CAPABILITY_IAM`