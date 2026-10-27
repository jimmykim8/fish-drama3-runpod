# -*- coding: utf-8 -*-
"""Runpod serverless handler for Fish Audio Drama 3 (fish-speech API server on 127.0.0.1:8080). 2026-10-27

Input (job["input"]):
  text            text to speak (inline tags such as [whisper] / [sigh] are passed through)
  references      [{"audio_b64": ..., "text": transcript}]  optional voice reference(s)
  seed, temperature, top_p, max_new_tokens, single_chunk, normalize, format ("wav"|"mp3")
Output: {"audio_b64": ..., "format": ..., "gen_seconds": ...}
"""
import base64
import time

import ormsgpack
import requests
import runpod
from fish_speech.utils.schema import ServeReferenceAudio, ServeTTSRequest

URL = "http://127.0.0.1:8080/v1/tts"


def handler(job):
    inp = job.get("input") or {}
    try:
        refs = [ServeReferenceAudio(audio=base64.b64decode(r["audio_b64"]), text=r.get("text", ""))
                for r in inp.get("references", []) if r.get("audio_b64")]
        kw = dict(text=inp["text"], references=refs, format=inp.get("format", "wav"), streaming=False,
                  single_chunk=bool(inp.get("single_chunk", True)), normalize=bool(inp.get("normalize", False)),
                  use_memory_cache="off")
        for k in ("seed", "temperature", "top_p", "max_new_tokens"):
            if inp.get(k) is not None:
                kw[k] = inp[k]
        req = ServeTTSRequest(**kw)
        t = time.time()
        r = requests.post(URL, params={"format": "msgpack"},
                          data=ormsgpack.packb(req, option=ormsgpack.OPT_SERIALIZE_PYDANTIC),
                          headers={"content-type": "application/msgpack"}, timeout=900)
        if r.status_code != 200:
            return {"error": "fish server %d" % r.status_code, "detail": r.text[:2000]}
        return {"audio_b64": base64.b64encode(r.content).decode(), "format": req.format, "gen_seconds": round(time.time() - t, 2)}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()[-3000:]}


runpod.serverless.start({"handler": handler})
