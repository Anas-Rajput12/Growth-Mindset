import streamlit as st
import pandas as pd
import json
import io
from docx import Document

st.set_page_config(page_title="Universal Data Sweeper", page_icon="🧹")

st.title("🧹 Universal Data Sweeper")
st.write("Upload a CSV, Excel, TXT, JSON, or Word file to clean it.")

uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx", "txt", "json", "docx"])

def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()

def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df = df.applymap(lambda x: clean_text(str(x)) if isinstance(x, str) else x)
    return df

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1]
        df = None

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
            doc = Document(uploaded_file)
            text_data = [para.text for para in doc.paragraphs if para.text.strip()]
            df = pd.DataFrame(text_data, columns=["Text"])

        st.subheader("📊 Original Data Preview")
        st.dataframe(df.head())

        cleaned_df = clean_data(df)
        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(cleaned_df.head())

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
        elif file_type == "txt" or file_type == "docx":
            output.write("\n".join(cleaned_df["Text"]).encode("utf-8"))
            mime_type = "text/plain"
            file_name = "cleaned_data.txt"

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
