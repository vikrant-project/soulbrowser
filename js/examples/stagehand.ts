/**
 * Stagehand + SoulBrowser: AI browser automation with stealth fingerprints.
 *
 * Stagehand handles AI-powered navigation and actions,
 * SoulBrowser handles bot detection.
 *
 * Requires: npm install @browserbasehq/stagehand soulbrowser
 * Set OPENAI_API_KEY for the AI model.
 *
 * Usage:
 *   SOULBROWSER_BINARY_PATH=/path/to/chrome npx tsx examples/stagehand.ts
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { ensureBinary } from "../src/download.js";
import { getDefaultStealthArgs } from "../src/config.js";

const binaryPath = await ensureBinary();
const stealthArgs = getDefaultStealthArgs();

const stagehand = new Stagehand({
  env: "LOCAL",
  localBrowserLaunchOptions: {
    executablePath: binaryPath,
    args: stealthArgs,
    headless: true,
  },
});

await stagehand.init();

const page = stagehand.context.pages()[0];
await page.goto("https://example.com");
console.log(`Stagehand + SoulBrowser: ${await page.title()}`);

await stagehand.close();
