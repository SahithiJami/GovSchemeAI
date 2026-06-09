import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from streamlit_option_menu import option_menu

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="GovScheme AI",
    page_icon="🏛️",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

scheme_df = pd.read_csv("schemes.csv")

try:
    survey_df = pd.read_csv("survey.csv")
except:
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
# OPENROUTER CLIENT
# =====================================================

client = None

try:
    client = OpenAI(
        api_key=st.secrets["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )
except:
    pass

# =====================================================
# NAVIGATION MENU
# =====================================================

selected = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
        "Eligibility Checker",
        "Community Survey",
        "AI Assistant"
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
# TITLE
# =====================================================

st.title("🏛️ GovScheme AI")
st.markdown(
    "### AI-Based Government Scheme Awareness & Eligibility Analyzer"
)

# =====================================================
# DASHBOARD
# =====================================================

if selected == "Dashboard":

    st.header("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Schemes",
        len(scheme_df)
    )

    col2.metric(
        "Survey Responses",
        len(survey_df)
    )

    col3.metric(
        "Categories",
        scheme_df["Category"].nunique()
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        pie_fig = px.pie(
            scheme_df,
            names="Category",
            title="Schemes by Category"
        )

        st.plotly_chart(
            pie_fig,
            width="stretch"
        )

    with right:

        bar_fig = px.bar(
            scheme_df,
            x="Category",
            title="Scheme Distribution"
        )

        st.plotly_chart(
            bar_fig,
            width="stretch"
        )

    st.divider()

    st.subheader("📈 Project Insights")

    st.info(
        f"""
Total Schemes Available: {len(scheme_df)}

Total Survey Responses: {len(survey_df)}

Unique Categories: {scheme_df['Category'].nunique()}
"""
    )

# =====================================================
# ELIGIBILITY CHECKER
# =====================================================

elif selected == "Eligibility Checker":

    st.header("✅ Eligibility Checker")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        value=20
    )

    income = st.number_input(
        "Annual Income (₹)",
        min_value=0,
        value=300000
    )

    category = st.selectbox(
        "Category",
        scheme_df["Category"].unique()
    )

    if st.button("Check Eligibility"):

        eligible = scheme_df[
            (scheme_df["MinAge"] <= age)
            & (scheme_df["MaxAge"] >= age)
            & (scheme_df["IncomeLimit"] >= income)
            & (scheme_df["Category"] == category)
        ]

        if len(eligible) > 0:

            st.success(
                f"{len(eligible)} Eligible Schemes Found"
            )

            st.dataframe(
                eligible[
                    [
                        "Scheme",
                        "Category",
                        "Benefit"
                    ]
                ],
                width="stretch"
            )

            if client is not None:

                if st.button("Get AI Recommendation"):

                    profile = f"""
Age: {age}
Income: {income}
Category: {category}

Eligible Schemes:
{eligible[['Scheme','Benefit']].to_string(index=False)}
"""

                    try:

                        response = client.chat.completions.create(
                            model="openai/gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": """
You are an expert Government Scheme Advisor.

Recommend the best schemes.
Explain:
- Why it matches
- Benefits
- Eligibility
- Application tips
"""
                                },
                                {
                                    "role": "user",
                                    "content": profile
                                }
                            ]
                        )

                        st.subheader(
                            "🤖 AI Recommendation"
                        )

                        st.write(
                            response.choices[0].message.content
                        )

                    except Exception as e:

                        st.error(str(e))

        else:

            st.warning(
                "No schemes found matching your criteria."
            )

# =====================================================
# COMMUNITY SURVEY
# =====================================================

elif selected == "Community Survey":

    st.header("📝 Community Survey")

    age = st.number_input(
        "Survey Age",
        min_value=1,
        max_value=100
    )

    gender = st.selectbox(
        "Gender",
        [
            "Male",
            "Female",
            "Other"
        ]
    )

    occupation = st.text_input(
        "Occupation"
    )

    income = st.number_input(
        "Income",
        min_value=0
    )

    state = st.text_input(
        "State"
    )

    if st.button("Submit Survey"):

        new_row = pd.DataFrame([
            {
                "Age": age,
                "Gender": gender,
                "Occupation": occupation,
                "Income": income,
                "State": state
            }
        ])

        new_row.to_csv(
            "survey.csv",
            mode="a",
            header=False,
            index=False
        )

        st.success(
            "Survey Submitted Successfully!"
        )

        survey_df = pd.concat(
            [survey_df, new_row],
            ignore_index=True
        )

    if len(survey_df) > 0:

        st.subheader("📊 Survey Analytics")

        c1, c2 = st.columns(2)

        with c1:

            age_fig = px.histogram(
                survey_df,
                x="Age",
                title="Age Distribution"
            )

            st.plotly_chart(
                age_fig,
                width="stretch"
            )

        with c2:

            gender_fig = px.pie(
                survey_df,
                names="Gender",
                title="Gender Distribution"
            )

            st.plotly_chart(
                gender_fig,
                width="stretch"
            )

        income_fig = px.histogram(
            survey_df,
            x="Income",
            title="Income Distribution"
        )

        st.plotly_chart(
            income_fig,
            width="stretch"
        )

        if "State" in survey_df.columns:

            state_counts = (
                survey_df["State"]
                .value_counts()
                .reset_index()
            )

            state_counts.columns = [
                "State",
                "Count"
            ]

            state_fig = px.bar(
                state_counts,
                x="State",
                y="Count",
                title="State-wise Participation"
            )

            st.plotly_chart(
                state_fig,
                width="stretch"
            )

        st.subheader("📥 Export Survey Data")

        csv_data = survey_df.to_csv(
            index=False
        )

        st.download_button(
            label="Download Survey Data",
            data=csv_data,
            file_name="survey_data.csv",
            mime="text/csv"
        )

# =====================================================
# AI ASSISTANT
# =====================================================

elif selected == "AI Assistant":

    st.header("🤖 AI Government Scheme Assistant")

    question = st.text_area(
        "Ask anything about government schemes"
    )

    if st.button("Ask AI"):

        if not question:

            st.warning(
                "Please enter a question."
            )

        elif client is None:

            st.error(
                "OpenRouter API key not found."
            )

        else:

            try:

                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are GovScheme AI.

Help users:
1. Find government schemes.
2. Explain eligibility.
3. Explain benefits.
4. Explain application process.
5. Suggest suitable schemes.

Respond clearly and professionally.
"""
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                )

                st.success(
                    "Response Generated"
                )

                st.write(
                    response.choices[0].message.content
                )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "Developed for CSP Project | Data Analytics for Community Development"
)