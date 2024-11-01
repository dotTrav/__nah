# Documentation for Device42 Bulk Import Application
This document provides a guide to running and configuring the Device42 bulk import application, which includes both a web application and a CLI tool. It also covers configuration details and other important aspects of using the application effectively.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Running as a Web Application](#2-running-as-a-web-application)
3. [Running as a CLI Tool](#3-running-as-a-cli-tool)
4. [Configuration (config.yaml)](#4-configuration-configyaml)
5. [Using the API](#5-using-the-api)
6. [Handling Custom Fields](#6-handling-custom-fields)
7. [Known Limitations and Notes](#7-known-limitations-and-notes)

---

# 1. Overview
This Device42 bulk import application allows users to upload CSV files to bulk import devices and other objects (e.g., buildings, applications, customers) into Device42. The application can be run in two modes:

- **Web Application**: Users can upload CSV files through a web interface, and the system processes the imports, displaying results in the browser.
- **CLI Tool**: Users can run the import directly from the command line by specifying the configuration file and CSV file as arguments.
The application also supports custom fields based on object types (e.g., Device, Customer, Building) and dynamically updates them using the appropriate Device42 APIs.

---

## 2. Running as a Web Application
### Prerequisites
- Python 3.8+
- Flask and other required dependencies (see requirements.txt for details)
- Docker (optional for running in a container)

### Steps to Run the Web Application
**Prepare the Environment**: 
Ensure you have the necessary dependencies installed. You can install them using:

```bash
pip install -r requirements.txt
```
**Prepare the Configuration**: Ensure that the config.yaml is correctly set up (see Configuration).

**Start the Flask Web Server**: You can run the web server using the following command:

```bash
python app.py
```
The web application will be available at http://localhost:5001.

**Uploading a CSV File**:

- Navigate to the homepage of the web app (http://localhost:5001).
- Upload a valid CSV file that matches the structure expected based on the configuration.
- After submitting the file, the system will display the results of the import, including successful and failed imports with detailed error messages.

### Running the Web App with Docker

If you prefer to run the web application in a Docker container:

1. **Build the Docker Image**:

```bash
docker build -t device42-bulk-import:1.0.0 .
```

2. **Run the Docker Container**:

To run the container, use the following command:

```bash
docker run -p 5001:5001 device42-bulk-import:1.0.0
```

This will expose the web app on port `5001` and reflect any changes made locally in the container.

## 3. Running as a CLI Tool
### Prerequisites
- Python 3.8+
- Ensure the required dependencies are installed (`pip install -r requirements.txt`).

### CLI Usage
To run the import via the command line, use the following syntax:

```bash
python cli_import.py --config /path/to/config.yaml --file /path/to/import.csv
```


### CLI Arguments
- `--config (-c)`: Path to the `config.yaml` file, which contains the necessary mappings and configuration.
- `--file (-f)`: Path to the CSV file to be imported.
### Example Command
```bash
python cli_import.py --config ./config.yaml --file ./devices.csv
```
### Results
The CLI tool will process the CSV file row by row and output the result to the console. This includes:

- The object type and name of each imported object.
- Any errors that occurred during the import.
## 4. Configuration (`config.yaml`)
The `config.yaml` file defines how the system maps CSV columns to Device42 API fields, as well as any custom fields specific to different object types.

### Example Configuration
```yaml
csv_mappings:
  object_type: "ObjectType"
  name: "Name"
  device_type: "DeviceType"
  parent_customer: "ParentCustomer"
  warranty_expiration: "WarrantyExpiration"
  support_contract: "SupportContract"

custom_fields:
  device:
    warranty_expiration: "WarrantyExpiration"
    support_contract: "SupportContract"
  customer:
    contract_start_date: "ContractStartDate"
    customer_priority: "CustomerPriority"
  building:
    occupancy_limit: "OccupancyLimit"

required_fields:
  - name
  - device_type
```
### Key Sections:
- `csv_mappings`: All fields in the CSV, including custom fields, must be declared here to be picked up by the application. This section maps columns in the CSV to Device42 API fields.
- `custom_fields`: Defines custom fields for different object types. These must also be declared in csv_mappings to be processed.
- `required_fields`: Lists the fields required for a successful import.

## 5. Using the API
### API Endpoints Used
The application interacts with several Device42 API endpoints to process the imports:

1. /appcomps/: For importing applications.
2. /buildings/: For importing buildings.
3. /customers/: For importing customers.
4. /devices/: For importing devices.
5. /custom_fields/appcomp/: For creating or updating new custom fields for applications.
6. /custom_fields/building/: For creating or updating new custom fields for buildings.
7. /custom_fields/customer/: For creating or updating new custom fields for customers.
8. /custom_fields/device/: For creating or updating new custom fields for devices.
### Authentication
The application uses OAuth tokens for authentication, which are obtained via the `/tauth/1.0/token/` endpoint using basic authentication with `client_id` and `client_secret`.

## 6. Handling Custom Fields
The system supports custom fields for different object types (e.g., devices, customers, buildings).

### Adding New Custom Fields
To add a new custom field:

1. Define the new field in the `csv_mappings` section under the appropriate object type.
2. Ensure that the CSV file contains the corresponding column with data for that custom field.

For example:

```yaml
custom_fields:
  device:
    new_custom_field: "NewCustomField"
```

This will map the CSV column `new_custom_field` to the Device42 API field `NewCustomField`.

## 7. Known Limitations and Notes
- **CSV Format**: Ensure that the CSV file format is consistent with the mappings defined in `config.yaml`. The import will fail if required fields are missing or improperly formatted.
- **SSL Verification**: SSL verification is disabled by default for development. In production, it's strongly recommended to enable SSL verification to ensure secure communication with the Device42 API.
- **Web Server and CLI Consistency**: The same configuration file is used for both the CLI and the web application, ensuring consistent behavior between the two interfaces.

## Conclusion
This application provides flexible bulk import functionality for Device42, supporting both a web interface and a CLI tool. With dynamic support for custom fields and object types, it's easy to extend and configure for different use cases.

