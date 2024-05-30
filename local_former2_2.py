import subprocess
import json

def get_resource_arns_by_application(tag_key, tag_value):
    import boto3
    client = boto3.client('resourcegroupstaggingapi')
    response = client.get_resources(
        TagFilters=[
            {
                'Key': tag_key,
                'Values': [tag_value]
            }
        ]
    )
    resource_arns = [resource['ResourceARN'] for resource in response['ResourceTagMappingList']]
    return resource_arns

def generate_cloudformation_with_former2(resource_arns):
    # Convert the list of ARNs to a comma-separated string
    arns_string = ','.join(resource_arns)

    # Call Former2 CLI to generate CloudFormation template
    result = subprocess.run(['former2', 'generate', '--arns', arns_string, '--format', 'cloudformation'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error generating CloudFormation template with Former2:", result.stderr)
        return None

    # Parse the generated CloudFormation template
    template = result.stdout
    return template

def deploy_cloudformation_stack(template_body, stack_name):
    import boto3
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
    return response

# Example usage
application_tag_key = 'Application'
application_tag_value = 'MyApp'
resource_arns = get_resource_arns_by_application(application_tag_key, application_tag_value)
print("Resource ARNs:", resource_arns)

cloudformation_template = generate_cloudformation_with_former2(resource_arns)
if cloudformation_template:
    print("CloudFormation Template:", cloudformation_template)

    stack_name = 'MyAppStack'
    response = deploy_cloudformation_stack(cloudformation_template, stack_name)
    print("CloudFormation Stack Creation Response:", response)
else:
    print("Failed to generate CloudFormation template.")
