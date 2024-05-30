import requests
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
    # Convert the list of ARNs to the expected input format for Former2
    data = {
        'arns': resource_arns
    }

    # Make a request to the Former2 local server to generate the template
    url = 'http://localhost:8000/api/former2'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code != 200:
        print("Error generating CloudFormation template with Former2:", response.text)
        return None

    # Parse the generated CloudFormation template
    template = response.json()
    return json.dumps(template, indent=2)

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
