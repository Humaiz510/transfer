import csv
import boto3

def is_valid_lambda(username):
    client = boto3.client('lambda')
    try:
        response = client.get_function(FunctionName=username)
        return True
    except client.exceptions.ResourceNotFoundException:
        return False

def check_csv_for_putobject(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['API'] == 'PutObject' and is_valid_lambda(row['UserName']):
                return True
    return False

if __name__ == "__main__":
    file_path = input("Enter the path to the CSV file: ")
    if check_csv_for_putobject(file_path):
        print("A valid Lambda function has performed a PutObject operation.")
    else:
        print("No valid Lambda function has performed a PutObject operation.")