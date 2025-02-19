from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'A3f6eXE1d2ukoMxnVdjm4mIXB0tRpZNY'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {
            1: {'username': 'admin', 'password': generate_password_hash('password')},
            2: {'username': 'tobey', 'password': generate_password_hash('password')},
            3: {'username': 'reef', 'password': generate_password_hash('password')}
        }

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user_data = users.get(int(user_id))
    if user_data:
        return User(int(user_id), user_data['username'], user_data['password'])
    return None

class OllamaChatbot:
    def __init__(self, base_url, model, system_prompt="", user_id=None):
        self.base_url = base_url
        self.model = model
        self.chat_history = self.load_chat_history(user_id)
        self.system_prompt = system_prompt
        self.keep_alive = "10m"
    #the init function is used to initialize the chatbot with the base url, model, chat history, system prompt, and keep alive time


    def load_chat_history(self, user_id):
        if os.path.exists(f"chat_history-{user_id}.json"):
            with open(f"chat_history-{user_id}.json", "r") as file:
                return json.load(file)
        return []
    #the load_chat_history function is used to load the chat history from the chat_history.json file


    def save_chat_history(self, user_id):
        with open(f"chat_history-{user_id}.json", "w") as file:
            json.dump(self.chat_history, file)
    #the save_chat_history function is used to save the chat history to the chat_history.json file


    def generate_completion(self, prompt, system_message="", stream=True):
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "system": system_message,
            "keep_alive": self.keep_alive
        }
        response = requests.post(f"{self.base_url}/api/generate", headers=headers, data=json.dumps(data), stream=stream)
        
        if stream:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        response_part = json.loads(line.decode('utf-8'))['response']
                        full_response += response_part
                        yield response_part
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"\nError parsing response: {e}")
                        return
        else:
            try:
                return response.json()['response']
            except (json.JSONDecodeError, KeyError) as e:
                print(f"\nError parsing response: {e}")
                return ""
    #the generate_completion function is used to generate a completion from the llama server using the prompt, system message, and keep alive time


    def chat(self, user_input, agent_name="ollama"):
        user_id = current_user.get_id()
        self.chat_history.append({"role": "user", "content": user_input})
        prompt = "\n".join([f"{entry['role']}: {entry['content']}" for entry in self.chat_history])
        try:
            full_message = ""
            for message in self.generate_completion(prompt, self.system_prompt):#generates completion
                full_message += message
            self.chat_history.append({"role": "bot", "content": full_message})#appends completion to chat history
            self.save_chat_history(user_id, agent_name)
            return full_message
        except requests.exceptions.RequestException as e:#checks if there is an error
            print(f"\nError: {e}")
            return "Error: Failed to generate response."
    #the chat function is used to handle the chat functionality of the chatbot, including user input, generating responses, and saving chat history

@app.route('/')
def index():
    return "Index TBD!"

# Mell AI Agent
@app.route('/mell')
@login_required
def mell():
    user_id = current_user.get_id()
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="", user_id=user_id, agent_name="mell")
    chat_history = chatbot.chat_history
    return render_template('mell/index.html', chat_history=chat_history)

@app.route('/mell-chat', methods=['POST'])
@login_required
def mell_handle_chat():
    user_input = request.form['user_input']
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="Your name is Mell a friendly Tech Support agent. You're here to help.")
    response = chatbot.chat(user_input)
    return jsonify({'response': response})


# Reef AI Agent
@app.route('/reef')
@login_required
def reef():
    user_id = current_user.get_id()
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="", user_id=user_id, agent_name="reef")
    chat_history = chatbot.chat_history
    return render_template('reef/index.html', chat_history=chat_history)

@app.route('/reef-chat', methods=['POST'])
@login_required
def reef_handle_chat():
    user_input = request.form['user_input']
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="You're a suffer dude right from CA. Your name is Reef. You love and live surfing.")
    response = chatbot.chat(user_input)
    return jsonify({'response': response})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = next((user for user_id, user in users.items() if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            loaded_user = load_user(list(users.keys())[list(users.values()).index(user)])
            login_user(loaded_user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
#this condition is used to run the web application if the app.py file is executed directly
