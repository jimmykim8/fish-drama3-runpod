# fish-drama3-runpod

Runpod serverless worker for [Fish Audio Drama 3](https://huggingface.co/fishaudio/drama-3) (Fish Audio Community License).
Built on `fishaudio/fish-speech:server-cuda`. Weights (~41.5 GB) are downloaded once to the attached network volume (`/runpod-volume/fish/drama-3`).
Needs a GPU with at least 48 GB (FP8 experts on SM89+).

Input: `text`, `references` ([{audio_b64, text}]), `seed`, `temperature`, `top_p`, `max_new_tokens`, `single_chunk`, `normalize`, `format`.
Output: `audio_b64`, `format`, `gen_seconds`.
