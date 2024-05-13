import pandas as pd
import boto3

# Assuming best_matches is a list of tuples like [(stack_name_env1, [(matching_stack_name_env2, score)])]
best_matches = [
    ('Stack1_Env1', [('Stack1_Env2', 0.9), ('Stack2_Env2', 0.8)]),
    ('Stack2_Env1', [('Stack3_Env2', 0.95)])
]

# Create a list to store the rows
rows = []

# Populate the list with the data
for match in best_matches:
    for m in match[1]:
        rows.append([match[0], m[0], m[1]])

# Create a DataFrame from the list
df = pd.DataFrame(rows, columns=['Stack Name Env1', 'Matching Stack Name Env2', 'Score'])

# AWS S3 bucket and file details
bucket_name = 'your-bucket-name'
file_key = 'path/to/stack_comparison.csv'

# Save DataFrame to S3
s3_path = f's3://{bucket_name}/{file_key}'

# Save the DataFrame to a CSV file in the S3 bucket
df.to_csv(s3_path, index=False, storage_options={
    'key': 'YOUR_AWS_ACCESS_KEY_ID',
    'secret': 'YOUR_AWS_SECRET_ACCESS_KEY'
})

print("DataFrame written to S3 successfully.")