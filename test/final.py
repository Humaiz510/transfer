import boto3
import json

# Initialize boto3 clients for all accounts
session_main = boto3.Session(profile_name='main_account')
session_account1 = boto3.Session(profile_name='account_1')
session_account2 = boto3.Session(profile_name='account_2')

app_registry_client_main = session_main.client('servicecatalog-appregistry')
app_registry_client_account1 = session_account1.client('servicecatalog-appregistry')
app_registry_client_account2 = session_account2.client('servicecatalog-appregistry')

cloudformation_client_main = session_main.client('cloudformation')
cloudformation_client_account1 = session_account1.client('cloudformation')
cloudformation_client_account2 = session_account2.client('cloudformation')

resource_groups_client_main = session_main.client('resource-groups')

app_name = "my-application"

def check_application_exists(client, app_name):
    try:
        response = client.list_applications()
        for app in response['applications']:
            if app['name'] == app_name:
                return app['id']
        return None
    except Exception as e:
        print(f"Error checking application existence: {e}")
        return None

def get_application_resources(client, app_id):
    try:
        resources = client.list_associated_resources(application=app_id)
        return resources['resources']
    except Exception as e:
        print(f"Error getting application resources: {e}")
        return []

def create_cloudformation_template(resources):
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {}
    }
    for resource in resources:
        resource_arn = resource['arn']
        resource_type = resource['type']
        resource_name = resource_arn.split('/')[-1]
        
        # Simplified example, in practice you'll need to fetch resource details
        template['Resources'][resource_name] = {
            "Type": resource_type,
            "Properties": {}
        }
    return json.dumps(template, indent=2)

def create_application(client, app_name):
    try:
        response = client.create_application(
            name=app_name,
            description='Created by automation script'
        )
        return response['application']['id']
    except Exception as e:
        print(f"Error creating application: {e}")
        return None

def deploy_stack(client, stack_name, template_body, tags):
    try:
        response = client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Tags=tags
        )
        return response['StackId']
    except Exception as e:
        print(f"Error creating stack: {e}")
        return None

def update_stack(client, stack_name, template_body, tags):
    try:
        response = client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Tags=tags,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        return response['StackId']
    except Exception as e:
        print(f"Error updating stack: {e}")
        return None

def main():
    # Check if application exists in the main account
    app_id_main = check_application_exists(app_registry_client_main, app_name)
    if not app_id_main:
        print(f"Application {app_name} does not exist in the main account.")
        return
    
    # Get resources associated with the application
    resources_main = get_application_resources(app_registry_client_main, app_id_main)
    
    # Check and create/update applications in other accounts if they do not exist
    for account_client, cloudformation_client, account_name in [
        (app_registry_client_account1, cloudformation_client_account1, "account_1"),
        (app_registry_client_account2, cloudformation_client_account2, "account_2")
    ]:
        app_id = check_application_exists(account_client, app_name)
        if not app_id:
            print(f"Creating application {app_name} in {account_name}.")
            app_id = create_application(account_client, app_name)
            if app_id:
                tags = [{'Key': 'aws:servicecatalog:appregistry:application', 'Value': app_id}]
                stack_name = f"{app_name}-stack"
                template_body = create_cloudformation_template(resources_main)
                stack_id = deploy_stack(cloudformation_client, stack_name, template_body, tags)
                if stack_id:
                    print(f"Stack {stack_name} deployed successfully in {account_name}.")
                else:
                    print(f"Failed to deploy stack {stack_name} in {account_name}.")
            else:
                print(f"Failed to create application {app_name} in {account_name}.")
        else:
            print(f"Application {app_name} already exists in {account_name}.")
            resources_existing = get_application_resources(account_client, app_id)
            existing_arns = {resource['arn'] for resource in resources_existing}
            new_resources = [res for res in resources_main if res['arn'] not in existing_arns]
            if new_resources:
                template_body = create_cloudformation_template(new_resources)
                tags = [{'Key': 'aws:servicecatalog:appregistry:application', 'Value': app_id}]
                stack_name = f"{app_name}-stack"
                stack_id = update_stack(cloudformation_client, stack_name, template_body, tags)
                if stack_id:
                    print(f"Stack {stack_name} updated successfully in {account_name}.")
                else:
                    print(f"Failed to update stack {stack_name} in {account_name}.")
            else:
                print(f"No new resources to add in {account_name}.")

if __name__ == "__main__":
    main()