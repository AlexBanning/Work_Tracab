import pandas as pd
from fpdf import FPDF

# Generating PDFs
# Create a sample DataFrame
data = {
    'Name': ['John', 'Anna', 'Peter', 'Linda'],
    'Age': [28, 24, 35, 29],
    'City': ['New York', 'Paris', 'London', 'Sydney']
}
df = pd.DataFrame(pdf_frontpage)
# Apply custom styling to the DataFrame
styled_df = df.style.set_table_styles([{
        'selector': 'th',
        'props': [('background-color', '#f2f2f2'),  # Header background color
                  ('color', 'black'),              # Header text color
                  ('border', '1px solid #dddddd'), # Header border
                  ('padding', '8px'),              # Header padding
                  ('font-weight', 'bold')]         # Header font weight
    }, {
        'selector': 'td',
        'props': [('border', '1px solid #dddddd'), # Cell border
                  ('padding', '8px')]              # Cell padding
    }])

# Extract underlying DataFrame
df_data = df.values.tolist()

# Convert styled DataFrame to list of lists
table_data = [styled_df.columns.tolist()] + df_data

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Add title
pdf.cell(200, 10, txt="Styled DataFrame PDF", ln=True, align="C")
pdf.ln(10)

# Get maximum width for each column
column_widths = []
for col in table_data[0]:
    max_width = max([pdf.get_string_width(str(row)) for row in col])
    column_widths.append(max_width + 60)  # Add some padding

# Set font size for cell content
pdf.set_font("Arial", size=10)

# Add table header
for item, width in zip(table_data[0], column_widths):
    pdf.cell(width, 10, str(item), border=1, ln=False, align="C", fill=True)
pdf.ln()

# Add table rows
for row in table_data[1:]:
    for item, width in zip(row, column_widths):
        pdf.cell(width, 10, str(item), border=1, ln=False, align="C")
    pdf.ln()

# Save the PDF to a file
pdf.output("styled_dataframe_pdf_fpdf.pdf")

