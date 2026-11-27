# Design

## Context

Home Assistant 2026.10+ builds the tools of the Assist LLM API from an `llm` integration platform. `llm.async_get_tools(hass, llm_context, api_id)` collects `async_get_tools` from each integration's `llm.py`, which returns `LLMTools(tools, prompt)` or `None`. The `intent_script` integration uses this platform; custom integrations are discovered the same way. A `Tool` has a `name`, a `description`, a voluptuous `parameters` schema and `async_call(hass, tool_input, llm_context)`, which returns a JSON-serialisable dict to the model.

The instance's pipeline uses `conversation.openai_conversation` with `prefer_local_intents`. A sentence the built-in intents do not match goes to OpenAI, which sees the Assist tools.

The services already hold the logic: `async_log(hass, entry, tracker, fields, when, notes)`, the timed trackers' start and stop, `async_log_dose`, and `async_delete`. The trackers' `log_fields` are `probatio` schemas.

## Goals / Non-Goals

**Goals:**
- Record every kind of entry, and start or stop timers, by voice or chat, through the agent the house already uses.
- Speak back what was recorded, so a misheard amount is caught, and allow undo.

**Non-Goals:**
- Questions such as "when did she last feed?". The agent can already read exposed sensors; dedicated query tools can come later.
- The built-in agent without an LLM (custom sentences).
- Editing an entry other than undoing it.

## Decisions

### One tool per action, named after the action
The tools are `baby_calendar__log_diaper`, `…__log_bottle`, `…__start_sleep`, `…__stop_sleep`, `…__log_medication`, `…__delete_entry`, and so on, mirroring the actions. Each has a one-line description of when to use it.

The parameters are explicit voluptuous schemas written for the LLM: enumerations with their values, units in the description ("amount in ml", "weight in g"). They are kept consistent with the trackers' fields by a test that calls each tool with valid fields. Converting the trackers' `probatio` schemas at runtime was rejected: their messages and types are written for the action form, and the LLM schema converter expects voluptuous.

- Alternative: one generic `log_entry` tool with a `tracker` field. Rejected: the fields differ by tracker, and a single schema loses the per-tracker enumerations that keep the model from inventing values.

### Baby resolution
The `baby` parameter is optional and matched to the loaded entries' names, ignoring case and accents. With one loaded baby it may be omitted. When it cannot be resolved, the tool returns an error that names the babies, for the model to ask or retry.

### Time
`time` takes a local date and time, `"YYYY-MM-DD HH:MM"`. `minutes_ago` is a non-negative integer. Passing both is an error. Without either, the entry is recorded now. The prompt fragment states the current local time, so relative phrases can be resolved either way.

### Results
A tool returns `{"recorded": <calendar title>, "baby": <name>, "time": "HH:MM", "entry_id": <id>}`. The title is the one the calendar shows, for example "🍼 Bottle 90 ml formula", so the reply matches what the parent will see. Errors are returned as `{"error": <message>}` instead of being raised. The model can then explain the problem: tracker not enabled, timer already running, unknown medication.

### Which tools exist
`async_get_tools` returns `None` when no baby is loaded. Otherwise it returns:
- the tools of trackers enabled on any loaded baby;
- the dose tool when any baby has an active medication;
- the undo tool.

The tools do not depend on entity exposure. The babies' entities are not what the tools act on, and asking the user to expose entities only to enable a tool would be a hidden step. This is noted in the README.

### Prompt fragment
The fragment is a few lines:
- that Baby Calendar records baby care entries;
- each baby's name, enabled trackers and active medications with their doses;
- the current local time;
- to confirm what was recorded in one short sentence.

It is built per request from `runtime_data`, so it is never stale.

## Risks / Trade-offs

- [The model records the wrong amount from a misheard sentence] → Each reply repeats what was recorded, and the undo tool removes it.
- [The `llm` platform API changes in a later Home Assistant release] → The tests run against the pinned Home Assistant and fail on such a change. The README states the minimum version.
- [The prompt fragment costs tokens on every request of the agent, also unrelated ones] → It is a few lines per baby.
- [Anyone who can talk to the assistant can record entries] → The same as anyone who can open the dashboard.

## Migration Plan

No data change. After installing, the tools appear in the next conversation. Rollback: reinstall the previous version.
