# -*- coding: utf-8 -*-
r"""fish_call.py — 런팟 서버리스 Fish Audio Drama 3(엔드포인트 fish-drama3)에 한 줄을 보내 wav 로 저장한다. (2026-10-27)

  python fish_call.py --out a.wav --text "한국어 대사"
  python fish_call.py --out b.wav --text "한국어 대사" --ref 견본.wav --ref-text "견본.wav 의 글"

런팟 호출은 rtv_run.RunpodMCP(Codex 앱 서버를 빌린 MCP 통로 · 열쇠 없음)로 한다.
첫 호출은 모델(약 41.5GB)을 저장소에 받느라 오래 걸린다.
"""
import argparse
import base64
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "h3_rtv_runpod"))
import rtv_run  # noqa: E402

ENDPOINT = "rw6tae6kpr7fbs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--ref", action="append", default=[], help="목소리 견본 wav (여러 번 가능)")
    ap.add_argument("--ref-text", action="append", default=[], help="견본의 글 (--ref 순서대로)")
    ap.add_argument("--seed", type=int, default=1895)
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--top-p", type=float, default=None)
    a = ap.parse_args()
    inp = {"text": a.text, "seed": a.seed, "format": "wav"}
    if a.temperature is not None:
        inp["temperature"] = a.temperature
    if a.top_p is not None:
        inp["top_p"] = a.top_p
    if a.ref:
        inp["references"] = [{"audio_b64": base64.b64encode(open(p, "rb").read()).decode(),
                              "text": a.ref_text[i] if i < len(a.ref_text) else ""} for i, p in enumerate(a.ref)]
    m = rtv_run.RunpodMCP()
    t0 = time.time()
    r = m.call("run-endpoint", {"endpointId": ENDPOINT, "input": inp, "policy": {"executionTimeout": 1800000, "ttl": 7200000}})
    jid = r["id"]
    while True:
        s = m.call("get-job-status", {"endpointId": ENDPOINT, "jobId": jid, "wait": 45000})
        st = s.get("status")
        if st in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            break
        print("  %s %.0f초" % (st, time.time() - t0), flush=True)
    out = s.get("output") or {}
    if st != "COMPLETED" or "audio_b64" not in out:
        raise SystemExit("실패 %s: %s" % (st, str(out.get("error") or s)[:1500] + "\n" + str(out.get("detail") or out.get("trace", ""))[-1500:]))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "wb").write(base64.b64decode(out["audio_b64"]))
    print("저장 %s · 만들기 %.1f초 · 전체 %.0f초(첫 호출은 모델 받기 포함)" % (a.out, out.get("gen_seconds", 0), time.time() - t0))


if __name__ == "__main__":
    main()
