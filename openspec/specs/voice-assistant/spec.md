# voice-assistant Specification

## Purpose

Let parents record entries by voice or chat through Home Assistant's conversation agents: tools for agents that use an LLM, with the babies as context, and the same rules, undo and calendar titles as the dashboard.

## Requirements

### Requirement: Logging tools for assistants
The integration SHALL offer tools to conversation agents that use Home Assistant's Assist LLM API to record an entry of each tracker, start and stop the timers of timed trackers, and record a dose of a medication by name. Each tool SHALL accept the same fields as the matching action, SHALL record through the same code as the action, and SHALL return what was recorded, as the calendar titles it, with the baby, the time and the entry id.

#### Scenario: Bottle by voice
- **WHEN** the assistant calls the bottle tool with 90 ml of formula and no time for the only baby
- **THEN** a bottle of 90 ml of formula is recorded now and the tool returns its calendar title, the time and the entry id

#### Scenario: Sleep timer
- **WHEN** the assistant calls the start sleep tool and later the stop sleep tool
- **THEN** a sleep is recorded from the start to the stop, as with the sleep switch

#### Scenario: Dose by name
- **WHEN** the assistant calls the dose tool with "paracetamol" and the baby has an active medication "Paracetamol"
- **THEN** a dose of Paracetamol is recorded

### Requirement: Time and notes
A tool SHALL accept an optional time, given either as a local date and time or as a number of minutes ago, and optional notes. Without a time the entry SHALL be recorded now.

#### Scenario: Minutes ago
- **WHEN** the assistant calls the diaper tool with a wet diaper and 10 minutes ago
- **THEN** the diaper change is recorded 10 minutes before now

#### Scenario: Both time forms
- **WHEN** a tool is called with both a time and minutes ago
- **THEN** nothing is recorded and the tool returns an error

### Requirement: Choosing the baby
A tool SHALL take the baby's name, matched without regard to case or accents. With one baby loaded the name MAY be left out. When no baby or more than one baby matches, the tool SHALL record nothing and SHALL return an error that lists the babies' names.

#### Scenario: Name left out
- **WHEN** only the baby "Duarte" is loaded and a tool is called without a baby
- **THEN** the entry is recorded for Duarte

#### Scenario: Two babies, no name
- **WHEN** babies "Alice" and "Bruno" are loaded and a tool is called without a baby
- **THEN** nothing is recorded and the error names Alice and Bruno

### Requirement: Only enabled trackers
The integration SHALL offer a tracker's tools only when the tracker is enabled on at least one loaded baby. It SHALL offer the dose tool only when a loaded baby has an active medication. It SHALL offer no tools when no baby is loaded, and none to APIs other than Assist. A tool called for a baby without that tracker enabled, or with a medication the baby does not have, SHALL record nothing and SHALL return an error.

#### Scenario: Diapers only
- **WHEN** the only baby has only the diaper tracker enabled and no medications
- **THEN** the tools offered are the diaper tool and the undo tool

#### Scenario: Tracker not enabled for the baby
- **WHEN** Alice has bottles enabled, Bruno does not, and the bottle tool is called for Bruno
- **THEN** nothing is recorded and the tool returns an error

### Requirement: Context for the assistant
With its tools, the integration SHALL give the assistant a prompt that lists each loaded baby with its enabled trackers and active medications with their doses, and states the current local time.

#### Scenario: Prompt contents
- **WHEN** the baby "Duarte" has diapers and bottles enabled and the medication "Vitamina D", "1 gota"
- **THEN** the prompt names Duarte, diapers, bottles, Vitamina D with 1 gota, and the current local time

### Requirement: Undo by voice
The integration SHALL offer a tool that deletes an entry by the entry id a logging tool returned. Deleting SHALL follow the rules of the delete action.

#### Scenario: Undo a misheard bottle
- **WHEN** the bottle tool returned an entry id and the undo tool is called with that id
- **THEN** the bottle is deleted and no longer counts in today's totals
