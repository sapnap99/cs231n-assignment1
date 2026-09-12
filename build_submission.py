"""Export executed notebooks with Chromium and collect the assignment code."""
from pathlib import Path
import asyncio
import json
import zipfile
import nbformat
from pypdf import PdfWriter
from nbconvert import HTMLExporter
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent
NAMES = ['knn', 'softmax', 'two_layer_net', 'features', 'FullyConnectedNets']
OUTPUT = ROOT / 'output' / 'pdf'
TEMP = ROOT / 'tmp' / 'pdfs'
CSS = '''<style>
@page {size: A4; margin: 12mm 12mm 15mm;}
html, body {background:white!important; font-size:10pt!important;}
.jp-Notebook {padding:0!important;}
.jp-Cell {padding:3px 0!important;}
.jp-InputPrompt,.jp-OutputPrompt {min-width:42px!important; font-size:8pt!important;}
pre,code {font-size:8pt!important; line-height:1.3!important;}
pre {white-space:pre-wrap!important; overflow-wrap:anywhere!important;}
.jp-OutputArea-output,.jp-OutputArea-child,.jp-InputArea-editor {overflow:visible!important; max-height:none!important;}
.jp-OutputArea-output img {max-width:100%!important; max-height:235mm!important; object-fit:contain;}
.jp-RenderedImage {break-inside:avoid;}
h1,h2,h3,h4 {break-after:avoid;}
.jp-Cell {break-inside:auto!important;}
.jp-RenderedHTMLCommon p {orphans:3; widows:3;}
</style>'''


async def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    exporter = HTMLExporter(template_name='lab')
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        for name in NAMES:
            notebook = nbformat.read(ROOT / f'{name}.ipynb', as_version=4)
            code = [c for c in notebook.cells if c.cell_type == 'code' and c.source.strip()]
            assert all(c.execution_count is not None for c in code), name
            assert not any(o.output_type == 'error' for c in code for o in c.outputs), name
            html, _ = exporter.from_notebook_node(notebook)
            html = html.replace('</head>', CSS + '</head>')
            html_path = TEMP / f'{name}.html'
            html_path.write_text(html, encoding='utf-8')
            await page.goto(html_path.as_uri(), wait_until='load', timeout=120000)
            await page.wait_for_function('window.MathJax && (MathJax.Hub || MathJax.startup)', timeout=60000)
            await page.evaluate('''async () => {
                if (MathJax.Hub) await new Promise(resolve => MathJax.Hub.Queue(resolve));
                else await MathJax.startup.promise;
                await document.fonts.ready;
            }''')
            await page.emulate_media(media='print')
            await page.pdf(path=str(TEMP / f'{name}.pdf'), format='A4',
                           print_background=True, prefer_css_page_size=True,
                           display_header_footer=True,
                           header_template='<span></span>',
                           footer_template=f'<div style="font-size:8px;width:100%;text-align:center">Assignment 1 / {name} - <span class="pageNumber"></span> / <span class="totalPages"></span></div>')
            print('Rendered:', name, flush=True)
        await browser.close()
    writer = PdfWriter()
    for name in NAMES:
        writer.append(TEMP / f'{name}.pdf', outline_item=name)
    writer.add_metadata({'/Title': 'Assignment 1 - Completed Notebooks'})
    with (OUTPUT / 'a1_inline_submission.pdf').open('wb') as stream:
        writer.write(stream)
    print('Merged submission PDF created.', flush=True)
    files = [ROOT / f'{name}.ipynb' for name in NAMES]
    files += sorted((ROOT / 'cs231n').rglob('*.py'))
    files += sorted((ROOT / 'cs231n' / 'saved').glob('*'))
    files += [ROOT / 'local_setup.py', ROOT / 'requirements-local.txt']
    with zipfile.ZipFile(OUTPUT / 'a1_code_submission.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            if path.is_file():
                archive.write(path, path.relative_to(ROOT).as_posix())
    print('Code ZIP created.', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
