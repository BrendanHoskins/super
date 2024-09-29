import json

def format_shortname(shortname):
    return f":{shortname}:"

def format_unified(unified):
    return f"&#x{unified.replace('-', '')};"

def extract_emoji_data(input_file, output_file):
    # Read the JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Extract and format the required fields
    extracted_data = []
    for item in data:
        extracted_item = {
            "unified": item["unified"],
            "short_names": [item["short_names"]],
            "category": item["category"],
            "name": item["name"],
            "subcategory": item["subcategory"],
            "sort_order": item["sort_order"]
        }
        extracted_data.append(extracted_item)

    # Write the extracted data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    print(f"Extracted and formatted data has been written to {output_file}")

# Usage
input_file = "/Users/brendanhoskins/Documents/VS Code/codesmith/soloproject/server/services/slack_default_emojis.json"
output_file = "/Users/brendanhoskins/Documents/VS Code/codesmith/soloproject/server/services/output1.json"
extract_emoji_data(input_file, output_file)
