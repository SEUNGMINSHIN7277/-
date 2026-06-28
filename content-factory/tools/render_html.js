#!/usr/bin/env node
// Render an HTML file (or stdin) to a PNG at an exact pixel size using the
// Chromium that ships with Playwright. Used to compose the call-UI frame.
//
// Usage:
//   node render_html.js --html <file> --out <png> --width 1080 --height 1920 [--selector "#stage"]
//
// Falls back to the global playwright install if a local one isn't present.

function loadPlaywright() {
  try { return require("playwright"); } catch (_) {}
  const { execSync } = require("child_process");
  try {
    const groot = execSync("npm root -g").toString().trim();
    return require(require("path").join(groot, "playwright"));
  } catch (e) {
    console.error("Could not load playwright:", e.message);
    process.exit(2);
  }
}

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

(async () => {
  const { chromium } = loadPlaywright();
  const htmlPath = arg("html");
  const out = arg("out", "out.png");
  const width = parseInt(arg("width", "1080"), 10);
  const height = parseInt(arg("height", "1920"), 10);
  const selector = arg("selector", null);
  const transparent = process.argv.includes("--transparent");

  const browser = await chromium.launch({ args: ["--no-sandbox", "--font-render-hinting=none"] });
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 2, // crisp text / edges
  });
  const fs = require("fs");
  const html = fs.readFileSync(htmlPath, "utf8");
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(120);

  if (selector) {
    const el = await page.$(selector);
    await el.screenshot({ path: out, omitBackground: transparent });
  } else {
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width, height }, omitBackground: transparent });
  }
  await browser.close();
  console.log("wrote", out);
})().catch((e) => { console.error(e); process.exit(1); });
