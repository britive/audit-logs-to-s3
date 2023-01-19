# Britive Audit Logs

This repo holds a sample AWS Serverless Application Model (SAM) template and associated resources which deploys
infrastructure to regularly query a Britive tenant's audit logs and store the results in S3 for further downstream processing.

## Python Environment Setup

We will use `python3.9` for this. Install python for your OS.

~~~

mkvirtualenv britive-audit-logs # or whatever virtual environment manager you use
pip install britive
~~~

## SAM CLI Install

Install the AWS SAM CLI tooling: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html.


## Britive Tenant Resources

First we need to create a service identity and associate a policy that allows access to read audit logs.

Reference the documentation at https://github.com/britive/python-sdk for details on how to use the Python SDK.

~~~
export BRITIVE_API_TOKEN=...
export BRITIVE_TENANT=...

python create-audit-logs-service-identity.py
~~~

This will create a service identity and api token and ensure it has read permissions on the audit logs.
Note the token as this will be required later.

If manual steps are preferred...

1. Admin > User Administration > Service Identities >  Create new service identity and token (note the token for later)
2. Admin > Role & Policy Management > Policies > Add Policy > under members select the newly created service identity and under roles choose AuditLogViewRole then save

## Deploy the Application

Deploy the template via SAM. You will need credentials with sufficient access to an AWS account to perform these actions.

~~~
sam deploy --guided
~~~
This will walk through all of the parameters and other questions. They are listed below for clarity.

~~~
Configuring SAM deploy
======================

	Looking for config file [samconfig.toml] :  Not found

	Setting default arguments for 'sam deploy'
	=========================================
	Stack Name [sam-app]: auditlogs                                 <--- the name of the stack you want to create
	AWS Region [us-west-2]: us-west-2                               <--- the region where you want to deploy
	Parameter Tenant []: example                                    <--- the name of your britive tenant
	Parameter CreateSplunkIamResources [False]: False               <--- whether to create some additional resources splunk requires
	Parameter SplunkIamUserName []:                                 <--- provide an existing IAM user name for splunk vs. creating a new IAM user
	Parameter DeleteLogsBucketObjectsOnStackDeletion [False]: True  <--- clean up all audit logs in the S3 bucket on stack deletion
	Parameter NumberDaysOfHistoryToPull [1]: 10                     <--- how many days of history to pull on the first run
	Parameter RetrievalInterval [60]:                               <--- how often the process should run
	Parameter CreateAthenaResources [True]:                         <--- should athena workgroup/database/table/view be created to query the S3 objects
	Confirm changes before deploy [y/N]: y                          <--- shows you resources changes to be deployed and require a 'Y' to initiate deploy
	Allow SAM CLI IAM role creation [Y/n]: y                        <--- SAM needs permission to be able to create roles to connect to the resources in your template
	Disable rollback [y/N]: n                                       <--- Preserves the state of previously provisioned resources when an operation fails
	Save arguments to configuration file [Y/n]: y                   <--- save the above configuration to a file which can be referenced later
	SAM configuration file [samconfig.toml]:                        <--- hit enter and leave the default samconfig.toml
	SAM configuration environment [default]:                        <--- leave as default unless you have a reason to change it
~~~


Then in the future we can call the below since the configuration will be saved to `samconfig.toml` under the `default` config environment.

~~~
sam deploy
~~~

Once done, let's set 2 variables that will be used by the remaining commands.

~~~
token=<source from above python script output>
stack=<name of deployed stack>
~~~

We need to set the secret value to a Britive API token that has access to pull audit logs.

~~~
secret=$(aws cloudformation describe-stack-resource --stack-name $stack --logical-resource-id BritiveAuditLogsApiToken --output text --query 'StackResourceDetail.PhysicalResourceId')
aws secretsmanager update-secret --secret-id $secret --secret-string '{"token": "'$token'"}'
~~~

To manually invoke the Lambda function to test that things are working as expected...

~~~
lambda=$(aws cloudformation describe-stack-resource --stack-name $stack --logical-resource-id LambdaCollectLogs --output text --query 'StackResourceDetail.PhysicalResourceId')
aws lambda invoke --function-name $lambda --cli-binary-format raw-in-base64-out --invocation-type Event --qualifier prod response.json
cat response.json
rm response.json
~~~

At this point some audit logs should appear in the S3 bucket and be queryable via Athena if Athena resources were enabled.

Navigate to Athena and run the following query, after selecting the appropriate database and workgroup.

~~~
select * from audit_logs
~~~


## Refresh the Lambda Layers

If the Lambda layer packages ever need to be refreshed run the following commands (or any subset thereof).

~~~
rm -rf ./lambda-layers/britive/python/*
pip install https://github.com/britive/python-sdk/releases/download/v2.7.1/britive-2.7.1.tar.gz -t ./lambda-layers/britive/python/

rm -rf ./lambda-layers/requests/python/*
pip install requests -t ./lambda-layers/requests/python/

rm -rf ./lambda-layers/jsonlines/python/*
pip install jsonlines -t ./lambda-layers/jsonlines/python/

rm -rf ./lambda-layers/crhelper/python/*
pip install crhelper -t ./lambda-layers/crhelper/python/
~~~


## Cleanup

Run `sam delete` to destroy the stack.