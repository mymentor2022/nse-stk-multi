FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/apps

# Install OS dependencies (for tzdata, if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Copy app code
COPY requirements.txt .
COPY ./src .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8050

# Run the app
CMD ["python", "app.py"]

