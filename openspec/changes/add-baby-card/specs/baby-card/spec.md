# Spec Delta

## Purpose

The card a parent uses on a phone to log a baby's day with one hand and see at a glance what happened last, showing only the trackers the baby has.

## ADDED Requirements

### Requirement: One card per baby
The card SHALL be configured with one baby and nothing else, and SHALL be available in any dashboard without installing anything beyond the integration. Its visual editor SHALL offer the babies to choose from.

#### Scenario: Added from the card picker
- **WHEN** the user adds "Baby Calendar card" to a dashboard and picks "Alice"
- **THEN** the card shows Alice's home tab

#### Scenario: Baby removed
- **WHEN** the baby configured on a card is removed
- **THEN** the card says the baby was not found instead of failing

### Requirement: Only enabled trackers
The card SHALL show only the trackers enabled for the baby and its active medications, and SHALL follow changes to them without being edited or the page reloaded.

#### Scenario: Tracker enabled later
- **WHEN** the sleep tracker is enabled while the card is open
- **THEN** the sleep buttons appear on the home tab

#### Scenario: Diapers only
- **WHEN** the baby has only the diaper tracker
- **THEN** the home tab shows the diaper buttons and no bottle, breastfeeding or sleep section

### Requirement: Facts at a glance
The home tab SHALL show at the top how long ago the last feed and the last diaper change were, and how long the baby has been awake or asleep, for the trackers the baby has, updating as time passes.

#### Scenario: Last feed
- **WHEN** the last feed was a bottle at 01:30 and it is 03:40
- **THEN** the card shows that the baby ate 2 h 10 min ago

### Requirement: Logging with one tap
Each of wet, dirty and both diapers, a bottle, and starting breastfeeding on a side or sleep SHALL be one tap on a button at least 56 px high. A repeated tap within 3 seconds SHALL record one entry.

#### Scenario: Wet diaper
- **WHEN** the parent taps "Wet"
- **THEN** a wet diaper is recorded at the current time

### Requirement: Bottle amount beside the button
The bottle button SHALL show the amount it will record, with buttons beside it that lower and raise it by 10 ml, and the content choices below it. The amount and content SHALL be kept for the next bottle.

#### Scenario: Larger bottle
- **WHEN** the button shows 90 ml and the parent taps "+" twice and then the button
- **THEN** a bottle of 110 ml is recorded and the button shows 110 ml

### Requirement: Entry time chip
The card SHALL offer a chip, "now" by default, to set the next entry minutes in the past, applying to the next logging tap only and going back to "now" afterwards.

#### Scenario: Diaper 15 minutes ago
- **WHEN** the chip is set to 15 minutes ago and the parent taps "Dirty"
- **THEN** the diaper is recorded 15 minutes ago and the chip shows "now" again

### Requirement: Running timers
While a breastfeeding or sleep timer runs, its button SHALL show the elapsed time, updating every second, and stop the timer when tapped.

#### Scenario: Stop breastfeeding
- **WHEN** breastfeeding on the left has run for 12 minutes 40 seconds
- **THEN** the left button shows "Stop" and 12:40, and tapping it records the entry

### Requirement: Breastfeeding side by side
Each side SHALL be started and stopped on its own. Tapping the other side while one runs SHALL stop the running side and start the other. The card SHALL suggest no side.

#### Scenario: Side change without a pause
- **WHEN** the left side runs and the parent taps "Right"
- **THEN** the left entry is finished and a right entry starts

#### Scenario: Pause to burp
- **WHEN** the parent stops the left side, waits 5 minutes and starts the right side
- **THEN** both entries belong to the same feed

### Requirement: Last feed as it happened
The breastfeeding section SHALL show the last feed's start time and each of its sides with its duration, and the pauses between them, in order.

#### Scenario: Two sides with a pause
- **WHEN** the last feed was left 12 minutes, a 5-minute pause, then right 8 minutes, starting at 03:12
- **THEN** the card shows 03:12 and "Left 12 min · pause 5 min · Right 8 min"

### Requirement: Stool type in place
While the baby's stool type prompt is on, the card SHALL ask for the stool type below the diaper buttons, as optional, and stop asking once a type is chosen or the prompt ends.

#### Scenario: Dirty diaper
- **WHEN** the parent taps "Dirty" and then "Soft"
- **THEN** the diaper's stool type is soft and the question disappears

### Requirement: Due medications on top
Each medication with a dose due SHALL appear at the top of the home tab with its name, dose text and a "Given" button that records a dose.

#### Scenario: Vitamin D due
- **WHEN** a dose of "Vitamin D", "1 drop", is due and the parent taps "Given"
- **THEN** a dose is recorded and the medication no longer appears at the top

### Requirement: Undo the entry just made
After an entry is recorded from the card, the card SHALL show for 60 seconds a bar naming it with an "Undo" button that deletes that entry.

#### Scenario: Wrong button
- **WHEN** the parent taps "Both" by mistake and then "Undo" in the bar
- **THEN** that diaper entry is deleted

### Requirement: More tab
A second tab SHALL show today's totals for the enabled trackers, a form for each other enabled tracker (weight, length, temperature, solids, pumping) and for recording a dose of any active medication, and the latest entries.

#### Scenario: Weight from the form
- **WHEN** the parent opens the weight form, enters 3450 and saves
- **THEN** a weight of 3450 g is recorded

#### Scenario: Value out of range
- **WHEN** the parent enters 3.45 in the weight form and saves
- **THEN** the form shows the accepted range and records nothing

### Requirement: Errors shown, nothing lost silently
When an action fails, the card SHALL show the error message from Home Assistant and keep the inputs as they were.

#### Scenario: Home Assistant unreachable
- **WHEN** the connection is lost and the parent taps "Wet"
- **THEN** the card says the entry was not recorded

### Requirement: Language
The card's text SHALL be in Portuguese when the user's Home Assistant language is Portuguese, and in English otherwise.

#### Scenario: Portuguese user
- **WHEN** the user's language is Portuguese
- **THEN** the diaper buttons read "Xixi", "Cocó" and "Os dois"
