## ADDED Requirements

### Requirement: Calendars by group
Each baby SHALL have one calendar entity per group of entries, attached to the baby's device:

| Group | Entries |
|---|---|
| Feeding | bottle, breastfeeding, solids, pumping |
| Diapers | diaper changes |
| Sleep | sleep |
| Health | temperature, weight, length, medication doses |

A calendar SHALL show the baby's recorded events of its group's trackers and no other events. Events of other babies SHALL NOT appear in it.

#### Scenario: Entries split by group
- **WHEN** a diaper change, a bottle and a sleep were recorded for a baby today
- **THEN** the Diapers calendar shows only the diaper change, the Feeding calendar only the bottle and the Sleep calendar only the sleep

#### Scenario: Health entries together
- **WHEN** a temperature of 38.5 °C, a weight of 4200 g and a paracetamol dose were recorded for a baby
- **THEN** all three appear in the baby's Health calendar and none appears in the other calendars

#### Scenario: Two babies
- **WHEN** babies "Alice" and "Bruno" exist and a diaper change is recorded for "Alice"
- **THEN** it appears in the Diapers calendar of "Alice" and not in the Diapers calendar of "Bruno"

#### Scenario: Filter in the calendar panel
- **WHEN** the user turns off every calendar of a baby except Health in the calendar panel
- **THEN** only temperatures, weights, lengths and medication doses are shown

### Requirement: Calendar names
Each calendar SHALL be named after its group, in the language of the Home Assistant instance.

#### Scenario: Portuguese instance
- **WHEN** a baby "Duarte" is added on a Portuguese instance
- **THEN** its calendars are named "Alimentação", "Fraldas", "Sono" and "Saúde" on the baby's device

### Requirement: When a group calendar exists
A group's calendar SHALL exist when at least one of the group's trackers is enabled for the baby, when the group is Health and the baby has a medication, or when the baby has recorded events of the group's trackers. Otherwise it SHALL NOT exist, and a calendar that stops meeting these conditions SHALL be removed.

#### Scenario: Diapers only
- **WHEN** a new baby has only the diaper tracker enabled and no medications
- **THEN** the baby has a Diapers calendar and no Feeding, Sleep or Health calendar

#### Scenario: Tracker disabled with history
- **WHEN** the pumping tracker was the only Feeding tracker enabled, pumpings were recorded and then the tracker is disabled
- **THEN** the Feeding calendar still exists and shows those pumpings

#### Scenario: Medication only
- **WHEN** a baby has no measurement tracker enabled but has a medication
- **THEN** the baby has a Health calendar

### Requirement: Own entries only
Changing the time of an event, editing its notes or deleting it through a calendar SHALL apply only to events of that calendar's group. A request for an event of another group or another baby SHALL be rejected with an error and the event SHALL be unchanged.

#### Scenario: Event of another group
- **WHEN** a delete is requested through the Diapers calendar for the uid of a bottle event
- **THEN** the request fails and the bottle still exists

### Requirement: Single calendar removed
The calendar that showed all of a baby's events SHALL NOT exist. When the integration starts, it SHALL remove that calendar from the entity registry if it is still there.

#### Scenario: Upgrade
- **WHEN** a baby set up with the single calendar is loaded by this version
- **THEN** the single calendar is gone from Home Assistant and the baby's group calendars exist instead

## MODIFIED Requirements

### Requirement: Full history
Each calendar SHALL show events of any date for which events of its group are recorded, without a retention limit, including events of a tracker that has since been disabled.

#### Scenario: Three months ago
- **WHEN** the user navigates the Diapers calendar to a week three months in the past
- **THEN** the diaper changes recorded in that week are shown

#### Scenario: Disabled tracker
- **WHEN** the bottle tracker is disabled after bottles were recorded
- **THEN** those bottles still appear in the Feeding calendar

### Requirement: Calendar state
A calendar SHALL be on while a timed event of its group for the baby is in progress and off otherwise. An instantaneous event SHALL NOT turn it on.

#### Scenario: Diaper logged
- **WHEN** a diaper change is recorded and no timer is running
- **THEN** every calendar of the baby stays off

#### Scenario: Sleep running
- **WHEN** a sleep timer of the baby is running and no breastfeeding timer is
- **THEN** the Sleep calendar is on and the Feeding calendar is off

## REMOVED Requirements

### Requirement: One calendar per baby
**Reason**: A single calendar with every entry cannot be filtered in Home Assistant, which filters by calendar. Replaced by "Calendars by group".
**Migration**: Replace `calendar.<baby>_calendar` in dashboards and automations with the baby's group calendars. To see every entry together, turn on all of the baby's calendars in the calendar panel or list them all in a calendar card.
