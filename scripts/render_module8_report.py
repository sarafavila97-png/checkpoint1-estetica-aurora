"""Render the evidence-backed M8 report; text-only output is a layout draft."""
import argparse
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image, Spacer
from render_module6_report import markdown_story, paragraph, HEAD, BODY, W, H

R = Path(__file__).resolve().parents[1]

def footer(canvas, document):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#526575'))
    canvas.setFont('Helvetica', 9)
    canvas.drawString(40, 25, 'Sara Adan | Módulo 8 | Supervisión y evaluación observada')
    canvas.drawRightString(W - 40, 25, str(document.page))
    canvas.restoreState()

def render(captures=None):
    source = R / 'submissions/m08/report.md'
    story = markdown_story(source.read_text())
    if captures is None:
        output = R / 'tmp/pdfs/m8-text-layout.pdf'
    else:
        items = json.loads(captures.read_text())
        required = {'manager', 'supervisor', 'parser', 'switch', 'correction', 'escalation'}
        if not required.issubset({item['category'] for item in items}):
            raise ValueError('Missing authentic M8 configuration captures')
        for item in items:
            path = R / item['file']
            if not path.is_file():
                raise FileNotFoundError(path)
            story.extend([PageBreak(), paragraph(item['title'], HEAD), paragraph(item['caption'])])
            width, height = ImageReader(str(path)).getSize()
            scale = min((W - 80) / width, (H - 205) / height)
            story.append(Image(str(path), width=width * scale, height=height * scale))
            story.extend([Spacer(1, 8), paragraph('Captura auténtica: ' + item['file'],
                ParagraphStyle('Caption', parent=BODY, fontSize=9, leading=12))])
        output = R / 'submissions/m08/Checkpoint_Modulo8_Adan_Sara.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(output), pagesize=(W, H), leftMargin=40, rightMargin=40,
        topMargin=40, bottomMargin=45, title='Checkpoint Módulo 8 - Sara Adan',
        author='Sara Adan').build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures', type=Path)
    render(parser.parse_args().captures)
