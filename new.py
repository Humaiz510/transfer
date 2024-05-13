import pandas as pd

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

# If you want to write the DataFrame to a CSV file
df.to_csv('stack_comparison.csv', index=False)

# If you want to just use the DataFrame
print(df)