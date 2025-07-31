import requests
from config import API_BASE_URL

def signup_user(user_data):
    url = API_BASE_URL + '/user/sign-up'
    response = requests.post(url, json= user_data)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error signing up: {response.text[:300]}")
    return response.json()

def login_user(credentials):
    url = API_BASE_URL + '/user/sign-in'
    response = requests.post(url, json=credentials)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error logging in: {response.text[:300]}")
    return response.json()

def hackathon_login_user(credentials):
    url = API_BASE_URL + '/user/hackathon-username-only-auth'
    response = requests.post(url, json=credentials)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error logging in for hackathon: {response.text[:300]}")
    return response.json()

def generate_session_id():
    url = API_BASE_URL + '/common/generate-session-id'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error generating session ID: {response.text[:300]}")
    return response.json()

def get_user_sessions(user_id):
    url = API_BASE_URL + f'/user/{user_id}/sessions'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching user sessions: {response.text[:300]}")
    return response.json()

def get_assessment_chat_response(assesment_data):
    url = API_BASE_URL + f'/assessment/assessment-chat'
    response = requests.post(url, json=assesment_data)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error getting assessment chat response: {response.text[:300]}")
    return response.json()

def generate_assessment_results_report(assessment_data_for_result):
    url = API_BASE_URL + f'/assessment/assessment-result'
    response = requests.post(url, json=assessment_data_for_result)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error getting assessment results: {response.text[:300]}")
    return response.json()

def get_talk_session_chat_response(tak_data):
    url = API_BASE_URL + f'/talk/talk-session'
    response = requests.post(url, json=tak_data)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error getting TalK chat response: {response.text[:300]}")
    return response.json()

def get_session_chat_messages(user_id, session_id, is_talk_session=False):
    url = API_BASE_URL + f'/user/{user_id}/{session_id}/session-chats?is_talk_session={is_talk_session}'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:400]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching session messages: {response.text[:400]}")
    return response.json()

def get_session_result_report(user_id, session_id):
    url = API_BASE_URL + f'/user/{user_id}/{session_id}/session-report'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching session result report: {response.text[:300]}")
    return response.json()

def add_note_or_goal(note_or_goal_data):
    url = API_BASE_URL + '/user/add-note-or-goal'
    response = requests.post(url, json=note_or_goal_data)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error adding note or goal: {response.text[:300]}")
    return response.json()

def get_user_notes_and_goals(user_id):
    url = API_BASE_URL + f'/user/{user_id}/get-notes-and-goals'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching user notes and goals: {response.text[:300]}")
    return response.json()

def delete_note_or_goal(uid, note_id):
    url = API_BASE_URL + f'/user/{uid}/delete-note-or-goal/{note_id}'
    response = requests.delete(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error deleting note or goal: {response.text[:300]}")
    return response.json()

def mark_goal_as_achieved(uid, note_id):
    url = API_BASE_URL + f'/user/{uid}/mark-goal-as-achieved/{note_id}'
    response = requests.post(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error marking goal as achieved: {response.text[:300]}")
    return response.json()

def get_daily_quotes(uid):
    url = API_BASE_URL + f'/talk/{uid}/personalized-quote'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching daily quotes: {response.text[:300]}")
    return response.json()

def get_daily_story(uid):
    url = API_BASE_URL + f'/talk/{uid}/daily-story'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching daily story: {response.text[:300]}")
    return response.json()

def get_recommendations(uid, rec_type, page=1):
    url = API_BASE_URL + f'/user/{uid}/alonis-recommendations/{rec_type}?page={page}'
    response = requests.get(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error fetching recommendations: {response.text[:300]}")
    return response.json()

def mark_user_interaction_with_recommendation(uid, rec_id):
    url = API_BASE_URL + f'/user/{uid}/mark-interaction-with-recommendation/{rec_id}'
    response = requests.post(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error marking recommendation interaction: {response.text[:300]}")
    return response.json()

def mark_recommendation_as_completed(uid, rec_id):
    url = API_BASE_URL + f'/user/{uid}/mark-recommendation-as-completed/{rec_id}'
    response = requests.post(url)
    print(f"API Response: {response.status_code} - {response.text[:300]}")
    if response.status_code != 200:
        raise Exception(f"Error marking recommendation as completed: {response.text[:300]}")
    return response.json()