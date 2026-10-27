#!/bin/bash
# Fish Audio Drama 3 on Runpod serverless.
# Weights (about 41.5 GB) live on the attached network volume; downloaded once on first start.
set -u
MODEL_DIR="${MODEL_DIR:-/runpod-volume/fish/drama-3}"
PY=/app/.venv/bin/python
cd /app

# A half-finished download leaves some shards behind, so only the marker written after a full download counts.
# The lock keeps several workers from downloading into the same folder at once.
mkdir -p "$MODEL_DIR"
(
  flock 9
  if [ ! -f "$MODEL_DIR/.download_complete" ]; then
    echo "[start] downloading fishaudio/drama-3 to $MODEL_DIR (first run only)"
    until $PY -c "from huggingface_hub import snapshot_download; snapshot_download('fishaudio/drama-3', local_dir='$MODEL_DIR')"; do
      echo "[start] download failed, retrying in 10s"; sleep 10
    done
    touch "$MODEL_DIR/.download_complete"
  fi
) 9>"$MODEL_DIR/../drama-3.lock"
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
