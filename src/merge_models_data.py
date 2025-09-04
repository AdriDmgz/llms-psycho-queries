# Read output.xlsx and models-data.xlsx. In each sheet of output.xlsx make a merge with sheet "models" of the other file by column "model", adding columns "type", "base", "version" and "params" from models-data.xlsx after the first column of the resulting dataframe. Save the result in output.xlsx again.
import pandas as pd
import os

output_file = "output.xlsx"
models_data_file = "models-data.xlsx"
result_file = "output-with-models.xlsx"

# Read all sheets from output.xlsx
output_sheets = pd.read_excel(output_file, sheet_name=None)
# Read "models" sheet from models-data.xlsx
models_df = pd.read_excel(models_data_file, sheet_name="models")[["model", "type", "family", "version", "size-order"]]

merged_sheets = {}

for sheet_name, df in output_sheets.items():
    if "model" not in df.columns:
        merged_sheets[sheet_name] = df
        continue
    merged = pd.merge(df, models_df, left_on="model", right_on="model", how="left")
    # Move the new columns after "model"
    cols = list(merged.columns)
    model_idx = cols.index("model")
    # Remove the new columns from their current positions
    for col in ["type", "family", "version", "size-order"]:
        cols.remove(col)
    # Insert them after "model"
    for i, col in enumerate(["type", "family", "version", "size-order"]):
        cols.insert(model_idx + 1 + i, col)
    merged = merged[cols]
    merged_sheets[sheet_name] = merged

with pd.ExcelWriter(result_file, engine="openpyxl") as writer:
    for sheet_name, df in merged_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
