// Renders each card in Chromium against a fake Home Assistant and checks
// what it shows and which services it calls. Screenshots go to
// e2e/screenshots (not committed) for a look by eye.

import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const BUNDLE = fileURLToPath(
  new URL("../../custom_components/baby_calendar/frontend/baby-calendar-cards.js", import.meta.url),
);
const SHOTS = fileURLToPath(new URL("./screenshots/", import.meta.url));
mkdirSync(SHOTS, { recursive: true });

const NOW = Date.parse("2026-11-20T03:40:00Z");
const iso = (minutesBefore) => new Date(NOW - minutesBefore * 60_000).toISOString();

const BABY = {
  entry_id: "entry1",
  device_id: "dev1",
  name: "Teste",
  trackers: ["diaper", "bottle", "breastfeeding", "sleep", "solids", "pumping", "weight", "length", "temperature"],
  medications: [
    { id: "m1", name: "Vitamina D", dose: "1 gota", entities: { take: "button.vit_take", due: "binary_sensor.vit_due", last_dose: "sensor.vit_last" } },
    { id: "m2", name: "Ferro", dose: null, entities: { take: "button.fe_take", last_dose: "sensor.fe_last" } },
  ],
  entities: {
    stool_prompt: "binary_sensor.stool_prompt",
    stool_normal: "button.stool_normal",
    stool_soft: "button.stool_soft",
    stool_hard: "button.stool_hard",
    stool_diarrhea: "button.stool_diarrhea",
    bottle_amount: "number.bottle_amount",
    bottle_content: "select.bottle_content",
    breastfeeding_timer: "switch.bf_timer",
    breastfeeding_last: "sensor.bf_last",
    sleep_timer: "switch.sleep_timer",
    awake_since: "sensor.awake_since",
    last_feed: "sensor.last_feed",
    diaper_last: "sensor.diaper_last",
    diaper_changes_today: "sensor.diaper_changes_today",
    diaper_wet_today: "sensor.diaper_wet_today",
    diaper_dirty_today: "sensor.diaper_dirty_today",
    bottle_count_today: "sensor.bottle_count_today",
    bottle_ml_today: "sensor.bottle_ml_today",
    breastfeeding_feeds_today: "sensor.bf_feeds_today",
    breastfeeding_duration_today: "sensor.bf_duration_today",
    sleep_count_today: "sensor.sleep_count_today",
    sleep_duration_today: "sensor.sleep_duration_today",
    solids_count_today: "sensor.solids_count_today",
    pumping_count_today: "sensor.pumping_count_today",
    pumping_ml_today: "sensor.pumping_ml_today",
  },
};

const STATES = {
  "binary_sensor.stool_prompt": { state: "off", attributes: {} },
  "number.bottle_amount": { state: "90", attributes: { max: 500 } },
  "select.bottle_content": { state: "formula", attributes: {} },
  "switch.bf_timer": { state: "off", attributes: { started_at: null } },
  "sensor.bf_last": {
    state: iso(148),
    attributes: {
      side: "right",
      in_progress: false,
      feed: [
        { side: "left", start: iso(148), end: iso(136) },
        { side: "right", start: iso(131), end: iso(123) },
      ],
    },
  },
  "switch.sleep_timer": { state: "off", attributes: { started_at: null } },
  "sensor.awake_since": { state: iso(65), attributes: {} },
  "sensor.last_feed": { state: iso(130), attributes: {} },
  "sensor.diaper_last": { state: iso(40), attributes: {} },
  "sensor.diaper_changes_today": { state: "6", attributes: {} },
  "sensor.diaper_wet_today": { state: "4", attributes: {} },
  "sensor.diaper_dirty_today": { state: "3", attributes: {} },
  "sensor.bottle_count_today": { state: "4", attributes: {} },
  "sensor.bottle_ml_today": { state: "420.0", attributes: {} },
  "sensor.bf_feeds_today": { state: "3", attributes: {} },
  "sensor.bf_duration_today": { state: "45.0", attributes: {} },
  "sensor.sleep_count_today": { state: "5", attributes: {} },
  "sensor.sleep_duration_today": { state: "560.0", attributes: {} },
  "sensor.solids_count_today": { state: "1", attributes: {} },
  "sensor.pumping_count_today": { state: "2", attributes: {} },
  "sensor.pumping_ml_today": { state: "140.0", attributes: {} },
  "binary_sensor.vit_due": { state: "off", attributes: {} },
};

// Runs in the page: a fake hass and helpers to mount and drive a card.
function pageSetup({ baby, states, now }) {
  const realNow = Date.now;
  const offset = now - realNow.call(Date);
  Date.now = () => realNow.call(Date) + offset;
  const RealDate = Date;
  // eslint-disable-next-line no-global-assign
  Date = class extends RealDate {
    constructor(...args) {
      super(...(args.length ? args : [RealDate.now()]));
    }
    static now() {
      return RealDate.now();
    }
  };

  customElements.define(
    "ha-card",
    class extends HTMLElement {
      connectedCallback() {
        this.style.display = "block";
        this.style.background = "var(--ha-card-background)";
        this.style.borderRadius = "var(--ha-card-border-radius)";
      }
    },
  );

  window.calls = [];
  window.failNext = null;
  window.responses = {};
  window.states = Object.fromEntries(
    Object.entries(states).map(([id, s]) => [id, { entity_id: id, last_changed: s.state, ...s }]),
  );
  let counter = 0;
  const connection = {
    subscribeMessage(callback) {
      setTimeout(() => callback({ babies: [baby] }), 0);
      return Promise.resolve(() => Promise.resolve());
    },
    sendMessagePromise(message) {
      window.calls.push(message);
      if (window.failNext) {
        const error = window.failNext;
        window.failNext = null;
        return Promise.reject({ code: "service_validation_error", message: error });
      }
      const key = `${message.domain}.${message.service}`;
      const response = window.responses[key] ?? { event_id: `event${++counter}` };
      return Promise.resolve({ context: {}, response });
    },
  };
  window.makeHass = (language) => ({ states: window.states, connection, locale: { language } });
  window.setState = (id, state, attributes) => {
    window.states = { ...window.states, [id]: { entity_id: id, state, attributes, last_changed: new Date().toISOString() } };
    for (const card of document.querySelectorAll("[data-card]")) {
      card.hass = { ...card.hass, states: window.states };
    }
  };
  window.mount = (type, config = {}, language = "pt") => {
    const card = document.createElement(type);
    card.setAttribute("data-card", "");
    card.setConfig({ type: `custom:${type}`, baby: "dev1", ...config });
    card.hass = window.makeHass(language);
    document.getElementById("cards").append(card);
    return card;
  };
}

const THEMES = {
  light: { bg: "#f0f2f5", card: "#ffffff", text: "#1c1c1e", secondary: "#5f6368", divider: "rgba(0,0,0,0.12)" },
  dark: { bg: "#111318", card: "#1c1f26", text: "#eef0f4", secondary: "#a9afbc", divider: "rgba(255,255,255,0.12)" },
};

let failures = 0;
function check(name, condition, detail = "") {
  if (condition) {
    console.log(`  ok  ${name}`);
  } else {
    failures += 1;
    console.log(`  FAIL ${name} ${detail}`);
  }
}

async function newPage(browser, theme = "light") {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const c = THEMES[theme];
  await page.setContent(`<!doctype html><html><head><style>
    body { margin: 0; padding: 16px; background: ${c.bg}; font-family: system-ui, sans-serif;
      --ha-card-background: ${c.card}; --card-background-color: ${c.card};
      --primary-text-color: ${c.text}; --secondary-text-color: ${c.secondary};
      --divider-color: ${c.divider}; --ha-card-border-radius: 12px; --primary-color: #03a9f4;
      --error-color: #db4437; color: ${c.text}; }
    #cards { display: flex; flex-direction: column; gap: 12px; }
  </style></head><body><div id="cards"></div></body></html>`);
  await page.evaluate(pageSetup, { baby: BABY, states: STATES, now: NOW });
  await page.addScriptTag({ path: BUNDLE, type: "module" });
  await page.waitForFunction(() => customElements.get("baby-calendar-diaper-card"));
  return page;
}

const text = (page, selector) =>
  page.evaluate((s) => {
    const el = document.querySelector(s);
    return el ? el.shadowRoot.textContent.replace(/\s+/g, " ").trim() : "";
  }, selector);
const tap = (page, card, label) =>
  page.evaluate(
    ({ card, label }) => {
      const root = document.querySelector(card).shadowRoot;
      const button = [...root.querySelectorAll("button")].find(
        (b) => b.textContent.replace(/\s+/g, " ").trim().startsWith(label) || b.getAttribute("aria-label") === label,
      );
      if (!button) throw new Error(`no button ${label}`);
      button.click();
    },
    { card, label },
  );
const calls = (page) => page.evaluate(() => window.calls);
const settle = (page) => page.waitForTimeout(80);

const browser = await chromium.launch();
try {
  // ------------------------------------------------------------ diapers
  console.log("Diapers");
  let page = await newPage(browser);
  await page.evaluate(() => window.mount("baby-calendar-diaper-card"));
  await settle(page);
  let shown = await text(page, "baby-calendar-diaper-card");
  check("Portuguese buttons", shown.includes("Xixi") && shown.includes("Cocó") && shown.includes("Os dois"), shown);
  await tap(page, "baby-calendar-diaper-card", "Xixi");
  await tap(page, "baby-calendar-diaper-card", "Xixi");
  await settle(page);
  let made = await calls(page);
  check("one call for a double tap", made.length === 1, JSON.stringify(made));
  check("log_diaper wet", made[0]?.service === "log_diaper" && made[0].service_data.content === "wet" && !made[0].service_data.time);
  shown = await text(page, "baby-calendar-diaper-card");
  check("undo bar", shown.includes("Registado: fralda com xixi"), shown);
  await tap(page, "baby-calendar-diaper-card", "Desfazer");
  await settle(page);
  made = await calls(page);
  check("undo deletes the entry", made[1]?.service === "delete_event" && made[1].service_data.event_id === "event1");
  await page.screenshot({ path: `${SHOTS}diaper-light.png` });

  await page.evaluate(() => {
    const card = document.querySelector("baby-calendar-diaper-card");
    const select = card.shadowRoot.querySelector(".chip select");
    select.value = "15";
    select.dispatchEvent(new Event("change"));
  });
  await settle(page);
  await tap(page, "baby-calendar-diaper-card", "Cocó");
  await page.evaluate(() => window.setState("binary_sensor.stool_prompt", "on", {}));
  await settle(page);
  made = await calls(page);
  const dirty = made[2];
  const minutes = (Date.parse("2026-11-20T03:40:00Z") - Date.parse(dirty?.service_data.time)) / 60000;
  check("chip sends 15 minutes ago", Math.abs(minutes - 15) < 1, JSON.stringify(dirty));
  check("chip back to now", await page.evaluate(() => document.querySelector("baby-calendar-diaper-card").shadowRoot.querySelector(".chip select").value === "0"));
  shown = await text(page, "baby-calendar-diaper-card");
  check("stool question", shown.includes("Como era?"), shown);
  await page.screenshot({ path: `${SHOTS}diaper-stool.png` });
  await tap(page, "baby-calendar-diaper-card", "Mole");
  await settle(page);
  made = await calls(page);
  check("stool soft pressed", made[3]?.domain === "button" && made[3].service_data.entity_id === "button.stool_soft");

  await page.evaluate(() => { window.failNext = "Home Assistant is unreachable"; });
  await tap(page, "baby-calendar-diaper-card", "Os dois");
  await settle(page);
  shown = await text(page, "baby-calendar-diaper-card");
  check("error shown", shown.includes("Não ficou registado: Home Assistant is unreachable"), shown);
  await page.close();

  // ------------------------------------------------------------- bottle
  console.log("Bottle");
  page = await newPage(browser, "dark");
  await page.evaluate(() => window.mount("baby-calendar-bottle-card"));
  await settle(page);
  shown = await text(page, "baby-calendar-bottle-card");
  check("amount shown as a value", shown.includes("90 ml") && shown.includes("Registar biberão"), shown);
  await tap(page, "baby-calendar-bottle-card", "Mais 10 ml");
  await settle(page);
  await tap(page, "baby-calendar-bottle-card", "Mais 10 ml");
  await settle(page);
  await tap(page, "baby-calendar-bottle-card", "Leite materno");
  await settle(page);
  shown = await text(page, "baby-calendar-bottle-card");
  check("amount raised twice", shown.includes("110 ml"), shown);
  made = await calls(page);
  check("adjusting records nothing", !made.some((m) => m.service === "log_bottle"), JSON.stringify(made));
  await page.evaluate(() => window.setState("select.bottle_content", "breast_milk", {}));
  await settle(page);
  await tap(page, "baby-calendar-bottle-card", "Registar biberão");
  await settle(page);
  made = await calls(page);
  check("set_value 100 then 110", made[0]?.service_data.value === 100 && made[1]?.service_data.value === 110, JSON.stringify(made));
  check("content set", made[2]?.service === "select_option" && made[2].service_data.option === "breast_milk", JSON.stringify(made[2]));
  check("log_bottle 110 breast milk", made[3]?.service === "log_bottle" && made[3].service_data.amount === 110 && made[3].service_data.content === "breast_milk", JSON.stringify(made[3]));
  await page.screenshot({ path: `${SHOTS}bottle-dark.png` });
  await page.close();

  // ------------------------------------------------------ breastfeeding
  console.log("Breastfeeding");
  page = await newPage(browser);
  await page.evaluate(() => window.mount("baby-calendar-breastfeeding-card"));
  await settle(page);
  shown = await text(page, "baby-calendar-breastfeeding-card");
  check("last feed line", shown.includes("Esquerda 12 min · pausa 5 min · Direita 8 min · 20 min no total"), shown);
  check("no side suggested", !shown.includes("sugest"), shown);
  check("idle buttons say start", shown.includes("Começar esquerda") && shown.includes("Começar direita"), shown);
  await tap(page, "baby-calendar-breastfeeding-card", "Começar esquerda");
  await settle(page);
  made = await calls(page);
  check("start left", made[0]?.service === "start_breastfeeding" && made[0].service_data.side === "left");
  await page.evaluate((started) => {
    window.setState("switch.bf_timer", "on", { started_at: started });
    window.setState("sensor.bf_last", started, {
      side: "left",
      in_progress: true,
      feed: [{ side: "left", start: started, end: null }],
    });
  }, iso(12.67));
  await settle(page);
  shown = await text(page, "baby-calendar-breastfeeding-card");
  check("running side shows stop and time", /Parar · esquerda 12:4\d/.test(shown), shown);
  check("running feed heading", shown.includes("Mamada desde as") && shown.includes("Esquerda a decorrer"), shown);
  await page.screenshot({ path: `${SHOTS}breastfeeding-running.png` });
  await new Promise((resolve) => setTimeout(resolve, 3100));
  await tap(page, "baby-calendar-breastfeeding-card", "Começar direita");
  await page.waitForTimeout(150);
  made = await calls(page);
  check("side change stops then starts right", made[1]?.service === "stop_breastfeeding" && made[2]?.service === "start_breastfeeding" && made[2].service_data.side === "right", JSON.stringify(made));
  await page.close();

  // -------------------------------------------------------------- sleep
  console.log("Sleep");
  page = await newPage(browser, "dark");
  await page.evaluate(() => {
    window.states["switch.sleep_timer"] = { entity_id: "switch.sleep_timer", state: "on", attributes: { started_at: new Date(Date.now() - 80 * 60000).toISOString() } };
    window.mount("baby-calendar-sleep-card");
  });
  await settle(page);
  shown = await text(page, "baby-calendar-sleep-card");
  check("woke up with time", /Acordou 1:20:\d\d/.test(shown), shown);
  await tap(page, "baby-calendar-sleep-card", "Acordou");
  await settle(page);
  made = await calls(page);
  check("stop_sleep", made[0]?.service === "stop_sleep");
  await page.close();

  // -------------------------------------------------------- medications
  console.log("Medications");
  page = await newPage(browser);
  await page.evaluate(() => window.mount("baby-calendar-medication-card"));
  await settle(page);
  shown = await text(page, "baby-calendar-medication-card");
  check("nothing due", shown.includes("Nenhuma dose por dar"), shown);
  await page.evaluate(() => window.setState("binary_sensor.vit_due", "on", {}));
  await settle(page);
  shown = await text(page, "baby-calendar-medication-card");
  check("due dose shown", shown.includes("Vitamina D · 1 gota") && !shown.includes("Ferro"), shown);
  await page.screenshot({ path: `${SHOTS}medication-due.png` });
  await tap(page, "baby-calendar-medication-card", "Dado");
  await settle(page);
  made = await calls(page);
  check("log_medication", made[0]?.service === "log_medication" && made[0].service_data.medication === "Vitamina D");
  await page.evaluate(() => window.mount("baby-calendar-medication-card", { show_all: true }));
  await settle(page);
  shown = await page.evaluate(() => document.querySelectorAll("baby-calendar-medication-card")[1].shadowRoot.textContent);
  check("show all lists Ferro", shown.includes("Ferro"));
  await page.close();

  // ---------------------------------------------------- summary, today
  console.log("Summary and today");
  page = await newPage(browser);
  await page.evaluate(() => {
    window.mount("baby-calendar-summary-card");
    window.mount("baby-calendar-today-card");
  });
  await settle(page);
  shown = await text(page, "baby-calendar-summary-card");
  check("ate 2 h 10 min ago", shown.includes("Comeu há 2 h 10 min"), shown);
  check("diaper and awake", shown.includes("Fralda há 40 min") && shown.includes("Acordado há 1 h 5 min"), shown);
  shown = await text(page, "baby-calendar-today-card");
  check("today totals", shown.includes("Biberões 4 420 ml") && shown.includes("4 xixi · 3 cocó") && shown.includes("9 h 20 min"), shown);
  await page.screenshot({ path: `${SHOTS}summary-today.png` });
  await page.close();

  // ------------------------------------------------------ other entries
  console.log("Other entries");
  page = await newPage(browser);
  await page.evaluate(() => window.mount("baby-calendar-entry-card"));
  await settle(page);
  const fill = (name, value) =>
    page.evaluate(
      ({ name, value }) => {
        const input = document.querySelector("baby-calendar-entry-card").shadowRoot.querySelector(`[name=${name}]`);
        input.value = value;
        input.dispatchEvent(new Event(input.tagName === "SELECT" ? "change" : "input"));
      },
      { name, value },
    );
  await tap(page, "baby-calendar-entry-card", "Peso");
  await settle(page);
  await page.evaluate(() => { window.failNext = "Indica um valor de 300 a 30000 g."; });
  await fill("value", "3,45");
  await tap(page, "baby-calendar-entry-card", "Guardar");
  await settle(page);
  shown = await text(page, "baby-calendar-entry-card");
  check("range shown, form kept", shown.includes("300 a 30000 g") && shown.includes("Guardar"), shown);
  await fill("value", "3450");
  await new Promise((resolve) => setTimeout(resolve, 3100));
  await tap(page, "baby-calendar-entry-card", "Guardar");
  await settle(page);
  made = await calls(page);
  check("log_weight 3450", made[1]?.service === "log_weight" && made[1].service_data.value === 3450, JSON.stringify(made));
  for (const typed of ["36.8", "36,8"]) {
    await new Promise((resolve) => setTimeout(resolve, 3100));
    await tap(page, "baby-calendar-entry-card", "Temperatura");
    await settle(page);
    const field = page.locator("baby-calendar-entry-card input[name=value]");
    await field.click();
    await field.pressSequentially(typed);
    await settle(page);
    check(`typed ${typed} kept`, (await field.inputValue()) === typed, await field.inputValue());
    await tap(page, "baby-calendar-entry-card", "Guardar");
    await settle(page);
    made = await calls(page);
    const last = made[made.length - 1];
    check(`log_temperature 36.8 from ${typed}`, last?.service === "log_temperature" && last.service_data.value === 36.8, JSON.stringify(last));
  }
  made = await calls(page);
  const before = made.length;
  await tap(page, "baby-calendar-entry-card", "Extração");
  await settle(page);
  await fill("amount", "80");
  await fill("side", "both");
  await tap(page, "baby-calendar-entry-card", "Guardar");
  await settle(page);
  made = await calls(page);
  check("log_pumping 80 both", made[before]?.service === "log_pumping" && made[before].service_data.amount === 80 && made[before].service_data.side === "both", JSON.stringify(made[before]));
  await tap(page, "baby-calendar-entry-card", "Medicamento");
  await settle(page);
  await fill("medication", "Ferro");
  await tap(page, "baby-calendar-entry-card", "Guardar");
  await settle(page);
  made = await calls(page);
  check("log_medication Ferro", made[before + 1]?.service === "log_medication" && made[before + 1].service_data.medication === "Ferro", JSON.stringify(made[before + 1]));
  await tap(page, "baby-calendar-entry-card", "Peso");
  await settle(page);
  await page.screenshot({ path: `${SHOTS}entry-form.png` });
  await page.close();

  // ----------------------------------------------------- recent entries
  console.log("Recent entries");
  page = await newPage(browser, "dark");
  await page.evaluate((events) => {
    window.responses["baby_calendar.list_events"] = { events };
    window.mount("baby-calendar-recent-card");
  }, [
    { event_id: "a", tracker: "diaper", time: iso(30), content: "dirty", stool: "soft" },
    { event_id: "b", tracker: "bottle", time: iso(5), amount: 90, content: "formula" },
    { event_id: "c", tracker: "breastfeeding", time: iso(60), side: "left", duration: 840, in_progress: false },
  ]);
  await settle(page);
  shown = await text(page, "baby-calendar-recent-card");
  const order = ["biberão 90 ml", "fralda com cocó (mole)", "mama esquerda · 14 min"].map((s) => shown.indexOf(s));
  check("newest first", order.every((i, k) => i >= 0 && (k === 0 || i > order[k - 1])), shown);
  await page.screenshot({ path: `${SHOTS}recent-dark.png` });
  await page.close();

  // ------------------------------------------------- baby and trackers
  console.log("Baby and trackers");
  page = await newPage(browser);
  await page.evaluate(() => {
    window.mount("baby-calendar-diaper-card", { baby: "gone" });
    window.mount("baby-calendar-diaper-card", {}, "en");
  });
  await settle(page);
  shown = await page.evaluate(() => [...document.querySelectorAll("baby-calendar-diaper-card")].map((c) => c.shadowRoot.textContent.replace(/\s+/g, " ")));
  check("baby not found", shown[0].includes("Bebé não encontrado"), shown[0]);
  check("English buttons", shown[1].includes("Wet") && shown[1].includes("Dirty") && shown[1].includes("Both"), shown[1]);
  await page.close();
} finally {
  await browser.close();
}

if (failures) {
  console.log(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nAll checks passed");
