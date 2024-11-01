# Base image
FROM python:3.8


# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Make ports accessible for the web server
EXPOSE 5001

# Command to run the Flask web server
#CMD ["python", "web/webserver.py"]
