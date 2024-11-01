import argparse
from device42_api import Device42API
import os
import csv

def parse_arguments():
    """Parse command-line arguments for CSV import."""
    parser = argparse.ArgumentParser(description="Bulk import devices or other objects into Device42.")
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to config.yaml')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the CSV file for import')
    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Validate that the config file and CSV file exist
    if not os.path.exists(args.config):
        print(f"Error: Config file {args.config} does not exist.")
        return

    if not os.path.exists(args.file):
        print(f"Error: CSV file {args.file} does not exist.")
        return

    # Initialize the Device42API with the config file
    device42_api = Device42API(args.config)

    # Open and import from the CSV file
    try:
        with open(args.file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # Pass the entire list of rows to the API for processing
            rows = [row for row in csv_reader]
            device42_api.import_from_csv(rows)
        print(f"CSV file {args.file} processed successfully.")
    except Exception as e:
        print(f"Error processing file {args.file}: {str(e)}")


if __name__ == '__main__':
    main()
