# Superset with Arc dialect pre-installed
FROM apache/superset:latest

USER root

# Install Arc dialect from PyPI
RUN pip install --no-cache-dir arc-superset-dialect

# Copy custom Superset configuration
COPY superset_config.py /app/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER superset

ENTRYPOINT ["/app/entrypoint.sh"]