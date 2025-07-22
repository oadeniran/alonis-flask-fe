from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_session import Session
import api_calls
import markdown
import textwrap
import time
from datetime import datetime, timedelta
from math import ceil
import random
import content_markdowns

app = Flask(__name__)
app.secret_key = "random_secret_key"  # Change this to a secure key in production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_FILE_THRESHOLD'] = 500  # max number of session files before it starts cleaning

def clean_session_if_login_expired():
    try:
        login_time_str = session.get('login_time')
        last_activity = session.get('last_activity')

        if not login_time_str:
            session.clear()
            return True

        # Convert login_time from ISO string
        if isinstance(login_time_str, str):
            login_time = datetime.fromisoformat(login_time_str)
        else:
            login_time = login_time_str  # Assume already a datetime

        # Convert last_activity if present
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)

        if datetime.now() - login_time > timedelta(hours=5) and \
           last_activity and last_activity < (datetime.now() - timedelta(minutes=30)):
            session.clear()
            print("Session cleared due to inactivity.")
            return True
        else:
            session['last_activity'] = datetime.now().isoformat()
            session.modified = True
            return False
    except Exception as e:
        print(f"Error during session check: {e}")
        session.clear()
        return True

@app.route('/')
def home():
    if 'user_data' in session:
        return redirect(url_for('home_page'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_data' in session:
        return redirect(url_for('home_page'))
    
    if request.method == 'POST':
        # Handle the form data
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        alonis_verbosity_level = request.form.get('ai_level')
        short_bio = request.form.get('description')

        # Quick validation
        # 1. Ensure username is not empty and does not contain spaces and @
        if not username or ' ' in username or '@' in username:
            return render_template('signup.html', error="Username cannot be empty, contain spaces, or '@'.")
        # 2. Ensure password is at least 8 characters
        if len(password) < 8:
            return render_template('signup.html', error="Password must be at least 8 characters long.")

        user_data = {
            'email': email,
            'username': username,
            'password': password,
            'alonis_verbosity': alonis_verbosity_level,
            'short_bio': short_bio
        }
        # Call the API to create the user account
        try:
            response = api_calls.signup_user(user_data)
            print(response)
        except Exception as e:
            # Handle API call failure (e.g., network error, server error)
            print(f"API call failed: {e}")
            return render_template('signup.html', error="Failed to create account. Please try again later.")

        if response.get('error'):
            # Handle error (e.g., user already exists)
            print(f"Error creating account: {response['error']}")
            return render_template('signup.html', error=response['error'])
        
        # If successful, ser data in the session
        session['user_data'] = {
            'email': email,
            'username': username,
            'alonis_verbosity': alonis_verbosity_level,
            'short_bio': short_bio,
            "user_id": response.get('uid')
        }
        session['login_time'] = datetime.now().isoformat()  # Store login time in ISO format
        session['last_activity'] = datetime.now().isoformat()  # Store last activity time in ISO format
        session.modified = True  # Mark the session as modified

        # Then redirect to the home page
        return redirect(url_for('home_page'))
        

    # If it's a GET request, just show the signup page
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_data' in session:
        return redirect(url_for('home_page'))
    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier')
        password = request.form.get('password')
        is_email_login = '@' in login_identifier

        login_credentials = {
            'email': login_identifier if is_email_login else None,
            'username': login_identifier if not is_email_login else None,
            'password': password,
            "is_email_login": is_email_login
        }

        # Call the API to log in
        try:
            response = api_calls.login_user(login_credentials)
            print(response)
        except Exception as e:
            # Handle API call failure (e.g., network error, server error)
            print(f"API call failed: {e}")
            return render_template('login.html', error="Failed to log in. Please try again later.")

        if response.get('error'):
            # Handle error (e.g., invalid credentials)
            print(f"Login error: {response['error']}")
            return render_template('login.html', error=response['error'])
        # If successful, store user data in the session
        session['user_data'] = {
            'email': response.get('email'),
            'username': response.get('username'),
            'alonis_verbosity': response.get('alonis_verbosity', 0),  # Default to 50 if not provided
            'short_bio': response.get('short_bio', ''),
            "user_id": response.get('uid'),
            'is_login_flow': True  # flag to indicate successful login
        }
        session['login_time'] = datetime.now().isoformat()  # Store login time in ISO format
        session['last_activity'] = datetime.now().isoformat()  # Store last activity time in ISO format
        session.modified = True  # Mark the session as modified
        
        return redirect(url_for('home_page')) 

    # For a GET request, just display the login page
    return render_template('login.html')

    
@app.route('/api/quote')
def api_quote():    
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    try:
        # Fetch the quote of the day
        if 'quote_of_day' not in session:
            quote_of_the_day = api_calls.get_daily_quotes(
                session.get('user_data', {}).get('user_id', '')
            ).get('quote', {'quote': "Stay positive!", "author": "Alonis"})
            session['quote_of_day'] = quote_of_the_day
        else:
            quote_of_the_day = session['quote_of_day']

        # Return all the data together as JSON
        return jsonify({
            'quote': quote_of_the_day
        })
    except Exception as e:
        print(f"API Error in home_data: {e}")
        return jsonify({'error': 'Could not load data.'}), 500
    
@app.route('/api/story')
def api_story():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    try:
        daily_story = api_calls.get_daily_story(
            session.get('user_data', {}).get('user_id', '')
        )
        story_text = daily_story.get('story', '')
        return jsonify({'story': story_text})
    except Exception as e:
        return jsonify({'error': 'Could not load story.'}), 500

@app.route('/home')
def home_page():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))

    username = session['user_data']['username']
    is_login_flow = session.get('user_data', {}).get('is_login_flow', False)

    welcome_texts = [
        "Welcome back", "Nice to see you again", "Glad you're here", "You're back!",
        "Hello again", "Welcome, friend", "Look who's here!",
        "Good to have you back", "Happy to see you again"
    ] if is_login_flow else [
        "Welcome", "Hello there", "Hi, welcome!", "Nice to meet you",
        "Hey! Good to have you", "Hello and welcome", "Greetings",
        "Glad you’re here", "Welcome aboard", "Welcome, explorer"
    ]
    welcome_text = random.choice(welcome_texts)

    # Time-based greeting
    current_hour = datetime.now().hour
    if 0 <= current_hour <= 5:
        time_greetings = [ "Night owl mode", "Midnight Vibes", "Late night thoughts",]
    elif 5 <= current_hour < 12:
        time_greetings = ["Good morning", "Morning sunshine", "Rise and shine", "Top of the morning", "A fresh start", "Early bird!", "New day, new ideas", "Let's make today count", "Wakey wakey", "Hello, morning star"]
    elif 12 <= current_hour < 17:
        time_greetings = ["Good afternoon", "Hope your day's going well", "Midday energy!", "Afternoon vibes", "You're halfway through!", "Sunny side up", "Keep going strong", "How’s the day so far?", "Let’s keep it moving", "Happy afternoon!"]
    elif 17 <= current_hour < 19:
        time_greetings = ["Good evening", "Evening glow", "Time to relax", "Evening calm", "How was your day?", "Evening reflections", "Wind down time", "Hello, evening star", "Evening vibes", "Unwind and relax"]
    else:
        time_greetings = ["Night mode: on", "How was your day?", "Time to reflect", "Nighttime thoughts", "Rest well", "Good night vibes", "Evening peace", "Late night musings", "Sleepy time soon"]

    greeting = random.choice(time_greetings)

    greeting_text = f"{welcome_text} {username}, {greeting}."

    intro_variants = [
        "Alonis here", "I'm Alonis", "This is Alonis", "You’re speaking with Alonis",
        "Alonis checking in", "It’s me, Alonis", "Hello from Alonis", "Alonis at your service",
        "Hey, it's Alonis", "Alonis — your AI companion"
    ]
    intro_text = random.choice(intro_variants)

    cta_variants = [
        "What can I do for you today?", "How can I assist you?", "Need something?", 
        "Want to explore something?", "Got a task for me?", "Let’s get started", 
        "What are we working on?", "Looking for help with something?", 
        "Tell me what’s on your mind", "Ready when you are"
    ]
    cta_text = random.choice(cta_variants)

    return render_template(
        'home.html',
        greeting_text=greeting_text,
        intro_text=intro_text,
        cta_text=cta_text,
        recommendations=[],
        quote={}
    )

@app.route('/assessment/<assessment_type>', methods=['GET', 'POST'])
def assessment_page(assessment_type):
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    # This part handles the background request from JavaScript
    if request.method == 'POST':
        if 'assessment' not in session:
            return jsonify({'ai_response': 'Your session has expired. Please refresh the page.'}), 400

        user_message = request.json.get('message')
        if user_message:
            session['assessment']['messages'].append({'sender': 'user', 'text': user_message})
            
            test_type = 'personality_test' if assessment_type == 'personality' else 'mindlab'
            
            # --- API CALL ---
            response = api_calls.get_assessment_chat_response({
                'user_id': session.get('user_data', {}).get('user_id'),
                'session_id': session['assessment']['session_id'],
                'test_type': test_type,
                'user_input': user_message
            })
            
            ai_message = response.get('message', 'Sorry, I did not understand that.')
            session['assessment']['messages'].append({'sender': 'ai', 'text': ai_message})
            session.modified = True

            if 'dictionary_data' not in response:
                # If no dictionary data, just continue the chat
                return jsonify({
                    'status': 'continue', 
                    'data': {'ai_response': ai_message}
                })
            else:
                # If we get dictionary data, the assessment is complete
                session['assessment']['is_completed'] = True
                session['assessment']['dictionary_data'] = response.get('dictionary_data', {})
                session.modified = True
                return jsonify({
                    'status': 'complete',
                    'data': {
                        'message': "I have all the information I need. You can now generate your report.",
                        'session_id': session['assessment']['session_id']
                    }
                })

    # This part handles the initial page load (GET request)
    if 'assessment' in session and 'report_text' in session['assessment'] and session['assessment'].get('is_completed', False) and session['assessment'].get('asessment_type') == assessment_type:
        return render_template(
            'assessment.html',
            title="Assessment Complete",
            is_report_generated=True, # New flag to show the buttons
            assessment_type=assessment_type,
            session_id=session['assessment']['session_id']
        )
    
    if 'assessment' in session and session['assessment'].get('asessment_type') != assessment_type:
        # Instead of resetting, render the page with a flag to show the popup
        if not session['assessment'].get('is_completed', False):
            # If its not completed then ask the user to confirm if they want to continue with the current assessment
            return render_template(
                'assessment.html',
                messages=session['assessment']['messages'],
                title=f"Assessment in Progress...",
                assessment_type=assessment_type,
                show_confirmation_modal=True # This is the new flag
            )
        else:
            if assessment_type == 'personality':
                page_title = "Personality Test"
                intro_text = "This assessment helps you understand your key personality traits based on the Big Five model. Your conversation will guide the analysis."
            else: 
                page_title = "MindLab"
                intro_text = "This is a safe space to reflect on your current mental state. Your responses will help identify patterns and provide insights."
            
            return render_template(
            'assessment.html',
            title=page_title,
            intro_text=intro_text,
            assessment_type=assessment_type,
            show_intro=True # Tell the template to show the intro screen
        )

    elif 'assessment' not in session:
        
        if assessment_type == 'personality':
            test_type = 'personality_test'
            default_message = 'Welcome to the Personality Test! Let us begin.'
            page_title = "Personality Test"
            intro_text = "This assessment helps you understand your key personality traits based on the Big Five model. Your conversation will guide the analysis."
        else: # mental_health
            test_type = 'mindlab'
            default_message = 'Welcome to MindLab. How can I help you today?'
            page_title = "MindLab"
            intro_text = "This is a safe space to reflect on your current mental state. Your responses will help identify patterns and provide insights."

        if session.get('start_assessment',  False):
            # if we can see the start_assessment flag, then we are starting a new assessment
            session_key = api_calls.generate_session_id().get('session_id')
        
            initial_message = api_calls.get_assessment_chat_response({
                'user_id': session.get('user_data', {}).get('user_id'),
                'session_id': session_key,
                'test_type': test_type,
                'user_input': ''
            }).get('message', default_message)
            
            session['assessment'] = {
                'session_id': session_key,
                'asessment_type': assessment_type,
                'messages': [{'sender': 'ai', 'text': initial_message}]
            }
            del session['start_assessment']  # Remove the flag after starting
        else:
            return render_template(
                'assessment.html',
                title=page_title,
                intro_text=intro_text,
                assessment_type=assessment_type,
                show_intro=True # Tell the template to show the intro screen
            )
    else:
        page_title = "Personality Test" if assessment_type == 'personality' else "MindLab"

    return render_template(
        'assessment.html',
        messages=session['assessment']['messages'],
        title=page_title,
        assessment_type=assessment_type
    )

@app.route('/generate_report/<assessment_type>/<session_id>')
def generate_report(assessment_type, session_id): 

    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    # --- API CALL ---
    assessment_result_object = api_calls.generate_assessment_results_report({
        'user_id': session.get('user_data', {}).get('user_id'),
        'session_id': session_id,
        'test_type': 'personality_test' if assessment_type == 'personality' else 'mindlab',
        "data_extracted": session.get('assessment', {}).get('dictionary_data', {})
    })

    report_text = assessment_result_object.get('report', None)

    # Save the report text in the session for later use
    session['assessment']['report_text'] = report_text
    session.modified = True
    # Redirect to the report page we created earlier
    return redirect(url_for('report_page', session_id=session_id))

@app.route('/reset_assessment/<assessment_type>')
def reset_assessment(assessment_type):
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    # Clear the old assessment from the session
    if 'assessment' in session:
        session.pop('assessment')
        session.modified = True
    # Redirect to the new assessment page, which will now start fresh
    return redirect(url_for('assessment_page', assessment_type=assessment_type))

@app.route('/start_assessment/<assessment_type>')
def start_assessment(assessment_type):
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    # Clear any existing assessment from the session
    if 'assessment' in session:
        session.pop('assessment')
        session.modified = True
    session['start_assessment'] = True
    # Redirect to the assessment page, which will now create a fresh session
    return redirect(url_for('assessment_page', assessment_type=assessment_type))


@app.route('/chat', methods=['GET', 'POST'])
def chat_page():

    if clean_session_if_login_expired():
        return redirect(url_for('login'))

    # Handle POST request (when user sends a message)
    if request.method == 'POST':
        user_message = request.json.get('message') # Get message from JSON
        if user_message:
            session['talk_session']['messages'].append({'sender': 'user', 'text': user_message})
            
            # --- API CALL ---
            ai_message = api_calls.get_talk_session_chat_response({
                'user_id': session.get('user_data', {}).get('user_id'),
                'session_id': session['talk_session']['session_id'],
                'user_input': user_message
            }).get('response', 'Sorry, I did not understand that.')
            
            # Add AI response to history
            session['talk_session']['messages'].append({'sender': 'ai', 'text': ai_message})
            session.modified = True
            
            # Return only the AI's response as JSON
            return jsonify({'ai_response': ai_message})
        return jsonify({'ai_response': 'An error occurred.'}), 400


    # On a GET request, just render since we have an init chat route
    return render_template('chat.html', messages=session.get('talk_session', {}).get('messages', []))

@app.route('/new_chat')
def new_chat():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    # Clear only the general chat history from the session
    if 'talk_session' in session:
        session.pop('talk_session')
        session.modified = True
    # Redirect back to the chat page to start a new session
    return redirect(url_for('chat_page'))

@app.route('/api/init_chat', methods=['POST'])
def api_init_chat():
    # If a session already exists and is valid, return it
    if 'talk_session' in session:
        return jsonify({'messages': session['talk_session']['messages']})

    # If no session, create a new one (this is the slow part)
    session_key = api_calls.generate_session_id().get('session_id')
    initial_message = api_calls.get_talk_session_chat_response({
        'user_id': session.get('user_data', {}).get('user_id'),
        'session_id': session_key,
        'user_input': ''
    }).get('response', "Hello! I'm Alonis. You can ask me anything you'd like.")
    
    session['talk_session'] = {
        'session_id': session_key,
        'messages': [{'sender': 'ai', 'text': initial_message}]
    }
    session.modified = True

    return jsonify({'messages': session['talk_session']['messages']})


@app.route('/notes', methods=['GET', 'POST'])
def notes_page():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    # Initialize notes in session if not present
    if 'notes' not in session:
        user_notes_obj = api_calls.get_user_notes_and_goals(
            user_id=session.get('user_data', {}).get('user_id')
        )
        if 'error' in user_notes_obj:
            # Handle error (e.g., user not found, API error)
            user_notes = []
        else:
            user_notes = user_notes_obj.get('notes_and_goals', [])

        session['notes'] = user_notes if user_notes else []

    # This block now handles the background request from JavaScript
    if request.method == 'POST':
        data = request.json
        title = data.get('title')
        details = data.get('details')
        is_goal = data.get('is_goal', False)

        if title and details:
            # Call the API to add a new note or goal
            new_note = {"uid":session.get('user_data', {}).get('user_id'), 'title': title, 'details': details, 'is_goal': is_goal}
            
            try:
                resp = api_calls.add_note_or_goal(new_note)
            except Exception as e:
                # Handle API call failure (e.g., network error, server error)
                print(f"API call failed: {e}")
                return jsonify({'status': 'error', 'message': 'Failed to add note. Please try again later.'}), 500

            # Add the new note to the session notes is successful
            if resp.get('status_code') == 200:
                # Add the new note to the session notes at the beginning
                session['notes'].insert(0, resp.get('note', {}))  # Assuming the API returns the new note in the response
                
                session.modified = True  # Mark the session as modified
            
                # Return a success response with the new note data
                resp['status'] = 'success'
                return jsonify(resp)
        
        return jsonify({'status': 'error', 'message': 'Title and details are required.'}), 400
    
    for note in session['notes']:
        if len(note['details']) > 100:
            note['truncated_details'] = note['details'][:100] + '...'
        else:
            note['truncated_details'] = note['details']

    page = request.args.get('page', 1, type=int)
    notes_per_page = 12 # Show 12 notes per page
    
    # Calculate the slice for the current page
    start = (page - 1) * notes_per_page
    end = start + notes_per_page
    print(f"Displaying notes from {start} to {end} for page {page}")
    paginated_notes = session['notes'][start:end]
    
    total_pages = ceil(len(session['notes']) / notes_per_page)

    return render_template(
        'notes.html', 
        notes=paginated_notes,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/achieve_goal/<note_id>', methods=['POST'])
def achieve_goal(note_id):
    if 'notes' in session:
        # Find the note by its ID
        for note in session['notes']:
            if note.get('_id') == note_id:
                note['is_achieved'] = True
                session.modified = True
                try:
                    api_calls.mark_goal_as_achieved(
                        uid=session.get('user_data', {}).get('user_id'),
                        note_id=note_id
                    )
                except Exception as e:
                    # Handle API call failure (e.g., network error, server error)
                    print(f"API call failed: {e}")
                    return jsonify({'status': 'error', 'message': 'Failed to mark goal as achieved. Please try again later.'}), 500
                
                return jsonify({'status': 'success', 'message': 'Goal marked as achieved.'})
        
        return jsonify({'status': 'error', 'message': 'Note not found.'}), 404
    
    return jsonify({'status': 'error', 'message': 'No notes in session.'}), 404

@app.route('/delete_note/<note_id>', methods=['POST'])
def delete_note(note_id):
    if 'notes' in session:
        # Get the current page from the incoming JSON data
        data = request.json
        page = data.get('page', 1)
        notes_per_page = 12 # Make sure this matches your notes_page route

        # Find and remove the note
        original_notes = session['notes']
        note_to_delete = next((note for note in original_notes if note.get('_id') == note_id), None)
        
        if not note_to_delete:
            return jsonify({'status': 'error', 'message': 'Note not found.'}), 404

        
        # Call the API to delete the note also delete it from the backend
        try:
            api_calls.delete_note_or_goal(
                uid=session.get('user_data', {}).get('user_id'),
                note_id=note_id
            )
        except Exception as e:
            # Handle API call failure (e.g., network error, server error)
            print(f"API call failed: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to delete note. Please try again later.'}), 500

        # Create the new list without the deleted note
        updated_notes = [note for note in original_notes if note.get('_id') != note_id]
        session['notes'] = updated_notes
        session.modified = True


        # --- New Logic: Find the note that should now be on this page ---
        next_note_to_add = None
        # The index of the last item that *should* be on the page
        last_item_index = (page * notes_per_page) - 1
        
        # If the full list of notes has an item at that index, it's our new note
        if len(updated_notes) > last_item_index:
            next_note_to_add = updated_notes[last_item_index]

        return jsonify({
            'status': 'success', 
            'message': 'Note deleted.',
            'next_note': next_note_to_add # Send the new note back to the frontend
        })

    return jsonify({'status': 'error', 'message': 'No notes in session.'}), 404

@app.route('/recommendations')
def recommendations_page():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    # This route loads instantly, passing no data.
    # JavaScript will fetch the data from the new API routes.
    return render_template('recommendations.html')

@app.route('/api/recommendations/alonis')
def api_alonis_recommendations():

    page = request.args.get('page', 1, type=int)

    try:
        # Fetch the alonis recommendations from the API
        api_data = api_calls.get_recommendations(
            uid=session.get('user_data', {}).get('user_id', ''),
            rec_type='alonis_recommendation',
            page=page
        )

        rec_items = api_data.get('recommendations', [])
        for item in rec_items:
            if len(item.get('description', '')) > 100:
                item['truncated_description'] = item['description'][:100] + '...'
            else:
                item['truncated_description'] = item['description']
        
        random.shuffle(rec_items)  # Shuffle the recommendations for variety
        return jsonify({
            'items': rec_items,
            'has_next_page': api_data.get('has_next_page', False)
        })
    except Exception as e:
        print(f"API Error in alonis_recommendations: {e}")
        return jsonify({'error': 'Could not load recommendations.'}), 500 
    

# 1. ADD a new API route for books
@app.route('/api/recommendations/books')
def api_books():

    page = request.args.get('page', 1, type=int)

    try:
        api_data = api_calls.get_recommendations(
                uid=session.get('user_data', {}).get('user_id', ''),
                rec_type='alonis_recommendation_books',
                page=page
        )
        all_books = api_data.get('recommendations', [])
        

        for book in all_books:
            if len(book['description']) > 100:
                book['truncated_description'] = book['description'][:100] + '...'
            else:
                book['truncated_description'] =book['description']
            
            # Do same for context
            if len(book.get('context', '')) > 100:
                book['truncated_context'] = book['context'][:100] + '...'
            else:
                book['truncated_context'] = book['context']

        # Shuffle the books to provide a different order each time
        random.shuffle(all_books)  # Shuffle the recommendations for variety

        return jsonify({
            'items': all_books,
            'has_next_page': api_data.get('has_next_page', False)
        })
    except Exception as e:
        print(f"API Error in books recommendations: {e}")
        return jsonify({'error': 'Could not load book recommendations.'}), 500


@app.route('/api/recommendations/movies')
def api_movies():
    
    page = request.args.get('page', 1, type=int)
    try:
        api_data = api_calls.get_recommendations(
            uid=session.get('user_data', {}).get('user_id', ''),
            rec_type='alonis_recommendation_movies',
            page=page
        )
        all_movies = api_data.get('recommendations', [])
        
        for movie in all_movies:
            if len(movie['description']) > 100:
                movie['truncated_description'] = movie['description'][:100] + '...'
            else:
                movie['truncated_description'] = movie['description']
            
            # Do same for context
            if len(movie.get('context', '')) > 100:
                movie['truncated_context'] = movie['context'][:100] + '...'
            else:
                movie['truncated_context'] = movie['context']
        
        # Shuffle the movies to provide a different order each time
        random.shuffle(all_movies)  # Shuffle the recommendations for variety

        return jsonify({
            'items': all_movies,
            'has_next_page': api_data.get('has_next_page', False)
        })
    except Exception as e:
        print(f"API Error in movies recommendations: {e}")
        return jsonify({'error': 'Could not load movie recommendations.'}), 500

@app.route('/api/recommendations/songs')
def api_songs():
    # Your logic to get song recommendations
    page = request.args.get('page', 1, type=int)

    try:
        api_data = api_calls.get_recommendations(
            uid=session.get('user_data', {}).get('user_id', ''),
            rec_type='alonis_recommendation_songs',
            page=page
        )
        all_songs = api_data.get('recommendations', [])
        
        for song in all_songs:
            if len(song['description']) > 100:
                song['truncated_description'] = song['description'][:100] + '...'
            else:
                song['truncated_description'] = song['description']

        return jsonify({
            'items': all_songs,
            'has_next_page': api_data.get('has_next_page', False)
        })
    except Exception as e:
        print(f"API Error in songs recommendations: {e}")
        return jsonify({'error': 'Could not load song recommendations.'}), 500

@app.route('/api/recommendations/news')
def api_news():
    # Your logic to get news recommendations
    page = request.args.get('page', 1, type=int)
    try:
        api_data = api_calls.get_recommendations(
            uid=session.get('user_data', {}).get('user_id', ''),
            rec_type='alonis_recommendation_news',
            page=page
        )
        all_news = api_data.get('recommendations', [])
        
        for news in all_news:
            if len(news['description']) > 100:
                news['truncated_description'] = news['description'][:100] + '...'
            else:
                news['truncated_description'] = news['description']

        return jsonify({
            'items': all_news,
            'has_next_page': api_data.get('has_next_page', False)
        })
    except Exception as e:
        print(f"API Error in news recommendations: {e}")
        return jsonify({'error': 'Could not load movie recommendations.'}), 500

@app.route('/api/recommendation/complete/<recommendation_id>', methods=['POST'])
def api_mark_recommendation_action(recommendation_id):
    # This route will handle marking a recommendation as done or not done
    print(f"Marking recommendation {recommendation_id} as done.")
    try:
        api_calls.mark_recommendation_as_completed(
            uid=session.get('user_data', {}).get('user_id'),
            rec_id=recommendation_id
        )
        return jsonify({
            'status': 'success',
            'message': f'Recommendation {recommendation_id} marked as done.'
        })
    except Exception as e:
        print(f"API Error in marking recommendation: {e}")
        return jsonify({'error': 'Could not mark recommendation as done.'}), 500

@app.route('/api/recommendation/note_interaction/<recommendation_id>', methods=['POST'])
def api_recommendation_note_interaction(recommendation_id):
    # This route will handle adding a note for a recommendation
    print(f"Adding note for recommendation {recommendation_id}.")
    api_calls.mark_user_interaction_with_recommendation(
        uid=session.get('user_data', {}).get('user_id'),
        rec_id=recommendation_id
    )
    
    return jsonify({
        'status': 'success',
        'message': f'Note added for recommendation {recommendation_id}.'
    })

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/profile_history')
def api_profile_history():
    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    try:
        user_sessions_history = api_calls.get_user_sessions(
            user_id=session.get('user_data', {}).get('user_id')
        )
        assessments_history = user_sessions_history.get("sessions", {}).get('assessments', [])
        talks_history = user_sessions_history.get("sessions", {}).get('talk_sessions', [])
        
        return jsonify({
            'assessments': assessments_history,
            'talks': talks_history
        })
    except Exception as e:
        print(f"API Error in profile_history: {e}")
        return jsonify({'error': 'Could not load history.'}), 500

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    # If user is not logged in, redirect to login
    if clean_session_if_login_expired():
        return redirect(url_for('login'))

    if request.method == 'POST':
        updated_data = request.form.to_dict()
        print(f"Updating user data: {updated_data}")
        time.sleep(1.5) # Simulate a delay for the loading state
        return redirect(url_for('profile_page'))

    # Ordered user info session and non editable fields
    user_data = session.get('user_data', {})
    
    # Define the exact order you want the fields to appear in
    field_order = ['username', 'email', 'short_bio', 'alonis_verbosity', 'user_id']
    # Define which fields cannot be edited
    non_editable_fields = {'user_id', 'email'}

    # Build the list of dictionaries
    user_details_list = []
    for key in field_order:
        if key in user_data:
            user_details_list.append({
                'key': key,
                # Create a nice label by replacing underscores and capitalizing
                'label': key.replace('_', ' ').capitalize(),
                'value': user_data[key],
                'editable': key not in non_editable_fields
            })

    return render_template(
        'profile.html',
        user_details=user_details_list,
        assessments=[],
        talks=[]
    )

@app.route('/report/<session_id>')
def report_page(session_id):

    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    

    if 'assessment' in session and session['assessment'].get('session_id') == session_id and 'report_text' in session['assessment']:
        # If the report text is already in the session, use it
        report_text = session['assessment']['report_text']
    else:
        assessment_result_object = api_calls.get_session_result_report(
            user_id=session.get('user_data', {}).get('user_id'),
            session_id=session_id
        )
        report_text = assessment_result_object.get('report_data', None)

    # Convert the Markdown text to HTML
    report_content = markdown.markdown(textwrap.dedent(report_text))

    print(report_content)

    return render_template('report.html', report_content=report_content)

@app.route('/view_chat/<session_id>')
def view_chat_page(session_id):

    if clean_session_if_login_expired():
        return redirect(url_for('login'))
    
    is_talk_session = request.args.get('is_talk_session', 'false').lower() in {
        '1', 'true', 'yes', 'y'
    }
    
    chat_history = api_calls.get_session_chat_messages(
        user_id=session.get('user_data', {}).get('user_id'),
        session_id=session_id,
        is_talk_session=is_talk_session
    )
    messages = chat_history.get('messages', [])

    return render_template('view_chat.html', messages=messages, title=f"Chat History - {session_id}")

@app.route('/about')
def about_page():
    # New data structure with summary and full markdown content
    about_sections = [
        {
            'id': 'personality-test',
            'title': 'Personality Assessment',
            'summary': "I'm Alonis — your AI companion designed to understand you through natural conversation.I use the Big Five Personality Model to gently uncover insights about your traits, goals, and emotional patterns. Together, we'll explore who you are — not with judgment, but with curiosity, care, and depth.",
            'content_md': content_markdowns.PERSONALITY_TEST_MD,
            'icon': 'fas fa-user-check'
        },
        {
            'id': 'mindlab',
            'title': 'MindLab',
            'summary': "MindLab is your private space to reflect on how you're really feeling. I gently analyze emotional patterns in your conversations to support self-awareness and clarity. No judgment — just insight, presence, and a safe place to explore your well-being.",
            'content_md': content_markdowns.MINDLAB_MD,
            'icon': 'fas fa-brain'
        },
        {
            'id': 'alonis-chat',
            'title': 'Alonis Chat',
            'summary': "I'm not just a chatbot — I remember your story and adapt to support you personally. By keeping track of your past conversations, notes, and goals, I offer relevant and thoughtful insights. Everything I retain is used only to help you — never for any outside purpose",
            'content_md': content_markdowns.ALONIS_CHAT_MD,
            'icon': 'fas fa-comments'
        },
        {
            'id' : 'notes-and-goals',
            'title': 'Notes and Goals',
            'summary': "This is your private space to write, reflect, and track progress at your own pace. Set meaningful goals, revisit your thoughts, and celebrate every milestone you reach. Together, we'll turn quiet reflections into confident forward steps.",
            'content_md': content_markdowns.NOTES_AND_GOALS_MD,
            'icon': 'fas fa-clipboard-list' 
        },
        {
            'id': 'recommendations',
            'title': 'Recommendations',
            'summary': "I provide handpicked recommendations tailored to your goals, personality, and emotional needs. From articles to activities, each suggestion is chosen to support your growth and well-being. Think of me as your personal guide — offering the right nudge, at the right time.",
            'content_md': content_markdowns.RECOMMENDATIONS_MD,
            'icon': 'fas fa-star'
        }
    ]

    # Pre-process the markdown content into HTML
    for section in about_sections:
        section['content_html'] = markdown.markdown(textwrap.dedent(section['content_md']))

    return render_template(
        'about.html', 
        sections=about_sections

    )

if __name__ == '__main__':
    app.run(debug=True)