import os
import json
import pandas as pd

def parse_responses_and_create_excel(responses_folder, output_excel):
    # Dictionary to store data for each scale
    scales_data = {}

    # Walk through the folder hierarchy
    for scale in os.listdir(responses_folder):
        scale_path = os.path.join(responses_folder, scale)
        if os.path.isdir(scale_path):
            if scale not in scales_data:
                scales_data[scale] = []

            for model in os.listdir(scale_path):
                model_path = os.path.join(scale_path, model)
                if os.path.isdir(model_path):
                    for repetition_file in os.listdir(model_path):
                        if repetition_file.endswith('.json'):
                            repetition_path = os.path.join(model_path, repetition_file)
                            with open(repetition_path, 'r', encoding='utf-8') as f:
                                data = {k.lower(): v for k, v in json.load(f).items()}
                                repetition_index = int(os.path.splitext(repetition_file)[0].split('_')[-1])
                                row = {'model': model, 'test': repetition_index}
                                row.update(data)
                                scales_data[scale].append(row)

    # Create an Excel file with one sheet per scale
    with pd.ExcelWriter(output_excel) as writer:
        for scale, data in scales_data.items():
            df = pd.DataFrame(data)
            df.sort_values(by=['model', 'test'], inplace=True)

            for col in df.columns:
                if col.startswith("item"):
                    invalid_mask = ~df[col].apply(lambda x: isinstance(x, (int, float)) and 1 <= x <= 7)
                    for idx in df[invalid_mask].index:
                        model = df.at[idx, 'model']
                        test = df.at[idx, 'test']
                        print(f"Invalid value in sheet '{scale}', model '{model}', test {test}, column '{col}'")

            df.to_excel(writer, index=False, sheet_name=scale)

# Define the folder containing the responses and the output Excel file
responses_folder = 'responses'
output_excel = 'output.xlsx'

# Run the function
parse_responses_and_create_excel(responses_folder, output_excel)

