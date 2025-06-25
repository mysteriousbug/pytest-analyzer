import streamlit as st
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Test Report Analyzer", layout="wide")
st.title("📋 AI-Powered Test Automation Report Analyzer")

uploaded_file = st.file_uploader("Upload HTML Report", type=["html"])

if uploaded_file:
    soup = BeautifulSoup(uploaded_file, "lxml")

    test_results = soup.find_all("div", class_="test")
    total_tests = len(test_results)
    failed_tests = [test for test in test_results if 'failed' in test.get("class", [])]
    passed_tests = total_tests - len(failed_tests)

    st.subheader("🧪 Test Summary")
    st.markdown(f"- **Total tests**: {total_tests}")
    st.markdown(f"- ✅ Passed: {passed_tests}")
    st.markdown(f"- ❌ Failed: {len(failed_tests)}")

    if failed_tests:
        st.subheader("❌ Failed Test Cases")
        for i, fail in enumerate(failed_tests[:10]):
            name = fail.find("h2") or fail.find("span")
            st.markdown(f"**{i+1}. {name.text.strip()}**" if name else f"**{i+1}. Unknown Test Name**")

    all_logs = "\n".join([t.get_text(separator="\n") for t in failed_tests])[:6000]

    if st.button("🔍 Analyze with AI"):
        with st.spinner("Calling OpenAI..."):
            try:
                user_prompt = f"""
You are a QA assistant. Analyze the following test automation logs and generate:

1. Summary of common failures
2. Root causes
3. Suggestions for fixing
4. Any test pattern anomalies

Test Logs:
{all_logs}
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful QA assistant."},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                st.subheader("🧠 AI Insights")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"❌ OpenAI API Error: {e}")
