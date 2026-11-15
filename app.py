import os
import streamlit as st
import pandas as pd
import plotly.express as px

from google import genai
from google.genai import types
from streamlit_option_menu import option_menu


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="GovScheme AI",
    page_icon="🏛️",
    layout="wide"
)


# =====================================================
# 2. SUPPORTED LANGUAGES
# =====================================================

LANGUAGES = {
    "English": "English",
    "తెలుగు": "Telugu",
    "हिन्दी": "Hindi",
    "தமிழ்": "Tamil",
    "ಕನ್ನಡ": "Kannada",
    "മലയാളം": "Malayalam",
    "বাংলা": "Bengali",
    "मराठी": "Marathi",
    "ગુજરાતી": "Gujarati",
    "ਪੰਜਾਬੀ": "Punjabi",
    "ଓଡ଼ିଆ": "Odia",
    "অসমীয়া": "Assamese"
}


# =====================================================
# 3. INTERFACE TRANSLATIONS
# =====================================================

UI = {
    "English": {
        "dashboard": "Dashboard",
        "eligibility": "Eligibility Checker",
        "survey": "Community Survey",
        "assistant": "AI Assistant",
        "tagline": "AI-Based Government Scheme Awareness & Eligibility Analyzer",
        "total": "Total Schemes",
        "responses": "Survey Responses",
        "categories": "Categories",
        "age": "Age",
        "income": "Annual Income (₹)",
        "category": "Category",
        "state": "State / Union Territory",
        "occupation": "Occupation",
        "check": "Check Matching Schemes",
        "ask": "Ask anything about government schemes",
        "send": "Ask AI",
        "no_match": "No possible matches found. Try changing your filters.",
        "disclaimer": "This tool provides preliminary information only. Always verify eligibility on the official portal.",
        "search": "Search schemes",
        "all": "All",
        "details": "Scheme details and official links",
        "benefit": "Benefit",
        "official": "Official portal",
        "survey_age": "Survey age",
        "gender": "Gender",
        "submit": "Submit Survey",
        "success": "Survey submitted successfully!",
        "no_key": "Gemini API key is not configured.",
        "response": "AI Response",
        "coverage": "Coverage",
        "ask_error": "Please enter a question."
    },

    "తెలుగు": {
        "dashboard": "డ్యాష్‌బోర్డ్",
        "eligibility": "అర్హత తనిఖీ",
        "survey": "సమాజ సర్వే",
        "assistant": "AI సహాయకుడు",
        "tagline": "ప్రభుత్వ పథకాల అవగాహన మరియు అర్హత విశ్లేషణ",
        "total": "మొత్తం పథకాలు",
        "responses": "సర్వే సమాధానాలు",
        "categories": "వర్గాలు",
        "age": "వయస్సు",
        "income": "వార్షిక ఆదాయం (₹)",
        "category": "వర్గం",
        "state": "రాష్ట్రం / కేంద్రపాలిత ప్రాంతం",
        "occupation": "వృత్తి",
        "check": "సరిపోయే పథకాలను చూడండి",
        "ask": "ప్రభుత్వ పథకాల గురించి ఏదైనా అడగండి",
        "send": "AI ని అడగండి",
        "no_match": "సరిపోయే పథకాలు కనబడలేదు.",
        "disclaimer": "ఇది ప్రాథమిక సమాచారం మాత్రమే. అధికారిక వెబ్‌సైట్‌లో అర్హతను నిర్ధారించండి.",
        "search": "పథకాలను వెతకండి",
        "all": "అన్నీ",
        "details": "పథక వివరాలు మరియు అధికారిక లింకులు",
        "benefit": "ప్రయోజనం",
        "official": "అధికారిక వెబ్‌సైట్",
        "survey_age": "సర్వే వయస్సు",
        "gender": "లింగం",
        "submit": "సర్వే సమర్పించండి",
        "success": "సర్వే విజయవంతంగా సమర్పించబడింది!",
        "no_key": "Gemini API Key నమోదు చేయండి.",
        "response": "AI సమాధానం",
        "coverage": "వర్తించే ప్రాంతం",
        "ask_error": "దయచేసి ప్రశ్న నమోదు చేయండి."
    },

    "हिन्दी": {
        "dashboard": "डैशबोर्ड",
        "eligibility": "पात्रता जाँच",
        "survey": "समुदाय सर्वेक्षण",
        "assistant": "AI सहायक",
        "tagline": "सरकारी योजनाओं की जानकारी और पात्रता विश्लेषण",
        "total": "कुल योजनाएँ",
        "responses": "सर्वेक्षण उत्तर",
        "categories": "श्रेणियाँ",
        "age": "आयु",
        "income": "वार्षिक आय (₹)",
        "category": "श्रेणी",
        "state": "राज्य",
        "occupation": "व्यवसाय",
        "check": "योजनाएँ देखें",
        "ask": "सरकारी योजनाओं के बारे में पूछें",
        "send": "AI से पूछें",
        "no_match": "कोई संभावित योजना नहीं मिली।",
        "disclaimer": "यह केवल प्रारंभिक जानकारी है। आधिकारिक पोर्टल पर जाँचें।",
        "search": "योजनाएँ खोजें",
        "all": "सभी",
        "details": "योजना विवरण और आधिकारिक लिंक",
        "benefit": "लाभ",
        "official": "आधिकारिक पोर्टल",
        "survey_age": "आयु",
        "gender": "लिंग",
        "submit": "जमा करें",
        "success": "सफलतापूर्वक जमा हुआ!",
        "no_key": "Gemini API Key सेट करें।",
        "response": "AI उत्तर",
        "coverage": "क्षेत्र",
        "ask_error": "कृपया प्रश्न दर्ज करें।"
    }
}

for lang in LANGUAGES:
    UI.setdefault(lang, UI["English"])


# =====================================================
# 4. LANGUAGE SELECTION
# =====================================================

language = st.selectbox(
    "🌐 Language / భాష / भाषा",
    list(LANGUAGES.keys())
)

t = UI[language]

st.title("🏛️ GovScheme AI")

st.markdown(f"### {t['tagline']}")

st.caption(
    "Government Scheme Awareness | AI | Data Analytics | Community Development"
)


# =====================================================
# 5. LOAD SCHEME DATA
# =====================================================

@st.cache_data
def load_schemes():

    df = pd.read_csv("schemes.csv")

    required = [
        "Scheme",
        "MinAge",
        "MaxAge",
        "IncomeLimit",
        "Category",
        "Benefit",
        "StateScope",
        "OfficialURL",
        "EligibilityNote"
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    for col in ["MinAge", "MaxAge", "IncomeLimit"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df


try:
    scheme_df = load_schemes()

except Exception as e:
    st.error(f"CSV loading error: {e}")
    st.stop()


# =====================================================
# 6. LOAD SURVEY DATA
# =====================================================

try:
    survey_df = pd.read_csv("survey.csv")

except (FileNotFoundError, pd.errors.EmptyDataError):

    survey_df = pd.DataFrame(
        columns=[
            "Age",
            "Gender",
            "Occupation",
            "Income",
            "State"
        ]
    )


# =====================================================
# 7. GEMINI CONFIGURATION
# =====================================================

gemini_client = None

try:

    api_key = st.secrets.get(
        "GEMINI_API_KEY",
        os.getenv("GEMINI_API_KEY", "")
    )

    if api_key:
        gemini_client = genai.Client(
            api_key=api_key
        )

except Exception as e:
    st.warning(f"Gemini configuration error: {e}")


# =====================================================
# 8. GEMINI AI FUNCTION
# =====================================================

def ask_gemini(system_prompt, user_prompt):

    if gemini_client is None:
        raise ValueError(
            "Gemini API key is missing. Configure GEMINI_API_KEY."
        )

    response = gemini_client.models.generate_content(

        model="gemini-2.5-flash",

        contents=user_prompt,

        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=2048
        )
    )

    if not response.text:
        raise ValueError("Empty response received from Gemini.")

    return response.text


# =====================================================
# 9. NAVIGATION MENU
# =====================================================

selected = option_menu(

    menu_title=None,

    options=[
        t["dashboard"],
        t["eligibility"],
        t["survey"],
        t["assistant"]
    ],

    icons=[
        "bar-chart",
        "check-circle",
        "clipboard-data",
        "robot"
    ],

    orientation="horizontal"
)


# =====================================================
# 10. DASHBOARD
# =====================================================

if selected == t["dashboard"]:

    st.header(f"📊 {t['dashboard']}")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        t["total"],
        len(scheme_df)
    )

    col2.metric(
        t["responses"],
        len(survey_df)
    )

    col3.metric(
        t["categories"],
        scheme_df["Category"].nunique()
    )

    st.divider()

    category_counts = (
        scheme_df["Category"]
        .fillna("Unspecified")
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Count"
    ]

    left, right = st.columns(2)

    with left:

        fig = px.pie(
            category_counts,
            names="Category",
            values="Count",
            title="Government Schemes by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.bar(
            category_counts,
            x="Category",
            y="Count",
            text="Count",
            title="Scheme Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader(t["details"])

    query = st.text_input(t["search"])

    categories = [
        t["all"]
    ] + sorted(
        scheme_df["Category"].dropna().unique().tolist()
    )

    chosen_category = st.selectbox(
        t["category"],
        categories
    )

    view = scheme_df.copy()

    if query:

        view = view[
            view["Scheme"].str.contains(
                query,
                case=False,
                na=False
            )
            |
            view["Benefit"].str.contains(
                query,
                case=False,
                na=False
            )
        ]

    if chosen_category != t["all"]:

        view = view[
            view["Category"] == chosen_category
        ]

    st.dataframe(
        view[
            [
                "Scheme",
                "Category",
                "Benefit",
                "StateScope"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    for _, row in view.iterrows():

        with st.expander(str(row["Scheme"])):

            st.write(
                f"**{t['benefit']}:** {row['Benefit']}"
            )

            st.write(
                f"**{t['coverage']}:** {row['StateScope']}"
            )

            st.info(row["EligibilityNote"])

            url = str(row["OfficialURL"]).strip()

            if url.startswith("https://"):
                st.link_button(t["official"], url)


# =====================================================
# 11. ELIGIBILITY CHECKER
# =====================================================

elif selected == t["eligibility"]:

    st.header(f"✅ {t['eligibility']}")

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            t["age"],
            min_value=0,
            max_value=110,
            value=25
        )

        income = st.number_input(
            t["income"],
            min_value=0,
            value=300000,
            step=10000
        )

    with col2:

        categories = [
            t["all"]
        ] + sorted(
            scheme_df["Category"].dropna().unique().tolist()
        )

        category = st.selectbox(
            t["category"],
            categories
        )

        state = st.selectbox(
            t["state"],
            [
                "Not specified",
                "Andhra Pradesh",
                "Telangana",
                "Tamil Nadu",
                "Karnataka",
                "Kerala",
                "Maharashtra",
                "Delhi",
                "Other"
            ]
        )

        occupation = st.text_input(t["occupation"])

    st.caption(t["disclaimer"])

    if st.button(t["check"], type="primary"):

        min_age = scheme_df["MinAge"].fillna(0)
        max_age = scheme_df["MaxAge"].fillna(110)
        income_limit = scheme_df["IncomeLimit"]

        matches = scheme_df[
            (min_age <= age)
            &
            (max_age >= age)
            &
            (
                (income_limit < 0)
                |
                (income_limit >= income)
            )
        ].copy()

        if category != t["all"]:
            matches = matches[
                matches["Category"] == category
            ]

        st.session_state["last_matches"] = matches

        st.session_state["profile"] = {
            "Age": age,
            "Income": income,
            "Category": category,
            "State": state,
            "Occupation": occupation
        }

        if not matches.empty:

            st.success(
                f"{len(matches)} possible schemes found."
            )

            st.dataframe(
                matches[
                    [
                        "Scheme",
                        "Category",
                        "Benefit",
                        "StateScope"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            for _, row in matches.iterrows():

                with st.expander(str(row["Scheme"])):

                    st.write(
                        f"**Benefit:** {row['Benefit']}"
                    )

                    st.info(row["EligibilityNote"])

                    url = str(row["OfficialURL"]).strip()

                    if url.startswith("https://"):
                        st.link_button(
                            t["official"],
                            url
                        )

        else:
            st.warning(t["no_match"])

    if (
        "last_matches" in st.session_state
        and gemini_client is not None
    ):

        if st.button("🤖 Get Gemini AI Explanation"):

            matches = st.session_state["last_matches"]

            profile = st.session_state["profile"]

            prompt = f"""
            User profile:
            {profile}

            Possible schemes:
            {matches[
                ["Scheme", "Benefit", "EligibilityNote", "OfficialURL"]
            ].to_string(index=False)}
            """

            try:

                result = ask_gemini(

                    system_prompt=f"""
                    You are GovScheme AI.

                    Respond only in {LANGUAGES[language]}.

                    Explain possible matching government schemes
                    in simple language.

                    Do not invent eligibility requirements.

                    Explain that these are preliminary matches,
                    not official eligibility decisions.

                    Use only the supplied information.

                    Mention official links when available.
                    """,

                    user_prompt=prompt
                )

                st.subheader(t["response"])
                st.write(result)

            except Exception as e:
                st.error(f"Gemini error: {e}")


# =====================================================
# 12. COMMUNITY SURVEY
# =====================================================

elif selected == t["survey"]:

    st.header(f"📝 {t['survey']}")

    with st.form("community_survey"):

        age = st.number_input(
            t["survey_age"],
            min_value=1,
            max_value=110,
            value=25
        )

        gender = st.selectbox(
            t["gender"],
            [
                "Female",
                "Male",
                "Other",
                "Prefer not to say"
            ]
        )

        occupation = st.text_input(t["occupation"])

        income = st.number_input(
            t["income"],
            min_value=0,
            value=0,
            step=10000
        )

        state = st.text_input(t["state"])

        submitted = st.form_submit_button(t["submit"])

    if submitted:

        new_row = pd.DataFrame([
            {
                "Age": age,
                "Gender": gender,
                "Occupation": occupation,
                "Income": income,
                "State": state
            }
        ])

        header = (
            not os.path.exists("survey.csv")
            or os.path.getsize("survey.csv") == 0
        )

        new_row.to_csv(
            "survey.csv",
            mode="a",
            header=header,
            index=False
        )

        survey_df = pd.concat(
            [survey_df, new_row],
            ignore_index=True
        )

        st.success(t["success"])

    if not survey_df.empty:

        st.subheader("📊 Community Survey Analytics")

        col1, col2 = st.columns(2)

        with col1:

            fig = px.histogram(
                survey_df,
                x="Age",
                nbins=10,
                title="Age Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.pie(
                survey_df,
                names="Gender",
                title="Gender Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        if "State" in survey_df.columns:

            state_counts = (
                survey_df["State"]
                .value_counts()
                .rename_axis("State")
                .reset_index(name="Count")
            )

            fig = px.bar(
                state_counts,
                x="State",
                y="Count",
                text="Count",
                title="State-wise Participation"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        csv_data = survey_df.to_csv(index=False)

        st.download_button(
            "📥 Download Survey Data",
            data=csv_data,
            file_name="survey_data.csv",
            mime="text/csv"
        )


# =====================================================
# 13. GEMINI AI ASSISTANT
# =====================================================

elif selected == t["assistant"]:

    st.header(f"🤖 {t['assistant']}")

    st.markdown(
        "Ask questions about Indian government schemes, "
        "eligibility, benefits and application procedures."
    )

    st.caption(
        f"AI responses will be generated in {LANGUAGES[language]}."
    )

    question = st.text_area(
        t["ask"],
        height=120,
        placeholder="Example: What schemes are available for farmers?"
    )

    if st.button(t["send"], type="primary"):

        if not question.strip():

            st.warning(t["ask_error"])

        elif gemini_client is None:

            st.error(t["no_key"])

        else:

            directory = scheme_df[
                [
                    "Scheme",
                    "Category",
                    "Benefit",
                    "StateScope",
                    "OfficialURL",
                    "EligibilityNote"
                ]
            ].to_string(index=False)

            system_prompt = f"""
            You are GovScheme AI, an Indian government
            scheme information assistant.

            Respond only in {LANGUAGES[language]}.

            Use simple and accessible language.

            Explain scheme benefits, eligibility and
            application procedures.

            Use the supplied scheme database as reference.

            Never invent:
            - Application deadlines
            - Benefit amounts
            - Eligibility criteria
            - Government approval status

            Clearly mention when information needs verification.

            Provide official URLs from the supplied dataset
            whenever relevant.

            Never request Aadhaar numbers, OTPs,
            bank account numbers or passwords.

            Scheme database:
            {directory}
            """

            try:

                result = ask_gemini(
                    system_prompt=system_prompt,
                    user_prompt=question
                )

                st.success("AI response generated successfully!")

                st.subheader(t["response"])

                st.write(result)

            except Exception as e:

                st.error(f"Gemini AI request failed: {e}")


# =====================================================
# 14. FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center;">
        🏛️ <b>GovScheme AI</b>
        <br>
        AI-Based Government Scheme Awareness
        & Eligibility Analyzer
        <br>
        Developed for CSP Project
        | Data Analytics for Community Development
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(t["disclaimer"])