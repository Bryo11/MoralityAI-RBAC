
import hashlib
import csv
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

USERS = {
    "admin@example.com": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "ADMIN"
    },
    "user@example.com": {
        "password": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "USER"
    }
}

current_user = {"email": None, "role": None}

def authenticate(email, password, login_mode):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user = USERS.get(email)

    if not user or user["password"] != hashed:
        return None

    if login_mode == "ADMIN" and user["role"] != "ADMIN":
        return None

    return {"email": email, "role": user["role"]}

class RoleSelectionScreen(Screen):
    pass

class LoginScreen(Screen):
    login_mode = StringProperty("")

    def do_login(self):
        email = self.ids.email.text
        password = self.ids.password.text

        user = authenticate(email, password, self.login_mode)
        if user:
            global current_user
            current_user = user

            if user["role"] == "ADMIN":
                self.manager.current = "admin"
            else:
                self.manager.current = "user"
        else:
            self.ids.message.text = "Invalid credentials or unauthorized access."

class UserScreen(Screen):
    def submit_feedback(self):
        feedback = self.ids.feedback.text
        if not feedback:
            return

        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "feedback.csv")

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([current_user["email"], feedback])

        self.ids.feedback.text = ""
        self.ids.status.text = "Feedback submitted successfully."

class AdminScreen(Screen):
    def load_feedback(self):
        file_path = os.path.join("data", "feedback.csv")
        self.ids.feedback_list.text = ""

        if not os.path.exists(file_path):
            self.ids.feedback_list.text = "No feedback found."
            return

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                self.ids.feedback_list.text += f"User: {row[0]}\nFeedback: {row[1]}\n\n"

KV = '''
ScreenManager:
    RoleSelectionScreen:
    LoginScreen:
    UserScreen:
    AdminScreen:

<RoleSelectionScreen>:
    name: "role_select"
    BoxLayout:
        orientation: "vertical"
        spacing: 20
        padding: 40
        Button:
            text: "Login as User"
            on_release:
                app.root.get_screen("login").login_mode = "USER"
                app.root.current = "login"
        Button:
            text: "Login as Administrator"
            on_release:
                app.root.get_screen("login").login_mode = "ADMIN"
                app.root.current = "login"

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: "vertical"
        spacing: 10
        padding: 40
        Label:
            text: "Login"
        TextInput:
            id: email
            hint_text: "Email"
            multiline: False
        TextInput:
            id: password
            hint_text: "Password"
            password: True
            multiline: False
        Button:
            text: "Login"
            on_release: root.do_login()
        Label:
            id: message
            text: ""
        Button:
            text: "Back"
            on_release: app.root.current = "role_select"

<UserScreen>:
    name: "user"
    BoxLayout:
        orientation: "vertical"
        padding: 40
        spacing: 10
        Label:
            text: "User Dashboard - Submit Feedback"
        TextInput:
            id: feedback
            hint_text: "Enter feedback here"
        Button:
            text: "Submit Feedback"
            on_release: root.submit_feedback()
        Label:
            id: status
            text: ""
        Button:
            text: "Logout"
            on_release: app.root.current = "role_select"

<AdminScreen>:
    name: "admin"
    BoxLayout:
        orientation: "vertical"
        padding: 40
        spacing: 10
        Label:
            text: "Admin Dashboard - View Feedback"
        ScrollView:
            Label:
                id: feedback_list
                text: ""
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
        Button:
            text: "Refresh Feedback"
            on_release: root.load_feedback()
        Button:
            text: "Logout"
            on_release: app.root.current = "role_select"
'''

class RBACApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    RBACApp().run()
