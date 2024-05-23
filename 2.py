import boto3
import subprocess

def lambda_handler(event, context):
    lambda_name = event['detail']['requestParameters']['functionName']
    
    test_class = TestLambdaRegressionSuite()
    test_class.set_lambda_name(lambda_name)
    
    # Run pytest programmatically
    result = subprocess.run(['pytest', '--tb=short', '-q'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Tests failed:\n{result.stdout}\n{result.stderr}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Tests executed successfully')
    }
