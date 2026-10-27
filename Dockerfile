# Runpod serverless worker for Fish Audio Drama 3, on top of the official fish-speech server image (CUDA 12.9, Drama 3 support).
FROM fishaudio/fish-speech:server-cuda
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
 && uv pip install --python /app/.venv/bin/python runpod requests ormsgpack huggingface_hub hf_transfer \
 && uv pip install --python /app/.venv/bin/python --reinstall-package torch --reinstall-package torchaudio \
      --index-url https://download.pytorch.org/whl/cu128 torch==2.8.0 torchaudio==2.8.0 \
 && /app/.venv/bin/python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_arch_list())"
COPY handler.py start.sh /app/runpod_worker/
RUN chmod +x /app/runpod_worker/start.sh
ENTRYPOINT []
CMD ["/app/runpod_worker/start.sh"]
