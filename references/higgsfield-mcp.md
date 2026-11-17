# Higgsfield MCP: call shapes, prices and gotchas

There are two ways to reach it:
- **Directly:** the Higgsfield MCP connector (`https://mcp.higgsfield.ai/mcp`) in the host, for example during the sponsored recording.
- **Through the local Test Lab:** `higgsfield-connector/`, served at `http://localhost:8790`. Start it from `.claude/launch.json` (name `higgsfield-connector`) with preview_start, because local port binding is blocked in the sandbox. Use `POST /api/call {"tool", "args", "log"}`.
  - `log: true` stores a run record with the credits before and after.
  - Calling localhost from Bash needs the sandbox disabled.
  - `scripts/hf_lab.py` wraps all of this.

## Call shapes

| Purpose | Tool | Args |
|---|---|---|
| Price check (free) | `generate_image` / `generate_video` | `{"params": {..., "get_cost": true}}` → `structuredContent.cost.credits` |
| Image | `generate_image` | `{"params": {"model": "gpt_image_2_6_flare", "prompt", "aspect_ratio": "9:16", "quality": "high", "resolution": "1k", "batch_size": 1, "medias": [{"role": "image_references", "value": "<media_id>"}]}}` |
| Video | `generate_video` | see video-generation.md |
| Result | — | `structuredContent.results[0].id` = job id |
| Wait | `jobs_wait` | `{"jobs": [{"index": 0, "job_id": "…"}], "timeout_seconds": 15}`. Loop until the status is completed, failed or nsfw. |
| Status | `job_status` | `{"jobId": "…"}` (camelCase; `job_id` fails validation) |
| Upload | `media_upload` | `{"filename": "x.png", "content_type": "image/png"}` or `{"files": [{"filename", "content_type"}, …]}`. The text result contains `- <media_id>: … curl … '<presigned URL>'` |
| PUT bytes | curl | `curl -X PUT -H 'Content-Type: image/png' -H 'If-None-Match: *' --data-binary @file '<url>'`. The presigned URL lists `if-none-match` among its signed headers, so send it exactly like this (every PUT returned 200 this way). |
| Confirm | `media_confirm` | `{"type": "image", "media_id": "…"}` or `{"type": "image", "media_ids": […]}` |
| Balance | `balance` | — |

- Media ID lifetime isn't verified. We reused IDs for about 6 h without problems. The `media_upload` schema has an `expires_in_seconds` field, so check the reply, and re-upload if a generation rejects an ID.
- Upload filenames must be unique within one call: every master is named `00-master-full-body.png`. `hf_lab.py` prefixes an index and the parent folder.
- Output URLs are on cloudfront: `.png`, `.mp4`, plus a `_min.webp` thumbnail you can ignore.

## Measured prices (credits)

| Job | Credits |
|---|---|
| gpt_image_2, 1k medium | 1 |
| gpt_image_2_6_flare, high 1k | 1.5 |
| gpt_image_2_6_flare, medium 1k | 0.5 |
| gpt_image_2_6_flare, medium 2k | 1 |
| gpt_image_2_6_flare, high 2k | 2.75 |
| seedance_2_5, 480p | 3 per second (audio on, audio off and draft cost the same) |
| seedance_2_5, 720p / 1080p, non-draft | 7 / 16 per second |
| seedance_2_5, finalise a 4 s draft (`draft_job_id`) | quoted 64 at both 720p and 1080p; re-check |
| seedance_2_5 `bitrate_mode: high` | same price as standard, but **failed 8 of 8 with image_references** (refunded); avoid |
| bytedance_video_upscale, 5 s clip → 1080p, `aigc` | 1 (standard), 10 (pro) |
| video_upscale / video_deflicker, 5 s clip | 2 each |
| fps_boost (ByteDance, 48 fps), 5 s clip | about 20 |
| kling4_0 / wan3_0, 5 s 1080p; veo3_1, 4 s high | 16.25 / 17.5 / 16 |
| cinematic_studio_video_4_0 / seedance_2_0 std, 5 s 1080p | 80 / 60 |
| seedance_2_0 std, 5 s 720p | 22.5 |
| seedance_2_0 fast, 5 s | 12.5 |
| kling3_0, 5 s, sound off | 7.5 |

Unlimited generations were not available on this account. Always confirm with `get_cost` before submitting.

## Post-processing models (priced through `generate_video` + `get_cost`)

- Upscalers and finishing models take an existing clip as `medias`: role `video_references` for `bytedance_video_upscale`, `topaz_video` and `fps_boost`; role `input_video` for `video_upscale`, `video_deflicker` and `sync_so` (which also takes `input_audio`).
- A **completed job id** was accepted as the media value in price checks, so a generated clip doesn't need re-uploading.
- The dedicated `upscale_video` tool has no cost preflight. `topaz_video` can't be priced by preflight either.

## Gotchas

- `batch_size: 2` on flare billed 3 credits and returned **one** image. Use separate jobs.
- `get_account_overview` with no args fails; use `balance`.
- Elements (`<<<element_id>>>` in the prompt) work only on supported models. **Seedance 2.5 isn't one of them**; image refs worked fine instead.
- Balance can change from outside the session (the web app, other agents). Report the credits before and after from the run log, not from assumptions.
- Never print or commit `higgsfield-connector/data/auth.json` (the OAuth tokens).
