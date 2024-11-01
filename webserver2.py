from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import csv
from device42_api import Device42API

# Initialize the Flask app
app = Flask(__name__)

# Set a secret key for session handling (optional but recommended)
app.secret_key = 'your_secret_key'

# Set the folder to store uploaded CSV files
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow only CSV files for uploads
ALLOWED_EXTENSIONS = {'csv'}


# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the file is present in the request
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # Check if the file is allowed (CSV only)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Initialize the Device42 API and process the CSV file
        try:
            # Update this line with the path to your config file
            device42_api = Device42API('/app/config.yaml')

            # Variables to track results
            imported_records = []
            error_records = []

            # Open the saved CSV file and process it
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    name = row.get('Name', 'Unknown')
                    object_type = row.get('ObjectType', 'Unknown')
                    try:
                        # Call the import function for each row
                        device42_api.import_from_csv([row])  # Process each row individually
                        imported_records.append({
                            "name": name,
                            "object_type": object_type
                        })
                    except Exception as e:
                        error_records.append({
                            "name": name,
                            "object_type": object_type,
                            "error": str(e)
                        })

            # Pass the results to the template to display
            return render_template('upload_result.html',
                                   imported=imported_records,
                                   errors=error_records)

        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(request.url)

    else:
        flash('Invalid file format. Only CSV files are allowed.')
        return redirect(request.url)


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
