import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from openai import OpenAI
import datetime

# -----------------------------
# 🔥 SAFE FIREBASE INITIALIZATION
# -----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://your-project-id-default-rtdb.firebaseio.com/"  # ← replace with your DB link
    })

# Firebase reference
content_ref = db.reference("/social_media_posts")

# -----------------------------
# 🔥 OPENAI MODEL SETUP
# -----------------------------
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")  # ← replace with your API key

def generate_social_media_content(topic, platform, tone):
    prompt = f"""
    Generate a professional social media post.

    Platform: {platform}
    Tone: {tone}
    Topic: {topic}

    Include:
    - catchy opening line
    - main message
    - call-to-action
    - 3 relevant hashtags
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# -----------------------------
# 🔥 SAVE DATA TO FIREBASE
# -----------------------------
def save_to_firebase(topic, platform, tone, output):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content_ref.push({
        "topic": topic,
        "platform": platform,
        "tone": tone,
        "content": output,
        "timestamp": now
    })

# -----------------------------
# 🔥 STREAMLIT UI
# -----------------------------
st.title("✨ AI Social Media Agent")
st.write("Generate high-quality social media posts for any platform.")

topic = st.text_input("Enter Topic")
platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "LinkedIn", "Facebook", "YouTube"])
tone = st.selectbox("Choose Tone", ["Professional", "Friendly", "Motivational", "Informative", "Funny"])

if st.button("Generate Post"):
    if topic.strip() == "":
        st.error("Please enter a topic first!")
    else:
        with st.spinner("Generating AI content..."):
            output = generate_social_media_content(topic, platform, tone)
        
        st.success("Content Generated Successfully!")
        st.write("### ✨ Your AI Generated Post:")
        st.write(output)

        # Save to Firebase
        save_to_firebase(topic, platform, tone, output)
        st.info("Saved to Firebase Database!")

# -----------------------------
# 🔥 SHOW SAVED CONTENT
# -----------------------------
if st.checkbox("View Past Generated Posts"):
    data = content_ref.get()

    if data:
        st.subheader("🗂 Past Posts from Database")
        for key, value in data.items():
            st.write(f"**Topic:** {value['topic']}")
            st.write(f"**Platform:** {value['platform']}")
            st.write(f"**Tone:** {value['tone']}")
            st.write(f"**Content:** {value['content']}")
            st.write(f"**Time:** {value['timestamp']}")
            st.write("---")
    else:
        st.info("No previous posts found.")
