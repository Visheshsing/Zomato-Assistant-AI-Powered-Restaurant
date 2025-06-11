import streamlit as st
from agent import agent_executor  # Make sure you import agent_executor, not just agent
from langchain_core.messages import AIMessage, HumanMessage

# Page config
st.set_page_config(
    page_title="Zomato-style Assistant",
    page_icon="🍽",
    layout="centered",
)

# Header
st.markdown("<h1 style='text-align: center;'>🍽 Zomato-style Restaurant Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Book tables, order food, check menus, and more!</p>", unsafe_allow_html=True)
st.divider()

# Initialize chat session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display past chat
for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Chat input
user_input = st.chat_input("Ask me anything (e.g. 'Show Italian restaurants in Mumbai')")

# Handle input
if user_input:
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Use dictionary input for agent_executor
                response = agent_executor.invoke({"input": user_input})
                output = response.get("output", str(response))  # Handle dict or string
            except Exception as e:
                output = f"❌ Error: {str(e)}"

            st.markdown(output)
            st.session_state.chat_history.append(AIMessage(content=output))