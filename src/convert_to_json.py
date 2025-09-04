from openai import OpenAI
import os
import json
import re

def extract_and_convert_to_json(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        text_content = file.read()

    lines = text_content.splitlines()
    result = {}

    index_expected = 1
    for line in lines:
        # Find two separated numbers in the line
        match = re.search(r'\b(\d+)\D+(\d+)\b', line)
        if match:
            idx = int(match.group(1))
            val = int(match.group(2))
            # Check index and value constraints
            if idx != index_expected:
                raise ValueError(f"Error in {file_path}: Expected index {index_expected}, found {idx} in line: {line}")
            if not (1 <= val <= 7):
                raise ValueError(f"Error in {file_path}: Value {val} out of range (1-7) in line: {line}")
            result[f"Item{idx}"] = val
            index_expected += 1

    if len(result) < 5:
        raise ValueError(f"Error in {file_path}: There must be at least 5 indexes in the file.")
    return json.dumps(result, ensure_ascii=False, indent=4)

def process_responses_folder(folder_path):
    # Iterate through all files in the folder
    for root, _, files in os.walk(folder_path):
    
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Skip non-text files
            if not file_name.endswith('.txt'):
                continue       
            
            try:
                # print(f"Processing {file_name}...")
                # If the file already has a corresponding JSON file, skip it
                json_file_path = os.path.splitext(file_path)[0] + ".json"
                if os.path.exists(json_file_path):
                    # print(f"JSON file already exists for {file_name}. Skipping...")
                    continue
                
                # Extract and convert the file content to JSON
                json_content = extract_and_convert_to_json(file_path)

                # Save the JSON content to a new file with .json extension
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(json_content)

                # print(f"Processed and saved JSON for: {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

# Call the function with the path to the responses folder
process_responses_folder("responses")
