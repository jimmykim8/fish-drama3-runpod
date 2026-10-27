#!/bin/bash
# Fish Audio Drama 3 on Runpod serverless.
# Weights (about 41.5 GB) live on the attached network volume; downloaded once on first start.
set -u
MODEL_DIR="${MODEL_DIR:-/runpod-volume/fish/drama-3}"
PY=/app/.venv/bin/python
cd /app

if [ ! -f "$MODEL_DIR/codec.pth" ] || [ ! -f "$MODEL_DIR/model-00008-of-00008.safetensors" ]; then
  echo "[start] downloading fishaudio/drama-3 to $MODEL_DIR (first run only)"
  mkdir -p "$MODEL_DIR"
  HF_HUB_ENABLE_HF_TRANSFER=1 $PY -c "from huggingface_hub import snapshot_download; snapshot_download('fishaudio/drama-3', local_dir='$MODEL_DIR')" \
    || $PY -c "from huggingface_hub import snapshot_download; snapshot_download('fishaudio/drama-3', local_dir='$MODEL_DIR')"
fi
echo "[start] model files:"; ls -la "$MODEL_DIR" | head -30

$PY tools/api_server.py --llama-checkpoint-path "$MODEL_DIR" --decoder-checkpoint-path "$MODEL_DIR/codec.pth" \
    --listen 127.0.0.1:8080 --device cuda:0 2>&1 | tee /tmp/fish.log &
FISH=$!

until curl -sf http://127.0.0.1:8080/v1/health > /dev/null; do
  if ! kill -0 $FISH 2>/dev/null; then echo "[start] fish server died"; tail -80 /tmp/fish.log; exit 1; fi
  sleep 3
done
echo "[start] fish server up"
exec $PY -u /app/runpod_worker/handler.py
