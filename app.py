from flask import Flask, render_template, url_for, request, redirect, session, jsonify
import api_calls
import markdown
import textwrap
import time
from datetime import datetime
from math import ceil

app = Flask(__name__)
app.secret_key = "random_secret_key"  # Change this to a secure key in production

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
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

        # Then redirect to the home page
        return redirect(url_for('home_page'))
        

    # If it's a GET request, just show the signup page
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            "user_id": response.get('uid')
        }
        session.modified = True  # Mark the session as modified
        
        return redirect(url_for('home_page')) 

    # For a GET request, just display the login page
    return render_template('login.html')

@app.route('/app-home')
def home_page():

    if 'user_data' not in session:
        # Means User is not logged in, redirect to login
        return redirect(url_for('login'))
    
    # Get the current time to determine greeting
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        greeting =  "Good morning"
    elif 12 <= current_hour < 17:
        greeting =  "Good afternoon"
    elif 17 <= current_hour < 21:
        greeting =  "Good evening"
    else:
        greeting =  "Hope your night is going well"
    
    user_name = session['user_data']['username']

    # --- SIMULATED API RESPONSE ---
    # In a real app, you would make an API call here.
    # We create a sample list with 7 items to test the "View More" logic.
    recommendations_from_api = [
        # {'title': 'Practice Mindfulness', 'details': 'Take 5 minutes to focus on your breath. This can help reduce stress and improve clarity.'},
        # {'title': 'Connect with a Friend', 'details': 'Reach out to someone you trust for a quick chat. Social connection is vital for well-being.'},
        # {'title': 'Start a Gratitude List', 'details': 'Write down three things you are grateful for today, no matter how small.'},
        # {'title': 'Plan Your Day', 'details': 'Organizing your tasks can provide a sense of control and accomplishment.'},
        # {'title': 'Go for a Short Walk', 'details': 'A brief walk outside can boost your mood and energy levels.'},
        # {'title': 'Explore a New Topic', 'details': 'Learning something new can be a great source of inspiration and motivation.'},
        # {'title': 'Listen to Calming Music', 'details': 'Create a playlist of soothing music to help you relax and unwind.'}
    ]
    # -----------------------------

    quote_of_the_day = {
        'text': 'The secret of getting ahead is getting started.',
        'author': 'Mark Twain'
    }

    return render_template(
        'home.html',
        user_name=user_name,
        greeting=greeting,
        recommendations=recommendations_from_api,  # Pass the list to the template
        quote =quote_of_the_day,
    )

@app.route('/assessment/<assessment_type>', methods=['GET', 'POST'])
def assessment_page(assessment_type):
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
    # Clear the old assessment from the session
    if 'assessment' in session:
        session.pop('assessment')
        session.modified = True
    # Redirect to the new assessment page, which will now start fresh
    return redirect(url_for('assessment_page', assessment_type=assessment_type))

@app.route('/start_assessment/<assessment_type>')
def start_assessment(assessment_type):
    # Clear any existing assessment from the session
    if 'assessment' in session:
        session.pop('assessment')
        session.modified = True
    session['start_assessment'] = True
    # Redirect to the assessment page, which will now create a fresh session
    return redirect(url_for('assessment_page', assessment_type=assessment_type))


@app.route('/chat', methods=['GET', 'POST'])
def chat_page():

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
    return render_template('chat.html', messages=[])

@app.route('/new_chat')
def new_chat():
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
    # --- SIMULATED API RESPONSES ---
    movies_data = [
        # {'title': 'Inception', 'year': '2010', 'description': 'A mind-bending thriller about stealing information by entering people\'s dreams.'},
        # {'title': 'The Social Network', 'year': '2010', 'description': 'The story of the founding of Facebook and the ensuing legal battles.'},
        # {'title': 'Parasite', 'year': '2019', 'description': 'A dark comedy thriller about class discrimination and greed.'}
    ]
    songs_data = [
        # {'title': 'Blinding Lights', 'artist': 'The Weeknd'},
        # {'title': 'As It Was', 'artist': 'Harry Styles'},
        # {'title': 'Good 4 U', 'artist': 'Olivia Rodrigo'}
    ]
    news_data = [
        # {'headline': 'Global Tech Summit Focuses on AI Ethics', 'source': 'Tech Chronicle'},
        # {'headline': 'New Breakthroughs in Renewable Energy Storage', 'source': 'Science Today'},
        # {'headline': 'The Rise of Remote Work and its Impact on Urban Economies', 'source': 'Economic Times'}
    ]
    # ---------------------------------

    return render_template(
        'recommendations.html',
        movies=movies_data,
        songs=songs_data,
        news=news_data
    )

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    # If user is not logged in, redirect to login
    if 'user_data' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        updated_data = request.form.to_dict()
        print(f"Updating user data: {updated_data}")
        time.sleep(1.5) # Simulate a delay for the loading state
        return redirect(url_for('profile_page'))

    # Data for the tabs
    try:
        user_sessions_history = api_calls.get_user_sessions(
            user_id=session.get('user_data', {}).get('user_id')
        )
    except Exception as e:
        # Handle API call failure (e.g., network error, server error)
        print("Failed to fetch user details.")
        
    assessments_history = user_sessions_history.get("sessions", {}).get('assessments', [])
    talks_history = user_sessions_history.get("sessions", {}).get('talk_sessions', [])

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
        assessments=assessments_history,
        talks=talks_history
    )

@app.route('/report/<session_id>')
def report_page(session_id):
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
    
    chat_history = api_calls.get_session_chat_messages(
        user_id=session.get('user_data', {}).get('user_id'),
        session_id=session_id
    )
    messages = chat_history.get('messages', [])

    return render_template('view_chat.html', messages=messages, title=f"Chat History - {session_id}")

if __name__ == '__main__':
    app.run(debug=True)