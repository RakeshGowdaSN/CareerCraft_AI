# CareerCraft AI

CareerCraft AI is an intelligent application designed to provide personalized career recommendations using advanced AI technologies. By leveraging a language model (OpenAI API) and local data persistence, the application offers features such as focus area suggestions and career path recommendations tailored to user profiles.

---

## Key Features and Highlights

- **Chatbot-Driven Profile Building**:  
  Engage with an interactive chatbot to build your profile. The chatbot gathers essential information like age, passions, and interests through targeted questions, inferring personality traits and career preferences.

- **Personality and Interest Analysis**:  
  The backend analyzes user responses to infer key personality traits and interests. This data forms the foundation of personalized career recommendations.

- **AI-Powered Focus Area Recommendations**:  
  Based on your profile, the application provides tailored focus area suggestions with explanations on why each area aligns with your unique traits.

- **Career Recommendations Based on Focus**:  
  After selecting a focus area, receive curated career paths linked to that area. These recommendations are drawn from a predefined knowledge base.

- **Essential Soft Skills**:  
  Alongside career suggestions, the app highlights evergreen soft skills valuable across professions to encourage personal development.

- **Persistent User Profiles**:  
  User data is saved in a `user_profiles.json` file, ensuring seamless continuity across sessions.

- **Modular Architecture**:  
  Built with a clear separation between frontend (Streamlit) and backend (FastAPI), promoting maintainability and scalability.

- **Configurable Language Model**:  
  The backend integrates with the OpenAI API, allowing for future upgrades or customization of the language model.

- **Extensive Knowledge Base**:  
  Incorporates predefined lists of focus areas, career paths, and soft skills to enhance recommendation accuracy.

---

## Code Repository Structure

CareerCraft-AI/
├── backend/
│ ├── app.py # FastAPI application entry point
│ ├── prompts/
│ │ └── prompts_templates.py # Prompt templates for the language model
│ ├── utils/
│ │ ├── constants.py # Application-wide constants (focus areas, careers, etc.)
│ │ ├── helper_functions.py # Utility functions (parsing LLM responses)
│ │ └── model_generations.py # Functions for interacting with the language model
│ ├── user_profiles.json # File to persist user profile data
│ └── requirements.txt # Backend dependencies
├── frontend/
│ ├── app.py # Streamlit application entry point
│ └── requirements.txt # Frontend dependencies
├── .env # Environment variables (e.g., OpenAI API key)
└── README.md # This file

text

---

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- OpenAI API key

### Installation

1. Clone the repository:
git clone <repository_url>
cd CareerCraft-AI

text

2. Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate # On macOS/Linux

venv\Scripts\activate # On Windows
text

3. Install the required dependencies:
pip install -r requirements.txt

text

4. Set up environment variables:
- Create a `.env` file in the root directory.
- Add your OpenAI API key:
  ```
  OPENAI_API_KEY=your-openai-api-key
  ```

---

## Usage

### Running the Application Locally

1. Start the FastAPI backend:
cd backend
uvicorn app:app --reload

text

2. Start the Streamlit frontend (in a separate terminal):
cd frontend
streamlit run app.py

text

3. Access the application through the Streamlit web interface at [http://localhost:8501](http://localhost:8501).

---

## API Endpoints

### Available Endpoints:

1. **GET `/users/{user_id}`**  
 Retrieves the complete learner profile for a given `user_id`.

2. **POST `/chatbot/interact`**  
 Sends a message to the chatbot for a given `user_id` and receives a response, updating the user's profile and assessment status.

3. **POST `/recommend/focus`**  
 Generates personalized focus area recommendations for a given `user_id`.

4. **POST `/recommend/careers`**  
 Provides career recommendations and soft skills for a given `user_id` and `chosen_focus_area`.

---

### Example Requests:

#### Get User Profile:
curl -X 'GET'
'http://127.0.0.1:8000/users/Rakesh_11'
-H 'accept: application/json'

text

#### Chatbot Interaction:
curl -X 'POST'
'http://127.0.0.1:8000/chatbot/interact'
-H 'accept: application/json'
-H 'Content-Type: application/json'
-d '{
"user_id": "Rakesh_11",
"message": "Tell me about your energy levels in social situations."
}'

text

#### Get Focus Recommendation:
curl -X 'POST'
'http://127.0.0.1:8000/recommend/focus'
-H 'accept: application/json'
-H 'Content-Type: application/json'
-d '{
"user_id": "Rakesh_11"
}'

text

#### Get Career Recommendation:
curl -X 'POST'
'http://127.0.0.1:8000/recommend/careers'
-H 'accept: application/json'
-H 'Content-Type: application/json'
-d '{
"user_id": "Rakesh_11",
"chosen_focus_area": "Technology"
}'

text

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.