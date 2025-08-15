
import random
import time
import groq
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from vector_search import *
import pymongo
import certifi
from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/",
    tlsCAFile=certifi.where()
)


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

if "selected_card" not in st.session_state:
    st.session_state.selected_card = []

if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = ""

if "liked" not in st.session_state:
    st.session_state["liked"] = False
if "liked_papers" not in st.session_state:
    st.session_state["liked_papers"] = set()
if "liked_papers_info" not in st.session_state:
    st.session_state["liked_papers_info"] = []
if "paper_info" not in st.session_state:
    st.session_state["paper_info"] = ""

if "results" not in st.session_state:
    st.session_state["results"] = []
if "summery" not in st.session_state:
    st.session_state["summery"] = ""

client = pymongo.MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/")
# client=pymongo.MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/my_database?retryWrites=true&w=majority")
db = client["RecommendationSystemDB"]
collection = db['UserData']
paper_collection = db['Data']

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

    st.write(f"{st.session_state.username} Welcome to Academic Paper Recommender")

    st.markdown("## 📚 Topics")
    if st.button("🔹Favourites"):
        st.session_state["mode"] = "add_favourites"
    if st.button("🔹 Liked"):
        st.session_state["mode"] = "Liked"
    if st.button("🔸Logout"):
        st.session_state["mode"] = "Logout"
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
    New_user_userName = st.text_input("Username", key="signup_username")
    New_user_password = st.text_input("Password", type="password", key="signup_password")

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
    username = st.text_input("Usernames", key="sign_in_username_11")
    password = st.text_input("Password", type="password", key="sign_in__password_11")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign In", key="sign_in_button"):
            if collection.find_one({"name": username}) and collection.find_one({"password": password}):
                st.session_state.current_user_id = collection.find_one({"name": username})['user_id']
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state['mode'] = 'add_favourites'

            else:
                st.error("Invalid credentials. Try again.")

    with col2:
        if st.button("Create Account", key="move_to_sign_Up_page_button"):
            st.session_state['mode'] = 'sign_up'


def predict_gender(pdf_url):
    prompt = f"""
    Read the research paper at {pdf_url}. Based on its abstract and main content, generate:

    1. A short summary (1–2 sentences) that captures the core idea.
    2. A long summary (3–5 bullet points) covering key findings, methods, and implications.

    Use clear, concise language suitable for students and researchers.
    """

    response = groq.Groq().chat.completions.create(
        model='llama3-70b-8192',

        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    predicted_gender = response.choices[0].message.content.strip()
    return predicted_gender


if "previous_papers" not in st.session_state:
    st.session_state.previous_papers = ""


def add_liked_papers_to_db():
    if collection.find_one({"user_id": st.session_state.current_user_id}) and "User_Liked" in collection.find_one({"user_id": st.session_state.current_user_id}) and collection.find_one({"user_id": st.session_state.current_user_id})["User_Liked"]:
        st.session_state.previous_papers = collection.find_one({"user_id": st.session_state.current_user_id})['User_Liked']
    else:
        st.session_state.previous_papers = []

    all_liked_papers = []
    # for previous_paper in st.session_state.previous_papers:
    #     if previous_paper not in st.session_state.liked_papers_info:
    #         st.session_state.liked_papers_info.append(previous_paper)
    for paper in st.session_state.previous_papers:
        if paper not in all_liked_papers:
            all_liked_papers.append(paper)

    # Add current session likes
    for paper in st.session_state.liked_papers_info:
        if paper not in all_liked_papers:
            all_liked_papers.append(paper)

    st.session_state.liked_papers_info = all_liked_papers
    collection.update_one(
        {"user_id": st.session_state.current_user_id},
        {"$set": {"User_Liked": st.session_state.liked_papers_info}},
        upsert=True
    )
if "liked_papers_dict" not in st.session_state:
    st.session_state["liked_papers_dict"] = {}

def recommendation_system():
    # st.title("Academic Paper Recommender")

    query_text = st.text_input("Search papers by keyword or topic:")
    max_results = st.slider("Number of results", 5, 100, 10)

    if st.button("Fetch Papers"):
        st.write(f"Fetching {max_results} papers for query: {query_text}")
        vector_search = VectorSearch(query_text)
        st.session_state["results"] = vector_search.encode_query()

    for idx, r in enumerate(st.session_state["results"]):
        st.session_state.paper_id = r.get('_id')
        st.session_state.summery = predict_gender(r.get('pdf_url'))
        st.markdown("---")
        st.markdown(f"****Title:**** {r.get('title', 'No Title')}")
        st.markdown(f"{st.session_state.summery}")

        st.markdown(f"[PDF Link]({r.get('pdf_url', '#')})")
        st.markdown(f"**Search Accuracy:** {r.get('score', 0):.3f}")

        col1, col2 = st.columns([1, 4])

        with col1:

            if st.button("❤️", key=f"like_{idx}"):
                isTrue = True
                if idx in st.session_state["liked_papers"]:
                    st.session_state["liked_papers"].remove(idx)
                if  st.session_state.paper_id in st.session_state.liked_papers_info:
                    st.session_state["liked_papers_info"].remove( st.session_state.liked_papers_info.index(st.session_state.paper_id))
                    isTrue = False
                if isTrue:
                    st.session_state["liked_papers"].add(idx)  # store index in set
                    st.session_state.paper_info =[ r.get('_id'), r.get('title', 'No Title'), r.get('pdf_url', '#'),
                                                   st.session_state.summery ]

                    if st.session_state.paper_info not in st.session_state.liked_papers_info:
                        st.session_state.liked_papers_info.append(st.session_state.paper_info)

        with col2:
            if idx in st.session_state["liked_papers"]:
                st.markdown(
                    "<span style='color:#ff4b4b; font-weight:bold;'>You liked this!</span>",
                    unsafe_allow_html=True
                )
        st.markdown("---")

        add_liked_papers_to_db()

    st.write(st.session_state.liked_papers_info)


if "previous_favourites" not in st.session_state:
    st.session_state.previous_favourites = ""


def add_favourites_to_db():
    if collection.find_one({"user_id": st.session_state.current_user_id}) and "Favourites" in collection.find_one({"user_id": st.session_state.current_user_id}) and collection.find_one({"user_id": st.session_state.current_user_id})["Favourites"]:
        st.session_state.previous_favourites = collection.find_one({"user_id": st.session_state.current_user_id})['Favourites']

    for previous_favourite in st.session_state.previous_favourites:
        if previous_favourite not in st.session_state.selected_card:
            st.session_state.selected_card.append(previous_favourite)

    collection.update_one(
        {"user_id": st.session_state.current_user_id},
        {"$set": {"Favourites": st.session_state.selected_card}}, upsert=True
    )


# $addToSet will avoid the duplications

def add_favourites():
    global removed_card
    st.markdown("""
            <style>
            .profile_icon {
                font-size: 32px;
                align-items: left;
            }
            </style>
            <br>
            <div class="profile_icon"><b>Add your Favourites!!</b></div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .card {
        display: inline-flex;
        padding: 0.6rem 1rem;
        margin: 0.5rem;
        border-radius: 10px;
        background: rgba(225, 25, 125, 0.8);
        color: white;
        cursor: pointer;
        transition: transform 0.2s ease, background 0.3s ease;
    }
    .card:hover {
        transform: translateY(-3px);
    }
    .card.selected {
        background: rgba(25, 125, 225, 0.9); /* selected color */
    }
    </style>
    """, unsafe_allow_html=True)
    cards = ["Machine Learning", "AI", "Cyber Security", "Deep Learning"]
    removed_card = ""

    for card in cards:
        add_card = True

        if st.button(f"🎯 {card}", key=card):
            for removing_card in st.session_state.selected_card:
                if removing_card == card:
                    st.session_state.selected_card.remove(card)
                    removed_card = card
                    add_card = False
                    break
            if add_card:
                st.session_state.selected_card.append(card)

    for clicked_card in st.session_state.selected_card:
        if not clicked_card == removed_card:
            st.success(f"You selected: {clicked_card}")
    if removed_card != "":
        st.warning(f"Removed {removed_card} from selected cards.")
        # st.write(st.session_state.selected_card)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Skip"):
            if st.session_state.selected_card:
                add_favourites_to_db()
            time.sleep(2)
            st.session_state["mode"] = "recommendation"
    with col2:
        if st.button("Done"):
            if st.session_state.selected_card:
                add_favourites_to_db()
            time.sleep(2)
            st.session_state["mode"] = "recommendation"


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
# recommendation_system()


try:
    client.admin.command('ping')
except Exception as e:
    st.error(f"Connection failed: {e}")



#solve the liked item adding ,removing
#check skip button in favourite without clicking one of  them


