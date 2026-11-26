# Spec Delta

## MODIFIED Requirements

### Requirement: Cards available with the integration
The integration SHALL provide the Diapers, Bottle, Breastfeeding, Sleep, Medications, Summary, Today and Other entries cards, all in the card picker of every dashboard with nothing to install beyond the integration.

#### Scenario: Card picker
- **WHEN** the user opens the card picker of any dashboard
- **THEN** the eight Baby Calendar cards are offered

## REMOVED Requirements

### Requirement: Recent entries card
**Reason**: On a real instance it confused more than it helped: entries of two days with only a time, and nothing the Registos page needed; stock tiles of the measurement sensors show what is wanted.
**Migration**: Remove the card from dashboards. To see entries use the calendar; to see a measurement and its history use a tile of its sensor.

### Requirement: Entry details from Recent entries
**Reason**: Goes with the Recent entries card.
**Migration**: A stock tile of an entity opens its more-info dialog with its history.
