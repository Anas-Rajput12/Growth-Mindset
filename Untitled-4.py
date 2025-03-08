import streamlit as st
import pandas as pd
import json
import io

try:
    from docx import Document  # Try importing docx (if available)
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

st.set_page_config(page_title="Universal Data Sweeper", page_icon="🧹")

st.title("🧹 Universal Data Sweeper")
st.write("Upload a **CSV, Excel, TXT, JSON, or DOCX** file to clean and download.")

# File Uploader
uploaded_file = st.file_uploader("📂 Upload Your File", type=["csv", "xlsx", "txt", "json", "docx"])

# Function to clean text
def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()

# Function to clean data
def clean_data(df):
    df.drop_duplicates(inplace=True)  # Remove Duplicates
    df.dropna(inplace=True)  # Remove Empty Rows
    df = df.applymap(lambda x: clean_text(str(x)) if isinstance(x, str) else x)  # Clean text
    return df

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1]
        df = None

        # Load Data Based on File Type
        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif file_type == "txt":
            text_data = uploaded_file.getvalue().decode("utf-8").splitlines()
            df = pd.DataFrame(text_data, columns=["Text"])
        elif file_type == "json":
            json_data = json.load(uploaded_file)
            df = pd.DataFrame(json_data)
        elif file_type == "docx" and DOCX_AVAILABLE:
            doc = Document(uploaded_file)
            text_data = [para.text for para in doc.paragraphs if para.text.strip()]
            df = pd.DataFrame(text_data, columns=["Text"])
        elif file_type == "docx" and not DOCX_AVAILABLE:
            st.error("❌ DOCX support is not available. Install `python-docx`.")

        if df is not None:
            st.subheader("📊 Original Data Preview")
            st.dataframe(df.head())

            # Clean the Data
            cleaned_df = clean_data(df)
            st.subheader("✅ Cleaned Data Preview")
            st.dataframe(cleaned_df.head())

            # Prepare File for Download
            output = io.BytesIO()
            file_name = f"cleaned_data.{file_type}"
            mime_type = ""

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
                text_data = "\n".join(cleaned_df["Text"])
                output.write(text_data.encode("utf-8"))
                mime_type = "text/plain"
                file_name = "cleaned_data.txt"

            # Ensure File is Ready for Download
            output.seek(0)

            st.download_button(
                label="⬇️ Download Cleaned File",
                data=output.getvalue(),
                file_name=file_name,
                mime=mime_type
            )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.write("✨ Built with ❤️ using Streamlit")
