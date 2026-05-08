import streamlit as st
import pandas as pd

st.set_page_config(page_title="Topic Modeling", layout="wide")
st.title("📊 Topic Modeling App")

st.write("Upload CSV file to analyze")

uploaded_file = st.file_uploader("Choose CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded {len(df)} rows")
    st.dataframe(df.head(10))
