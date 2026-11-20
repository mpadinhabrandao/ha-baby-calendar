# Spec Delta

## Purpose

What the integration provides so its card works with no setup: the card's registration, a live description of each baby, and the entries of the last feed.

## ADDED Requirements

### Requirement: Card registered by the integration
When the integration is loaded, it SHALL serve the card's module and add it to every dashboard, so the card needs no dashboard resource. The module's URL SHALL change with the integration's version, so an update reaches clients.

#### Scenario: After installing
- **WHEN** the integration is installed and Home Assistant restarted
- **THEN** "Baby Calendar card" is in the card picker of every dashboard

### Requirement: Baby description subscription
The integration SHALL offer a WebSocket subscription that sends, for every baby, its name, device id, enabled trackers, active medications with their name and dose text, and the entity id of each of its entities by purpose, and sends it again whenever a baby is added, removed or reconfigured.

#### Scenario: Medication added
- **WHEN** a card is subscribed and a medication is added to the baby
- **THEN** the card receives the baby again with the new medication and its entity ids

#### Scenario: Not an administrator
- **WHEN** a non-administrator user's card subscribes
- **THEN** it receives the babies, since logging is for every household member

### Requirement: Last feed entries
The last breastfeeding sensor SHALL have an attribute `feed` listing the entries of the last feed in order, each with its side, start and end, where a feed is the run of entries that start within 30 minutes of the previous entry's end.

#### Scenario: Two sides with a pause
- **WHEN** left ran 03:12 to 03:24 and right 03:29 to 03:37
- **THEN** `feed` lists left 03:12–03:24 and right 03:29–03:37

#### Scenario: Running side
- **WHEN** the last entry is still running
- **THEN** it is in `feed` with no end
