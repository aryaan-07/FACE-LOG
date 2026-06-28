from fpdf import FPDF # pyright: ignore[reportMissingModuleSource]

# Create PDF object
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Add content
content = """
[PASTE ALL THE SOLUTIONS HERE]
"""

for line in content.split('\n'):
    pdf.cell(200, 10, txt=line, ln=1)

# Save PDF
pdf.output("PPS_Unit3_Solutions.pdf")
print("PDF generated successfully!")