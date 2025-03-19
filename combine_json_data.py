import os
import json

def combine_json_files(input_directory, output_filename="combined.json"):
    """
    Combines all JSON files in the specified directory into a single JSON file,
    processing them in alphabetical order.

    Parameters:
        input_directory (str): Path to the directory containing JSON files.
        output_filename (str): Name of the output JSON file (default: "combined.json").

    Returns:
        str: Path of the combined JSON file.
    """
    all_data = []

    # Ensure the directory exists
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Directory '{input_directory}' not found.")

    # Get JSON files sorted alphabetically
    json_files = sorted(f for f in os.listdir(input_directory) if f.endswith(".json"))

    # Loop through sorted JSON files
    for filename in json_files:
        file_path = os.path.join(input_directory, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):  # Ensure data is a list
                    all_data.extend(data)
                else:
                    all_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")

    # Define output file path
    output_path = os.path.join(input_directory, output_filename)

    # Save combined JSON data to a new file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Combined JSON saved as {output_path}")
    return output_path


if __name__ == "__main__":
    combine_json_files("exhibitors_data/extracted_details")