# Tasks

## 1. Tools

- [x] 1.1 Add `llm.py` with `async_get_tools`: baby resolution (case and accent insensitive, optional with one baby), time and minutes-ago handling, results and errors as dicts; add `llm` to `after_dependencies`
- [x] 1.2 Add the log tools of every tracker, the start and stop tools of timed trackers, the dose tool and the undo tool, with voluptuous parameters, enumerations and units; record through `async_log`, the timer start and stop, `async_log_dose` and `async_delete`
- [x] 1.3 Offer tools only for trackers enabled on a loaded baby, the dose tool only with an active medication, nothing without babies or for other APIs; build the prompt fragment with babies, trackers, medications and the local time
- [x] 1.4 `tests/test_llm.py` for every spec scenario, through `llm.async_get_api` and the tools as an agent calls them, plus a test that calls each log tool with valid fields; run the full `pytest` and `ruff check`

## 2. Documentation

- [x] 2.1 README: a Voice assistant section with the requirements (an LLM agent with Assist control), example sentences in Portuguese and English, undo, and that the tools do not depend on exposed entities
- [x] 2.2 Run `openspec validate assist-logging --strict`

## 3. Real instance

- [x] 3.1 After the merge, install through the Marketplace and restart; run through the Assist pipeline, for the Teste baby: "o bebé bebeu um biberão de 90 ml de leite artificial", "mudei uma fralda molhada há 10 minutos", "a temperatura é 37,2", "afinal apaga o biberão"; check the replies, the entries in the calendars and that the bottle was deleted

## Workflow follow-up

- Archive the change with `openspec archive assist-logging --yes`, in its own PR.
