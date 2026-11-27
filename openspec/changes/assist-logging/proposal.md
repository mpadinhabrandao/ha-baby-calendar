# Proposal

## Why

Logging an entry means taking out the phone and opening the dashboard, often with the baby in one's arms. Home Assistant's voice assistant is already set up in the house with an OpenAI conversation agent. It can control what Home Assistant offers it, but Baby Calendar offers it nothing, so "the baby drank 90 ml" goes unrecorded.

## What Changes

- The integration offers tools to assistants that use Home Assistant's **Assist** API (an LLM conversation agent such as OpenAI or Anthropic with "Control Home Assistant" set to Assist):
  - record an entry of each tracker: diaper, bottle, breastfeeding, sleep, solids, pumping, weight, length, temperature;
  - start and stop the breastfeeding and sleep timers;
  - record a medication dose by name.
- Each tool takes the same fields as the matching action. The time is optional: an exact local time, or minutes ago for "há 10 minutos". Notes are optional too.
- **Choosing the baby:** the baby is chosen by name. With one baby the name can be left out. An unknown or ambiguous name fails and lists the babies.
- **Only what is in use:** tools are offered only for trackers enabled on at least one baby, and the dose tool only when a baby has an active medication. A tool fails for a baby that does not have the tracker enabled.
- **Context for the assistant:** each request gets a short prompt with the babies, their enabled trackers, their active medications and the current local time. "Biberão de 90" then becomes a bottle of 90 ml for the only baby.
- **Undo:** each tool returns what was recorded and its entry id. An undo tool deletes an entry by that id, so "afinal não, apaga isso" works in the same conversation.
- README: a Voice assistant section that explains the setup and gives example sentences in Portuguese and English.

## Capabilities

### New Capabilities

- `voice-assistant`: tools for LLM assistants to record entries, start and stop timers, record doses and undo, with the context prompt.

### Modified Capabilities

None.

## Impact

- New `custom_components/baby_calendar/llm.py`, Home Assistant's `llm` integration platform. The `llm` integration is added to `after_dependencies` in `manifest.json`.
- Recording reuses the code behind the actions (`async_log`, the timer start and stop, `async_log_dose`, `async_delete`), so rules, undo and sensors behave as with the cards.
- New `tests/test_llm.py`.
- `README.md`.
- No change to the built-in agent without an LLM: sentences for it would be a separate change.
