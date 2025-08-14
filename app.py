

import random
import time

import streamlit as st
from vector_search import *
import pymongo

if "mode" not in st.session_state:
    st.session_state["mode"] = "headTopic"  # default mode

if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""
if "results" not in st.session_state:
    st.session_state["results"] = []
if "vector_search" not in st.session_state:
    st.session_state["vector_search"] =""
if "topic" not in st.session_state:
    st.session_state["topic"] = ""

if "username" not in st.session_state:
    st.session_state["username"] = ""
if "Password" not in st.session_state:
    st.session_state["Password"] = ""
if "new_user" not in st.session_state:
    st.session_state["new_user"] = {"New_user_userName": "", "New_user_password": "", "submitted": False}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


client = MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/")
db =  client["RecommendationSystemDB"]
collection =db['UserData']


with st.sidebar:
    st.markdown("""
        <style>
        .profile_icon {
            font-size: 52px;
            align-items: center;
        }
        </style>
    
        <div class="profile_icon">🙍🏻</div>
    """, unsafe_allow_html=True)
    # st.title('🙍🏻‍♂️')

    st.markdown("## 📚 Topics")
    if st.button("🔹Favourites"):
        st.session_state.topic = "Topic 1"
    # if st.button("🔹 Psychology aspects"):
    #     st.session_state.topic = "Topic 2"
    if st.button("🔸Logout"):
        st.session_state.topic = "Topic 3"
st.markdown("""
            <style>
            .main-topic {
                font-size: 51px;
                color: #ff6f00;
                font-weight: bold;
                text-align: center;
                border-bottom: 2px solid #ff6f00;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            </style>
            <div class="main-topic">Academic Paper Recommender</div>
        """, unsafe_allow_html=True)
def headTopic():
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", key="move_to_sign_in_page"):
            st.session_state["mode"] = "sign_in"


    with col2:
        if st.button("SignUp", key="move_to_sign_up_page"):
            st.session_state["mode"] = "sign_up"





def sign_up():
    st.title("🔐 Sign Up")
    New_user_userName=st.text_input("Username", key="signup_username")
    New_user_password=st.text_input("Password",type="password", key="signup_password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Submit", key="signup_button"):
            st.session_state["new_user"]["New_user_userName"] = New_user_userName
            st.session_state["new_user"]["New_user_password"] = New_user_password
            st.session_state["new_user"]["submitted"] = True

            id = f"{New_user_userName}{New_user_password}{New_user_userName}"

            if collection.find_one({"user_id": id}):
                st.error("Username already exists. Try again.")

            else:
                collection.update_one(
                    {"user_id": id},  # search filter
                    {"$setOnInsert": {  # only set if inserting
                        "name": New_user_userName,
                        "password": New_user_password
                    }},
                    upsert=True
                )
                print(f"User: {New_user_userName} account was created successfully.")
                time.sleep(1)
                st.session_state['mode'] = 'sign_in'

    with col2:
        if st.button("Login", key="move_to_sign_in_page_button"):
            st.session_state['mode'] = 'sign_in'


def sign_in():
    st.title("🔐 Sign In")
    username=st.text_input("Usernames", key="sign_in_username_11")
    password = st.text_input("Password",type="password", key="sign_in__password_11")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign In", key="sign_in_button"):
            if collection.find_one({"name": username}) and collection.find_one({"password": password}):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state['mode'] = 'add_favourites'

            else:
                st.error("Invalid credentials. Try again.")

    with col2:
        if st.button("Create Account", key="move_to_sign_Up_page_button"):
            st.session_state['mode'] = 'sign_up'


def recommendation_system():
    # abstract = st.text_area("Paste abstract here:")
    st.title("Academic Paper Recommender")

    query_text = st.text_input("Search papers by keyword or topic:")
    max_results = st.slider("Number of results", 5, 100, 10)

    if st.button("Fetch Papers"):
        st.write(f"Fetching {max_results} papers for query: {query_text}")
        vector_search = VectorSearch(query_text)
        results = vector_search.encode_query()
        for r in results:
            st.markdown(f"**Score:** {r.get('score', 0):.3f}")
            st.markdown(f"**Title:** {r.get('title', 'No Title')}")
            st.markdown(f"[PDF Link]({r.get('pdf_url', '#')})")
            st.markdown("---")


def add_favourites():
    st.markdown("""
            <style>
            .profile_icon {
                font-size: 32px;
                align-items: center;
            }
            </style>

            <div class="profile_icon"><b>Add your Favourites!!</b></div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Skip"):
            st.session_state["mode"] = "recommendation"
    with col2:
        if st.button("Done"):
            st.session_state["mode"] = "recommendation"




# if st.session_state["mode"] == "add_favourites":
#     add_favourites()
# elif st.session_state["mode"] == "recommendation":
#     recommendation_system()
# elif st.session_state["mode"] == "sign_in":
#     sign_in()
# elif st.session_state["mode"] == "sign_up":
#     sign_up()

# Initialize session state
if st.session_state["mode"] == "headTopic":
    headTopic()
elif st.session_state["mode"] == "sign_in":
    sign_in()
elif st.session_state["mode"] == "sign_up":
    sign_up()
elif st.session_state["mode"] == "add_favourites":
    add_favourites()
elif st.session_state["mode"] == "recommendation":
    recommendation_system()
# if not st.button("Skip") or st.button("Done")   :
#     add_favourites()









