# Tasks

## 1. Remove the card

- [x] 1.1 Delete `frontend/src/cards/recent.ts`, its registration in `frontend/src/index.ts` and the strings and styles only it used; verify with the type check and the unit tests
- [x] 1.2 Remove the Recent entries checks from `frontend/e2e/run.mjs`, add a check that the card picker list has eight cards and no `baby-calendar-recent-card`, rebuild the bundle and run the Playwright checks

## 2. Documentation and checks

- [x] 2.1 Update `README.md`: drop the card from the table and the card list, and add a line that a stock tile of the weight, length or temperature sensor shows the value and opens its history
- [x] 2.2 On the real instance, after installing, verify the card picker offers eight Baby Calendar cards and the Teste dashboard has no card errors
- [x] 2.3 Run `openspec validate remove-recent-entries-card --strict`
