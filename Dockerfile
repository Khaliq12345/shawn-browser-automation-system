FROM ubuntu:24.04

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Set working directory
WORKDIR /app

# Copy all files
COPY ./interface ./interface

# Install Python dependencies
RUN uv sync --locked

RUN uv run camoufox fetch
RUN uv run playwright install-deps
RUN uv run playwright install

