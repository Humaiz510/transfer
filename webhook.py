import os
import time
import requests
import sys

# Configuration - Ensure these environment variables are set in Gearset
WEBHOOK1_URL = os.getenv('WEBHOOK1_URL')  # URL to trigger the test suite
WEBHOOK2_URL = os.getenv('WEBHOOK2_URL')  # URL to retrieve test results
API_KEY = os.getenv('API_KEY')            # API key for authentication, if needed

# Headers for authentication if required
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def trigger_test_suite():
    try:
        response = requests.post(WEBHOOK1_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        execution_id = data.get('executionId')  # Adjust based on actual response
        if not execution_id:
            print("Execution ID not found in the response.")
            sys.exit(1)
        print(f"Triggered test suite. Execution ID: {execution_id}")
        return execution_id
    except requests.exceptions.RequestException as e:
        print(f"Error triggering test suite: {e}")
        sys.exit(1)

def check_test_completion(execution_id, timeout=600, interval=30):
    """
    Polls the test execution status until completion or timeout.
    """
    elapsed = 0
    while elapsed < timeout:
        try:
            response = requests.get(f"{WEBHOOK2_URL}/{execution_id}", headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            status = data.get('status')  # Adjust based on actual response
            if status == 'completed':
                print("Test execution completed.")
                return data
            elif status == 'failed':
                print("Test execution failed.")
                sys.exit(1)
            else:
                print(f"Current status: {status}. Waiting...")
        except requests.exceptions.RequestException as e:
            print(f"Error checking test status: {e}")
            sys.exit(1)
        
        time.sleep(interval)
        elapsed += interval
    
    print("Timeout waiting for test completion.")
    sys.exit(1)

def evaluate_test_results(results):
    """
    Evaluates test results and exits with non-zero code if any test fails.
    """
    tests = results.get('tests', [])  # Adjust based on actual response
    failed_tests = [test for test in tests if test.get('status') == 'failed']
    
    if failed_tests:
        print(f"Number of failed tests: {len(failed_tests)}")
        for test in failed_tests:
            print(f"Failed Test: {test.get('name')}")
        sys.exit(1)
    else:
        print("All tests passed successfully.")

def main():
    execution_id = trigger_test_suite()
    results = check_test_completion(execution_id)
    evaluate_test_results(results)
    print("Test suite completed successfully.")

if __name__ == "__main__":
    main()