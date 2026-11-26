"""Render the M6 report source and authentic screenshots; never invent evidence."""
import argparse,json,re
from html import escape
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image
R=Path(__file__).resolve().parents[1]
W,H=landscape(A3)
BODY=ParagraphStyle('Body',fontName='Helvetica',fontSize=12,leading=17,spaceAfter=9)
CODE=ParagraphStyle('Code',parent=BODY,fontName='Courier',fontSize=9,leading=13,backColor=colors.HexColor('#f3f5f7'),borderPadding=8,spaceAfter=12)
HEAD=ParagraphStyle('Heading',parent=BODY,fontName='Helvetica-Bold',fontSize=21,leading=26,spaceBefore=15,spaceAfter=12,keepWithNext=True)
SUB=ParagraphStyle('Subheading',parent=HEAD,fontSize=15,leading=20)
def inline(text):
    text=escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text)
    return re.sub(r'\[([^]]+)\]\(([^)]+)\)',lambda m:m[1]+' ('+m[2]+')',text)
def paragraph(text,style=BODY):return Paragraph(inline(text),style)
def markdown_story(text):
    lines=text.splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i];i+=1
        if not line.strip():continue
        if line.startswith('```'):
            block=[]
            while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
            i+=1
            # Paragraph wraps long expressions instead of clipping a preformatted line.
            story.append(Paragraph(escape('\n'.join(block)).replace('\n','<br/>'),CODE));continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].startswith('|'):rows.append(lines[i]);i+=1
            cells=[[paragraph(x.strip()) for x in row.strip('|').split('|')] for row in rows if not re.fullmatch(r'[| :\-]+',row)]
            count=len(cells[0]);t=Table(cells,colWidths=[(W-80)/count]*count,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eef4')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#bac7d2')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.extend([t,Spacer(1,12)]);continue
        if line.startswith('### '):story.append(paragraph(line[4:],SUB))
        elif line.startswith('## '):story.append(paragraph(line[3:],HEAD))
        elif line.startswith('# '):story.append(paragraph(line[2:],HEAD))
        elif line.startswith('> '):story.append(paragraph(line[2:],ParagraphStyle('Quote',parent=BODY,leftIndent=16,textColor=colors.HexColor('#193d56'))))
        else:story.append(paragraph(line))
    return story
def footer(c,doc):
    c.saveState();c.setFillColor(colors.HexColor('#526575'));c.setFont('Helvetica',9)
    c.drawString(40,25,'Sara Adan | Módulo 6 | Configuración y resultados con límites explícitos')
    c.drawRightString(W-40,25,str(doc.page));c.restoreState()
def render(manifest):
    items=json.loads(manifest.read_text())
    required={'ingress','transcription','whisper','guard','agent','tts','delivery','settings'}
    assert required.issubset({x['category'] for x in items}), 'Required authentic screenshot category missing'
    for item in items:assert (R/item['file']).is_file(),item['file']
    story=markdown_story((R/'submissions/m06/report.md').read_text())
    for item in items:
        story.extend([PageBreak(),paragraph(item['title'],HEAD),paragraph(item['caption'])])
        path=R/item['file'];iw,ih=ImageReader(str(path)).getSize()
        scale=min((W-80)/iw,(H-205)/ih)
        story.append(Image(str(path),width=iw*scale,height=ih*scale))
        story.append(Spacer(1,8));story.append(paragraph('Captura auténtica: '+item['file'],ParagraphStyle('Caption',parent=BODY,fontSize=9,leading=12)))
    out=R/'submissions/m06/PreEntrega_Modulo6_SaraAdan.pdf'
    SimpleDocTemplate(str(out),pagesize=(W,H),leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=45,title='PreEntrega Módulo 6 - Sara Adan',author='Sara Adan').build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--captures',type=Path,required=True)
    render(parser.parse_args().captures)
