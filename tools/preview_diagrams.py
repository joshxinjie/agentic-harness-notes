# Usage: python3 tools/preview_diagrams.py out.png diagrams/a.svg [...]  -> PNG of the SVGs as <img> on a dark page at phone width (390px), to check legibility.
import sys, asyncio, pathlib
from playwright.async_api import async_playwright
async def main():
    out, files = sys.argv[1], sys.argv[2:]
    html = "<body style='background:#0d1117;margin:0;padding:16px;width:390px'>" + "".join(
        f"<p style='color:#aaa;font:12px sans-serif'>{pathlib.Path(f).name}</p><img src='file://{pathlib.Path(f).resolve()}' style='max-width:100%'>" for f in files) + "</body>"
    p = pathlib.Path(out).with_suffix('.html'); p.write_text(html)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = await b.new_page(viewport={"width": 422, "height": 800}, device_scale_factor=2)
        await pg.goto(f"file://{p.resolve()}"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=out, full_page=True); await b.close()
asyncio.run(main())
