FROM python:3.11-slim

WORKDIR /workspace

# Copy the evaluation code
COPY . .

# Install mxeval package
RUN cd mxeval && python -m pip install -e .

RUN bash language_setup/docker.sh

# Set up environment variables
ENV PYTHONPATH=/workspace

CMD ["python", "-m", "mxeval.evaluate_functional_correctness", "--help"]
