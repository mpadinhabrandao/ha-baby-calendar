## ADDED Requirements

### Requirement: Built-in agent sentences
The integration SHALL let Home Assistant's built-in conversation agent record entries from fixed sentences in Portuguese and English:
- each tracker's entry;
- starting and stopping the timers of timed trackers;
- a dose of a medication by name.

A sentence MAY name the baby and MAY say how many minutes ago it happened. Without a name it SHALL apply to the only baby. Numbers SHALL be accepted with a comma or a point as the decimal separator.

#### Scenario: Bottle in Portuguese
- **WHEN** the only baby has bottles enabled and the built-in agent hears "bebeu um biberão de 90 ml de leite artificial"
- **THEN** a bottle of 90 ml of formula is recorded now

#### Scenario: Diaper some minutes ago
- **WHEN** the agent hears "mudei uma fralda molhada há 10 minutos"
- **THEN** a wet diaper is recorded 10 minutes before now

#### Scenario: Temperature with a comma
- **WHEN** the agent hears "tem 37,2 graus"
- **THEN** a temperature of 37.2 °C is recorded

#### Scenario: Sleep in English
- **WHEN** the agent hears "Alice fell asleep" and later "Alice woke up"
- **THEN** a sleep for Alice is recorded from the first sentence to the second

#### Scenario: Dose by name
- **WHEN** the baby has the active medication "Vitamina D" and the agent hears "dei a vitamina D"
- **THEN** a dose of Vitamina D is recorded

### Requirement: Spoken reply
Each sentence SHALL be answered in its language with what was recorded and at what time, or with why nothing was recorded:
- the baby is unknown or not named when there are several;
- the tracker is not enabled;
- the timer is already running or not running;
- the number cannot be read.

#### Scenario: Confirmation
- **WHEN** a bottle of 90 ml of formula is recorded by voice at 21:20 on a Portuguese pipeline
- **THEN** the reply says a bottle of 90 ml of formula was recorded at 21:20

#### Scenario: Tracker not enabled
- **WHEN** the agent hears "comeu sólidos" and the baby does not have solids enabled
- **THEN** nothing is recorded and the reply says solids are not enabled for the baby

### Requirement: Managed sentence files
The integration SHALL keep the sentences in `custom_sentences/pt/baby_calendar.yaml` and `custom_sentences/en/baby_calendar.yaml` in the configuration folder. It SHALL rewrite them, and reload the built-in agent, when a baby is added, renamed or removed or its medications change. Each file SHALL start with a header that marks it as generated. The integration SHALL NOT change or delete a file at those paths that lacks the header. It SHALL delete its files when the last baby is removed.

#### Scenario: New baby
- **WHEN** a baby "Bruno" is added next to "Alice"
- **THEN** the files list Alice and Bruno, and "Bruno adormeceu" starts Bruno's sleep timer

#### Scenario: A file of the user's
- **WHEN** `custom_sentences/pt/baby_calendar.yaml` exists without the header
- **THEN** it is left unchanged and a warning is logged

#### Scenario: Last baby removed
- **WHEN** the only baby is removed
- **THEN** both generated files are deleted

### Requirement: Undo by voice with the built-in agent
The built-in agent SHALL understand a sentence to undo, such as "desfaz o último registo" or "undo the last entry". It SHALL delete the most recent entry that a sentence recorded for the baby in the last 10 minutes. When there is none, it SHALL reply that there is nothing to undo.

#### Scenario: Undo a misheard bottle
- **WHEN** a bottle was recorded by voice 2 minutes ago and the agent hears "desfaz o último registo"
- **THEN** the bottle is deleted and the reply says so

#### Scenario: Nothing recent
- **WHEN** the last entry recorded by voice is 30 minutes old and the agent hears "desfaz o último registo"
- **THEN** nothing is deleted and the reply says there is nothing to undo
