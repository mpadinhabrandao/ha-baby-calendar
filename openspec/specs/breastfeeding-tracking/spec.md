# breastfeeding-tracking Specification

## Purpose

Defines what is specific to tracking breastfeeding on top of the shared timer behaviour: the side of each entry, how consecutive sides form one feed, and a last-feed time shared with bottles.

## Requirements

### Requirement: Breastfeeding tracker
Breastfeeding SHALL be a timed tracker that the user can enable per baby, with its own start, stop and log services and its own switch, duration input, button and sensors.

#### Scenario: Enabled for a baby
- **WHEN** the user enables the breastfeeding tracker on a baby
- **THEN** the breastfeeding switch, duration input, button, side selector and sensors become available

### Requirement: Side
A breastfeeding event MAY carry a side, left or right. The side MAY be given when starting the timer and when logging a finished entry, and SHALL be changeable and clearable by the correction service.

#### Scenario: Started on the left
- **WHEN** the breastfeeding timer is started with the side left
- **THEN** the in-progress event carries the side left

#### Scenario: Invalid side
- **WHEN** an entry is started or logged with a side other than left or right
- **THEN** the call fails with an error and nothing is recorded

#### Scenario: Side omitted
- **WHEN** an entry is logged with a duration and no side
- **THEN** the event is recorded with no side

### Requirement: Side selector
A baby with the breastfeeding tracker SHALL have a selector entity offering left, right and a "not specified" choice, which is the initial value. The switch and the button SHALL use the current selection. The selection SHALL be kept across restarts.

#### Scenario: Selection used by the switch
- **WHEN** the selector shows right and the breastfeeding switch is turned on
- **THEN** an in-progress event with the side right exists

#### Scenario: Selection used by the button
- **WHEN** the selector shows left, the duration input shows 15 and the button is pressed
- **THEN** a finished fifteen-minute entry with the side left is recorded

### Requirement: Selector moves to the other side
When a breastfeeding entry that has a side is finished, by stopping the timer or by logging it afterwards, the side selector SHALL change to the other side. An entry with no side SHALL leave the selector unchanged.

#### Scenario: After a left feed
- **WHEN** a left entry is stopped
- **THEN** the side selector shows right

#### Scenario: Which side next
- **WHEN** the last entry of the previous feed was on the right
- **THEN** the side selector shows left when the next feed begins

#### Scenario: No side
- **WHEN** an entry with no side is stopped
- **THEN** the side selector is unchanged

### Requirement: Side change is two entries
A breastfeeding event SHALL carry at most one side for its whole duration. A change of side SHALL be recorded by stopping the timer and starting it again.

#### Scenario: Left then right
- **WHEN** a left entry runs eight minutes and is stopped, and the switch is turned on again and runs six minutes
- **THEN** two events exist, left with eight minutes and right with six minutes, and the daily duration shows fourteen minutes

### Requirement: Feeds today
The breastfeeding daily count SHALL count feeds, not entries. An entry that starts within 30 minutes of the end of the previous entry SHALL belong to the same feed. A feed SHALL count on the day its first entry started.

#### Scenario: Both sides in one sitting
- **WHEN** a left entry ends at 10:08 and a right entry starts at 10:10
- **THEN** feeds today increases by one, not two

#### Scenario: Two separate feeds
- **WHEN** an entry ends at 10:10 and the next starts at 12:30
- **THEN** they count as two feeds

### Requirement: Last side
The breastfeeding last-event sensor SHALL expose the side of the most recent entry as an attribute.

#### Scenario: Which side was last
- **WHEN** the most recent entry was on the right
- **THEN** the last-event sensor's side attribute is right

### Requirement: Last feed across breast and bottle
A baby with the breastfeeding tracker, the bottle tracker or both SHALL have a timestamp sensor with the time of the most recent feed of either kind, the start for a breastfeeding entry, with the kind of feed as an attribute. With no feeds it SHALL report an unknown state.

#### Scenario: Bottle after breast
- **WHEN** a breastfeeding entry started at 08:00 and a bottle is logged at 11:00
- **THEN** the last feed sensor shows 11:00 with the kind bottle

#### Scenario: Only bottles enabled
- **WHEN** only the bottle tracker is enabled and a bottle is logged
- **THEN** the last feed sensor shows the time of that bottle
