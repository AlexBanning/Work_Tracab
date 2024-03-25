import pandas as pd
from weasyprint import HTML

# Generating PDFs
# Create a sample DataFrame
data = {
    'Name': ['John', 'Anna', 'Peter', 'Linda'],
    'Age': [28, 24, 35, 29],
    'City': ['New York', 'Paris', 'London', 'Sydney']
}
df = pd.DataFrame(data)

# Apply custom styling to the DataFrame
styled_df = df.style.set_table_styles([{
    'selector': 'th',
    'props': [('background-color', '#f2f2f2'),  # Header background color
              ('color', 'black'),  # Header text color
              ('border', '1px solid #dddddd'),  # Header border
              ('padding', '8px'),  # Header padding
              ('font-weight', 'bold')]  # Header font weight
}, {
    'selector': 'td',
    'props': [('border', '1px solid #dddddd'),  # Cell border
              ('padding', '8px')]  # Cell padding
}])

# Convert styled DataFrame to HTML
html = styled_df.to_html()

# Generate PDF from HTML
HTML(string=html).write_pdf("styled_dataframe_pdf.pdf")

