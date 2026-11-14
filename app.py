import os
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from streamlit_option_menu import option_menu

st.set_page_config(page_title="GovScheme AI", page_icon="🏛️", layout="wide")

LANGUAGES = {
    "English": "English", "తెలుగు": "Telugu", "हिन्दी": "Hindi",
    "தமிழ்": "Tamil", "ಕನ್ನಡ": "Kannada", "മലയാളം": "Malayalam",
    "বাংলা": "Bengali", "मराठी": "Marathi", "ગુજરાતી": "Gujarati",
    "ਪੰਜਾਬੀ": "Punjabi", "ଓଡ଼ିଆ": "Odia", "অসমীয়া": "Assamese"
}

# Core interface labels. Scheme names remain in their official/common form;
# explanatory answers are generated in the selected language by the AI assistant.
UI = {
    "English": {
        "language":"Language", "dashboard":"Dashboard", "eligibility":"Eligibility Checker",
        "survey":"Community Survey", "assistant":"AI Assistant", "tagline":"AI-Based Government Scheme Awareness & Eligibility Analyzer",
        "total":"Total Schemes", "responses":"Survey Responses", "categories":"Categories",
        "age":"Age", "income":"Annual Income (₹)", "category":"Category",
        "state":"State / Union Territory", "occupation":"Occupation", "check":"Check Matching Schemes",
        "ask":"Ask anything about government schemes", "send":"Ask AI",
        "no_match":"No likely matches found using these basic filters. Try broadening your search.",
        "disclaimer":"This tool provides preliminary information only. A match is not an official eligibility decision. Always verify current rules and apply through the official scheme portal.",
        "search":"Search schemes", "all":"All", "details":"Scheme details and official links",
        "benefit":"Benefit", "official":"Official portal", "survey_age":"Survey age",
        "gender":"Gender", "submit":"Submit Survey", "success":"Survey submitted successfully!",
        "no_key":"AI is unavailable because OPENROUTER_API_KEY is not configured in Streamlit secrets."
    },
    "తెలుగు": {
        "language":"భాష", "dashboard":"డ్యాష్‌బోర్డ్", "eligibility":"అర్హత తనిఖీ",
        "survey":"సమాజ సర్వే", "assistant":"AI సహాయకుడు", "tagline":"ప్రభుత్వ పథకాల అవగాహన మరియు అర్హత విశ్లేషణ",
        "total":"మొత్తం పథకాలు", "responses":"సర్వే సమాధానాలు", "categories":"వర్గాలు",
        "age":"వయస్సు", "income":"వార్షిక ఆదాయం (₹)", "category":"వర్గం",
        "state":"రాష్ట్రం / కేంద్రపాలిత ప్రాంతం", "occupation":"వృత్తి", "check":"సరిపోయే పథకాలను చూడండి",
        "ask":"ప్రభుత్వ పథకాల గురించి ఏదైనా అడగండి", "send":"AI ని అడగండి",
        "no_match":"ఈ ప్రాథమిక వివరాలతో సరిపోయే పథకాలు కనబడలేదు. ఫిల్టర్లను మార్చి ప్రయత్నించండి.",
        "disclaimer":"ఇది ప్రాథమిక సమాచారం మాత్రమే. ఇక్కడ చూపిన సరిపోలిక అధికారిక అర్హత నిర్ణయం కాదు. తాజా నిబంధనలను అధికారిక పోర్టల్‌లో నిర్ధారించండి.",
        "search":"పథకాలను వెతకండి", "all":"అన్నీ", "details":"పథక వివరాలు మరియు అధికారిక లింకులు",
        "benefit":"ప్రయోజనం", "official":"అధికారిక వెబ్‌సైట్", "survey_age":"సర్వే వయస్సు",
        "gender":"లింగం", "submit":"సర్వే సమర్పించండి", "success":"సర్వే విజయవంతంగా సమర్పించబడింది!",
        "no_key":"Streamlit secrets లో OPENROUTER_API_KEY లేకపోవడంతో AI అందుబాటులో లేదు."
    },
    "हिन्दी": {
        "language":"भाषा", "dashboard":"डैशबोर्ड", "eligibility":"पात्रता जाँच",
        "survey":"समुदाय सर्वेक्षण", "assistant":"AI सहायक", "tagline":"सरकारी योजनाओं की जानकारी और पात्रता विश्लेषण",
        "total":"कुल योजनाएँ", "responses":"सर्वेक्षण उत्तर", "categories":"श्रेणियाँ",
        "age":"आयु", "income":"वार्षिक आय (₹)", "category":"श्रेणी",
        "state":"राज्य / केंद्र शासित प्रदेश", "occupation":"व्यवसाय", "check":"मेल खाने वाली योजनाएँ देखें",
        "ask":"सरकारी योजनाओं के बारे में कुछ भी पूछें", "send":"AI से पूछें",
        "no_match":"इन प्रारंभिक फ़िल्टरों से कोई संभावित योजना नहीं मिली। फ़िल्टर बदलकर देखें।",
        "disclaimer":"यह केवल प्रारंभिक जानकारी है। संभावित मिलान आधिकारिक पात्रता निर्णय नहीं है। वर्तमान नियम आधिकारिक पोर्टल पर जाँचें।",
        "search":"योजनाएँ खोजें", "all":"सभी", "details":"योजना विवरण और आधिकारिक लिंक",
        "benefit":"लाभ", "official":"आधिकारिक पोर्टल", "survey_age":"सर्वेक्षण आयु",
        "gender":"लिंग", "submit":"सर्वेक्षण जमा करें", "success":"सर्वेक्षण सफलतापूर्वक जमा हुआ!",
        "no_key":"Streamlit secrets में OPENROUTER_API_KEY सेट नहीं है, इसलिए AI उपलब्ध नहीं है।"
    }
}

# For other supported languages, the selector and AI response language work immediately.
# Core UI labels fall back to English until their complete reviewed translation is added.
for language in LANGUAGES:
    UI.setdefault(language, UI["English"])

t = UI[st.session_state.get("language", "English")]

@st.cache_data
def load_schemes():
    data = pd.read_csv("schemes.csv")
    required = {"Scheme", "MinAge", "MaxAge", "IncomeLimit", "Category", "Benefit"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"schemes.csv is missing columns: {', '.join(sorted(missing))}")
    for col, default in [
        ("StateScope", "Central / verify applicable state"),
        ("OfficialURL", ""),
        ("EligibilityNote", "Verify all conditions on the official portal.")
    ]:
        if col not in data.columns:
            data[col] = default
    return data

try:
    scheme_df = load_schemes()
except Exception as exc:
    st.error(f"Could not load schemes.csv: {exc}")
    st.stop()

try:
    survey_df = pd.read_csv("survey.csv")
except (FileNotFoundError, pd.errors.EmptyDataError):
    survey_df = pd.DataFrame(columns=["Age", "Gender", "Occupation", "Income", "State"])

client = None
try:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    if api_key:
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
except Exception:
    client = None

# Language selector is kept above navigation so it is available on every page.
language = st.selectbox(t["language"], list(LANGUAGES.keys()), key="language")
t = UI[language]
st.title("🏛️ GovScheme AI")
st.markdown(f"### {t['tagline']}")

nav_labels = [t["dashboard"], t["eligibility"], t["survey"], t["assistant"]]
selected = option_menu(
    menu_title=None, options=nav_labels,
    icons=["bar-chart", "check-circle", "clipboard-data", "robot"],
    orientation="horizontal"
)

if selected == t["dashboard"]:
    st.header(f"📊 {t['dashboard']}")
    c1, c2, c3 = st.columns(3)
    c1.metric(t["total"], len(scheme_df))
    c2.metric(t["responses"], len(survey_df))
    c3.metric(t["categories"], scheme_df["Category"].nunique())
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.pie(scheme_df, names="Category", title="Schemes by category"), use_container_width=True)
    with right:
        counts = scheme_df["Category"].value_counts().rename_axis("Category").reset_index(name="Count")
        st.plotly_chart(px.bar(counts, x="Category", y="Count", title="Scheme distribution"), use_container_width=True)
    st.subheader(t["details"])
    query = st.text_input(t["search"])
    category_options = [t["all"]] + sorted(scheme_df["Category"].dropna().unique().tolist())
    chosen_category = st.selectbox(t["category"], category_options)
    view = scheme_df.copy()
    if query:
        view = view[view["Scheme"].str.contains(query, case=False, na=False) |
                    view["Benefit"].str.contains(query, case=False, na=False)]
    if chosen_category != t["all"]:
        view = view[view["Category"] == chosen_category]
    st.dataframe(view[["Scheme", "Category", "Benefit", "StateScope"]], use_container_width=True, hide_index=True)
    for _, row in view.iterrows():
        with st.expander(str(row["Scheme"])):
            st.write(f"**{t['benefit']}:** {row['Benefit']}")
            st.write(f"**Coverage:** {row['StateScope']}")
            st.info(str(row["EligibilityNote"]))
            if pd.notna(row["OfficialURL"]) and str(row["OfficialURL"]).startswith("https://"):
                st.link_button(t["official"], str(row["OfficialURL"]))

elif selected == t["eligibility"]:
    st.header(f"✅ {t['eligibility']}")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(t["age"], min_value=1, max_value=110, value=25)
        income = st.number_input(t["income"], min_value=0, value=300000, step=10000)
    with col2:
        category = st.selectbox(t["category"], [t["all"]] + sorted(scheme_df["Category"].dropna().unique().tolist()))
        state = st.selectbox(t["state"], ["Not specified", "Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka",
            "Kerala", "Maharashtra", "Delhi", "Other"])
        occupation = st.text_input(t["occupation"])
    st.caption(t["disclaimer"])
    if st.button(t["check"], type="primary"):
        # IncomeLimit=-1 means no numeric income filter is encoded in this directory.
        matches = scheme_df[
            (pd.to_numeric(scheme_df["MinAge"], errors="coerce").fillna(0) <= age) &
            (pd.to_numeric(scheme_df["MaxAge"], errors="coerce").fillna(110) >= age) &
            ((pd.to_numeric(scheme_df["IncomeLimit"], errors="coerce") < 0) |
             (pd.to_numeric(scheme_df["IncomeLimit"], errors="coerce") >= income))
        ].copy()
        if category != t["all"]:
            matches = matches[matches["Category"] == category]
        st.session_state["last_matches"] = matches
        st.session_state["profile"] = {"age": age, "income": income, "category": category,
                                       "state": state, "occupation": occupation}
        if len(matches):
            st.success(f"{len(matches)} possible schemes to review")
            st.dataframe(matches[["Scheme", "Category", "Benefit", "StateScope"]], use_container_width=True, hide_index=True)
            for _, row in matches.iterrows():
                with st.expander(str(row["Scheme"])):
                    st.write(row["EligibilityNote"])
                    if pd.notna(row["OfficialURL"]) and str(row["OfficialURL"]).startswith("https://"):
                        st.link_button(t["official"], str(row["OfficialURL"]))
        else:
            st.warning(t["no_match"])
    if "last_matches" in st.session_state and client is not None:
        if st.button("🤖 Get AI explanation in " + language):
            m = st.session_state["last_matches"]
            profile = st.session_state.get("profile", {})
            prompt = f"User profile: {profile}\nPossible schemes from local dataset:\n{m[['Scheme','Benefit','EligibilityNote']].to_string(index=False)}"
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role":"system","content":f"You are GovScheme AI. Respond only in {LANGUAGES[language]}. Explain that matches are preliminary, do not invent eligibility rules, distinguish dataset filters from official rules, and direct the user to each official portal. If data is missing, say so."},
                        {"role":"user","content":prompt}
                    ]
                )
                st.write(response.choices[0].message.content)
            except Exception as exc:
                st.error(f"AI request failed: {exc}")

elif selected == t["survey"]:
    st.header(f"📝 {t['survey']}")
    with st.form("community_survey"):
        age = st.number_input(t["survey_age"], min_value=1, max_value=110, value=25)
        gender = st.selectbox(t["gender"], ["Female", "Male", "Other", "Prefer not to say"])
        occupation = st.text_input(t["occupation"])
        income = st.number_input(t["income"], min_value=0, value=0, step=10000)
        state = st.text_input(t["state"])
        submitted = st.form_submit_button(t["submit"])
    if submitted:
        new_row = pd.DataFrame([{"Age": age, "Gender": gender, "Occupation": occupation, "Income": income, "State": state}])
        header = not os.path.exists("survey.csv") or os.path.getsize("survey.csv") == 0
        new_row.to_csv("survey.csv", mode="a", header=header, index=False)
        survey_df = pd.concat([survey_df, new_row], ignore_index=True)
        st.success(t["success"])
    if len(survey_df):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.histogram(survey_df, x="Age", title="Age distribution"), use_container_width=True)
        with c2:
            st.plotly_chart(px.pie(survey_df, names="Gender", title="Gender distribution"), use_container_width=True)
        if "State" in survey_df.columns:
            state_counts = survey_df["State"].value_counts().rename_axis("State").reset_index(name="Count")
            st.plotly_chart(px.bar(state_counts, x="State", y="Count", title="State-wise participation"), use_container_width=True)
        st.download_button("📥 Download Survey Data", survey_df.to_csv(index=False), "survey_data.csv", "text/csv")

elif selected == t["assistant"]:
    st.header(f"🤖 {t['assistant']}")
    st.caption("The assistant will answer in your selected language.")
    question = st.text_area(t["ask"])
    if st.button(t["send"], type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        elif client is None:
            st.error(t["no_key"])
        else:
            # Give the model the local scheme directory as context to reduce unsupported claims.
            directory = scheme_df[["Scheme", "Category", "Benefit", "StateScope", "OfficialURL", "EligibilityNote"]].to_string(index=False)
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role":"system","content":f"""You are GovScheme AI, an Indian government scheme information assistant.
Reply in {LANGUAGES[language]}. Use simple, accessible language.
Use the supplied directory as a starting point, not as proof of current eligibility.
Never invent deadlines, benefit amounts, eligibility criteria or application status.
When relevant, provide the official portal URL included in the directory.
Clearly say when information needs verification. Do not ask for Aadhaar, bank account numbers,
OTP, passwords or other sensitive personal information.
Scheme directory:\n{directory}"""},
                        {"role":"user","content":question}
                    ]
                )
                st.success("Response generated")
                st.write(response.choices[0].message.content)
            except Exception as exc:
                st.error(f"AI request failed: {exc}")

st.divider()
st.caption("Developed for CSP Project | Data Analytics for Community Development")
st.caption(t["disclaimer"])
