# app.py
# Streamlit BoM Generator
# Install dependencies with:
#   pip install streamlit openai pandas openpyxl

import os
import io
import streamlit as st
import openai
import pandas as pd

# Load API key from environment variable
#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key =              
if not openai.api_key:
    st.error("Please set the OPENAI_API_KEY environment variable.")
    st.stop()

st.title("Solutioning Engine")

# Text input area
user_input = st.text_area(
    "Paste your text here...", 
    height=200,
    placeholder="Enter your requirement or description..."
)

# Hardcoded system prompt
hardcoded_prompt = (
    "You are a Solution Architect working at Connection. Based on the user's input, generate a comprehensive and technically complete "
    "Bill of Materials (BoM). Identify the main request and intelligently infer all required supporting components, dependencies, "
    "licensing, hardware, software, support packages, and configurations needed to fully implement the requested solution in an enterprise environment. "
    "The BoM should include not only the primary item but also any infrastructure, prerequisites, or optional additions that would commonly be needed. "
    "Each item must include a part number if one is known or can be reasonably inferred. Use realistic vendor-style part numbers (e.g., Microsoft, Dell, Pure Storage). "
    "Return a single, clean Markdown table with dynamically inferred columns based on the input (e.g. Item Description, Part Number, Quantity, License Type, Notes, etc.). "
    "If any field is not applicable or unknown, leave it blank — except for the part number, which must be included where possible. Return only the table."
)

# Function to call OpenAI
@st.cache_data
def generate_bom(user_text: str) -> str:
    messages = [
        {"role": "system", "content": hardcoded_prompt},
        {"role": "user",   "content": user_text}
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()



# Helper to parse Markdown table into DataFrame
def markdown_table_to_dataframe(md_table: str) -> pd.DataFrame:
    lines = [line for line in md_table.splitlines() if line.strip()]
    header = [h.strip() for h in lines[0].strip("|").split("|")]
    data_rows = []
    for line in lines[2:]:  # skip header and separator
        cells = [c.strip() for c in line.strip("|").split("|")]
        data_rows.append(cells)
    return pd.DataFrame(data_rows, columns=header)

# Generate and display
if st.button("Generate BoM"):
    if not user_input.strip():
        st.warning("Please enter some text to generate the BoM.")
    else:
        with st.spinner("Generating BoM..."):
            bom_markdown = generate_bom(user_input)

        # Display the markdown table
        st.markdown(bom_markdown)

        # Convert to DataFrame and display in-app
        try:
            df_bom = markdown_table_to_dataframe(bom_markdown)
            st.subheader("BoM Table")
            st.table(df_bom)
        except Exception as e:
            st.error(f"⚠️ Could not parse BoM table: {e}")
