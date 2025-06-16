import streamlit as st
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
from autogen.cache import Cache

# Disable Docker mode
os.environ["AUTOGEN_USE_DOCKER"] = "0"

if 'output' not in st.session_state:
    st.session_state.output = {
        'assessment': '',
        'action': '',
        'followup': ''
    }

st.sidebar.title("OpenAI API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

st.sidebar.warning("""
## ⚠️ Important Notice

This application is a supportive tool and does not replace professional mental health care. If you're experiencing thoughts of self-harm or severe crisis:

- Call National Crisis Hotline: 988
- Call Emergency Services: 911
- Seek immediate professional help
""")

st.title("🧠 Mental Wellbeing Agent")

st.info("""
**Meet Your Mental Wellbeing Agent Team:**

🧠 **Assessment Agent** - Analyzes your situation and emotional needs  
🎯 **Action Agent** - Creates immediate action plan and connects you with resources  
🔄 **Follow-up Agent** - Designs your long-term support strategy
""")

st.subheader("Personal Information")
col1, col2 = st.columns(2)

with col1:
    mental_state = st.text_area("How have you been feeling recently?",
                                placeholder="Describe your emotional state, thoughts, or concerns...")
    sleep_pattern = st.select_slider(
        "Sleep Pattern (hours per night)",
        options=[f"{i}" for i in range(0, 13)],
        value="7"
    )

with col2:
    stress_level = st.slider("Current Stress Level (1-10)", 1, 10, 5)
    support_system = st.multiselect(
        "Current Support System",
        ["Family", "Friends", "Therapist", "Support Groups", "None"]
    )

recent_changes = st.text_area(
    "Any significant life changes or events recently?",
    placeholder="Job changes, relationships, losses, etc..."
)

current_symptoms = st.multiselect(
    "Current Symptoms",
    ["Anxiety", "Depression", "Insomnia", "Fatigue", "Loss of Interest",
     "Difficulty Concentrating", "Changes in Appetite", "Social Withdrawal",
     "Mood Swings", "Physical Discomfort"]
)

if st.button("Get Support Plan"):
    if not api_key:
        st.error("Please enter your OpenAI API key.")
    else:
        with st.spinner('🤖 AI Agents are analyzing your situation...'):
            try:
                task = f"""
You are a team of mental wellbeing agents. Based on the user’s current condition, generate a 3-part support plan:

1. **Assessment** - Emotional State: {mental_state}, Sleep: {sleep_pattern} hours, Stress Level: {stress_level}/10, Support System: {', '.join(support_system) if support_system else 'None'}
2. **Recent Changes**: {recent_changes}
3. **Symptoms**: {', '.join(current_symptoms) if current_symptoms else 'None reported'}

Generate a detailed:
- Emotional and psychological **assessment**
- Specific, actionable **plan**
- Long-term **follow-up strategy**
                """

                config_list = [
                    {
                        "model": "gpt-4o",
                        "api_key": api_key
                    }
                ]

                assessment_agent = AssistantAgent(
                    name="AssessmentAgent",
                    system_message="You are a compassionate clinical psychologist. Write the assessment part of the support plan.",
                    llm_config={"config_list": config_list}
                )

                action_agent = AssistantAgent(
                    name="ActionAgent",
                    system_message="You are a crisis and wellness expert. Write the immediate action plan part of the support plan.",
                    llm_config={"config_list": config_list}
                )

                followup_agent = AssistantAgent(
                    name="FollowupAgent",
                    system_message="You are a long-term mental health planner. Write the follow-up strategy part of the support plan.",
                    llm_config={"config_list": config_list}
                )

                user_proxy = UserProxyAgent(name="User", human_input_mode="NEVER", code_execution_config=False)

                groupchat = GroupChat(
                    agents=[user_proxy, assessment_agent, action_agent, followup_agent],
                    messages=[],
                    max_rounds=3
                )

                manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

                user_proxy.initiate_chat(manager, message=task)

                history = groupchat.messages[-3:]

                st.session_state.output = {
                    'assessment': history[0]['content'],
                    'action': history[1]['content'],
                    'followup': history[2]['content']
                }

                with st.expander("Situation Assessment"):
                    st.markdown(st.session_state.output['assessment'])

                with st.expander("Action Plan & Resources"):
                    st.markdown(st.session_state.output['action'])

                with st.expander("Long-term Support Strategy"):
                    st.markdown(st.session_state.output['followup'])

                st.success("✨ Mental health support plan generated successfully!")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
