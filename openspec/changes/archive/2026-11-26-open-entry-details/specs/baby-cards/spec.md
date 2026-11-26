# Spec Delta

## ADDED Requirements

### Requirement: Entry details from Recent entries
Tapping an entry in the Recent entries card SHALL open Home Assistant's more-info dialog of the entity that holds that kind of entry: the value sensor for a weight, length or temperature; the tracker's last entry sensor for a diaper change, bottle, breastfeeding, sleep, solids or pumping entry; and the medication's last dose sensor for a dose. An entry whose entity does not exist SHALL open nothing.

#### Scenario: Weight history
- **WHEN** the parent taps the line "weight 3480 g"
- **THEN** the more-info dialog of the baby's weight sensor opens, with its history

#### Scenario: Bottle
- **WHEN** the parent taps a bottle line
- **THEN** the more-info dialog of the baby's last bottle sensor opens

#### Scenario: Medication dose
- **WHEN** the parent taps a dose of "Vitamin D"
- **THEN** the more-info dialog of Vitamin D's last dose sensor opens

#### Scenario: Medication removed
- **WHEN** the parent taps a dose of a medication that has since been removed
- **THEN** nothing opens
