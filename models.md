# Chutes API Models

Base URLs and auth: `Authorization: Bearer $CHUTES_API_TOKEN`

**Autonomous pipeline:** `python run_dharmakirti.py --agent` uses Qwen3.5 for sayability, decomposition, formalization. LLM never proves — Lean does. PLACEHOLDER = Lean ran and said "sorry" (proofenginge.md); when Lean unavailable → UNPROVED.

---

api = cpk_94ddac5de1054212b9bdb9ac891b6dba.381752230628574db598f8cd09be095a.yhMoHY9QKOewnBUJhfakWwx3dqYi23by

## Endpoints

### Embeddings (Qwen)

```bash
curl -X POST \
  https://chutes-qwen-qwen3-embedding-8b.chutes.ai/v1/embeddings \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "example-string",
    "model": null
  }'
```

### Chat completions (LLM)

```bash
curl -X POST \
  https://llm.chutes.ai/v1/chat/completions \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<MODEL_ID>",
    "messages": [{"role": "user", "content": "Tell me a 250 word story."}],
    "stream": true,
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

---

## Model profiles

| Model | ID | Best for | Speed | Notes |
|-------|-----|----------|-------|-------|
| **GLM-5** | `zai-org/GLM-5-TEE` | Agentic all-rounder | Medium | Strong generalist, good for tool use, planning, multi-step tasks |
| **Kimi K2.5** | `moonshotai/Kimi-K2.5-TEE` | Agentic all-rounder | Medium | Strong generalist, good for tool use, planning, multi-step tasks |
| **DeepSeek V3.2** | `deepseek-ai/DeepSeek-V3.2-TEE` | Math, reasoning | Slower | Best at math and formal reasoning; use when precision matters |
| **Qwen 3.5 397B** | `Qwen/Qwen3.5-397B-A17B-TEE` | Languages, writing, images | Fastest | Fast; strong at languages, writing, image extraction |

---

## When to use which

- **Agentic / multi-step / tool use:** GLM-5 or Kimi K2.5
- **Math, proofs, formal reasoning:** DeepSeek V3.2
- **Speed, languages, writing, image extraction:** Qwen 3.5 397B

---

## Example curl commands by model

### GLM-5 (agentic)

```bash
curl -X POST \
  https://llm.chutes.ai/v1/chat/completions \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "zai-org/GLM-5-TEE",
    "messages": [{"role": "user", "content": "Tell me a 250 word story."}],
    "stream": true,
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

### Kimi K2.5 (agentic)

```bash
curl -X POST \
  https://llm.chutes.ai/v1/chat/completions \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshotai/Kimi-K2.5-TEE",
    "messages": [{"role": "user", "content": "Tell me a 250 word story."}],
    "stream": true,
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

### DeepSeek V3.2 (math)

```bash
curl -X POST \
  https://llm.chutes.ai/v1/chat/completions \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3.2-TEE",
    "messages": [{"role": "user", "content": "Tell me a 250 word story."}],
    "stream": true,
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

### Qwen 3.5 397B (fast, languages, images)

```bash
curl -X POST \
  https://llm.chutes.ai/v1/chat/completions \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-397B-A17B-TEE",
    "messages": [{"role": "user", "content": "Tell me a 250 word story."}],
    "stream": true,
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```
