import streamlit as st
import pandas as pd
import json
import io
import PyPDF2
from docx import Document

# Set Page Title
st.set_page_config(page_title="Universal Data Sweeper", page_icon="🧹", layout="centered")

# Title
st.title("🧹 Universal Data Sweeper - Clean Any File!")
st.write("Upload a **CSV, Excel, TXT, JSON, PDF, or Word** file, and we'll clean it for you!")

# File Upload
uploaded_file = st.file_uploader("📂 Upload Your File", type=["csv", "xlsx", "txt", "json", "pdf", "docx"])

# Data Cleaning Function
def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()  # Remove special characters & trim

def clean_data(df):
    df.drop_duplicates(inplace=True)  # Remove Duplicates
    df.dropna(inplace=True)  # Remove Empty Rows
    df = df.applymap(lambda x: clean_text(str(x)) if isinstance(x, str) else x)  # Clean text
    return df

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1]

        # Load & Process Data
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
        elif file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_data = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            df = pd.DataFrame(text_data.split("\n"), columns=["Text"])
        elif file_type == "docx":
            doc = Document(uploaded_file)
            text_data = "\n".join([para.text for para in doc.paragraphs])
            df = pd.DataFrame(text_data.split("\n"), columns=["Text"])

        st.subheader("📊 Original Data Preview")
        st.dataframe(df.head())

        # Clean Data
        cleaned_df = clean_data(df)
        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(cleaned_df.head())

        # Download Cleaned Data
        output = io.BytesIO()
        if file_type in ["csv", "json", "xlsx", "txt"]:
            cleaned_df.to_csv(output, index=False) if file_type == "csv" else None
            cleaned_df.to_excel(output, index=False, engine="openpyxl") if file_type == "xlsx" else None
            cleaned_df.to_json(output, orient="records", indent=4) if file_type == "json" else None
            output.write("\n".join(cleaned_df["Text"]).encode()) if file_type == "txt" else None
            mime_type = "text/csv" if file_type == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_type == "xlsx" else "application/json" if file_type == "json" else "text/plain"
            file_name = f"cleaned_data.{file_type}"
        elif file_type in ["pdf", "docx"]:
            cleaned_text = "\n".join(cleaned_df["Text"])
            output.write(cleaned_text.encode())
            mime_type = "application/pdf" if file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_name = f"cleaned_data.{file_type}"

        output.seek(0)

        st.download_button(
            label="⬇️ Download Cleaned File",
            data=output,
            file_name=file_name,
            mime=mime_type
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Footer
st.write("✨ Built with ❤️ using Streamlit")
