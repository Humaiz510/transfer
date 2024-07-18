import boto3
import re
import datetime

def get_lambda_details(lambda_name):
    client = boto3.client('lambda')
    response = client.get_function(FunctionName=lambda_name)
    return response

def get_s3_buckets_from_logs(log_group_name):
    client = boto3.client('logs')
    
    query = """
    fields @timestamp, @message
    | filter @message like /s3/
    | parse @message /"([^"]*\.s3\.bucket)"/ as bucket
    | display bucket
    """
    
    start_query_response = client.start_query(
        logGroupName=log_group_name,
        startTime=int((datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()),
        endTime=int(datetime.datetime.now().timestamp()),
        queryString=query,
        limit=1000
    )
    
    query_id = start_query_response['queryId']
    
    response = None
    while response == None or response['status'] == 'Running':
        response = client.get_query_results(
            queryId=query_id
        )
    
    buckets = set()
    for result in response['results']:
        for field in result:
            if field['field'] == 'bucket':
                buckets.add(field['value'])
    
    return list(buckets)

def find_associated_resources(lambda_name_or_arn):
    lambda_name = lambda_name_or_arn.split(':')[-1]
    lambda_details = get_lambda_details(lambda_name)
    log_group_name = f'/aws/lambda/{lambda_name}'
    
    buckets = get_s3_buckets_from_logs(log_group_name)
    
    associated_resources = {
        'Lambda': [lambda_details['Configuration']['FunctionArn']],
        'S3': buckets
    }
    return associated_resources

if __name__ == "__main__":
    lambda_name_or_arn = input("Enter the Lambda function name or ARN: ")
    resources = find_associated_resources(lambda_name_or_arn)
    print(f"Associated resources for Lambda {lambda_name_or_arn}:")
    for resource_type, resource_list in resources.items():
        print(f"{resource_type}:")
        for resource in resource_list:
            print(f"  - {resource}")
