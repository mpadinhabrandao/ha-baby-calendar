# Baby Calendar

A Home Assistant custom integration to log a baby's day: diapers and bottles
first, with more trackers planned. It has no frontend of its own. It provides
entities and services, and you build the dashboard with stock cards.

All data stays on your Home Assistant host. The integration records and
displays data only; it gives no health advice.

**Status:** under development, not ready for use yet.

## Babies

### Adding a baby

Settings > Devices & services > Add integration > **Baby Calendar**.

1. Enter the baby's name. The birth date is optional, so you can add the
   baby before it is born and set the date later.
2. Tick the trackers to use for this baby. You can tick none and enable them
   later.

Each baby is one device, named after it, holding all of its entities. Add one
entry per baby; two babies cannot share a name.

### Editing a baby

Open the baby's entry and choose **Configure** to change the name, the birth
date or the enabled trackers. Nothing recorded is lost.

Disabling a tracker removes its entities and keeps its events. Enabling it
again brings the entities back with the same default entity ids, but any
entity id you renamed and any dashboard card pointing at it must be set up
again.

### Removing a baby and its history

Deleting a baby's entry removes its device and entities and **keeps its
history** in `baby_calendar.db`. Removing and re-adding an entry is a common
troubleshooting step, and it should not cost months of records.

When you add a baby with the same name as a removed one, the integration asks
whether to:

- **Restore that history**: the baby comes back with all of its events.
- **Start empty**: the baby starts with no events, and the old history stays
  stored but unattached.

To delete the stored history of a removed baby for good, call the
`baby_calendar.purge_history` action with its name:

```yaml
action: baby_calendar.purge_history
data:
  name: Alice
```

It refuses to act on a baby that is still configured. If several removed
babies share the name, it deletes all of them and its response says how
many babies and events were deleted.

### Where the data lives

Events are stored in `baby_calendar.db` in the Home Assistant configuration
directory, independent of the recorder, so they are kept beyond its retention
period. The file is part of standard Home Assistant backups.

## License

[MIT](LICENSE)
