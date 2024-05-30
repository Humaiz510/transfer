import os
import subprocess
import json

def get_resource_config(resource_arn, region):
    resource_type = resource_arn.split(':')[2]  # e.g., 'lambda'
    resource_name = resource_arn.split(':')[-1]  # e.g., 'my-function'

    print(f"Retrieving configuration for {resource_type} resource: {resource_name}")

    if resource_type == 'lambda':
        command = [
            "aws", "lambda", "get-function",
            "--function-name", resource_name,
            "--region", region
        ]
    elif resource_type == 's3':
        command = [
            "aws", "s3api", "get-bucket-acl",
            "--bucket", resource_name
        ]
    elif resource_type == 'ec2':
        command = [
            "aws", "ec2", "describe-instances",
            "--instance-ids", resource_name,
            "--region", region
        ]
    elif resource_type == 'dynamodb':
        command = [
            "aws", "dynamodb", "describe-table",
            "--table-name", resource_name,
            "--region", region
        ]
    elif resource_type == 'rds':
        command = [
            "aws", "rds", "describe-db-instances",
            "--db-instance-identifier", resource_name,
            "--region", region
        ]
    elif resource_type == 'sqs':
        command = [
            "aws", "sqs", "get-queue-attributes",
            "--queue-url", f"https://sqs.{region}.amazonaws.com/{resource_name}",
            "--region", region,
            "--attribute-names", "All"
        ]
    elif resource_type == 'sns':
        command = [
            "aws", "sns", "get-topic-attributes",
            "--topic-arn", resource_arn,
            "--region", region
        ]
    elif resource_type == 'cloudwatch':
        command = [
            "aws", "cloudwatch", "describe-alarms",
            "--alarm-names", resource_name,
            "--region", region
        ]
    elif resource_type == 'apigateway':
        command = [
            "aws", "apigateway", "get-rest-api",
            "--rest-api-id", resource_name,
            "--region", region
        ]
    elif resource_type == 's3':
        command = [
            "aws", "s3api", "get-bucket-acl",
            "--bucket", resource_name
        ]
    elif resource_type == 'iam':
        command = [
            "aws", "iam", "get-role",
            "--role-name", resource_name
        ]
    elif resource_type == 'elasticbeanstalk':
        command = [
            "aws", "elasticbeanstalk", "describe-environments",
            "--environment-names", resource_name,
            "--region", region
        ]
    elif resource_type == 'kms':
        command = [
            "aws", "kms", "describe-key",
            "--key-id", resource_name,
            "--region", region
        ]
    elif resource_type == 'cloudfront':
        command = [
            "aws", "cloudfront", "get-distribution",
            "--id", resource_name
        ]
    elif resource_type == 'elasticache':
        command = [
            "aws", "elasticache", "describe-cache-clusters",
            "--cache-cluster-id", resource_name,
            "--region", region
        ]
    else:
        raise NotImplementedError(f"Resource type {resource_type} is not supported yet")

    try:
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving configuration for {resource_name}: {e.stderr}")
        return None

def generate_cloudformation_template(resource_arns, region):
    resource_configs = []

    for resource_arn in resource_arns:
        config = get_resource_config(resource_arn, region)
        if config:
            resource_configs.append(config)

    # Generate CloudFormation template using Former2
    print("Generating CloudFormation template using Former2")
    former2_command = [
        "former2",
        "--region", region,
    ]

    for resource_arn in resource_arns:
        former2_command.extend(["--resource-arn", resource_arn])

    former2_command.append("--output-template")

    try:
        result = subprocess.run(former2_command, capture_output=True, check=True, text=True)
        cloudformation_template = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error generating CloudFormation template: {e.stderr}")
        return

    # Save the template to a file
    template_filename = "combined-cloudformation-template.yaml"
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
    # Replace with your resource ARNs and region
    resource_arns = [
        "arn:aws:lambda:us-east-1:123456789012:function:my-function1",
        "arn:aws:s3:::my-bucket",
        "arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
        "arn:aws:dynamodb:us-east-1:123456789012:table/my-table",
        "arn:aws:rds:us-east-1:123456789012:db:my-db-instance",
        "arn:aws:sqs:us-east-1:123456789012:my-queue",
        "arn:aws:sns:us-east-1:123456789012:my-topic",
        "arn:aws:cloudwatch:us-east-1:123456789012:alarm:my-alarm",
        "arn:aws:apigateway:us-east-1::/restapis/my-rest-api",
        "arn:aws:iam::123456789012:role/my-role",
        "arn:aws:elasticbeanstalk:us-east-1:123456789012:environment/my-env",
        "arn:aws:kms:us-east-1:123456789012:key/my-key",
        "arn:aws:cloudfront::123456789012:distribution/my-distribution",
        "arn:aws:elasticache:us-east-1:123456789012:cluster/my-cluster",
        # Add more resource ARNs as needed
    ]
    region = "us-east-1"

    generate_cloudformation_template(resource_arns, region)
