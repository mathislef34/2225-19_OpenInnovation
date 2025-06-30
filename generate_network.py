import sys
import json
from main import process_network

if __name__ == "__main__":
    input_json = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_json, "r") as f:
        data = json.load(f)

    process_network(data, output_dir)
