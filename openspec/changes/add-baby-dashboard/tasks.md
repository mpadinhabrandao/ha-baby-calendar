# Tasks

## 1. Attributes

- [x] 1.1 Add the `medication` attribute to every medication entity (button, last dose, doses today, next dose, due) and the `stool_type` attribute to each stool type button; verify with tests in English and Portuguese, and that existing attributes are unchanged

## 2. View

- [x] 2.1 Write `dashboards/baby.yaml` per design D3 and D4 with the `BABY_NAME` and `STOOL_PROMPT_ENTITY` placeholders; verify it parses as YAML and that every filter uses only domains, classes, the device, the integration and the two attributes
- [ ] 2.2 Document the dashboard in `README.md`: installing auto-entities from the Marketplace and its MIT licence, adding the view with its two values, one view per baby, renaming a baby, and that the integration works without the card; verify the steps against a real instance
- [ ] 2.3 Update `openspec/config.yaml`: the project context names the documented dashboard and its auto-entities dependency, and lists this change as the eighth; verify `openspec validate add-baby-dashboard --strict` passes

## 3. Integration checks

- [ ] 3.1 On a real instance, install auto-entities and add the view for the test baby; verify on a phone the section order, that the stool type appears only while the prompt is on, and that logging, timers and medications work from it
- [ ] 3.2 On the real instance, add a medication and enable a tracker; verify both appear in the view without editing it, and disappear when deactivated and disabled
- [ ] 3.3 Verify the view in Portuguese and in English shows the same sections

## Workflow follow-up

- Archive the change after review, with the other changes.
