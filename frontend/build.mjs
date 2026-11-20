// Bundle the cards into one module served by the integration.
import { build } from "esbuild";
import { readFileSync } from "node:fs";

const lit = readFileSync(new URL("./node_modules/lit/LICENSE", import.meta.url), "utf8");

await build({
  entryPoints: ["src/index.ts"],
  bundle: true,
  format: "esm",
  target: "es2022",
  minify: true,
  legalComments: "none",
  outfile: "../custom_components/baby_calendar/frontend/baby-calendar-cards.js",
  banner: {
    js:
      "/*! Baby Calendar cards. MIT licence. https://github.com/mpadinhabrandao/ha-baby-calendar\n" +
      " * Bundles Lit (https://lit.dev), BSD-3-Clause:\n" +
      lit.split("\n").map((line) => ` * ${line}`.trimEnd()).join("\n") +
      "\n */",
  },
});
