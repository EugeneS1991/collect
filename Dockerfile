# Python image to use.
FROM python:3.10

# Set the working directory to /app
WORKDIR /collect

# copy the requirements file used for dependencies
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . /collect

# Run app.py when the container launches
#ENTRYPOINT ["python", "app.py","test_1.py","tasks_handler.py"]
ENTRYPOINT ["python"]

CMD ["app_1.0.py"]