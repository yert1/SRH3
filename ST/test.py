# Modules
import pyrebase
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as componentsu
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import json

# Configuration Key
firebaseConfig = {
  'apiKey': "AIzaSyDw0M6N6ZW1O-hcAJOJGIn0t3Mq1ULn8MA",
  'authDomain': "streamlit-2-8b3b5.firebaseapp.com",
  'databaseURL': "https://streamlit-2-8b3b5-default-rtdb.europe-west1.firebasedatabase.app",
  'projectId': "streamlit-2-8b3b5",
  'storageBucket': "streamlit-2-8b3b5.appspot.com",
  'messagingSenderId': "603770947784",
  'appId': "1:603770947784:web:12b7c6e43cf02ad62b3dfd",
  'measurementId': "G-Y8K1VTYWLH"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()


def render_signup():
    st.subheader("Sign Up")
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    handle = st.text_input('Please input your app handle name', value='Default')
    submit = st.button('Create my account')

    if submit:
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success('Your account is created successfully!')
            # Sign in
            user = auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])
            st.write('Welcome ' + handle)
            st.info('Login via login drop down selection')
        
        except Exception as e:
            st.error("An error occurred during signup. Try again.")


def render_login(session_state):
    st.subheader("Login")
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    login_button = st.button('Login')

    if login_button:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_data = db.child(user['localId']).get().val()
            user_handle = user_data["Handle"]
            session_state.logged_in = True
            session_state.user_handle = user_handle
            st.success(f"Welcome , {user_handle}!")
        except Exception as e:
            st.error("An error occurred during login. Please check your email and password.")    
    
        

# Function to render sign-out button
def render_sign_out(session_state):
    sign_out_button = None  # Initialize sign_out_button

    if session_state.logged_in:
        st.write(f"Handle: {session_state.user_handle}")
        sign_out_button = st.button("Sign Out")
        

    if sign_out_button:
        session_state.logged_in = False
        session_state.user_handle = None
        st.success("You have been signed out.")


# Main function
def app():
    st.title("Your Account")
    
    
    # Create session state
    session_state = st.session_state
    if "logged_in" not in session_state:
        session_state.logged_in = False
        session_state.user_handle = None
    
    if session_state.logged_in:
        render_sign_out(session_state)
    else:
        # Display selectbox to choose between login and signup forms
        form_choice = st.selectbox("Choose Form", ["Login", "Signup"])
        
        if form_choice == "Signup":
            render_signup()
        else:
            render_login(session_state)

if __name__ == "__main__":
    app()
