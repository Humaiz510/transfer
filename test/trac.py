import boto3
import datetime

def get_lambda_details(lambda_name):
    client = boto3.client('lambda')
    response = client.get_function(FunctionName=lambda_name)
    return response

def get_xray_traces(lambda_arn, start_time, end_time):
    client = boto3.client('xray')
    
    response = client.get_trace_summaries(
        StartTime=start_time,
        EndTime=end_time,
        FilterExpression=f"service(id: '{lambda_arn}')"
    )
    
    trace_ids = [trace['Id'] for trace in response['TraceSummaries']]
    return trace_ids

def get_s3_buckets_from_traces(trace_ids):
    client = boto3.client('xray')
    
    buckets = set()
    
    for trace_id in trace_ids:
        response = client.batch_get_traces(
            TraceIds=[trace_id]
        )
        
        for trace in response['Traces']:
            for segment in trace['Segments']:
                document = json.loads(segment['Document'])
                for subsegment in document.get('subsegments', []):
                    if subsegment['namespace'] == 'aws' and 's3' in subsegment['name'].lower():
                        s3_arn = subsegment.get('aws', {}).get('resource_arn', '')
                        if s3_arn:
                            buckets.add(s3_arn.split(':::')[1])
    
    return list(buckets)

def find_associated_resources(lambda_name_or_arn):
    lambda_name = lambda_name_or_arn.split(':')[-1]
    lambda_details = get_lambda_details(lambda_name)
    lambda_arn = lambda_details['Configuration']['FunctionArn']
    
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=7)  # Adjust the time range as needed
    
    trace_ids = get_xray_traces(lambda_arn, start_time, end_time)
    buckets = get_s3_buckets_from_traces(trace_ids)
    
    associated_resources = {
        'Lambda': [lambda_arn],
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


# enable active tracing:
# aws lambda update-function-configuration --function-name YOUR_LAMBDA_FUNCTION_NAME --tracing-config Mode=Active
