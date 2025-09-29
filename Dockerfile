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

# Install basic programming languages
RUN apt-get update && apt-get install -y \
    ruby-full \
    openjdk-8-jdk \
    nodejs \
    npm \
    scala \
    build-essential \
    g++ \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install PHP from default Ubuntu repository (simpler)
RUN apt-get update && apt-get install -y \
    php \
    php-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js packages globally
RUN npm install -g n && \
    n 16.10.0

# Update PATH and install packages with new npm
ENV PATH="/usr/local/bin:$PATH"
RUN npm install -g typescript lodash

# Install Go
RUN cd /usr/local && \
    wget https://go.dev/dl/go1.19.1.linux-amd64.tar.gz && \
    tar -xzf go1.19.1.linux-amd64.tar.gz && \
    rm go1.19.1.linux-amd64.tar.gz

# Install Swift
RUN cd /usr/local && \
    wget "https://download.swift.org/swift-5.7-release/ubuntu2004/swift-5.7-RELEASE/swift-5.7-RELEASE-ubuntu20.04.tar.gz" && \
    tar -xzf swift-5.7-RELEASE-ubuntu20.04.tar.gz && \
    rm swift-5.7-RELEASE-ubuntu20.04.tar.gz

# Install Kotlin
RUN cd /tmp && \
    wget https://github.com/JetBrains/kotlin/releases/download/v1.7.10/kotlin-compiler-1.7.10.zip && \
    unzip kotlin-compiler-1.7.10.zip && \
    mv kotlinc /usr/local/ && \
    ln -s /usr/local/kotlinc/bin/kotlin /usr/local/bin/kotlin && \
    ln -s /usr/local/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    rm kotlin-compiler-1.7.10.zip

# Install .NET
RUN apt-get update && \
    apt-get install -y dotnet6 && \
    rm -rf /var/lib/apt/lists/*

# Install Perl modules
RUN cpan -T Data::Compare

# Copy everything
COPY . .

# Install mxeval package
RUN cd mxeval && python -m pip install -e .

# Set up environment variables
ENV PYTHONPATH=/workspace
ENV PATH="${PATH}:/usr/local/swift-5.7-RELEASE-ubuntu20.04/usr/bin:/usr/local/go/bin:/usr/local/kotlinc/bin"

# Default command
CMD ["python", "-m", "mxeval.evaluate_functional_correctness", "--help"]
