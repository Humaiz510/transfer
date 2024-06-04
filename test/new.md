integrate this process with GitHub Actions and ensure that each new Lambda function has its own repository under the GitHub organization, you can follow these steps:

1. GitHub Actions Workflow
Set up a GitHub Actions workflow to automate the process of assuming roles and deploying CloudFormation stacks across multiple AWS accounts. This workflow can also handle the creation of new repositories for Lambda functions.

2. Creating Repositories for Lambdas
Use the GitHub API to create new repositories under your organization whenever a new stack is deployed.

Example Implementation
Step 1: Create GitHub Actions Workflow
Create a GitHub Actions workflow file in your repository (e.g., .github/workflows/deploy.yml).



name: Deploy CloudFormation Stacks

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Assume role and deploy stack
      id: deploy
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Assume role in target accounts
      run: |
        ROLE_ARN="arn:aws:iam::TARGET_ACCOUNT_ID:role/ROLE_NAME"
        CREDS=$(aws sts assume-role --role-arn $ROLE_ARN --role-session-name deploy-session)
        export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
        export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
        export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

    - name: Deploy CloudFormation stack
      run: |
        aws cloudformation deploy \
          --template-file path/to/template.yaml \
          --stack-name MyStack \
          --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

    - name: Check for new Lambdas and create repositories
      run: |
        # Check for new Lambda functions in the deployed stack
        NEW_LAMBDAS=$(aws cloudformation describe-stack-resources --stack-name MyStack | jq -r '.StackResources[] | select(.ResourceType=="AWS::Lambda::Function") | .PhysicalResourceId')
        
        for LAMBDA in $NEW_LAMBDAS; do
          REPO_NAME=$(echo $LAMBDA | tr ' ' '-')
          curl -u ${{ secrets.GITHUB_TOKEN }}:x-oauth-basic https://api.github.com/orgs/YOUR_GITHUB_ORG/repos -d "{\"name\":\"$REPO_NAME\"}"
          
          # Optional: Push initial code to the new repository
          git init
          git remote add origin https://github.com/YOUR_GITHUB_ORG/$REPO_NAME.git
          echo "# $REPO_NAME" > README.md
          git add README.md
          git commit -m "Initial commit"
          git push -u origin main
        done



Detailed Steps
1. Checkout Code
This step checks out the code from your repository.

2. Configure AWS Credentials
Use the aws-actions/configure-aws-credentials action to configure AWS credentials.

3. Assume Role in Target Accounts
Use AWS CLI to assume a role in the target account and export the temporary credentials.

4. Deploy CloudFormation Stack
Deploy the CloudFormation stack using the temporary credentials.

5. Check for New Lambdas and Create Repositories
Use the AWS CLI to check for new Lambda functions in the deployed stack and create new repositories for each Lambda function using the GitHub API.

GitHub Secrets
Ensure you have the following secrets set in your GitHub repository:

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
GITHUB_TOKEN (A personal access token with permissions to create repositories in your organization)
