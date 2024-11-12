import csv
import requests
import yaml
from requests.auth import HTTPBasicAuth
import urllib3
import pprint
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Device42API:
    def __init__(self, config_file):
        # Load configuration from YAML file
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

        # Extract configuration values
        self.host = self.config['host']  # The host, e.g., https://your-device42-instance
        self.api_uri_prefix = self.config['api_uri_prefix']  # The first part of the URI, e.g., /api/1.0
        self.client_id = self.config['client_id']
        self.client_secret = self.config['client_secret']
        self.ssl_verification = self.config.get('ssl_verification', True)
        self.csv_mappings = self.config['csv_mappings']
        self.custom_fields = self.config.get('custom_fields', {})  # Load custom fields for all object types
        self.required_fields = self.config.get('required_fields', [])  # Load required fields, allow empty list

        # Get the token on initialization
        self.token = self.get_token()

    def get_token(self):
        """Retrieve the access token from the Device42 authentication endpoint using Basic Authentication."""
        token_url = f"{self.host}/tauth/1.0/token/"
        data = {
            "grant_type": "client_credentials"
        }

        # Use HTTP Basic Auth to send client_id and client_secret in the Authorization header
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        # Send the data as form-encoded
        response = requests.post(token_url, data=data, auth=auth, verify=self.ssl_verification)
        if response.status_code == 200:
            token = response.json().get("token")
            return token
        else:
            raise Exception(f"Error fetching token: {response.status_code} - {response.text}")

    def get_headers(self):
        """Construct the headers required for authenticated API calls."""
        return {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }

    def device_id_by_name(self, name):
        """Get id of a device with the given name exists."""
        url = f"{self.host}{self.api_uri_prefix}/devices/"
        params = {"name": name}
        response = requests.get(url, headers=self.get_headers(), params=params, verify=self.ssl_verification)
        if response.status_code == 200:
            data = response.json()
            res = {}
            for obj in data['Devices']:
                if obj.get('name') == name:
                    if 'device_id' in obj:
                        return obj['device_id']
                    else:
                        return None
        return None
        # return self._process_response(response, "device")

    def building_id_by_name(self, name):
        """Get id of a building with the given name exists."""
        url = f"{self.host}{self.api_uri_prefix}/buildings/"
        params = {"name": name}
        response = requests.get(url, headers=self.get_headers(), params=params, verify=self.ssl_verification)
        if response.status_code == 200:
            data = response.json()
            for obj in data['buildings']:
                if obj.get('name') == name:
                    if 'building_id' in obj:
                        return obj['building_id']
                    else:
                        return None
        return None

    def application_id_by_name(self, name):
        """Get id of an application with the given name exists."""
        url = f"{self.host}{self.api_uri_prefix}/appcomps/"
        params = {"name": name}
        response = requests.get(url, headers=self.get_headers(), params=params, verify=self.ssl_verification)
        if response.status_code == 200:
            data = response.json()
            for obj in data['appcomps']:
                if obj.get('name') == name:
                    if 'appcomp_id' in obj:
                        return obj['appcomp_id']
                    else:
                        return None
        return None

    #Customers is different than the other check by name functions it returns a list of customers without filtering
    def customer_id_by_name(self, name):
        """Get id of a customer with the given name exists."""
        url = f"{self.host}{self.api_uri_prefix}/customers/"
        params = {"name": name}
        response = requests.get(url, headers=self.get_headers(), params=params, verify=self.ssl_verification)
        if response.status_code == 200:
            data = response.json()
            custs = data['Customers']
            for obj in custs:
                if obj.get('name') == name:
                    if 'id' in obj:
                        return obj['id']
                    else:
                        return None
        return None

    def get_device_by_id(self, device_id):
        """Check if a device with the given ID exists."""
        url = f"{self.host}{self.api_uri_prefix}/devices/{device_id}/"
        response = requests.get(url, headers=self.get_headers(), verify=self.ssl_verification)
        return self._process_response(response, "device")

    def get_building_by_id(self, building_id):
        """Check if a building with the given ID exists."""
        url = f"{self.host}{self.api_uri_prefix}/buildings/{building_id}/"
        response = requests.get(url, headers=self.get_headers(), verify=self.ssl_verification)
        return self._process_response(response, "building")

    def get_application_by_id(self, application_id):
        """Check if an application with the given ID exists."""
        url = f"{self.host}{self.api_uri_prefix}/appcomps/{application_id}/"
        response = requests.get(url, headers=self.get_headers(), verify=self.ssl_verification)
        return self._process_response(response, "application")

    def get_customer_by_id(self, customer_id):
        """Check if a customer with the given ID exists."""
        url = f"{self.host}{self.api_uri_prefix}/customers/{customer_id}/"
        response = requests.get(url, headers=self.get_headers(), verify=self.ssl_verification)
        return self._process_response(response, "customer")

    def _process_response(self, response, obj_type):
        """Process the API response and return data if it exists."""
        if response.status_code == 200:
            data = response.json()
            if data:  # Adjust based on API response structure
                val = {"type": obj_type, "data": data}
                return val
        return None

    def check_existing(self, name, object_type):
        """Check if an object with the given name exists in Device42 for multiple object types."""
        if object_type == "Device":
            id = self.device_id_by_name(name)
            if id is not None:
                return self.get_device_by_id(id)
            else:
                return {"type": object_type, "data": {}}
        elif object_type == "Building":
            id = self.building_id_by_name(name)
            if id is not None:
                return self.get_building_by_id(id)
            else:
                return {"type": object_type, "data": {}}
        elif object_type == "Application":
            id = self.application_id_by_name(name)
            if id is not None:
                return self.get_application_by_id(id)
            else:
                return {"type": object_type, "data": {}}
        elif object_type == "Customer":
            id = self.customer_id_by_name(name)
            if id is not None:
                return self.get_customer_by_id(id)
            else:
                return {"type": object_type, "data": {}}
        else:
            return None


    def get_endpoint_for_object_type(self, object_type):
        """Return the correct API endpoint based on the object type."""
        endpoints = {
            "Device": f"{self.host}{self.api_uri_prefix}/devices/",
            "Building": f"{self.host}{self.api_uri_prefix}/buildings/",
            "Application": f"{self.host}{self.api_uri_prefix}/appcomps/",
            "Customer": f"{self.host}{self.api_uri_prefix}/customers/",  # Customer endpoint
        }
        return endpoints.get(object_type, None)

    def get_custom_field_endpoint(self, object_type, object_id):
        """Return the correct custom field API endpoint based on the object type."""
        custom_field_endpoints = {
            "Device": f"{self.host}{self.api_uri_prefix}/custom_fields/device/",
            "Building": f"{self.host}{self.api_uri_prefix}/custom_fields/building/",
            "Application": f"{self.host}{self.api_uri_prefix}/custom_fields/appcomp/",
            "Customer": f"{self.host}{self.api_uri_prefix}/custom_fields/customer/",
        }
        return custom_field_endpoints.get(object_type, None)

    def set_custom_field_data(self, object_type, object_id, key, value):
        """Return the correct data to submit to the custom field API endpoint based on the object type."""

        custom_field_data = {
            "Device": {
                "device_id": object_id,
                "key": key,
                "value": value
            },
            "Building": {
                "id": object_id,
                "key": key,
                "value": value
            },
            "Application": {
                "id": object_id,
                "key": key,
                "value": value
            },
            "Customer": {
                "id": object_id,
                "key": key,
                "value": value
            }
        }
        return custom_field_data.get(object_type, {})

    def bulk_import(self, devices, endpoint, object_type):
        """Send a list of devices (or other objects) to the Device42 API for bulk import as form data."""
        headers = {
            'Authorization': f'Bearer {self.token}'  # Add token to the header
        }

        # Step 1: Send the standard fields to the device endpoint
        standard_fields = {field: value for field, value in devices[0].items() if field in self.csv_mappings.keys()}
        response = requests.post(endpoint, data=standard_fields, headers=headers, verify=self.ssl_verification)
        if response.status_code == 200:
            # Object (device, customer, etc.) created or updated successfully
            print(f"{object_type} import successful: {devices[0]['name']}")

            # Step 2: Update custom fields for the object
            object_id = response.json().get("msg")[1]  # Get the object ID from the response
            if object_id:
                custom_field_endpoint = self.get_custom_field_endpoint(object_type, object_id)

                # Prepare custom fields based on object type
                custom_fields_for_type = self.custom_fields.get(object_type.lower(), {})
                # print(custom_fields_for_type)
                for csv_field, device42_field in custom_fields_for_type.items():
                    # print(devices[0], csv_field)
                    if devices[0].get(csv_field):
                        custom_field_data = self.set_custom_field_data(object_type, object_id, csv_field, devices[0][csv_field])

                        # Send the custom field update
                        # print(custom_field_endpoint, custom_field_data)
                        custom_field_response = requests.put(custom_field_endpoint, data=custom_field_data, headers=headers, verify=self.ssl_verification)
                        # print(custom_field_response.json())
                        # pprint(json.loads(custom_field_response.text))
                        if custom_field_response.status_code == 200:
                            print(f"Custom field '{device42_field}' update successful for {object_type} {object_id}")
                        else:
                            print(f"Error updating custom field '{csv_field}' for {object_type} {object_id}: {custom_field_response.status_code} - {custom_field_response.text}")
        else:
            # Print error if the object creation/update fails
            print(f"Error importing {object_type}: {response.status_code} - {response.text}")

        return response

    def pre_check_csv(self, csv_file):
        """Pre-check the CSV data for required fields and return issues if found."""
        csv_reader = csv.DictReader(csv_file)
        issues = []
        for row_num, row in enumerate(csv_reader, start=1):
            # If there are required fields, check them; otherwise skip this step
            if self.required_fields:
                for field in self.required_fields:
                    csv_field = self.csv_mappings.get(field)
                    if not row.get(csv_field):
                        issues.append(f"Row {row_num}: Missing or empty required field '{field}'.")

            # Check if object_type exists in each row
            object_type = row.get(self.csv_mappings['object_type'])
            if not object_type:
                issues.append(f"Row {row_num}: Missing or invalid 'ObjectType' field.")

        return issues
    def import_from_csv(self, csv_data):
        """Process a single row or a list of rows for import."""
        if isinstance(csv_data, list):
            # Iterate over the list of rows and import each one
            for row in csv_data:
                self.process_row(row)
        else:
            # Single row processing
            self.process_row(csv_data)

    def process_row(self, row):
        """Process a single row of CSV data and send it to the appropriate API endpoint."""
        object_type = row.pop(self.csv_mappings['object_type'], None)
        endpoint = self.get_endpoint_for_object_type(object_type)
        
        if endpoint is None:
            print(f"Skipping unsupported object type: {object_type}")
            return
        
        device = {}
        # Dynamically map CSV columns to API fields based on config.yaml, excluding object_type
        for api_field, csv_column in self.csv_mappings.items():
            if csv_column in row and api_field != 'object_type':  # Ensure object_type is not included
                device[api_field] = row[csv_column]
        
        # Call the bulk import for the specific object type and endpoint
        response = self.bulk_import([device], endpoint, object_type)

        # Check response status
        if response.status_code == 200:
            print(f"Successfully imported {object_type}: {row.get(self.csv_mappings['name'])}")
        else:
            print(f"Error importing {object_type}: {response.status_code} - {response.text}")
