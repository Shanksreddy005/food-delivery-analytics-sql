import os
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Paths
md_path = os.path.abspath('c:/Users/ShaShank/OneDrive/Desktop/food-delivery-sql-analysis/case_study/Executive_Case_Study.md')
pdf_path = os.path.abspath('c:/Users/ShaShank/OneDrive/Desktop/food-delivery-sql-analysis/case_study/Executive_Case_Study.pdf')
image_path = os.path.abspath('c:/Users/ShaShank/OneDrive/Desktop/food-delivery-sql-analysis/case_study/executive_summary.png')

# Read markdown content
with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

styles = getSampleStyleSheet()
story = []

# Add executive summary image on first page
if os.path.exists(image_path):
    img = Image(image_path, width=400, height=200)
    story.append(img)
    story.append(Spacer(1, 12))

# Simple conversion: treat lines starting with # as headings, else paragraphs
for line in lines:
    stripped = line.strip('\n')
    if stripped.startswith('### '):
        story.append(Paragraph(stripped[4:], styles['Heading3']))
    elif stripped.startswith('## '):
        story.append(Paragraph(stripped[3:], styles['Heading2']))
    elif stripped.startswith('# '):
        story.append(Paragraph(stripped[2:], styles['Heading1']))
    elif stripped:
        story.append(Paragraph(stripped, styles['BodyText']))
    story.append(Spacer(1, 12))

# Build PDF
doc = SimpleDocTemplate(pdf_path, pagesize=LETTER)
doc.build(story)
print('PDF generated at', pdf_path)
