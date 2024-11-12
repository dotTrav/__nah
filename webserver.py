import json
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import csv
import urllib.parse
from device42_api import Device42API

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set the folder to store uploaded CSV files
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        device42_api = Device42API('/app/config.yaml')
        comparison_data = []

        # Process CSV and query Device42 for each row
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                name = row.get('Name')
                obj_type = row.get('ObjectType')
                existing_data = device42_api.check_existing(name, obj_type)
                # Map existing_data to CSV field names based on csv_mappings
                mapped_existing_data = {}
                if existing_data:
                    print(existing_data)
                    for api_field, csv_field in device42_api.csv_mappings.items():
                        mapped_existing_data[csv_field] = existing_data['data'].get(api_field, 'N/A')

                new = json.dumps(row)
                new2 = urllib.parse.quote(new)
                comparison_data.append({
                    "csv_data": row,
                    "post_data": new2,
                    "existing_data": mapped_existing_data,
                    "name": name
                })

        return render_template('compare.html', comparison_data=comparison_data)

    else:
        flash('Invalid file format. Only CSV files are allowed.')
        return redirect(request.url)


@app.route('/confirm_upload', methods=['POST'])
def confirm_upload():
    device42_api = Device42API('/app/config.yaml')

    # Iterate over selected checkboxes by row index
    for row_index in request.form.getlist('selected_rows'):
        # Access the hidden field corresponding to the row index
        encoded_row_data = request.form.get(f'csv_data_{row_index}')
        row_data = urllib.parse.unquote(encoded_row_data)
        print(row_data)
        try:
            print("try")
            # Decode JSON data for each selected row
            csv_data = json.loads(row_data)
            print("json")
            device42_api.import_from_csv([csv_data])
            print("import")
        except json.JSONDecodeError as e:
            print("except")
            flash(f"Error decoding row {row_index}: {e}")
            return redirect(url_for('upload_form'))

    flash('Selected records uploaded successfully')
    return redirect(url_for('upload_form'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
