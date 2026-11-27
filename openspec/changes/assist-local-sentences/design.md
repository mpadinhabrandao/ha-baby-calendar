# Design

## Context

The built-in conversation agent matches sentences with hassil. Its templates come from `home-assistant-intents` and from YAML files in `<config>/custom_sentences/<language>/`, which it reads when it loads a language. `conversation.reload` makes it read them again. A matched sentence becomes an intent with slots, handled by whatever handler is registered for that intent type with `intent.async_register`, a public API. Custom integrations cannot ship sentences to the agent any other public way. The user chose this mechanism over copying files by hand, the agent's internal trigger API and an automation blueprint.

Lists in a sentence file can be:
- fixed values with `in`/`out`;
- integer ranges (`range: from/to`, with `multiplier`);
- wildcards, which capture free text.

`assist-logging` adds `llm.py` with the recording code for tools: baby resolution, time handling, recording through the services' code, and result text.

## Goals / Non-Goals

**Goals:**
- Record every kind of entry by voice with the built-in agent, in Portuguese and English.
- No manual step: install, add a baby, speak.
- Never overwrite a file the user wrote.

**Non-Goals:**
- Other languages. The structure allows adding a `<language>.yaml` template later.
- Questions ("when did she last feed?") and editing entries.
- Exact times ("às 14:30") in the first version. "há N minutos" covers the common case.

## Decisions

### Templates in the package, lists generated
`sentences/pt.yaml` and `sentences/en.yaml` in the integration hold the intents and their sentence templates, written by hand. At write time `sentences.py` adds the generated lists:
- `baby_calendar_baby`: each loaded baby's name, with `out` set to its `entry_id`;
- `baby_calendar_medication`: each active medication's name, with `out` set to `<entry_id>:<medication id>`.

It then writes the result with a header comment. The fixed lists, such as diaper contents, bottle contents and sides, are in the templates, with `out` set to the tracker's stored keys.

### Numbers through wildcards, parsed in the handler
Amounts, weights, lengths and temperatures are wildcard slots at the end of their phrase or before the unit. The handler parses them, accepting "90", "37,2", "37.2" and "4,2 kg" with a conversion to grams. Speech-to-text writes numbers as digits.

- Alternative: integer ranges. Rejected: no decimals, and a split "37 vírgula 2" form is brittle.

The minutes in "há N minutos" use an integer range from 1 to 600.

### Intents
The intent types are `BabyCalendarLog<Tracker>`, `BabyCalendarStart<Timer>`, `BabyCalendarStop<Timer>`, `BabyCalendarLogMedication` and `BabyCalendarUndo`. Handlers are registered once in `async_setup` and look babies up at call time. Slots:
- `baby` (optional);
- the tracker's fields;
- `minutes`;
- `medication`.

The reply is set with `response.async_set_speech`, in the intent's language (`intent_obj.language`), from texts held in `voice.py` for `en` and `pt`.

### When files are written
The files are written on setup and unload of any baby entry, and on an options change, which reloads the entry. Writes are debounced by one second, so a restart writes once. The write runs in the executor. Then `conversation.reload` runs, if the conversation integration is loaded.

The files are deleted in `async_remove_entry` when no other Baby Calendar entry remains. A file is ours only when its first line is the header. Otherwise it is left alone and a warning is logged, once.

### Voice undo
`voice.py` keeps, per baby, the id and time of the last entry recorded by an intent. Undo deletes it through `async_delete` when it is under 10 minutes old, and then forgets it. Otherwise the reply says there is nothing to undo. This is in memory and lost on restart, which is acceptable for a 10-minute window.

### Shared code
`assist-logging`'s baby resolution, recording and result text move to `voice.py`, used by `llm.py` and `intents.py`, so both paths record and describe entries the same way.

## Risks / Trade-offs

- [Writing to the configuration folder surprises a user] → Only two named files, marked as generated; the README says so; deleted on removal.
- [A sentence of ours collides with a built-in one] → Our sentences all name a baby concept ("fralda", "biberão", "mama", "adormeceu"…). The tests run the built-in sentences next to ours and check that ours win only for our phrases.
- [Wildcards make matching greedy] → Each wildcard is followed by a unit word or ends the sentence, and the handler rejects text that is not a number, with a reply.
- [The agent caches sentences until reload] → `conversation.reload` after each write.

## Migration Plan

Install and restart: the files are written and the agent reloaded. Rollback: reinstall the previous version and delete the two files, as the README explains.

## Open Questions

None.
