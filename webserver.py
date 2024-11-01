from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import csv
from device42_api import Device42API

# Initialize the Flask app
app = Flask(__name__)

# Set a secret key for session handling
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

# Login route for API key and secret
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Collect the API key and secret from the form
        client_key = request.form.get('client_key')
        secret_key = request.form.get('secret_key')

        # Validate (mock check for this example)
        if client_key and secret_key:
            session['client_key'] = client_key
            session['secret_key'] = secret_key
            flash("Login successful")
            return redirect(url_for('upload_form'))
        
        # If authentication fails, notify the user
        flash('Invalid API key or secret')
        return redirect(url_for('login'))

    return render_template('login.html')

# Logout route to clear session
@app.route('/logout')
def logout():
    session.pop('client_key', None)
    session.pop('secret_key', None)
    flash("You have been logged out")
    return redirect(url_for('login'))

# Protected upload form route
@app.route('/')
def upload_form():
    # Redirect to login if not authenticated
    if 'client_key' not in session or 'secret_key' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html')


# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check authentication
    if 'client_key' not in session or 'secret_key' not in session:
        return redirect(url_for('login'))

    # Use session-stored credentials
    client_key = session['client_key']
    secret_key = session['secret_key']

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
                        # Call the import function for each row, passing user credentials
                        device42_api.import_from_csv([row], client_key, secret_key)
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

            # Display the results of the import
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
