# Superset with Arc dialect pre-installed
FROM apache/superset:latest

USER root

# Option 1: Install from PyPI (once published)
# RUN pip install --no-cache-dir arc-superset-dialect

# Option 2: Install from local build (for development)
COPY . /tmp/arc-superset-dialect
RUN pip install --no-cache-dir /tmp/arc-superset-dialect && \
    rm -rf /tmp/arc-superset-dialect

# Copy custom Superset configuration
COPY superset_config.py /app/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER superset

ENTRYPOINT ["/app/entrypoint.sh"]