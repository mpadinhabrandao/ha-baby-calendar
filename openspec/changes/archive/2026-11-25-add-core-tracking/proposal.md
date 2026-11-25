# Proposal

## Why

Parents log a newborn's diapers and feeds many times a day, often one-handed at 3 a.m., and both parents need to see the same record. Home Assistant is already on every phone and wall tablet in the house, but its helpers lose history after the recorder purge window and past entries cannot be corrected. This change delivers the smallest version of Baby Calendar that is usable from the first day: a durable log with purpose-built diaper and bottle trackers, where a slip is undone with one tap and an entry can be back-dated without leaving the dashboard.

## What Changes

- New custom integration `baby_calendar`, installable through HACS as a custom repository.
- A baby is added from the Home Assistant UI. Each baby is one device, and several babies can coexist.
- The trackers are defined by the integration. When adding a baby the user ticks the ones to use, and can change the selection later. This change provides two: diaper and bottle.
- Diaper tracker: one diaper change is wet, dirty or both. Three one-tap buttons log it. After a dirty one, stool type buttons add the type to that diaper as an optional second tap. Sensors for the last change, last wet, last dirty, and today's changes, wet and dirty counts.
- Bottle tracker: amount in ml and content (formula or breast milk); sensors for the last bottle, today's bottles and today's ml.
- A "minutes ago" input per baby, so a button press can record something that happened earlier. It returns to zero after each entry.
- An "undo last entry" button per baby, for the wrong button or a double tap.
- A durable event log that is independent of the recorder retention, and services to correct, delete and list entries.
- Removing a baby keeps its history, which can be re-attached when the baby is added again. Deleting history is a separate, explicit action.
- English and Portuguese translations of every name and option.

Out of scope for this change (each is a later change): breastfeeding and sleep with timers, the calendar entity, medication with reminders, measurements, solids, pumping. Not planned: an ICS feed, user-defined trackers, any custom dashboard card.

## Capabilities

### New Capabilities

- `baby-profile`: adding, editing and removing a baby from the UI, choosing its enabled trackers, what happens to its history, and how a baby is represented in Home Assistant.
- `event-log`: the durable record of baby events, covering retention, back-dating, undo, correction, deletion and querying, and the rules shared by all daily values.
- `diaper-tracking`: logging diaper changes, adding a stool type, and the sensors derived from them.
- `feeding-tracking`: logging bottles and the sensors derived from them.

### Modified Capabilities

None.

## Impact

- New repository content: `custom_components/baby_calendar/`, `hacs.json`, `README.md`, `LICENSE` (MIT), tests and CI.
- A new data file in the Home Assistant configuration directory, included in Home Assistant backups.
- No new Python dependencies beyond what Home Assistant ships.
- No network access. No effect on existing integrations or entities.
