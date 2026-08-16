import streamlit as st

from agents.router import route_question


st.set_page_config(
    page_title="Banking AI Analytics",
    page_icon="🏦",
    layout="wide"
)


st.title("🏦 Banking AI Analytics")
st.subheader("Data Engineering + Data Science + Agentic AI")

st.markdown("---")


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Home",
        "🤖 AI Assistant",
        "📊 Data Analytics",
        "🧠 Machine Learning",
        "👥 Customer Segmentation",
        "📄 Reports"
    ]
)


if page == "🏠 Home":

    st.header("Welcome to Banking AI Analytics")

    st.write(
        """
        This application extends the Banking Data Engineering project
        with Data Science, Machine Learning and Agentic AI capabilities.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Pipeline", "Active")

    with col2:
        st.metric("Data Layer", "Bronze → Silver → Gold")

    with col3:
        st.metric("ML Engine", "Ready")

    with col4:
        st.metric("AI Agents", "3")


    st.markdown("---")

    st.subheader("Agentic AI Architecture")

    st.code(
        """
User Question
      ↓
AI Agent Router
      ↓
┌───────────────┬───────────────┬───────────────┐
│               │               │
Support Agent   Data Agent      ML Agent
│               │               │
Help / FAQ      SQL / Data      Prediction
                Analysis        / Insights
└───────────────┴───────────────┴───────────────┘
                  ↓
             Insight / Action
                  ↓
                Report
        """,
        language="text"
    )


elif page == "🤖 AI Assistant":

    st.header("🤖 Banking AI Assistant")

    st.write(
        "Ask a question and the AI Router will select the appropriate agent."
    )

    question = st.text_area(
        "Enter your question",
        placeholder="Example: What is the average customer balance?"
    )

    if st.button("Ask AI", type="primary"):

        if question.strip():

            selected_agent = route_question(question)

            st.markdown("### 🔀 Agent Routing")

            st.success(
                f"Selected Agent: **{selected_agent}**"
            )

            st.markdown("### 📝 Your Question")

            st.write(question)

            st.markdown("### 🤖 Agent Status")

            if selected_agent == "Support Agent":

                st.info(
                    "Support Agent selected. "
                    "This agent will handle application and support questions."
                )

            elif selected_agent == "Data Agent":

                st.info(
                    "Data Agent selected. "
                    "This agent will analyze banking data from the Gold layer."
                )

            elif selected_agent == "ML Agent":

                st.info(
                    "ML Agent selected. "
                    "This agent will perform Machine Learning based analysis."
                )

        else:

            st.warning("Please enter a question.")


elif page == "📊 Data Analytics":

    st.header("📊 Data Analytics")

    st.info(
        "The Data Agent will be connected to the PostgreSQL Gold layer here."
    )


elif page == "🧠 Machine Learning":

    st.header("🧠 Machine Learning")

    st.info(
        "Machine Learning models will be implemented here."
    )


elif page == "👥 Customer Segmentation":

    st.header("👥 Customer Segmentation")

    st.info(
        "Customer segmentation using Machine Learning will be implemented here."
    )


elif page == "📄 Reports":

    st.header("📄 Reports")

    st.info(
        "AI-generated banking reports will be implemented here."
    )