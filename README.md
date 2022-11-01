# ta-data-lake-integration

## Description
Due to the fact that there have been multiple problems when testing the data load to Snowflake within the project in which the company is currently working, which has caused us on several occasions delays in the delivery of the development tasks for the different improvements requested to the platform since it is not possible to perform these data load tests before deploying to other development environments, it is necessary to integrate the test environments through an API that allows us to make requests through the existing ta-warehouse microservice to a Snowflake account previously assigned for testing and thus avoid delays and implement more quickly the necessary improvements or corrections each time a change is made within the project related to the data load to Snowflake.

This application expose a API from AWS API Gateway and Lambda functions to insert records in snowflake databases and update schemas, connecting to snowflake through http request from AWS Lambda functions.

## Setup

### Prerequisites
  - AWS account
  - Snowflake account
  
### Deploy AWS Lambda function
  - Download ta-data-lake-integration repository, go to Snowflake integration section and replace variables in scripts
  - Download and install aws-cli (Guide:  https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - Create a execution role and policy from command line:
  
    <pre><code> aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' </code></pre>
    
    You should can see the Arn fro the previus command output, save it. Now execute:
    
    <pre><code> aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole </code></pre>

  - Into repository folder execute: 
  
    <pre><code> zip function.zip lambda_function.py jwtAuthentication.py </code></pre>

    <pre><code> aws lambda create-function --function-name data-lake-integration \ 
    --zip-file function.zip --handler lambda_function.handler --runtime python3.8 \ 
    --role <your_arn> </code></pre>
    
### Integrate Lambda function with API Gateway
  
  #### Create API Gateway
  1. Sign in to the API Gateway console at https://console.amazonaws.cn/apigateway.
  2. Choose Create API, and then for HTTP API, choose Build.
  3. For API name, enter **data-lake-integration-api**.
  4. Choose Next.
  5. For Configure routes, choose Next to skip route creation. You create routes later.
  6. Review the stage that API Gateway creates for you, and then choose Next.
  7. Choose Create.
    
  #### Create routes
  1. Choose **Routes**.
  2. Choose Create.
  3. For method, choose **POST**.
  4. For the path, enter **/data-lake-gateway/insert.
  5. Choose Create.
  6. Repeat steps 2-5 for **PUT /data-lake-gateway/schema**.
    
  #### Create integration
  1. Choose **Integrations**.
  2. Choose Manage integrations and then choose Create.
  3. Skip Attach this integration to a route. You complete that in a later step.
  4. For Integration type, choose **Lambda function**.
  5. For Lambda function, enter **data-lake-integration**.
  6. Choose Create.
    
  #### Attach integration
  1. Choose **Integrations**.
  2. Choose a route.
  3. Under Choose an existing integration, choose **data-lake-integration**.
  4. Choose Attach integration.
  5. Repeat steps 2-4 for all routes.
  
  
### Snowflake integration

  #### Generate rsa keys
  
  <pre><code>openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 des3 -inform PEM -out snowflake_rsa_key.p8</code></pre>
  
  <pre><code>openssl rsa -in snowflake_rsa_key.p8 -pubout -out rsa_key.pub</code></pre>
  
  #### Set rsa key
  - In a snowflake worksheet execute:
  
  <pre><code>ALTER USER <username> SET RSA_PUBLIC_KEY='<public_key>'</code></pre>
  
  - Check RSA_PUBLIC_KEY and RSA_PUBLIC_KEY_FP
  
  <pre><code>DESC USER '<username>'</code></pre>


  
  
    
 

  
 
    
    
    
    
