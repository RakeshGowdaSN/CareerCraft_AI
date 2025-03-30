from typing import Optional

def get_interests_prompt(conversation_history: str) -> str:
    """Generates a prompt for inferring the user's interests based on the conversation history."""
    return f"""Based on the following conversation history:

    {conversation_history}

    What are the user's primary interests? Provide a brief summary.
    """

def get_focus_recommendation_prompt(profile: dict, focus_areas: list):
    prompt_parts = ["You are an expert career advisor. A learner with the following profile has requested your advice on potential focus areas:", "\nAvailable Focus Areas:", ", ".join(focus_areas), "\nInstructions:", "1. Carefully consider the learner's profile and the available focus areas.", "2. **Select 3-5 focus areas from the list above that are the BEST FIT for this learner.**", "3. **For EACH selected focus area, provide a concise and UNIQUE explanation (1-2 sentences) of WHY it is a good fit, highlighting specific aspects of the learner's profile that align with the focus area.**", "4. **Do not repeat the same reasoning for different focus areas.**", "\nOutput Format:", "Focus Area 1: [Name of Focus Area from the list]", "Reasoning: [Your unique explanation]", "\nFocus Area 2: [Name of Focus Area from the list]", "Reasoning: [Your unique explanation]", "... (and so on)", "\nRecommendations:"]

    profile_details = []
    if profile.get('age'):
        profile_details.append(f"Age: {profile['age']}")
    if profile.get('passion'):
        profile_details.append(f"Passion: {profile['passion']}")
    if profile.get('interests') and profile['interests'] != 'Not specified':
        profile_details.append(f"Interests: {profile['interests']}")
    personality_traits = profile.get('personality_traits')
    if personality_traits and personality_traits != 'Not specified':
        profile_details.append(f"Personality Traits: {personality_traits}")

    if profile_details:
        prompt_parts.insert(1, "Learner Profile:")
        for detail in profile_details:
            prompt_parts.insert(2, f"- {detail}")
    else:
        prompt_parts.insert(1, "Learner Profile: No specific information provided yet.")

    prompt = " ".join(prompt_parts)
    return prompt

def get_career_recommendation_prompt(profile: dict, chosen_focus_area: str, location: Optional[str] = None):
    personality_info = f"Personality Traits (inferred from chat): {profile.get('personality_traits')}" if profile.get('personality_traits') else "No personality information inferred yet."
    location_context = f"Knowing the user is in {location}," if location else ""
    return f"""Based on the following learner profile with a chosen focus area of '{chosen_focus_area}':
    Age: {profile.get('age', 'Not specified')}
    Educational Background: {profile.get('educational_background', 'Not provided.')}
    Professional Experience: {profile.get('professional_experience', 'Not provided.')}
    Passion: {profile.get('passion', 'Not specified.')}
    Skills: {profile.get('skills', 'Not provided.')}
    Interests: {profile.get('interests', 'Not specified.')}
    Values: {profile.get('values', 'Not provided.')}
    Career Goals: {profile.get('career_goals', 'Not provided.')}
    {personality_info}

    {location_context} suggest 3-5 potential career paths within '{chosen_focus_area}'. Briefly explain why these careers might be a good fit.
    """

def get_personality_inference_prompt(conversation_history: str):
    return f"""Based on the following conversation, infer the user's key personality traits relevant to career choices:
    {conversation_history}
    Provide a concise summary of their personality in 2-3 sentences.
    """

def get_job_description_prompt(job_title: str) -> str:
    """Generates a prompt for getting a one-line job description."""
    return f"""Provide a concise, one-line description for the job title: {job_title}."""

def get_soft_skills_prompt(focus_area: str) -> str:
    """Generates a prompt for getting a natural language explanation of relevant soft skills for a focus area."""
    return f"""Explain in a few sentences the key soft skills that are generally important for professionals working in the field of {focus_area}."""

def get_detailed_personality_analysis_prompt(conversation_history: str) -> str:
    """Generates a prompt for a more detailed analysis of the user's personality based on their answers."""
    return f"""You are an expert in personality analysis for career guidance. Based on the following conversation where the user answered questions about their preferences and tendencies:

    {conversation_history}

    Analyze the user's responses to identify their key personality traits. Provide a summary of their personality that includes:

    - Their likely tendencies in social situations (e.g., introverted, extroverted, comfortable in groups).
    - Their approach to tasks and challenges (e.g., organized, spontaneous, persistent, adaptable).
    - Their emotional style (e.g., calm, expressive, empathetic, analytical).
    - Any other relevant personality characteristics that stand out from their answers.

    Structure your analysis as a few short paragraphs, providing a holistic view of the user's personality as revealed through their responses. Focus on aspects that would be relevant to making career recommendations.
    """