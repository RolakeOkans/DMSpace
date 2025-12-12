#import libraries
import os
from datetime import datetime
import hashlib
import time
import random

import streamlit as st
import openai
from openai import OpenAI
from dotenv import load_dotenv


#Load env + configure API client

load_dotenv()

# Try to get API key from environment, then from streamlit secrets
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

if api_key is not None:
    openai.api_key = api_key
    client = OpenAI(api_key=api_key)
    DEMO_MODE = False
else:
    client = None
    DEMO_MODE = True

#Constants/configuration

SYSTEM_PROMPT="You are a highly empathetic and supportive assistant. Your main goal is to listen actively and respond with understanding and compassion. Use gentle language, acknowledge the user's feelings, and offer encouragement or helpful, non-judgmental advice when appropriate. Focus on creating a safe and warm environment for the user. Be culturally sensitive and respectful of different backgrounds, perspectives, and experiences. Do not claim to be a therapist or crisis service."

#Default model
DEFAULT_MODEL= "gpt-4o-mini"

# Cultural contexts for reflection
CULTURAL_CONTEXTS = {
    "western": {
        "name": "Western/Individualistic",
        "values": ["personal growth", "self-care", "boundaries", "independence"],
        "reflection_style": "Focus on your personal needs and growth"
    },
    "collectivist": {
        "name": "Collectivist/Community-Focused",
        "values": ["family harmony", "community", "interdependence", "group wellbeing"],
        "reflection_style": "Consider how this affects your relationships and community"
    },
    "spiritual": {
        "name": "Spiritual/Faith-Based",
        "values": ["purpose", "faith", "acceptance", "inner peace"],
        "reflection_style": "Reflect on meaning and spiritual growth"
    },
    "balanced": {
        "name": "Balanced/Hybrid",
        "values": ["both personal and collective wellbeing", "cultural respect", "flexibility"],
        "reflection_style": "Honor both yourself and your connections"
    }
}

# ============ GAME 1: WORD GAME ============

WELLNESS_WORDS = [
    ("XAEITNY", "ANXIETY"),
    ("MLAC", "CALM"),
    ("VRABE", "BRAVE"),
    ("ULFGRTA", "GRATEFUL"),
    ("FULECAPE", "PEACEFUL"),
    ("YJOYLF", "JOYFUL"),
    ("RTOCOSMF", "COMFORT"),
    ("EOHP", "HOPE"),
    ("RTSONG", "STRONG"),
    ("NEIHT", "INTENT"),
]

def init_game_state():
    """Initialize all game states"""
    if "word_game_score" not in st.session_state:
        st.session_state.word_game_score = 0
    if "word_game_current" not in st.session_state:
        st.session_state.word_game_current = 0
    if "word_game_words" not in st.session_state:
        st.session_state.word_game_words = random.sample(WELLNESS_WORDS, 5)
    if "word_game_guessed" not in st.session_state:
        st.session_state.word_game_guessed = False
    
    if "gratitude_jar" not in st.session_state:
        st.session_state.gratitude_jar = []
    if "gratitude_streak" not in st.session_state:
        st.session_state.gratitude_streak = 0
    if "gratitude_last_date" not in st.session_state:
        st.session_state.gratitude_last_date = None
    
    if "breathing_sessions" not in st.session_state:
        st.session_state.breathing_sessions = 0
    if "breathing_total_time" not in st.session_state:
        st.session_state.breathing_total_time = 0

def show_word_game():
    """Word unscramble game"""
    st.markdown("### 🔍 Word Detective")
    st.caption("Unscramble wellness words! 30 seconds per word.")
    
    init_game_state()
    
    if st.session_state.word_game_current >= 5:
        st.markdown(f"## 🎉 Game Complete!")
        st.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.2); border-radius: 12px; padding: 2rem; border: 1px solid rgba(102, 126, 234, 0.5); text-align: center;">
            <h2 style="color: #fff; margin: 0;">Final Score: {st.session_state.word_game_score}</h2>
            <p style="color: rgba(255,255,255,0.9); margin-top: 1rem;">You unscrambled {st.session_state.word_game_current}/5 words!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Play Again", use_container_width=True, key="word_replay"):
                st.session_state.word_game_score = 0
                st.session_state.word_game_current = 0
                st.session_state.word_game_words = random.sample(WELLNESS_WORDS, 5)
                st.session_state.word_game_guessed = False
                st.rerun()
        with col2:
            if st.button("Back to Games", use_container_width=True, key="word_back"):
                st.rerun()
    else:
        scrambled, answer = st.session_state.word_game_words[st.session_state.word_game_current]
        
        st.markdown(f"**Word {st.session_state.word_game_current + 1}/5**")
        st.write(f"Score: {st.session_state.word_game_score}")
        
        st.markdown("")
        st.markdown(f"# {scrambled}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            guess = st.text_input("Your answer:", key=f"word_guess_{st.session_state.word_game_current}", label_visibility="collapsed")
        with col2:
            submit = st.button("Submit", use_container_width=True)
        
        if submit and guess:
            if guess.upper() == answer:
                st.success(f"✅ Correct! It's {answer}!")
                st.session_state.word_game_score += 10
                time.sleep(1.5)
                st.session_state.word_game_current += 1
                st.session_state.word_game_guessed = False
                st.rerun()
            else:
                st.error(f"❌ Not quite. The answer is {answer}.")
                time.sleep(1.5)
                st.session_state.word_game_current += 1
                st.session_state.word_game_guessed = False
                st.rerun()


def show_gratitude_jar():
    """Gratitude jar game"""
    st.markdown("### 🏺 Gratitude Jar")
    st.caption("Add what you're grateful for today. Build your jar over time.")
    
    init_game_state()
    
    today = datetime.now().date()
    if st.session_state.gratitude_last_date:
        last_date = datetime.fromisoformat(st.session_state.gratitude_last_date).date()
        if last_date == today:
            st.info(f"✨ You already added gratitude today! Streak: {st.session_state.gratitude_streak} days")
        elif (today - last_date).days == 1:
            pass
        else:
            st.session_state.gratitude_streak = 0
    
    st.markdown("**What are you grateful for today?**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        gratitude_text = st.text_input("", placeholder="I'm grateful for...", label_visibility="collapsed")
    with col2:
        if st.button("Add ✨", use_container_width=True):
            if gratitude_text.strip():
                st.session_state.gratitude_jar.append({
                    "text": gratitude_text.strip(),
                    "date": today.isoformat()
                })
                
                if not st.session_state.gratitude_last_date or datetime.fromisoformat(st.session_state.gratitude_last_date).date() != today:
                    st.session_state.gratitude_streak += 1
                    st.session_state.gratitude_last_date = datetime.now().isoformat()
                
                st.success("Added to your jar! 🌟")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Write something to add!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Gratitudes", len(st.session_state.gratitude_jar))
    with col2:
        st.metric("Current Streak", f"{st.session_state.gratitude_streak} days")
    with col3:
        if st.button("🎲 Random Gratitude", use_container_width=True):
            if st.session_state.gratitude_jar:
                random_item = random.choice(st.session_state.gratitude_jar)
                st.info(f"💭 Reminder: {random_item['text']}")
    
    st.markdown("---")
    
    if st.session_state.gratitude_jar:
        st.markdown("**Your Gratitudes:**")
        for i, item in enumerate(reversed(st.session_state.gratitude_jar[-10:])):
            st.caption(f"✨ {item['text']}")


def show_breathing_exercise():
    """Guided breathing exercise"""
    st.markdown("### 🫁 Breathing Exercise")
    st.caption("Guided breathing to calm your mind and body.")
    
    init_game_state()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("4-7-8\n(Anxiety)", use_container_width=True, key="breath_478"):
            run_breathing_exercise("4-7-8", 4, 7, 8, "Calm Anxiety")
    
    with col2:
        if st.button("5-5-5\n(Relax)", use_container_width=True, key="breath_555"):
            run_breathing_exercise("5-5-5", 5, 5, 5, "Deep Relaxation")
    
    with col3:
        if st.button("Box\n(Focus)", use_container_width=True, key="breath_box"):
            run_breathing_exercise("Box", 4, 4, 4, "Mental Focus")
    
    st.markdown("---")
    st.markdown("**Your Sessions:**")
    st.metric("Total Sessions", st.session_state.breathing_sessions)
    if st.session_state.breathing_total_time > 0:
        st.caption(f"Total time: {st.session_state.breathing_total_time} seconds")


def run_breathing_exercise(name, inhale, hold, exhale, purpose):
    """Run the breathing exercise animation"""
    st.markdown(f"## {name} Breathing - {purpose}")
    
    placeholder = st.empty()
    
    cycles = 3
    
    for cycle in range(cycles):
        for i in range(inhale):
            with placeholder.container():
                st.markdown(f"""
                <div style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin: 2rem 0;">
                        <span style="display: inline-block; width: {100 + (i/inhale)*100}px; height: {100 + (i/inhale)*100}px; border-radius: 50%; background: rgba(102, 126, 234, 0.3); border: 2px solid rgba(102, 126, 234, 0.8);"></span>
                    </div>
                    <h3 style="color: #fff;">INHALE... {i+1}/{inhale}</h3>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(1)
        
        for i in range(hold):
            with placeholder.container():
                st.markdown(f"""
                <div style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin: 2rem 0;">
                        <span style="display: inline-block; width: 200px; height: 200px; border-radius: 50%; background: rgba(102, 126, 234, 0.5); border: 2px solid rgba(102, 126, 234, 0.8);"></span>
                    </div>
                    <h3 style="color: #fff;">HOLD... {i+1}/{hold}</h3>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(1)
        
        for i in range(exhale):
            size = 200 - (i/exhale)*100
            with placeholder.container():
                st.markdown(f"""
                <div style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin: 2rem 0;">
                        <span style="display: inline-block; width: {size}px; height: {size}px; border-radius: 50%; background: rgba(102, 126, 234, 0.2); border: 2px solid rgba(102, 126, 234, 0.6);"></span>
                    </div>
                    <h3 style="color: #fff;">EXHALE... {i+1}/{exhale}</h3>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(1)
    
    placeholder.empty()
    st.success(f"✅ Great job! You completed {cycles} cycles of {name} breathing.")
    
    st.session_state.breathing_sessions += 1
    st.session_state.breathing_total_time += (cycles * (inhale + hold + exhale))
    
    time.sleep(2)
    st.rerun()


# ============ MAIN APP FUNCTIONS ============

CRISIS_KEYWORDS = [
    "kill myself", "killing myself", "want to die", "want to disappear",
    "end it all", "end my life", "suicide", "suicidal", "hurt myself",
    "self-harm", "self harm", "cut myself", "overdose", "take my life",
    "no reason to live", "can't go on",
]

CRISIS_RESPONSE = (
    "Thank you for sharing that. What you're describing sounds really serious, "
    "and you deserve support from a real person, not just an app.\n\n"
    "DMSpace can't provide crisis help or emergency support. If you're in "
    "immediate danger or feel like you might hurt yourself, please contact "
    "local emergency services if you can, or reach out to a trusted person in "
    "your life.\n\n"
    "If it's available in your region, you can also reach out to a crisis "
    "hotline or text line for immediate support."
)

def is_possible_crisis(text:str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in CRISIS_KEYWORDS)

def generate_assistant_reply(conversation_messages):
    if DEMO_MODE or not client:
        return "💬 Chat is in demo mode. To enable AI responses, add your OpenAI API key to a .env file or Streamlit secrets."
    
    try:
        cultural_context = st.session_state.get("cultural_context", "balanced")
        context_info = CULTURAL_CONTEXTS.get(cultural_context, CULTURAL_CONTEXTS["balanced"])
        
        cultural_prompt = f"\nAlso consider this user's perspective: {context_info['reflection_style']}"
        adjusted_prompt = SYSTEM_PROMPT + cultural_prompt
        
        if st.session_state.get("show_debug"):
            st.info(f"🔍 **Debug**: Using cultural prompt: '{context_info['reflection_style']}'")
        
        api_messages = [{"role": "system", "content": adjusted_prompt}] + conversation_messages

        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=api_messages,
            stream=True,
        )

        response_text = st.write_stream(stream)
        return response_text
    
    except openai.RateLimitError:
        st.error("We've hit the OpenAI usage limit for now. Please wait a bit or check your billing/usage")
    except Exception as e:
        st.error("Something went wrong while generating a response.")
        st.write(e)
    
    return None

def generate_journal_prompts(emotion_log):
    if DEMO_MODE or not client:
        return "📝 Journal prompts require API key. Add OPENAI_API_KEY to .env file."
    
    recent_entries = emotion_log[-5:]
    context_lines = []
    for entry in recent_entries:
        context_lines.append(f"User: {entry['user_text']}")
        context_lines.append(f"DMSpace: {entry['assistant_text']}")
        context_lines.append("")

    context_text = "\n".join(context_lines)
    
    cultural_context = st.session_state.get("cultural_context", "balanced")
    context_info = CULTURAL_CONTEXTS.get(cultural_context, CULTURAL_CONTEXTS["balanced"])

    prompt_text = (
        "You are a gentle journaling coach. "
        "Based on the user's recent emotional check-ins and the supportive "
        "reflections they received, identify the main emotional themes and "
        "generate 3 short, simple journaling prompts that feel warm and human.\n\n"
        f"The user values: {', '.join(context_info['values'])}\n"
        f"Perspective: {context_info['reflection_style']}\n\n"
        "Here are some recent check-ins:\n"
        f"{context_text}\n\n"
        "First, in 1–2 short sentences, summarize the overall themes you're noticing. "
        "Then, on new lines, return 3 journaling prompts as a numbered list."
    )

    try:
        resp = client.chat.completions.create(
            model=st.session_state.get("openai_model", DEFAULT_MODEL),
            messages=[
                {"role": "system", "content": "You create gentle, supportive journaling prompts that respect diverse cultural perspectives."},
                {"role": "user", "content": prompt_text},
            ],
        )
        return resp.choices[0].message.content
    except Exception:
        return None

def init_peer_state():
    if "peers" not in st.session_state:
        st.session_state.peers = {}
    if "peer_chats" not in st.session_state:
        st.session_state.peer_chats = {}
    if "my_user_id" not in st.session_state:
        st.session_state.my_user_id = hashlib.md5(
            str(datetime.now().timestamp()).encode()
        ).hexdigest()[:6]
    if "cultural_context" not in st.session_state:
        st.session_state.cultural_context = "balanced"
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False

def extract_themes(messages):
    themes = {
        "anxiety": 0, "depression": 0, "relationships": 0,
        "work_school": 0, "identity": 0, "family": 0,
    }
    
    keywords = {
        "anxiety": ["anxious", "worried", "nervous", "panic", "stress", "overwhelm"],
        "depression": ["sad", "depressed", "hopeless", "down", "empty", "lonely"],
        "relationships": ["friend", "partner", "love", "breakup", "dating", "conflict"],
        "work_school": ["work", "school", "job", "deadline", "exam", "pressure"],
        "identity": ["identity", "culture", "belong", "different", "acceptance"],
        "family": ["parent", "family", "sibling", "home", "support"],
    }
    
    user_text = " ".join([m["content"] for m in messages if m["role"] == "user"]).lower()
    
    for theme, words in keywords.items():
        themes[theme] = sum(user_text.count(word) for word in words)
    
    return {k: v for k, v in themes.items() if v > 0}

def create_profile(user_id, messages):
    if len(messages) < 2:
        return None
    
    themes = extract_themes(messages)
    if not themes:
        return None
    
    num_messages = len([m for m in messages if m["role"] == "user"])
    if num_messages < 5:
        stage = "🌱 Just Starting"
    elif num_messages < 15:
        stage = "🔍 Exploring"
    else:
        stage = "✨ Reflecting"
    
    return {
        "user_id": user_id,
        "top_themes": sorted(themes.items(), key=lambda x: x[1], reverse=True)[:2],
        "stage": stage,
        "opt_in": False,
    }

def match_score(profile1, profile2):
    if not profile1 or not profile2:
        return 0
    
    themes1 = set(t[0] for t in profile1.get("top_themes", []))
    themes2 = set(t[0] for t in profile2.get("top_themes", []))
    
    theme_overlap = len(themes1 & themes2) / max(len(themes1 | themes2), 1)
    score = theme_overlap * 50
    
    if profile1["stage"] == profile2["stage"]:
        score += 50
    else:
        score += 25
    
    return int(score)

def find_matches(my_id, min_score=40):
    my_profile = st.session_state.peers.get(my_id)
    
    if not my_profile or not my_profile.get("opt_in"):
        return []
    
    matches = []
    for user_id, profile in st.session_state.peers.items():
        if user_id == my_id or not profile.get("opt_in"):
            continue
        
        score = match_score(my_profile, profile)
        if score >= min_score:
            matches.append((user_id, score))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

def create_peer_chat(user1, user2):
    chat_id = hashlib.md5(f"{sorted([user1, user2])}".encode()).hexdigest()[:8]
    
    for cid in st.session_state.peer_chats:
        if set(st.session_state.peer_chats[cid]["participants"]) == {user1, user2}:
            return cid
    
    st.session_state.peer_chats[chat_id] = {
        "participants": [user1, user2],
        "messages": [],
        "created": datetime.now().isoformat(),
    }
    return chat_id

def create_test_profiles():
    test_data = {
        "user1": {
            "messages": [
                {"role": "user", "content": "I've been feeling really anxious about my job lately"},
                {"role": "assistant", "content": "That sounds stressful. Tell me more about what's making you anxious."},
                {"role": "user", "content": "The deadline pressure is overwhelming and I worry I'm not good enough"},
                {"role": "assistant", "content": "Those are common feelings. You're being hard on yourself."},
                {"role": "user", "content": "Yeah, I struggle with work stress and self-doubt a lot"},
            ]
        },
        "user2": {
            "messages": [
                {"role": "user", "content": "I'm dealing with anxiety at work"},
                {"role": "assistant", "content": "Work anxiety is really common. What's triggering it?"},
                {"role": "user", "content": "Panic about meetings and performance reviews stress me out"},
                {"role": "assistant", "content": "That's tough. Many people feel this way about work."},
            ]
        },
        "user3": {
            "messages": [
                {"role": "user", "content": "I'm having relationship issues with my partner"},
                {"role": "assistant", "content": "That's difficult. What's happening?"},
                {"role": "user", "content": "We're fighting more and I feel disconnected from them"},
                {"role": "assistant", "content": "Communication is key in relationships."},
                {"role": "user", "content": "I love them but the conflict is draining"},
            ]
        },
        "user4": {
            "messages": [
                {"role": "user", "content": "I feel really depressed and empty lately"},
                {"role": "assistant", "content": "I'm sorry you're feeling this way. Tell me more."},
                {"role": "user", "content": "Nothing feels meaningful. I'm just going through the motions"},
                {"role": "assistant", "content": "Depression can make everything feel hopeless."},
                {"role": "user", "content": "It's like a weight I can't shake off"},
            ]
        },
        "user5": {
            "messages": [
                {"role": "user", "content": "I'm struggling with my identity and where I belong"},
                {"role": "assistant", "content": "Identity questions are important. What's on your mind?"},
                {"role": "user", "content": "I feel different from my family and culture expectations"},
                {"role": "assistant", "content": "That can be isolating. You're not alone in this."},
                {"role": "user", "content": "I want to honor my culture but also be myself"},
                {"role": "assistant", "content": "Finding that balance is a real journey."},
            ]
        },
        "user6": {
            "messages": [
                {"role": "user", "content": "Feeling lonely and anxious about my social life"},
                {"role": "assistant", "content": "Social anxiety is real. What makes you anxious?"},
                {"role": "user", "content": "I worry people don't like me and I stress about being judged"},
                {"role": "assistant", "content": "Those worries are common but not necessarily true."},
            ]
        },
    }
    
    for user_id, data in test_data.items():
        profile = create_profile(user_id, data["messages"])
        if profile:
            st.session_state.peers[user_id] = profile

def show_test_controls():
    with st.expander("🧪 Testing Controls"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Only enable button if user has chatted
            my_id = st.session_state.my_user_id
            has_chat = len(st.session_state.messages) >= 2
            
            if st.button("Load Peers", use_container_width=True, disabled=not has_chat):
                create_test_profiles()
                
                # Opt in current user if they have a profile
                if my_id in st.session_state.peers:
                    st.session_state.peers[my_id]["opt_in"] = True
                
                # Enable all other peers
                for user_id in st.session_state.peers:
                    if user_id != my_id:
                        st.session_state.peers[user_id]["opt_in"] = True
                
                peer_count = len([u for u in st.session_state.peers if u != my_id])
                st.success(f"✅ Loaded {peer_count} peers! Go to Connect tab.")
                st.rerun()
            
            if not has_chat:
                st.caption("💬 Chat first to build your profile, then load peers!")

        
        with col2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.peers = {}
                st.session_state.peer_chats = {}
                st.rerun()
        
        with col3:
            if st.button("Reset Profile", use_container_width=True):
                my_id = st.session_state.my_user_id
                if my_id in st.session_state.peers:
                    del st.session_state.peers[my_id]
                st.session_state.messages = []
                st.rerun()

def show_peer_support_tab():
    my_id = st.session_state.my_user_id
    my_profile = st.session_state.peers.get(my_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if my_profile:
            themes = ", ".join([t[0] for t in my_profile.get("top_themes", [])])
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.15);">
                    <h4 style="margin: 0; color: #fff;">👤 Your Profile</h4>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);"><strong>Topics:</strong> {themes}</p>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);"><strong>Stage:</strong> {my_profile['stage']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            opt_in = st.checkbox("✅ Open to peer connections", value=my_profile.get("opt_in"), key="peer_optin")
            if opt_in != my_profile.get("opt_in"):
                st.session_state.peers[my_id]["opt_in"] = opt_in
                st.rerun()
        else:
            st.info("💭 Chat more to build your profile")
    
    with col2:
        matches = find_matches(my_id) if my_profile and my_profile.get("opt_in") else []
        
        if matches:
            st.markdown(f"✨ **Found {len(matches)} match(es)**")
            for other_id, score in matches[:3]:
                other = st.session_state.peers[other_id]
                themes = ", ".join([t[0] for t in other.get("top_themes", [])])
                
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{score}%** • {themes}")
                with col_b:
                    if st.button("Connect", key=other_id, use_container_width=True):
                        chat_id = create_peer_chat(my_id, other_id)
                        st.session_state.current_peer_chat = chat_id
                        st.rerun()
        else:
            st.info("👤 Opt in to see matches")
    
    st.divider()
    
    if st.session_state.peer_chats:
        for chat_id, chat_data in st.session_state.peer_chats.items():
            other_user = [u for u in chat_data["participants"] if u != my_id][0]
            is_new = st.session_state.get("current_peer_chat") == chat_id
            
            with st.expander(f"💬 Chat with {other_user}", expanded=is_new):
                if chat_data["messages"]:
                    for msg in chat_data["messages"]:
                        role = "You" if msg["sender"] == my_id else "Peer"
                        with st.chat_message("user" if msg["sender"] == my_id else "assistant"):
                            st.write(msg["text"])
                else:
                    st.caption("Start with something kind...")
                
                new_msg = st.chat_input("Type a message...", key=f"peer_chat_{chat_id}")
                if new_msg and new_msg.strip():
                    chat_data["messages"].append({
                        "sender": my_id,
                        "text": new_msg.strip(),
                        "time": datetime.now().isoformat()
                    })
                    st.rerun()

#Session state initialization

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = DEFAULT_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

if "emotion_log" not in st.session_state:
    st.session_state.emotion_log = []

if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

init_peer_state()
init_game_state()

# Page config
st.set_page_config(
    page_title="DMSpace",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional app styling
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #5a6c8a 100%);
        background-attachment: fixed;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 3rem 3rem 2rem 3rem !important;
    }
    
    .main { padding: 0 !important; }
    
    h1 {
        color: #ffffff !important;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    h2, h3 { color: rgba(255, 255, 255, 0.95) !important; font-weight: 700 !important; font-size: 1.3rem !important; }
    p, label, span { color: rgba(255, 255, 255, 0.9) !important; font-size: 1.05rem !important; }
    
    [role="tablist"] {
        gap: 0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.15) !important;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem !important;
        border-radius: 12px 12px 0 0;
    }
    
    [role="tab"] {
        padding: 1.5rem 2.5rem !important;
        font-size: 18px !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.3s ease;
        font-weight: 700;
    }
    
    [role="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #ffffff !important;
        background: rgba(255, 255, 255, 0.08);
    }
    
    input, textarea {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 2px solid rgba(102, 126, 234, 0.5) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
    }
    
    input:focus, textarea:focus {
        background: rgba(20, 20, 40, 0.95) !important;
        border-color: rgba(102, 126, 234, 0.9) !important;
        color: #ffffff !important;
    }
    
    input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    [data-testid="stChatInputContainer"] input {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stChatMessage"] {
        background: transparent;
        padding: 1.2rem 0;
    }
    
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #ffffff;
        line-height: 1.6;
    }
    
    button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        font-size: 16px !important;
    }
    
    button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }
    
    button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    [data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    hr { border: 1px solid rgba(255, 255, 255, 0.15) !important; }
    
    [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .caption { color: rgba(255, 255, 255, 0.65) !important; font-size: 15px !important; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(20, 20, 50, 0.95) 0%, rgba(40, 40, 70, 0.95) 100%) !important;
    }
    
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stSidebar"] .caption {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 14px !important;
    }
    
    [data-testid="stSidebar"] [role="radio"] {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] input {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(102, 126, 234, 0.5) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] button {
        background: rgba(102, 126, 234, 0.3) !important;
        border: 1px solid rgba(102, 126, 234, 0.6) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: rgba(102, 126, 234, 0.5) !important;
        border-color: rgba(102, 126, 234, 0.8) !important;
    }
    
    /* Sidebar toggle button - make it dark and visible */
    button[kind="tertiary"] {
        color: #000000 !important;
        background: #333333 !important;
        border: 1px solid #555555 !important;
    }
    
    button[kind="tertiary"]:hover {
        background: #444444 !important;
        border-color: #666666 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebarNav"] {
        background: transparent !important;
    }
    
    [data-testid="stSidebarNav"] button {
        color: #ffffff !important;
    }
    
    html { scroll-behavior: smooth; }
    
    /* Style Streamlit top header bar - make it dark */
    header[data-testid="stHeader"] {
        background-color: #1a1a2e !important;
    }
    
    /* Entire header section */
    [data-testid="stApp"] header {
        background-color: #1a1a2e !important;
        background-image: none !important;
    }
    
    /* Top toolbar with Deploy, Rerun buttons */
    [data-testid="stToolbar"] {
        background-color: #1a1a2e !important;
    }
    
    /* Make text in header white/visible */
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] span,
    [data-testid="stHeader"] div {
        color: #ffffff !important;
    }
    
    /* Toolbar buttons text */
    [data-testid="stToolbar"] button {
        color: #ffffff !important;
    }
    
    /* Force sidebar toggle button to be dark */
    [data-testid="baseButton-secondary"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #333333 !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Alternative targeting for hamburger menu */
    button[data-testid*="stSidebar"] {
        background: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Target any button in top area */
    [data-testid="stApp"] > header button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

#Sidebar

with st.sidebar:
    st.markdown("---")
    st.subheader("🌍 Your Perspective")
    st.session_state.cultural_context = st.radio(
        "How do you see mental wellness?",
        options=["western", "collectivist", "spiritual", "balanced"],
        format_func=lambda x: CULTURAL_CONTEXTS[x]["name"],
        key="cultural_radio"
    )
    st.caption(f"*{CULTURAL_CONTEXTS[st.session_state.cultural_context]['reflection_style']}*")
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.caption("A culturally-informed space for mental wellness, games, and peer support.")
    st.markdown("---")
    show_test_controls()

#Main layout with logo

if DEMO_MODE:
    st.info("🎮 **DEMO MODE**: Games work fully! Chat & Journal features need OpenAI API key. Use 🧪 Testing Controls to load sample peer profiles.")

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <svg width="120" height="120" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.9" />
              <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.9" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#c7d2fe;stop-opacity:0.9" />
              <stop offset="100%" style="stop-color:#a5b4fc;stop-opacity:0.9" />
            </linearGradient>
            <filter id="shadow">
              <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.4"/>
            </filter>
          </defs>
          <circle cx="100" cy="100" r="95" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
          <circle cx="60" cy="100" r="28" fill="url(#grad1)" filter="url(#shadow)"/>
          <circle cx="140" cy="100" r="28" fill="url(#grad2)" filter="url(#shadow)"/>
          <circle cx="100" cy="60" r="28" fill="url(#grad1)" filter="url(#shadow)"/>
          <line x1="60" y1="100" x2="100" y2="60" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
          <line x1="100" y1="60" x2="140" y2="100" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
          <line x1="140" y1="100" x2="60" y2="100" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
          <circle cx="100" cy="100" r="14" fill="rgba(102, 126, 234, 0.8)" filter="url(#shadow)"/>
          <circle cx="100" cy="100" r="11" fill="none" stroke="rgba(255,255,255,0.8)" stroke-width="2"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 14rem; color: #ffffff; margin: -1rem 0 0 0; padding: 0; font-weight: 800; letter-spacing: -4px;'>DMSpace</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.8); margin-bottom: 3rem; margin-top: 0;'>Express yourself. Find clarity. Connect with others.</p>", unsafe_allow_html=True)

chat_tab, journal_tab, peer_tab, games_tab = st.tabs(["💭 Chat", "📔 Journal", "🤝 Connect", "🎮 Wellness Games"])

# --- CHAT TAB ---

with chat_tab:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("What's on your mind?")

    if prompt:
        clean_prompt = prompt.strip()

        if not clean_prompt:
            st.info("Share something to continue.")
        else:
            st.session_state.messages.append({"role": "user", "content": clean_prompt})

            if is_possible_crisis(clean_prompt):
                st.session_state.messages.append({"role": "assistant", "content": CRISIS_RESPONSE})
            else:
                assistant_reply = generate_assistant_reply(st.session_state.messages)

                if assistant_reply is not None:
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

                    st.session_state.emotion_log.append({
                        "user_text": clean_prompt,
                        "assistant_text": assistant_reply,
                        "timestamp": datetime.now().strftime("%b %d, %Y • %I:%M %p"),
                    })
                    
                    if len(st.session_state.messages) >= 2:
                        profile = create_profile(st.session_state.my_user_id, st.session_state.messages)
                        if profile:
                            st.session_state.peers[st.session_state.my_user_id] = profile
                
                st.rerun()

# --- JOURNAL TAB ---

with journal_tab:
    if not st.session_state.emotion_log:
        st.info("Chat to unlock personalized journal prompts")
    else:
        with st.expander("📋 Today's Prompts", expanded=True):
            ai_prompts = generate_journal_prompts(st.session_state.emotion_log)
            if ai_prompts:
                st.markdown(ai_prompts)
        
        st.markdown("")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        mood = st.select_slider("Mood", options=["😞", "😐", "🙂", "😊", "😌", "💪"])
    
    journal_text = st.text_area("Write your thoughts", key="journal_input", height=150)
    highlight = st.text_input("One thing to remember", key="journal_highlight")

    if st.button("Save", use_container_width=True):
        if journal_text.strip() or highlight.strip():
            st.session_state.journal_entries.append({
                "text": journal_text.strip(),
                "highlight": highlight.strip(),
                "mood": mood,
                "timestamp": datetime.now().strftime("%b %d, %Y • %I:%M %p"),
            })
            st.success("Saved ✓")
        else:
            st.info("Write something first")

    if st.session_state.journal_entries:
        st.divider()
        st.markdown("### Past Entries")
        
        for entry in reversed(st.session_state.journal_entries[-10:]):
            with st.container():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"**{entry['mood']}**")
                    st.caption(entry['timestamp'])
                with col2:
                    if entry.get("highlight"):
                        st.markdown(f"__{entry['highlight']}__")
                    if entry.get("text"):
                        st.caption(entry["text"][:120] + "..." if len(entry["text"]) > 120 else entry["text"])
                st.divider()

# --- PEER SUPPORT TAB ---

with peer_tab:
    show_peer_support_tab()

# --- GAMES TAB ---

with games_tab:
    st.markdown("## 🎮 Wellness Games")
    st.caption("Play games for mental wellness. Pick one to get started!")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Word Detective", use_container_width=True, key="select_word_game"):
            st.session_state.current_game = "word"
            st.rerun()
    
    with col2:
        if st.button("🏺 Gratitude Jar", use_container_width=True, key="select_gratitude_game"):
            st.session_state.current_game = "gratitude"
            st.rerun()
    
    with col3:
        if st.button("🫁 Breathing Exercise", use_container_width=True, key="select_breathing_game"):
            st.session_state.current_game = "breathing"
            st.rerun()
    
    st.divider()
    
    if "current_game" not in st.session_state:
        st.session_state.current_game = None
    
    if st.session_state.current_game == "word":
        show_word_game()
    elif st.session_state.current_game == "gratitude":
        show_gratitude_jar()
    elif st.session_state.current_game == "breathing":
        show_breathing_exercise()
    else:
        st.info("👆 Select a game above to start!")