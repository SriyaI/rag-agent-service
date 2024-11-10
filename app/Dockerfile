# Use the CUDA base image with Ubuntu 20.04 (GPU-enabled)
FROM ghcr.io/ggerganov/llama.cpp@sha256:bd390a1cc93f71c675d4eae420cccc9e432954a59458dbde7fff4f74c0898975

# Install necessary dependencies
WORKDIR /app

# Copy all necessary files into the container
COPY . /app

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r /app/requirements.txt


# Set environment variables for CUDA
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Expose any ports if necessary
EXPOSE 8000

# Set entrypoint to llama-cli (or your app)
#ENTRYPOINT ["/llama-cli"]

# Default command (for FastAPI or other purposes)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
