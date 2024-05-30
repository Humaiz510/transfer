import os
import subprocess
import json

def generate_cloudformation_template(lambda_arn, region):
    # Extract the Lambda function name from the ARN
    lambda_name = lambda_arn.split(':')[-1]

    # Retrieve Lambda function configuration using AWS CLI
    print(f"Retrieving configuration for Lambda function: {lambda_name}")
    get_function_command = [
        "aws", "lambda", "get-function",
        "--function-name", lambda_name,
        "--region", region
    ]
    try:
        result = subprocess.run(get_function_command, capture_output=True, check=True, text=True)
        lambda_config = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving Lambda function configuration: {e.stderr}")
        return

    # Generate CloudFormation template using Former2
    print("Generating CloudFormation template using Former2")
    former2_command = [
        "former2",
        "--region", region,
        "--service", "lambda",
        "--resource-arn", lambda_arn,
        "--output-template"
    ]
    try:
        result = subprocess.run(former2_command, capture_output=True, check=True, text=True)
        cloudformation_template = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error generating CloudFormation template: {e.stderr}")
        return

    # Save the template to a file
    template_filename = f"{lambda_name}-cloudformation-template.yaml"
    with open(template_filename, 'w') as f:
        f.write(cloudformation_template)
    print(f"CloudFormation template saved to {template_filename}")

    # Validate the CloudFormation template using AWS CLI
    print("Validating CloudFormation template")
    validate_command = [
        "aws", "cloudformation", "validate-template",
        "--template-body", f"file://{template_filename}"
    ]
    try:
        result = subprocess.run(validate_command, capture_output=True, check=True, text=True)
        print("CloudFormation template is valid")
    except subprocess.CalledProcessError as e:
        print(f"Error validating CloudFormation template: {e.stderr}")

if __name__ == "__main__":
    # Replace with your Lambda function ARN and region
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:my-function"
    region = "us-east-1"

    generate_cloudformation_template(lambda_arn, region)
