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
        "language": "Language",
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
        "no_match": "No likely matches found using these basic filters. Try broadening your search.",
        "disclaimer": "This tool provides preliminary information only. A match is not an official eligibility decision. Always verify current rules and apply through the official scheme portal.",
        "search": "Search schemes",
        "all": "All",
        "details": "Scheme details and official links",
        "benefit": "Benefit",
        "official": "Official portal",
        "survey_age": "Survey age",
        "gender": "Gender",
        "submit": "Submit Survey",
        "success": "Survey submitted successfully!",
        "no_key": "Gemini AI is unavailable. Please configure GEMINI_API_KEY in Streamlit secrets.",
        "ai_success": "AI response generated successfully!",
        "response": "AI Response",
        "coverage": "Coverage",
        "ask_error": "Please enter a question.",
        "state_note": "State and occupation are collected but are not used as eligibility filters unless the scheme dataset contains those rules."
    },

    "తెలుగు": {
        "language": "భాష",
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
        "no_match": "ఈ ప్రాథమిక వివరాలతో సరిపోయే పథకాలు కనబడలేదు.",
        "disclaimer": "ఇది ప్రాథమిక సమాచారం మాత్రమే. ఇక్కడ చూపిన సరిపోలిక అధికారిక అర్హత నిర్ణయం కాదు. తాజా నిబంధనలను అధికారిక పోర్టల్‌లో నిర్ధారించండి.",
        "search": "పథకాలను వెతకండి",
        "all": "అన్నీ",
        "details": "పథక వివరాలు మరియు అధికారిక లింకులు",
        "benefit": "ప్రయోజనం",
        "official": "అధికారిక వెబ్‌సైట్",
        "survey_age": "సర్వే వయస్సు",
        "gender": "లింగం",
        "submit": "సర్వే సమర్పించండి",
        "success": "సర్వే విజయవంతంగా సమర్పించబడింది!",
        "no_key": "Gemini API Key అందుబాటులో లేదు. Streamlit secrets లో GEMINI_API_KEY నమోదు చేయండి.",
        "ai_success": "AI సమాధానం విజయవంతంగా రూపొందించబడింది!",
        "response": "AI సమాధానం",
        "coverage": "వర్తించే ప్రాంతం",
        "ask_error": "దయచేసి ఒక ప్రశ్న నమోదు చేయండి.",
        "state_note": "రాష్ట్రం మరియు వృత్తి వివరాలు సేకరించబడతాయి. డేటాసెట్‌లో సంబంధిత నియమాలు ఉంటేనే అవి అర్హత తనిఖీలో ఉపయోగించబడతాయి."
    },

    "हिन्दी": {
        "language": "भाषा",
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
        "state": "राज्य / केंद्र शासित प्रदेश",
        "occupation": "व्यवसाय",
        "check": "मेल खाने वाली योजनाएँ देखें",
        "ask": "सरकारी योजनाओं के बारे में कुछ भी पूछें",
        "send": "AI से पूछें",
        "no_match": "इन प्रारंभिक फ़िल्टरों से कोई संभावित योजना नहीं मिली।",
        "disclaimer": "यह केवल प्रारंभिक जानकारी है। संभावित मिलान आधिकारिक पात्रता निर्णय नहीं है। वर्तमान नियम आधिकारिक पोर्टल पर जाँचें।",
        "search": "योजनाएँ खोजें",
        "all": "सभी",
        "details": "योजना विवरण और आधिकारिक लिंक",
        "benefit": "लाभ",
        "official": "आधिकारिक पोर्टल",
        "survey_age": "सर्वेक्षण आयु",
        "gender": "लिंग",
        "submit": "सर्वेक्षण जमा करें",
        "success": "सर्वेक्षण सफलतापूर्वक जमा हुआ!",
        "no_key": "Gemini API Key उपलब्ध नहीं है। Streamlit secrets में GEMINI_API_KEY सेट करें।",
        "ai_success": "AI उत्तर सफलतापूर्वक तैयार हुआ!",
        "response": "AI उत्तर",
        "coverage": "क्षेत्र",
        "ask_error": "कृपया अपना प्रश्न दर्ज करें।",
        "state_note": "राज्य और व्यवसाय की जानकारी एकत्र की जाती है। इनका उपयोग पात्रता जाँच में तभी होगा जब डेटासेट में संबंधित नियम उपलब्ध हों।"
    }
}

# Other languages currently use English interface labels.
# Gemini responses will still be generated in the selected language.

for language_name in LANGUAGES:
    UI.setdefault(language_name, UI["English"])


# =====================================================
# 4. LANGUAGE SELECTION
# =====================================================

language = st.selectbox(
    "🌐 Language / భాష / भाषा",
    list(LANGUAGES.keys()),
    key="language"
)

t = UI[language]

st.title("🏛️ GovScheme AI")

st.markdown(
    f"### {t['tagline']}"
)

st.caption(
    "Government Scheme Awareness | AI | Data Analytics | Community Development"
)


# =====================================================
# 5. LOAD GOVERNMENT SCHEMES
# =====================================================

@st.cache_data
def load_schemes():

    data = pd.read_csv("schemes.csv")

    required_columns = {
        "Scheme",
        "MinAge",
        "MaxAge",
        "IncomeLimit",
        "Category",
        "Benefit"
    }

    missing = required_columns - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns in schemes.csv: {', '.join(sorted(missing))}"
        )

    optional_columns = {
        "StateScope": "Central / Verify applicable state",
        "OfficialURL": "",
        "EligibilityNote": "Verify all conditions on the official portal."
    }

    for column, default in optional_columns.items():

        if column not in data.columns:
            data[column] = default

    return data


try:

    scheme_df = load_schemes()

except Exception as exc:

    st.error(f"Could not load schemes.csv: {exc}")
    st.stop()


# =====================================================
# 6. LOAD COMMUNITY SURVEY DATA
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
# 7. GEMINI API CONFIGURATION
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

except Exception as exc:

    st.warning(
        f"Gemini configuration error: {exc}"
    )


# =====================================================
# 8. GEMINI AI FUNCTION
# =====================================================

def ask_gemini(system_prompt, user_prompt):

    if gemini_client is None:

        raise ValueError(
            "Gemini API key is not configured."
        )

    response = gemini_client.models.generate_content(

        model="gemini-3.8-flash",

        contents=user_prompt,

        config=types.GenerateContentConfig(

            system_instruction=system_prompt,

            temperature=0.3
        )
    )

    if not response.text:

        raise ValueError(
            "Gemini returned an empty response."
        )

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

    # Dashboard statistics

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

    # Charts

    left, right = st.columns(2)

    with left:

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
            title="Scheme Distribution",
            text="Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Scheme details

    st.subheader(
        f"📋 {t['details']}"
    )

    query = st.text_input(
        t["search"]
    )

    category_options = [
        t["all"]
    ] + sorted(
        scheme_df["Category"]
        .dropna()
        .unique()
        .tolist()
    )

    chosen_category = st.selectbox(
        t["category"],
        category_options
    )

    view = scheme_df.copy()

    # Search filter

    if query:

        view = view[
            view["Scheme"].astype(str).str.contains(
                query,
                case=False,
                na=False
            )
            |
            view["Benefit"].astype(str).str.contains(
                query,
                case=False,
                na=False
            )
        ]

    # Category filter

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

    # Expandable scheme details

    for _, row in view.iterrows():

        with st.expander(
            str(row["Scheme"])
        ):

            st.write(
                f"**{t['benefit']}:** {row['Benefit']}"
            )

            st.write(
                f"**{t['coverage']}:** {row['StateScope']}"
            )

            st.info(
                str(row["EligibilityNote"])
            )

            official_url = str(
                row["OfficialURL"]
            ).strip()

            if official_url.startswith("https://"):

                st.link_button(
                    t["official"],
                    official_url
                )


# =====================================================
# 11. ELIGIBILITY CHECKER
# =====================================================

elif selected == t["eligibility"]:

    st.header(
        f"✅ {t['eligibility']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            t["age"],
            min_value=1,
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

        category_options = [
            t["all"]
        ] + sorted(
            scheme_df["Category"]
            .dropna()
            .unique()
            .tolist()
        )

        category = st.selectbox(
            t["category"],
            category_options
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

        occupation = st.text_input(
            t["occupation"]
        )

    st.caption(
        t["disclaimer"]
    )

    st.caption(
        t["state_note"]
    )

    # Check eligibility

    if st.button(
        t["check"],
        type="primary"
    ):

        min_age = pd.to_numeric(
            scheme_df["MinAge"],
            errors="coerce"
        ).fillna(0)

        max_age = pd.to_numeric(
            scheme_df["MaxAge"],
            errors="coerce"
        ).fillna(110)

        income_limit = pd.to_numeric(
            scheme_df["IncomeLimit"],
            errors="coerce"
        )

        # IncomeLimit = -1 means no numeric
        # income filter is encoded in this dataset.

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

        # Save results in session state

        st.session_state["last_matches"] = matches

        st.session_state["profile"] = {

            "age": age,
            "income": income,
            "category": category,
            "state": state,
            "occupation": occupation

        }

        # Display possible matches

        if len(matches) > 0:

            st.success(
                f"{len(matches)} possible schemes to review."
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

                with st.expander(
                    str(row["Scheme"])
                ):

                    st.write(
                        f"**{t['benefit']}:** {row['Benefit']}"
                    )

                    st.write(
                        row["EligibilityNote"]
                    )

                    official_url = str(
                        row["OfficialURL"]
                    ).strip()

                    if official_url.startswith("https://"):

                        st.link_button(
                            t["official"],
                            official_url
                        )

        else:

            st.warning(
                t["no_match"]
            )

    # Gemini eligibility explanation

    if (
        "last_matches" in st.session_state
        and gemini_client is not None
    ):

        if st.button(
            "🤖 Get Gemini AI Explanation"
        ):

            matches = st.session_state["last_matches"]

            profile = st.session_state["profile"]

            prompt = f"""
            User profile:
            {profile}

            Possible government schemes from local dataset:

            {matches[
                ["Scheme", "Benefit", "EligibilityNote"]
            ].to_string(index=False)}
            """

            try:

                response_text = ask_gemini(

                    system_prompt=f"""

                    You are GovScheme AI.

                    Respond only in {LANGUAGES[language]}.

                    Explain the possible matching schemes
                    in simple language.

                    Explain that these are preliminary matches.

                    Do not invent eligibility rules.

                    Distinguish dataset filters from official
                    eligibility requirements.

                    Explain the benefits using only supplied data.

                    Direct the user to the official scheme portal.

                    If information is missing, clearly say so.

                    """,

                    user_prompt=prompt

                )

                st.subheader(
                    f"🤖 {t['response']}"
                )

                st.write(
                    response_text
                )

            except Exception as exc:

                st.error(
                    f"Gemini AI request failed: {exc}"
                )


# =====================================================
# 12. COMMUNITY SURVEY
# =====================================================

elif selected == t["survey"]:

    st.header(
        f"📝 {t['survey']}"
    )

    with st.form(
        "community_survey"
    ):

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

        occupation = st.text_input(
            t["occupation"]
        )

        income = st.number_input(
            t["income"],
            min_value=0,
            value=0,
            step=10000
        )

        state = st.text_input(
            t["state"]
        )

        submitted = st.form_submit_button(
            t["submit"]
        )

    # Save survey data

    if submitted:

        new_row = pd.DataFrame(
            [
                {
                    "Age": age,
                    "Gender": gender,
                    "Occupation": occupation,
                    "Income": income,
                    "State": state
                }
            ]
        )

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

        st.success(
            t["success"]
        )

    # Survey analytics

    if len(survey_df) > 0:

        st.subheader(
            "📊 Community Survey Analytics"
        )

        col1, col2 = st.columns(2)

        with col1:

            fig = px.histogram(

                survey_df,

                x="Age",

                title="Age Distribution",

                nbins=10

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

        # State-wise participation

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

                title="State-wise Participation",

                text="Count"

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Download survey data

        csv_data = survey_df.to_csv(
            index=False
        )

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

    st.header(
        f"🤖 {t['assistant']}"
    )

    st.markdown(
        "Ask questions about Indian government schemes, "
        "eligibility, benefits and application procedures."
    )

    st.caption(
        f"AI responses will be generated in {LANGUAGES[language]}."
    )

    # User question

    question = st.text_area(
        t["ask"],
        height=120,
        placeholder="Example: What government schemes are available for farmers?"
    )

    if st.button(
        t["send"],
        type="primary"
    ):

        if not question.strip():

            st.warning(
                t["ask_error"]
            )

        elif gemini_client is None:

            st.error(
                t["no_key"]
            )

        else:

            # Provide scheme dataset to Gemini

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

            try:

                response_text = ask_gemini(

                    system_prompt=f"""

                    You are GovScheme AI, an Indian government
                    scheme information assistant.

                    Your main purpose is to help citizens understand
                    government schemes.

                    Respond only in {LANGUAGES[language]}.

                    Use simple and accessible language.

                    Explain scheme eligibility, benefits and
                    application procedures clearly.

                    Use the supplied scheme directory as a starting
                    point, not as proof of current eligibility.

                    Never invent:

                    - Application deadlines
                    - Benefit amounts
                    - Eligibility criteria
                    - Government approval status
                    - Application status

                    When relevant, provide official portal URLs
                    included in the supplied directory.

                    Clearly mention when information needs
                    verification.

                    Do not ask users for Aadhaar numbers,
                    bank account numbers, OTPs or passwords.

                    If information is unavailable in the directory,
                    clearly explain that it needs verification.

                    Government scheme directory:

                    {directory}

                    """,

                    user_prompt=question

                )

                st.success(
                    t["ai_success"]
                )

                st.subheader(
                    f"🤖 {t['response']}"
                )

                st.write(
                    response_text
                )

            except Exception as exc:

                st.error(
                    f"Gemini AI request failed: {exc}"
                )


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

st.caption(
    t["disclaimer"]
)