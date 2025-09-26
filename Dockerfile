# Use Ubuntu base since language setup script is designed for Ubuntu
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and essential tools first (better caching)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python-is-python3 \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Copy only the language setup script first (for better caching)
COPY mxeval/language_setup/docker.sh /tmp/language_setup.sh

# Run language setup (this takes the longest, so do it early for caching)
RUN chmod +x /tmp/language_setup.sh && \
    bash /tmp/language_setup.sh && \
    rm /tmp/language_setup.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy mxeval package files (separate from main code for better caching)
COPY mxeval/ ./mxeval/

# Install mxeval package
RUN cd mxeval && python -m pip install -e .

# Copy the rest of the application code last (changes most frequently)
COPY . .

# Set up environment variables
ENV PYTHONPATH=/workspace
ENV PATH="${PATH}:/usr/local/swift-5.7-RELEASE-ubuntu20.04/usr/bin:/usr/local/go/bin"

# Create non-root user for security
RUN useradd -m -s /bin/bash evaluser && \
    chown -R evaluser:evaluser /workspace
USER evaluser

# Default command
CMD ["python", "-m", "mxeval.evaluate_functional_correctness", "--help"]
