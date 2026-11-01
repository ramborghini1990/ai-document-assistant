# app/ai — local rules

- `providers/base.py` defines the Protocols: `TextLLM`, `StructuredLLM`, `VisionOCR`, `Embedder`.
  Every backend (Gemini, OpenAI-compatible local server, fake) implements them. Nothing outside
  `app/ai/providers/` imports `google.genai`, `openai`, `httpx` for model calls, or `ollama`.
- Errors are typed: `ProviderRateLimited`, `ProviderUnavailable`, `ProviderEmptyResponse`,
  `ProviderInvalidOutput`. Never return a sentinel string ("The model returned…") or `"{}"` on
  failure: raise, and let the service decide.
- No `time.sleep` inside a provider call. Retry policy lives in the caller (service or Celery task).
- Prompts must work on a 14B local model: explicit JSON schema, no grounding/tools, bounded context.
- Structured extraction passes a JSON Schema built from `SchemaDef` (`json_schema_for(schema)`), so
  local servers can enforce it with constrained decoding.
- Every call logs model id, prompt hash, latency and token counts (no document text) for the audit trail.
- Zero egress: in `AI_BACKEND=local` mode a startup check refuses any non-local base URL.
