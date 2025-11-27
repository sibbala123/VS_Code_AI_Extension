FROM ollama/ollama:latest

# Expose Ollama's API port
EXPOSE 11434

# Pre-pull Qwen 2.5 model to bake it into the image
# This is crucial - otherwise each pod downloads the model on startup
RUN ollama serve & \
    sleep 10 && \
    ollama pull qwen2.5:latest && \
    pkill ollama

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/ || exit 1

# Start Ollama server
CMD ["ollama", "serve"]