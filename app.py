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

temp_user_password = generate_password_hash(os.environ.get('TEMP_USER_PASSWORD', 'password'))
users = {
            1: {'username': 'admin', 'password': temp_user_password},
            2: {'username': 'tobey', 'password': temp_user_password},
            3: {'username': 'reef', 'password': temp_user_password}
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
    def __init__(self, base_url, model, system_prompt="", user_id=None, agent_name="ollama"):
        self.base_url = base_url
        self.model = model
        self.chat_history = self.load_chat_history(user_id, agent_name)
        self.system_prompt = system_prompt
        self.keep_alive = "60m"

    def load_chat_history(self, user_id, agent_name):
        if os.path.exists(f"chats/{agent_name}-chat_history-{user_id}.json"):
            with open(f"chats/{agent_name}-chat_history-{user_id}.json", "r") as file:
                return json.load(file)
        return []

    def save_chat_history(self, user_id, agent_name):
        with open(f"chats/{agent_name}-chat_history-{user_id}.json", "w") as file:
            json.dump(self.chat_history, file)

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

    def chat(self, user_input, agent_name):
        user_id = current_user.get_id()
        usernaeme = current_user.username
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "bot", "content": f"The current users name is {usernaeme}."})
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
    return render_template('index.html')

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
    response = chatbot.chat(user_input, "mell")
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
    response = chatbot.chat(user_input, "reef")
    return jsonify({'response': response})

# Marley AI Agent
@app.route('/marley')
@login_required
def marley():
    user_id = current_user.get_id()
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="", user_id=user_id, agent_name="marley")
    chat_history = chatbot.chat_history
    return render_template('marley/index.html', chat_history=chat_history)

@app.route('/marley-chat', methods=['POST'])
@login_required
def marley_handle_chat():
    user_input = request.form['user_input']
    base_url = "http://192.168.4.14:11434"
    model = "deep-mell:latest"
    chatbot = OllamaChatbot(base_url, model, system_prompt="You're a cannabis lover and know everything cannabis from the island of Jamaica. Your name is Marley. Cannabis is legal. You're here to help. Please be respectful.")
    response = chatbot.chat(user_input, "marley")
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