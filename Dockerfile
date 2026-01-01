# Use the base image
FROM python:3.12-slim-bookworm

# Development(dev) or production(prd) image
ARG ENV="dev"
ENV ENV=${ENV}
ARG SERVICE_NAME="service"
ENV SERVICE_NAME=${SERVICE_NAME}

# Set project directory
ENV PROJECT_ROOT="/app"
ENV PYTHONPATH=${PROJECT_ROOT}
WORKDIR ${PROJECT_ROOT}

# Set the timezone to Asia/Seoul
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# Create non-root user
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} appuser && \
    useradd -u ${UID} -g ${GID} -ms /bin/bash appuser

# Install system dependencies
RUN apt-get update -qqy && \
    apt-get install -y --no-install-recommends \
        git build-essential curl && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf ~/.cache

# Install dependencies
COPY pyproject.toml uv.lock .
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
RUN uv sync

# Switch to non-root user
RUN chown -R appuser:appuser ${PROJECT_ROOT}
USER appuser

# # Expose ports
# EXPOSE 8000

# Run the application
# CMD ["python", "/app/app/main.py"]