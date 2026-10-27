# Runpod serverless worker for Fish Audio Drama 3, on top of the official fish-speech server image (CUDA 12.9, Drama 3 support).
FROM fishaudio/fish-speech:server-cuda
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
 && uv pip install --python /app/.venv/bin/python runpod requests ormsgpack huggingface_hub hf_transfer
COPY handler.py start.sh /app/runpod_worker/
RUN chmod +x /app/runpod_worker/start.sh
ENTRYPOINT []
CMD ["/app/runpod_worker/start.sh"]
