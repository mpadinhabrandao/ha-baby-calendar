# Spec Delta

## Purpose

The cards a parent uses on a phone to log a baby's day with one hand and see what happened last, one card per job, to be combined into dashboards of the household's own design.

## ADDED Requirements

### Requirement: Cards available with the integration
The integration SHALL provide the Diapers, Bottle, Breastfeeding, Sleep, Medications, Summary, Today, Other entries and Recent entries cards, all in the card picker of every dashboard with nothing to install beyond the integration.

#### Scenario: Card picker
- **WHEN** the user opens the card picker of any dashboard
- **THEN** the nine Baby Calendar cards are offered

### Requirement: One baby per card
Each card SHALL be configured with one baby, through a visual editor that lists the babies, and SHALL say so when that baby no longer exists instead of failing.

#### Scenario: Baby chosen in the editor
- **WHEN** the user adds the Diapers card and picks "Alice"
- **THEN** the card logs Alice's diapers

#### Scenario: Baby removed
- **WHEN** the baby configured on a card is removed
- **THEN** the card says the baby was not found

### Requirement: Tracker not enabled
A card for a tracker the baby does not have SHALL say that the tracker is not enabled for the baby, and SHALL work as soon as it is enabled, without being edited or the page reloaded.

#### Scenario: Sleep enabled later
- **WHEN** the Sleep card shows that sleep is not enabled and sleep is then enabled for the baby
- **THEN** the card shows its sleep button

### Requirement: Fits the dashboard
Cards SHALL use the Home Assistant theme's colours, fonts and card style in light and dark mode, SHALL size themselves in the sections grid, and SHALL add no navigation of their own.

#### Scenario: Dark theme
- **WHEN** the dashboard uses a dark theme
- **THEN** the cards are drawn with that theme's card background and text colours

### Requirement: Logging with one tap
Every logging button SHALL record its entry in one tap, SHALL be at least 56 px high, and a repeated tap within 3 seconds SHALL record one entry.

#### Scenario: Double tap
- **WHEN** the parent taps "Wet" twice in a second
- **THEN** one wet diaper is recorded

### Requirement: Entry time chip
Every logging card SHALL offer a chip, "now" by default, to set its next entry minutes in the past. It SHALL apply to that card's next entry only and go back to "now" afterwards.

#### Scenario: Diaper 15 minutes ago
- **WHEN** the Diapers card's chip is set to 15 minutes ago and the parent taps "Dirty"
- **THEN** the diaper is recorded 15 minutes ago and the chip shows "now" again

### Requirement: Undo the entry just made
After a card records an entry, it SHALL show for 60 seconds a bar naming the entry with an "Undo" button that deletes that entry.

#### Scenario: Wrong button
- **WHEN** the parent taps "Both" by mistake and then "Undo"
- **THEN** that diaper entry is deleted

### Requirement: Errors shown
When an action fails, the card SHALL show the message from Home Assistant and keep its inputs as they were.

#### Scenario: Connection lost
- **WHEN** the connection is lost and the parent taps "Wet"
- **THEN** the card says the entry was not recorded

### Requirement: Diapers card
The Diapers card SHALL offer wet, dirty and both. While the baby's stool type prompt is on, it SHALL ask the stool type, as optional, until a type is chosen or the prompt ends.

#### Scenario: Dirty diaper with its type
- **WHEN** the parent taps "Dirty" and then "Soft"
- **THEN** the diaper's stool type is soft and the question disappears

### Requirement: Bottle card
The Bottle card SHALL show the amount it will record as a value, not a button, between buttons lowering and raising it by 10 ml, then the content choices, then one "Log bottle" button that records it. The amount and content SHALL be kept for the next bottle. Changing the amount or the content SHALL record nothing.

#### Scenario: Larger bottle
- **WHEN** the card shows 90 ml and the parent taps "+" twice and then "Log bottle"
- **THEN** a 110 ml bottle is recorded and the card shows 110 ml

#### Scenario: Only adjusting
- **WHEN** the parent taps "+" and chooses breast milk
- **THEN** no bottle is recorded

### Requirement: Breastfeeding sides
The Breastfeeding card SHALL offer left and right, each started and stopped on its own. The running side SHALL show "Stop" and its live time. Tapping the other side while one runs SHALL stop it and start the other. The card SHALL suggest no side.

#### Scenario: Stop
- **WHEN** the left side has run for 12 minutes 40 seconds
- **THEN** the left button shows "Stop" and 12:40, and tapping it finishes the entry

#### Scenario: Side change without a pause
- **WHEN** the left side runs and the parent taps "Right"
- **THEN** the left entry is finished and a right entry starts

### Requirement: Last feed as it happened
The Breastfeeding card SHALL show the last feed's start time and how long ago it was, each side with its duration in order, the pauses between them, and the time spent feeding when there is more than one entry. A running feed SHALL be shown as running.

#### Scenario: One side
- **WHEN** the last feed was the right side for 15 minutes from 03:12
- **THEN** the card shows "Last feed · 03:12" with how long ago, and "Right 15 min"

#### Scenario: Two sides with a pause
- **WHEN** the last feed was left 12 minutes, a 5-minute pause, then right 8 minutes
- **THEN** the card shows "Left 12 min · pause 5 min · Right 8 min · 20 min in total"

#### Scenario: Same side twice
- **WHEN** the last feed was left 10 minutes, a 6-minute pause, then left 5 minutes
- **THEN** the card shows "Left 10 min · pause 6 min · Left 5 min · 15 min in total"

#### Scenario: Running
- **WHEN** left ran 12 minutes, then after a 5-minute pause right is running
- **THEN** the card shows "Feeding since 03:12" and "Left 12 min · pause 5 min · Right running"

### Requirement: Sleep card
The Sleep card SHALL offer "Fell asleep" and, while the sleep timer runs, "Woke up" with the live time asleep.

#### Scenario: Asleep
- **WHEN** the baby fell asleep 1 hour 20 minutes ago
- **THEN** the card shows "Woke up" and 1:20:00

### Requirement: Medications card
The Medications card SHALL show each medication with a dose due, with its dose text and a "Given" button that records a dose, and SHALL show nothing due when none is. When configured to, it SHALL also list every active medication with "Given".

#### Scenario: Vitamin D due
- **WHEN** a dose of "Vitamin D", "1 drop", is due and the parent taps "Given"
- **THEN** a dose is recorded and Vitamin D is no longer shown as due

### Requirement: Summary card
The Summary card SHALL show how long ago the last feed and the last diaper change were, and how long the baby has been awake or asleep, for the trackers the baby has, updating as time passes.

#### Scenario: Last feed
- **WHEN** the last feed was a bottle at 01:30 and it is 03:40
- **THEN** the card shows that the baby ate 2 h 10 min ago

### Requirement: Today card
The Today card SHALL show the day's totals for the baby's enabled trackers: diaper changes with wet and dirty, bottles with millilitres, feeds with time, sleep time, solids, and pumping with millilitres.

#### Scenario: Bottles today
- **WHEN** four bottles totalling 420 ml were recorded today
- **THEN** the card shows 4 bottles and 420 ml

### Requirement: Other entries card
The Other entries card SHALL offer a small form for each of weight, length, temperature, solids and pumping that the baby has, and for a dose of any active medication, showing the accepted range when a value is refused.

#### Scenario: Weight
- **WHEN** the parent enters 3450 in the weight form and saves
- **THEN** a weight of 3450 g is recorded

#### Scenario: Value out of range
- **WHEN** the parent enters 3.45 in the weight form and saves
- **THEN** the form shows the accepted range and records nothing

### Requirement: Recent entries card
The Recent entries card SHALL list the baby's latest entries, newest first, each with its time and a short description, refreshed when an entry is added, changed or deleted.

#### Scenario: After a bottle
- **WHEN** a 90 ml bottle is recorded at 03:40
- **THEN** the card's first line is the 90 ml bottle at 03:40

### Requirement: Language
Cards SHALL be in Portuguese when the user's Home Assistant language is Portuguese, and in English otherwise.

#### Scenario: Portuguese user
- **WHEN** the user's language is Portuguese
- **THEN** the Diapers card reads "Xixi", "Cocó" and "Os dois"
