import streamlit as st
import pandas as pd
import json
import io

# Set Streamlit Page Config
st.set_page_config(page_title="Universal Data Sweeper", page_icon="🧹")

# App Title
st.title("🧹 Universal Data Sweeper")
st.write("Upload a **CSV, Excel, TXT, or JSON file** to clean it.")

# File Upload
uploaded_file = st.file_uploader("📂 Upload File", type=["csv", "xlsx", "txt", "json"])

# Function to clean text
def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()

# Function to clean data
def clean_data(df):
    df.drop_duplicates(inplace=True)  # Remove duplicates
    df.dropna(inplace=True)  # Remove empty rows
    df = df.applymap(lambda x: clean_text(str(x)) if isinstance(x, str) else x)
    return df

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1]
        df = None

        # Read file
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

        # Show original data
        st.subheader("📊 Original Data Preview")
        st.dataframe(df.head())

        # Clean data
        cleaned_df = clean_data(df)
        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(cleaned_df.head())

        # Convert DataFrame to output format
        output = io.BytesIO()
        file_name = f"cleaned_data.{file_type}"
        mime_type = "text/csv"

        if file_type == "csv":
            cleaned_df.to_csv(output, index=False)
            mime_type = "text/csv"
        elif file_type == "xlsx":
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                cleaned_df.to_excel(writer, index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_type == "json":
            json.dump(cleaned_df.to_dict(orient="records"), output, indent=4)
            mime_type = "application/json"
        elif file_type == "txt":
            output.write("\n".join(cleaned_df["Text"]).encode("utf-8"))
            mime_type = "text/plain"
            file_name = "cleaned_data.txt"

        output.seek(0)

        # Download button
        st.download_button(
            label="⬇️ Download Cleaned File",
            data=output.getvalue(),
            file_name=file_name,
            mime=mime_type
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer
st.write("✨ Built with ❤️ using Streamlit")
