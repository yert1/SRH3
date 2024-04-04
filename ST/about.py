import streamlit as st
import firebase_admin
from firebase_admin import auth
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
import pymongo



# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://ndutatracey:p431DOwzijLQGygw@cluster0.2mtghyy.mongodb.net/")
db = client.mydatabase
posts_collection = db.posts

# Function to authenticate user using Firebase
def authenticate_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        if user:
            # Check if password matches (in real-world scenario, use Firebase Authentication methods)
            # For simplicity, we're assuming the password is correct
            return user.uid
    except firebase_admin.auth.AuthError as e:
        st.error("Invalid email or password")
        return None

# Function to fetch posts from MongoDB
def fetch_posts(user_handle=None):
    query = {}
    if user_handle:
        query["user_handle"] = user_handle
    posts = posts_collection.find(query)
    return posts

# Function to add a post
def add_post(user_handle, content):
    post = {
        "user_handle": user_handle,
        "content": content,
        "posted_at": datetime.now()
    }
    posts_collection.insert_one(post)

# Function to delete a post
def delete_post(post_id):
    posts_collection.delete_one({'_id': ObjectId(post_id)})

def delete_all_posts_by_user(user_handle):
    if st.session_state.user_handle:
        posts = fetch_posts(user_handle)
        for post in posts:
            delete_post(post["_id"])

# Streamlit UI
def app():
    user_posts = {}


    # Sidebar menu
    page = st.selectbox("Forums Navigation", ["Home", "Add Post"])
    
    if page == "Home":
        if st.session_state.user_handle:
            # Display posts
            st.write("## Posts")
            posts = fetch_posts()
            for post in posts:
                st.write(f"@ {post['user_handle']}")
                st.write(f" {post['content']}")
                st.write(f"**Posted At:** {post['posted_at']}")
                st.markdown("---")
                # Add post to the user_posts dictionary
                user_posts[str(post["_id"])] = post
        else:
            st.write("Please log in for access")
    elif page == "Add Post":
        # Post section
        st.write("## Add Post")
        if st.session_state.user_handle:
            content = st.text_area("Write your post here:")
            if st.button("Post"):
                add_post(st.session_state.user_handle, content)
                st.success("Post added successfully")

            # Show user's posts
            user_posts = fetch_posts(st.session_state.user_handle)
            st.markdown("---")
            if user_posts:
                st.write("## Your Posts")
                for post in user_posts:
                    st.write(f"{post['content']}")
                    st.write(f"**Posted At:** {post['posted_at']}")
                    st.markdown("---")
                    
            if st.button("Delete all posts by user"):
                delete_all_posts_by_user(st.session_state.user_handle) 
                st.success("all posts deleted")   
        
        
        else:
            st.write("Please log in to add a post.")
    
    
if __name__ == "__main__":
    app()

