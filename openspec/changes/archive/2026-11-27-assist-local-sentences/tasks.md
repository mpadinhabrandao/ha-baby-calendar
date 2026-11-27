# Tasks

Implement after `assist-logging` is merged; archive after it.

## 1. Shared code and intents

- [x] 1.1 Move baby resolution, recording, time handling and result text from `llm.py` to `voice.py`, with spoken texts in `en` and `pt`; `assist-logging`'s tests still pass
- [x] 1.2 Add `intents.py`: one handler per intent (log per tracker, start and stop per timer, medication, undo), registered once in `async_setup`; number parsing with comma or point and kg to g; the voice undo memory with its 10-minute window; add `conversation` to `after_dependencies`

## 2. Sentence files

- [x] 2.1 Write `sentences/pt.yaml` and `sentences/en.yaml` with the intents' sentence templates, the fixed lists and wildcard number slots
- [x] 2.2 Add `sentences.py`: generate the baby and medication lists, write both files with the header in the executor, debounced, then `conversation.reload`; skip a file without the header with one warning; delete the files when the last entry is removed
- [x] 2.3 Add `hassil` and `home-assistant-intents` to the dev dependencies; `tests/test_intents.py` running every spec scenario through the built-in agent (`conversation.async_converse`), and checking that built-in sentences such as "liga a luz da cozinha" still match their own intents; `tests/test_sentences.py` for writing, rewriting, the user's file and removal; run the full `pytest` and `ruff check`

## 3. Documentation

- [x] 3.1 README Voice assistant section: the built-in agent, the two managed files, the sentence list in Portuguese and English, voice undo, and how to remove the files after uninstalling an older version
- [x] 3.2 Run `openspec validate assist-local-sentences --strict`

## 4. Real instance

- [x] 4.1 After the merge, install through the Marketplace and restart; check that both files exist with the Teste baby; run through the built-in agent ("conversation.home_assistant"): "mudei uma fralda molhada", "bebeu um biberão de 90 ml de leite artificial", "tem 37,2 graus" and "desfaz o último registo"; check the replies and the calendars; then run "bebeu um biberão de 60 ml" through the Assist pipeline and check that it is answered locally, without OpenAI

## Workflow follow-up

- Archive the change with `openspec archive assist-local-sentences --yes`, after `assist-logging`, in its own PR.
