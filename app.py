import streamlit as st
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Test Report Analyzer", layout="wide")
st.title("📋 AI-Powered Test Automation Report Analyzer")

uploaded_file = st.file_uploader("Upload HTML Report", type=["html"])

if uploaded_file:
    soup = BeautifulSoup(uploaded_file, "lxml")

    # Display raw HTML content (optional)
    if st.checkbox("Show Raw HTML"):
        st.code(soup.prettify()[:3000])

    # Extract metadata (customize based on your report layout)
    env_info = soup.find("div", class_="environment")
    test_results_section = soup.find_all("div", class_="test")

    total_tests = len(test_results_section)
    failed_tests = [test for test in test_results_section if 'failed' in test.get("class", [])]
    passed_tests = total_tests - len(failed_tests)

    st.subheader("🧪 Test Summary")
    st.markdown(f"- **Total tests**: {total_tests}")
    st.markdown(f"- ✅ Passed: {passed_tests}")
    st.markdown(f"- ❌ Failed: {len(failed_tests)}")

    # Display failed test cases
    if failed_tests:
        st.subheader("❌ Failed Test Cases")
        for i, fail in enumerate(failed_tests[:10]):
            name = fail.find("h2") or fail.find("span")
            st.markdown(f"**{i+1}. {name.text.strip()}**" if name else f"**{i+1}. Unknown Test Name**")

    # Extract error messages or logs if available
    all_logs = "\n".join([t.get_text(separator="\n") for t in failed_tests])

    if st.button("🔍 Analyze with AI"):
        with st.spinner("Summarizing test failures..."):
            prompt = f"""
            You are a QA assistant. Analyze the following failed test logs:
            {all_logs[:6000]}  # Truncate to avoid token overflow

            Summarize:
            1. Common failure reasons
            2. Suggestions to fix
            3. Any suspicious patterns
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                result = response['choices'][0]['message']['content']
                st.subheader("🧠 AI Insights")
                st.markdown(result)
            except Exception as e:
                st.error(f"OpenAI API Error: {e}")
