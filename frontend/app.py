import streamlit as st
import requests
import json

# --- Constants ---
API_BASE_URL = "http://localhost:8000"

# --- Helper Functions ---
def call_api(endpoint, method="get", data=None, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "get":
            response = requests.get(url, params=params)
        elif method == "post":
            response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def fetch_user_profile(user_id: str):
    """Fetches the latest user profile from the backend."""
    response = call_api(f"/users/{user_id}", method="get")
    return response

# --- Streamlit App ---
def main():
    st.title("CareerCraft AI")

    # --- Initialize Session State ---
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {} # Initialize as an empty dict
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "is_assessment_complete" not in st.session_state:
        st.session_state.is_assessment_complete = False
    if "focus_recommendations" not in st.session_state:
        st.session_state.focus_recommendations = None

    # --- User Identification ---
    user_id = st.text_input("User ID", "Rakesh_11") # Use the same ID for testing

    # --- User Profile Section (Sidebar) ---
    st.sidebar.header("Your Profile")
    st.session_state.user_profile["age"] = st.sidebar.number_input("Age", min_value=10, max_value=100, value=st.session_state.user_profile.get("age"), placeholder="Enter your age")
    st.session_state.user_profile["educational_background"] = st.sidebar.text_area("Educational Background", value=st.session_state.user_profile.get("educational_background"), placeholder="Your highest degree, major, etc.")
    st.session_state.user_profile["professional_experience"] = st.sidebar.text_area("Professional Experience", value=st.session_state.user_profile.get("professional_experience"), placeholder="Previous roles, industries, etc.")
    st.session_state.user_profile["passion"] = st.sidebar.text_input("Passion", value=st.session_state.user_profile.get("passion"), placeholder="What are you most passionate about?")
    st.session_state.user_profile["skills"] = st.sidebar.text_area("Skills", value=st.session_state.user_profile.get("skills"), placeholder="Technical and soft skills you possess.")
    st.session_state.user_profile["interests"] = st.sidebar.text_area("Interests", value=st.session_state.user_profile.get("interests"), placeholder="Hobbies, areas of interest, etc.")
    st.session_state.user_profile["values"] = st.sidebar.text_area("Values", value=st.session_state.user_profile.get("values"), placeholder="What's important to you in a career?")
    st.session_state.user_profile["career_goals"] = st.sidebar.text_area("Career Goals", value=st.session_state.user_profile.get("career_goals"), placeholder="Your aspirations for your career.")
    st.session_state.user_profile["location"] = st.sidebar.text_input("Location", value=st.session_state.user_profile.get("location"), placeholder="Where are you located?")

    # --- Chatbot Interaction ---
    st.header("Chatbot")
    chat_placeholder = st.empty()

    user_message = st.text_input("Your Message:")
    if st.button("Send Message"):
        if user_id and user_message:
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            data = {"user_id": user_id, "message": user_message}
            response = call_api("/chatbot/interact", method="post", data=data)
            if response:
                chatbot_response = response.get("response")
                is_complete = response.get("is_assessment_complete", False)
                if chatbot_response:
                    st.session_state.chat_history.append({"role": "chatbot", "content": chatbot_response})
                st.session_state.is_assessment_complete = is_complete
                # Fetch updated profile after assessment completion
                if st.session_state.is_assessment_complete:
                    updated_profile = fetch_user_profile(user_id)
                    if updated_profile:
                        st.session_state.user_profile.update(updated_profile)
                        st.write("Updated User Profile in Frontend:", st.session_state.user_profile) # Debugging
            else:
                st.session_state.chat_history.append({"role": "chatbot", "content": "Sorry, I encountered an error."})
        else:
            st.warning("Please enter both User ID and a message.")
        st.rerun()

    with chat_placeholder.container():
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div style="text-align: right; background-color: #e0f2f7; padding: 8px; border-radius: 5px; margin-bottom: 5px;">User: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align: left; background-color: #f0f0f0; padding: 8px; border-radius: 5px; margin-bottom: 5px;">Chatbot: {message["content"]}</div>', unsafe_allow_html=True)

    # --- Focus Recommendation ---
    st.header("Focus Recommendation")
    if st.button("Get Focus Recommendation", disabled=not st.session_state.is_assessment_complete):
        if user_id:
            print("User Profile for Focus Recommendation:", st.session_state.user_profile)
            response = call_api("/recommend/focus", method="post", data={"user_id": user_id})
            if response:
                st.session_state.focus_recommendations = response
                st.subheader("Recommended Focus Areas:")
                for area in response.get("recommended_focus_areas", []):
                    st.markdown(f"- **{area}**")
                if "reasoning" in response:
                    st.write("Reasoning:", response["reasoning"])
            else:
                st.error("Failed to get focus recommendations.")
        else:
            st.warning("Please enter a User ID.")

    # --- Career Recommendation ---
    st.header("Career Recommendation")
    chosen_focus_area = st.text_input("Chosen Focus Area:", "")
    if st.button("Get Career Recommendation", disabled=not st.session_state.is_assessment_complete or not st.session_state.focus_recommendations):
        if user_id and chosen_focus_area:
            data = {"user_id": user_id, "chosen_focus_area": chosen_focus_area}
            response = call_api("/recommend/careers", method="post", data=data)
            if response:
                st.subheader("Recommended Careers:")
                for career in response.get("recommended_careers", []):
                    st.markdown(f"- **{career}**")
                if "soft_skills" in response:
                    st.write("Soft Skills:", response["soft_skills"])
                if "reasoning" in response:
                    st.write("Reasoning:", response["reasoning"])
            else:
                st.error("Failed to get career recommendations.")
        else:
            st.warning("Please enter User ID and Chosen Focus Area.")

    # --- Utility Buttons for Debugging ---
    if st.sidebar.checkbox("Show Session State"):
        st.sidebar.write(st.session_state)

    if st.sidebar.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Run the app ---
if __name__ == "__main__":
    main()