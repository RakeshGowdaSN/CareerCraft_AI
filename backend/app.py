from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Optional
from utils.model_generations import generate_llm_response
from utils.constants import FOCUS_AREAS, CAREER_RECOMMENDATIONS, EVERGREEN_SOFT_SKILLS, PERSONALITY_QUESTIONS
from prompts.prompt_templates import get_focus_recommendation_prompt, get_career_recommendation_prompt, get_personality_inference_prompt, get_interests_prompt
from utils.helper_functions import parse_llm_list_response, parse_llm_reasoning_response
import json

app = FastAPI()

# --- Data Models ---
class LearnerProfile(BaseModel):
    age: Optional[int] = None  # Make age optional
    educational_background: Optional[str] = None
    professional_experience: Optional[str] = None
    passion: Optional[str] = None  # Make passion optional
    skills: Optional[str] = None
    interests: Optional[str] = None
    values: Optional[str] = None
    career_goals: Optional[str] = None
    personality_traits: Optional[str] = None
    chatbot_state: Optional[dict] = None
    location: Optional[str] = None # Add location to the profile
    location_asked: bool = False # Flag to track if we've asked for location

class ChatbotInteractionRequest(BaseModel):
    user_id: str
    message: str

class ChatbotResponse(BaseModel):
    user_id: str
    response: str
    is_assessment_complete: bool = False

class FocusRecommendationResponse(BaseModel):
    recommended_focus_areas: List[str]
    reasoning: str

class CareerRecommendationResponse(BaseModel):
    recommended_careers: List[str]
    soft_skills: List[str]  # Changed field name
    reasoning: str

# --- In-Memory User Data ---
USER_PROFILES_FILE = "user_profiles.json"

# Load user profiles from file at startup
try:
    with open(USER_PROFILES_FILE, "r") as f:
        user_profiles = json.load(f)
        print("User profiles loaded from file:", user_profiles)  # Add this line
        # Convert loaded data back to LearnerProfile objects
        for user_id, profile_data in user_profiles.items():
            user_profiles[user_id] = LearnerProfile(**profile_data)
            print(f"Loaded profile for user {user_id}:", user_profiles[user_id])  # Add this line
except FileNotFoundError:
    user_profiles = {}  # Start with an empty dictionary if the file doesn't exist
    print("User profiles file not found. Starting with an empty dictionary.")  # Add this line
except json.JSONDecodeError:
    user_profiles = {}  # Handle potential JSON decoding errors
    print("Error decoding user profiles JSON. Starting with an empty dictionary.")  # Add this line

# --- Endpoints ---
@app.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    profile = user_profiles.get(user_id)
    if profile:
        return profile.dict()
    else:
        raise HTTPException(status_code=404, detail="User profile not found")
    
@app.post("/chatbot/interact", response_model=ChatbotResponse)
async def chatbot_interact(request: ChatbotInteractionRequest):
    user_id = request.user_id
    user_message = request.message

    if user_id not in user_profiles:
        user_profiles[user_id] = LearnerProfile(age=0, passion="")  # Provide default values
        user_profiles[user_id].chatbot_state = {"step": "initial", "responses": []}

    profile = user_profiles[user_id]
    state = profile.chatbot_state

    if state["step"] == "initial":
        if profile.age == 0:
            profile.chatbot_state["step"] = "ask_age"
            return {"user_id": user_id, "response": "Hello! To get started, could you please tell me your age?", "is_assessment_complete": False}
        elif profile.passion == "":
            profile.chatbot_state["step"] = "ask_passion"
            return {"user_id": user_id, "response": "That's great. What are you most passionate about?", "is_assessment_complete": False}
        else:
            profile.chatbot_state["step"] = "personality_questions"
            profile.chatbot_state["question_index"] = 0
            return {"user_id": user_id, "response": PERSONALITY_QUESTIONS[0], "is_assessment_complete": False}

    elif state["step"] == "ask_age":
        try:
            profile.age = int(user_message)
            profile.chatbot_state["step"] = "ask_passion"
            return {"user_id": user_id, "response": "Thank you. What are you most passionate about?", "is_assessment_complete": False}
        except ValueError:
            return {"user_id": user_id, "response": "Please enter a valid age (a number).", "is_assessment_complete": False}

    elif state["step"] == "ask_passion":
        profile.passion = user_message
        profile.chatbot_state["step"] = "personality_questions"
        profile.chatbot_state["question_index"] = 0
        return {"user_id": user_id, "response": PERSONALITY_QUESTIONS[0], "is_assessment_complete": False}

    elif state["step"] == "personality_questions":
        question_index = state.get("question_index", 0)
        responses = state.get("responses", [])

        if question_index < len(PERSONALITY_QUESTIONS):
            responses.append(f"User: {user_message}")
            state["responses"] = responses
            state["question_index"] = question_index + 1  # Increment the question_index
            if question_index < len(PERSONALITY_QUESTIONS)-1:
                next_question = PERSONALITY_QUESTIONS[question_index+1]
                return {"user_id": user_id, "response": next_question, "is_assessment_complete": False}
            else:
                profile.location_asked = True
                return {"user_id": user_id, "response": "Thank you for answering the personality questions. Could you please tell me where you are currently located? This will help me provide more relevant career information.", "is_assessment_complete": False}
        elif not profile.location_asked:
            profile.location_asked = True
            return {"user_id": user_id, "response": "Thank you for answering the personality questions. Could you please tell me where you are currently located? This will help me provide more relevant career information.", "is_assessment_complete": False}
        elif not profile.location:
            profile.location = user_message
            # profile.chatbot_state = None # Remove this line
            # Save user profiles to file
            with open(USER_PROFILES_FILE, "w") as f:
                json.dump({k: v.dict() for k, v in user_profiles.items()}, f, indent=4)
            return {"user_id": user_id, "response": f"Thank you for sharing your location ({profile.location}). We are now processing your information.", "is_assessment_complete": True}
        else:
            conversation_history = "\n".join(responses)
            prompt = get_personality_inference_prompt(conversation_history)
            personality_summary = await generate_llm_response(prompt, max_tokens=100)
            profile.personality_traits = personality_summary

            # Infer user interests
            interests_prompt = get_interests_prompt(conversation_history)
            interests_summary = await generate_llm_response(interests_prompt, max_tokens=100)
            profile.interests = interests_summary

            profile.chatbot_state = None
            # Save user profiles to file
            with open(USER_PROFILES_FILE, "w") as f:
                json.dump({k: v.dict() for k, v in user_profiles.items()}, f, indent=4)
            return {"user_id": user_id, "response": "Thank you for completing the personality questions. We are now processing your responses.", "is_assessment_complete": True}

# @app.post("/recommend/focus", response_model=FocusRecommendationResponse)
# async def recommend_focus_areas_llm(user_id: str):
#     profile = user_profiles.get(user_id)
#     if not profile:
#         raise HTTPException(status_code=404, detail="User profile not found.")

#     # Construct the prompt using the LearnerProfile data
#     prompt = get_focus_recommendation_prompt(profile.dict(), FOCUS_AREAS)
#     print("Prompt being sent to LLM:", prompt)  # Add this line

#     llm_response = await generate_llm_response(prompt, model="gpt-4o-mini", max_tokens=350)
#     recommended_focus_areas = parse_llm_list_response(llm_response)
#     reasoning_dict = parse_llm_reasoning_response(llm_response)
#     reasoning_text = "\n".join([f"{focus}: {reasoning_dict.get(focus, '')}" for focus in recommended_focus_areas])
#     return {"recommended_focus_areas": recommended_focus_areas, "reasoning": reasoning_text}

@app.post("/recommend/focus", response_model=FocusRecommendationResponse)
async def recommend_focus_areas_llm(user_id: str = Body(..., embed=True)):
    profile = user_profiles.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found.")

    print("Learner Profile received for /recommend/focus:", profile.dict())
    prompt = get_focus_recommendation_prompt(profile.dict(), FOCUS_AREAS)
    print("Prompt being sent to LLM:", prompt)

    llm_response = await generate_llm_response(prompt, model="gpt-4o-mini", max_tokens=350)
    recommended_focus_areas = parse_llm_list_response(llm_response)
    reasoning_dict = parse_llm_reasoning_response(llm_response)
    reasoning_text = "\n".join([f"{focus}: {reasoning_dict.get(focus, '')}" for focus in recommended_focus_areas])
    return {"recommended_focus_areas": recommended_focus_areas, "reasoning": reasoning_text}

# @app.post("/recommend/careers", response_model=CareerRecommendationResponse)
# async def recommend_careers(user_id: str, chosen_focus_area: str):
#     try:
#         profile = user_profiles.get(user_id)
#         if not profile:
#             raise HTTPException(status_code=404, detail="User profile not found.")

#         if chosen_focus_area not in CAREER_RECOMMENDATIONS:
#             raise HTTPException(status_code=400, detail="Invalid chosen_focus_area.")

#         recommended_careers = CAREER_RECOMMENDATIONS[chosen_focus_area]
#         soft_skills = EVERGREEN_SOFT_SKILLS  # Changed variable name
#         reasoning = f"Based on your chosen focus area of {chosen_focus_area}, here are some potential career paths and soft skills to consider."

#         return {"recommended_careers": recommended_careers, "soft_skills": soft_skills, "reasoning": reasoning}  # Changed field name
#     except Exception as e:
#         print(f"Error in /recommend/careers: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/recommend/careers", response_model=CareerRecommendationResponse)
async def recommend_careers(user_id: str = Body(..., embed=True), chosen_focus_area: str = Body(..., embed=True)):
    try:
        profile = user_profiles.get(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found.")

        if chosen_focus_area not in CAREER_RECOMMENDATIONS:
            raise HTTPException(status_code=400, detail="Invalid chosen_focus_area.")

        recommended_careers = CAREER_RECOMMENDATIONS[chosen_focus_area]
        soft_skills = EVERGREEN_SOFT_SKILLS
        reasoning = f"Based on your chosen focus area of {chosen_focus_area}, here are some potential career paths and soft skills to consider."

        return {"recommended_careers": recommended_careers, "soft_skills": soft_skills, "reasoning": reasoning}
    except Exception as e:
        print(f"Error in /recommend/careers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.");