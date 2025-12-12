FROM ubuntu:24.04

# Install dependencies: curl, certificates, build tools, Python 3.12 and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
        software-properties-common \
        lsb-release \
        wget \
        gnupg \
        libffi-dev \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        uuid-dev \
        liblzma-dev \
        xclip \
        git && \
    apt-get update && \
    rm -rf /var/lib/apt/lists/*


# Update & install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    xvfb \
    xserver-xephyr \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Google Chrome
# -----------------------------
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Node.js (via NodeSource)
# -----------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    node --version && npm --version


# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN uv sync

RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

RUN uv run camoufox fetch
RUN uv run playwright install-deps
RUN uv run playwright install
# RUN uv run camoufox fetch

CMD ["uv", "run", "src/utils/browser_runner.py"]
