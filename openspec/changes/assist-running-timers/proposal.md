# Proposal

## Why

On 27 Nov at 23:53, with a right-side breastfeeding timer running for 30 minutes on the Teste baby, the parent said "Parei de dar de mamar". Two things went wrong:
- **The built-in agent had no matching sentence.** Its sentences only cover "acabou a mama" and "<baby> acabou de mamar", so the request went to OpenAI.
- **OpenAI did not know that a timer was running.** It read the sentence as weaning and offered to note that, so the parent had to say explicitly "quero que pares a mamada que está a correr agora".

Once stopped, the reply said "registada às 23:24", which is the start time, while the feed ended at 23:54.

## What Changes

- **Running timers in the prompt:** the prompt given to LLM agents lists each baby's running timers, with the side and the start time. It also says that, while a timer runs, sentences like "parei", "acabou", "terminei" or "acordou" refer to stopping it.
- **End time in the results:** a tool result for an entry with an end gives the end time and the duration as well, and the prompt asks to say when it ended.
- **More built-in sentences** for starting and stopping timers, so the common phrasings are handled locally, without OpenAI:
  - Portuguese: "comecei a dar de mamar", "estou a dar de mamar", "a dar de mamar na esquerda", "parei de dar de mamar", "terminei de dar de mamar", "já mamou", "parei a mamada", "adormeceu", "já acordou";
  - English: "started feeding", "feeding on the left", "stopped feeding", "done feeding", "finished feeding".
- **Reply of the built-in agent for a stopped timer:** it says the span, "das 23:24 às 23:54", instead of the start time alone.
- The README tables get the new sentences.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `voice-assistant`: the context lists running timers; results and replies of entries with an end give the end; the built-in sentences cover more phrasings for timers.

## Impact

- `custom_components/baby_calendar/llm.py` (prompt) and `voice.py` (`describe` and the reply texts).
- `custom_components/baby_calendar/intents.py` (reply for a stopped timer).
- `custom_components/baby_calendar/sentences/pt.yaml` and `en.yaml`.
- `tests/test_llm.py`, `tests/test_intents.py`.
- `README.md`.
- No change to the store, the services or the cards.
