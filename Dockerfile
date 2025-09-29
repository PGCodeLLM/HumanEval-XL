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

# Copy everything
COPY . .

# Run language setup
RUN bash mxeval/language_setup/docker.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install mxeval package
RUN cd mxeval && python -m pip install -e .

# Set up environment variables
ENV PYTHONPATH=/workspace
ENV PATH="${PATH}:/usr/local/swift-5.7-RELEASE-ubuntu20.04/usr/bin:/usr/local/go/bin:/root/.rbenv/shims:/root/.sdkman/candidates/kotlin/current/bin"

# Default command
CMD ["python", "-m", "mxeval.evaluate_functional_correctness", "--help"]
