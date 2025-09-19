FROM ubuntu:20.04

# Install basic dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /workspace

# Copy the evaluation code
COPY . .

# Install mxeval package
RUN cd mxeval && python3 -m pip install -e .

RUN bash language_setup/ubuntu.sh

# Set up environment variables
ENV PYTHONPATH=/workspace

CMD ["python3", "-m", "mxeval.evaluate_functional_correctness", "--help"]
