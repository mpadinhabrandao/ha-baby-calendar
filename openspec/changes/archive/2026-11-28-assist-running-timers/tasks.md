# Tasks

## 1. LLM agents

- [x] 1.1 Add each baby's running timers (tracker, side, start time) and the stopping hint to the prompt in `llm.py`; add `ended` and `duration_minutes` to `describe` for entries with an end; ask in the prompt to say the end of such entries; tests for the Running timer and Stopped timer result scenarios

## 2. Built-in agent

- [x] 2.1 Add the Portuguese and English timer phrasings to `sentences/pt.yaml` and `en.yaml`; reply with "das HH:MM às HH:MM" / "from HH:MM to HH:MM" for entries with an end; tests for each phrasing, the Parei de dar de mamar, Comecei a dar de mamar and Stopped timer scenarios, and that built-in sentences still match their own intents; run the full `pytest` and `ruff check`
- [x] 2.2 README: add the new phrasings to both tables
- [x] 2.3 Run `openspec validate assist-running-timers --strict`

## 3. Real instance

- [x] 3.1 After the merge, install through the Marketplace and restart. For the Teste baby, through the Assist pipeline:
  - start a breastfeeding timer with "comecei a dar de mamar na direita" and check `processed_locally`;
  - say "parei de dar de mamar" and check that it stopped locally, with the span in the reply;
  - start one again by voice and send "acabámos a mamada" (not a fixed sentence) to OpenAI, checking that it stops the timer without asking.

## Workflow follow-up

- Archive the change with `openspec archive assist-running-timers --yes`, in its own PR.
