# Tasks

## 1. Card

- [x] 1.1 In the Recent entries card, map each entry to its entity per design D1 and render lines with an entity as buttons that dispatch `hass-more-info`; lines without one stay plain; verify with the type check and the unit tests
- [x] 1.2 Rebuild the bundle and extend the Playwright check: tapping "peso 3480 g" fires `hass-more-info` with the weight sensor, a dose fires it with the medication's last dose sensor, a dose of an unknown medication fires nothing, and the line is reachable with the keyboard

## 2. Documentation and checks

- [x] 2.1 Add to the README's cards table that tapping a Recent entries line opens the entity's history
- [ ] 2.2 On the real instance, tap a weight line and a bottle line in the Recent entries card and verify Home Assistant's dialog opens with the history
- [x] 2.3 Run `openspec validate open-entry-details --strict`
