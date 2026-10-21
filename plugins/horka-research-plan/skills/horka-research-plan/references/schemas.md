# JSON schemas to impose on agents

Use them as the `schema` option of `agent()` in a Workflow script, or paste them in the brief with "return exactly this JSON".

## Researcher

```json
{
  "type": "object",
  "required": ["actions", "not_found"],
  "properties": {
    "actions": {"type": "array", "items": {"type": "object",
      "required": ["title", "type", "audience", "steps", "expectation", "cost", "delay"],
      "properties": {
        "title": {"type": "string"},
        "type": {"type": "string"},
        "audience": {"type": "string"},
        "steps": {"type": "array", "items": {"type": "string"}},
        "expectation": {"type": "object", "required": ["figure", "source_url", "date", "status"],
          "properties": {"figure": {"type": "string"}, "source_url": {"type": "string"}, "date": {"type": "string"},
                         "status": {"type": "string", "enum": ["verified", "partial", "hypothesis", "not_found"]}}},
        "comparable": {"type": "string"},
        "cost": {"type": "string"},
        "delay": {"type": "string"},
        "risk": {"type": "string"}
      }}},
    "not_found": {"type": "array", "items": {"type": "string"}}
  }
}
```

## Validator

```json
{
  "type": "object",
  "required": ["checks"],
  "properties": {
    "checks": {"type": "array", "items": {"type": "object",
      "required": ["claim", "url", "status"],
      "properties": {
        "claim": {"type": "string"},
        "url": {"type": "string"},
        "status": {"type": "string", "enum": ["verified", "partial", "unverifiable", "false"]},
        "note": {"type": "string"}
      }}}
  }
}
```

## Persona

```json
{
  "type": "object",
  "required": ["persona", "overall_reaction", "actions", "missing", "rules", "sources"],
  "properties": {
    "persona": {"type": "string"},
    "overall_reaction": {"type": "string"},
    "actions": {"type": "array", "items": {"type": "object",
      "required": ["title", "effect", "why", "condition"],
      "properties": {"title": {"type": "string"}, "effect": {"type": "string", "enum": ["try", "neutral", "flee"]},
                     "why": {"type": "string"}, "condition": {"type": "string"}}}},
    "missing": {"type": "array", "items": {"type": "string"}},
    "rules": {"type": "array", "items": {"type": "string"}},
    "sources": {"type": "array", "items": {"type": "object", "required": ["claim", "url"],
      "properties": {"claim": {"type": "string"}, "url": {"type": "string"}}}}
  }
}
```

## Critic

```json
{
  "type": "object",
  "required": ["kept", "dropped", "duplicates", "fragile_figures", "risks", "sequence_90d"],
  "properties": {
    "kept": {"type": "array", "items": {"type": "object", "required": ["title", "order", "first_step", "gate"],
      "properties": {"title": {"type": "string"}, "order": {"type": "integer"}, "first_step": {"type": "string"}, "gate": {"type": "string"}}}},
    "dropped": {"type": "array", "items": {"type": "object", "required": ["title", "reason"],
      "properties": {"title": {"type": "string"}, "reason": {"type": "string"}}}},
    "duplicates": {"type": "array", "items": {"type": "string"}},
    "fragile_figures": {"type": "array", "items": {"type": "string"}},
    "risks": {"type": "array", "items": {"type": "string"}},
    "sequence_90d": {"type": "array", "items": {"type": "string"}}
  }
}
```

## Demand probe

```json
{
  "type": "object",
  "required": ["method", "topics", "ranking", "not_found"],
  "properties": {
    "method": {"type": "string"},
    "topics": {"type": "array", "items": {"type": "object",
      "required": ["topic", "stackoverflow", "hn", "autocomplete", "verdict", "recommended_title"],
      "properties": {"topic": {"type": "string"}, "stackoverflow": {"type": "string"}, "hn": {"type": "string"},
                     "autocomplete": {"type": "string"}, "github": {"type": "string"},
                     "verdict": {"type": "string", "enum": ["strong", "medium", "weak"]}, "recommended_title": {"type": "string"}}}},
    "ranking": {"type": "array", "items": {"type": "string"}},
    "not_found": {"type": "array", "items": {"type": "string"}}
  }
}
```
