## MODIFIED Requirements

### Requirement: Context for the assistant
With its tools, the integration SHALL give the assistant a prompt that:
- lists each loaded baby with its enabled trackers, its active medications with their doses, and its running timers with their side and start time;
- states the current local time;
- states that, while a timer runs, a sentence saying that the activity stopped refers to stopping that timer.

#### Scenario: Prompt contents
- **WHEN** the baby "Duarte" has diapers and bottles enabled and the medication "Vitamina D", "1 gota"
- **THEN** the prompt names Duarte, diapers, bottles, Vitamina D with 1 gota, and the current local time

#### Scenario: Running timer
- **WHEN** Duarte's breastfeeding timer has been running on the right side since 23:24
- **THEN** the prompt says that Duarte's breastfeeding timer is running on the right side since 23:24, and that stopping phrases refer to it

### Requirement: Spoken reply
Each sentence SHALL be answered in its language with what was recorded and at what time, or, for an entry with an end, from what time to what time. Otherwise it SHALL say why nothing was recorded:
- the baby is unknown or not named when there are several;
- the tracker is not enabled;
- the timer is already running or not running;
- the number cannot be read.

#### Scenario: Confirmation
- **WHEN** a bottle of 90 ml of formula is recorded by voice at 21:20 on a Portuguese pipeline
- **THEN** the reply says a bottle of 90 ml of formula was recorded at 21:20

#### Scenario: Stopped timer
- **WHEN** a breastfeeding timer started at 23:24 is stopped by voice at 23:54 on a Portuguese pipeline
- **THEN** the reply says the breastfeed was recorded from 23:24 to 23:54

#### Scenario: Tracker not enabled
- **WHEN** the agent hears "comeu sólidos" and the baby does not have solids enabled
- **THEN** nothing is recorded and the reply says solids are not enabled for the baby

## ADDED Requirements

### Requirement: End of entries in tool results
For an entry with an end, such as a stopped timer, a tool's result SHALL also give the end time and the duration in minutes.

#### Scenario: Stopped timer result
- **WHEN** a breastfeeding timer started at 23:24 is stopped with the tool at 23:54
- **THEN** the result gives 23:24 as the time, 23:54 as the end and 30 as the duration in minutes

### Requirement: Timer phrasings
The built-in agent SHALL understand common ways of saying that a timed activity started or stopped:
- in Portuguese, "comecei a dar de mamar", "estou a dar de mamar", "parei de dar de mamar", "terminei de dar de mamar", "já mamou", "parei a mamada" and "já acordou";
- in English, "started feeding", "stopped feeding", "done feeding" and "finished feeding".

#### Scenario: Parei de dar de mamar
- **WHEN** the breastfeeding timer is running and the built-in agent hears "parei de dar de mamar"
- **THEN** the breastfeeding timer is stopped and the feed is recorded

#### Scenario: Comecei a dar de mamar
- **WHEN** no breastfeeding timer runs and the built-in agent hears "comecei a dar de mamar na direita"
- **THEN** a breastfeeding timer starts on the right side
