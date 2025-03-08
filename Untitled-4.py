import streamlit as st
import pandas as pd
import json
import io
from fpdf import FPDF  # PDF generation library

# Streamlit Page Config
st.set_page_config(page_title="Universal Data Sweeper", page_icon="🧹")

# App Title
st.title("🧹 Universal Data Sweeper")
st.write("Upload a CSV, Excel, TXT, JSON, or Word file to clean it.")

# File Upload
uploaded_file = st.file_uploader("📂 Upload Your File", type=["csv", "xlsx", "txt", "json", "docx"])

# Data Cleaning Function
def clean_text(text):
    """Removes special characters and trims whitespace."""
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()

def clean_data(df):
    """Removes duplicates, empty rows, and cleans text."""
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df = df.applymap(lambda x: clean_text(str(x)) if isinstance(x, str) else x)
    return df

def generate_pdf(dataframe):
    """Generates a PDF file from a cleaned DataFrame."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Cleaned Data Report", ln=True, align="C")
    pdf.ln(10)

    for index, row in dataframe.iterrows():
        row_data = " | ".join(str(value) for value in row)
        pdf.multi_cell(0, 10, row_data)
        pdf.ln(5)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output, "F")
    pdf_output.seek(0)
    return pdf_output

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1]
        df = None

        # Read the Uploaded File
        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)
        elif file_type == "txt":
            text_data = uploaded_file.getvalue().decode("utf-8").splitlines()
            df = pd.DataFrame(text_data, columns=["Text"])
        elif file_type == "json":
            json_data = json.load(uploaded_file)
            df = pd.DataFrame(json_data)
        elif file_type == "docx":
            from docx import Document  # Imported here to avoid unnecessary dependency issues
            doc = Document(uploaded_file)
            text_data = [para.text for para in doc.paragraphs if para.text.strip()]
            df = pd.DataFrame(text_data, columns=["Text"])

        st.subheader("📊 Original Data Preview")
        st.dataframe(df.head())

        # Clean Data
        cleaned_df = clean_data(df)
        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(cleaned_df.head())

        # File Output
        output = io.BytesIO()
        file_name = f"cleaned_data.{file_type}"
        mime_type = "text/csv"

        if file_type == "csv":
            cleaned_df.to_csv(output, index=False)
            mime_type = "text/csv"
        elif file_type == "xlsx":
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                cleaned_df.to_excel(writer, index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_type == "json":
            json.dump(cleaned_df.to_dict(orient="records"), output, indent=4)
            mime_type = "application/json"
        elif file_type == "txt":
            output.write("\n".join(cleaned_df["Text"]).encode("utf-8"))
            mime_type = "text/plain"
            file_name = "cleaned_data.txt"
        elif file_type == "pdf":
            output = generate_pdf(cleaned_df)
            mime_type = "application/pdf"
            file_name = "cleaned_data.pdf"

        output.seek(0)

        # Download Button
        st.download_button(
            label="⬇️ Download Cleaned File",
            data=output.getvalue(),
            file_name=file_name,
            mime=mime_type
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.write("✨ Built with ❤️ using Streamlit")
