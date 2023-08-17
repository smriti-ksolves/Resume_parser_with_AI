# Use a base Python image
FROM python:3.9
RUN apt-get update

# Set the working directory
WORKDIR /usr/src/app
RUN touch ai.log
# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the port on which your Flask application runs
EXPOSE 6754

# Run the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:6754", "--timeout", "600" , "run:flask_app"]