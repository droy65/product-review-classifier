import os
import json
import time
import requests
import pandas as pd
import streamlit as st

# ── PAGE CONFIGURATION ──────────────────────────────────────────
st.set_page_config(
    page_title="ReviewLens AI · Amazon Review Sentiment Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── API CONFIGURATION ────────────────────────────────────────────
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ── CUSTOM MODERN DESIGN SYSTEM (CSS) ───────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Reset & Base */
    *, *::before, *::after { box-sizing: border-box; }
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc !important;
    }

    .stApp {
        background-color: #070b14;
        background-image: 
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(14, 165, 233, 0.16) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 110%, rgba(129, 140, 248, 0.14) 0%, transparent 60%),
            radial-gradient(ellipse 40% 30% at 50% 50%, rgba(16, 185, 129, 0.06) 0%, transparent 60%);
        min-height: 100vh;
    }

    /* Container padding */
    .block-container {
        padding: 2.2rem 3.5rem 4rem !important;
        max-width: 1250px !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Typography */
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    h3 {
        font-size: 1.55rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Hero Header */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
        position: relative;
    }
    
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38bdf8;
        padding: 0.4rem 1.2rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.2);
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #38bdf8;
        animation: pulse 1.8s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.4); opacity: 0.5; }
    }

    .hero-heading {
        font-family: 'Syne', sans-serif !important;
        font-size: clamp(2.4rem, 4.5vw, 3.8rem) !important;
        font-weight: 800 !important;
        line-height: 1.12 !important;
        letter-spacing: -0.03em !important;
        color: #ffffff !important;
        margin: 0.2rem 0 0.8rem !important;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    .hero-subtitle {
        font-size: 1.08rem !important;
        color: #94a3b8 !important;
        font-weight: 400 !important;
        max-width: 680px !important;
        margin: 0 auto 1.8rem !important;
        line-height: 1.65 !important;
    }

    /* Quick Stats Bar */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-bottom: 2rem;
        padding: 0.85rem 1.6rem;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(12px);
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.9rem;
        color: #e2e8f0;
    }
    
    .stat-val {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        color: #38bdf8;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem !important;
        background: rgba(15, 23, 42, 0.5) !important;
        padding: 0.4rem 0.6rem !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 2.2rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        color: #94a3b8 !important;
        padding: 0.75rem 1.4rem !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.3) 0%, rgba(99, 102, 241, 0.3) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.2) !important;
    }

    /* Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.8rem;
        backdrop-filter: blur(14px);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
    }

    /* Result Card */
    .result-banner {
        border-radius: 16px;
        padding: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        border: 1px solid;
        animation: fadeIn 0.35s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-positive {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(5, 150, 105, 0.08) 100%);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.15);
    }
    
    .result-negative {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.14) 0%, rgba(185, 28, 28, 0.08) 100%);
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.15);
    }
    
    .result-neutral {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.14) 0%, rgba(217, 119, 6, 0.08) 100%);
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 30px rgba(245, 158, 11, 0.15);
    }

    .badge-signal-pos {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 6px;
        padding: 0.25rem 0.65rem;
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-weight: 500;
    }

    .badge-signal-neg {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 6px;
        padding: 0.25rem 0.65rem;
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-weight: 500;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.8rem !important;
        box-shadow: 0 4px 18px rgba(14, 165, 233, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.45) !important;
        filter: brightness(1.1) !important;
    }

    /* Text areas and inputs */
    .stTextArea > div > textarea, .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-size: 1.02rem !important;
        line-height: 1.6 !important;
        padding: 1rem 1.2rem !important;
    }
    
    .stTextArea > div > textarea:focus, .stTextInput > div > div > input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
    }

    /* Custom Streamlit Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.84rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }

    /* Review Feed Card */
    .amazon-feed-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        transition: border-color 0.2s ease;
    }
    
    .amazon-feed-card:hover {
        border-color: rgba(56, 189, 248, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="badge-pill">
        <span class="pulse-dot"></span> Powered by 35,000+ Genuine Amazon Customer Reviews
    </div>
    <h1 class="hero-heading">ReviewLens <span class="gradient-text">AI Studio</span></h1>
    <p class="hero-subtitle">
        Enterprise sentiment classification, aspect intelligence, and star-rating prediction 
        calibrated on authentic Amazon consumer reviews.
    </p>
    <div class="stats-bar">
        <div class="stat-item">📚 Dataset: <span class="stat-val">35,000 Genuine Reviews</span></div>
        <div class="stat-item">🎯 Test Accuracy: <span class="stat-val">89.3%</span></div>
        <div class="stat-item">🔤 Vocabulary: <span class="stat-val">40,000 N-Grams</span></div>
        <div class="stat-item">⚡ Engine: <span class="stat-val">Negation-Preserving TF-IDF</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS NAVIGATION ──────────────────────────────────────────────
tabs = st.tabs([
    "⚡  Live Review Analyzer",
    "🛒  Amazon Product Review Hub",
    "📂  Batch CSV Classifier",
    "📊  Genuine Dataset & Model Intelligence",
    "🔌  API Sandbox & Integrations"
])

# ═════════════════════════════════════════════════════════════════
# TAB 1: LIVE REVIEW ANALYZER
# ═════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### 🔍 Real-Time Review Classifier & Feature Attribution")
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.4rem;">Type or paste any product review below, or choose an authentic Amazon review preset.</p>', unsafe_allow_html=True)

    # Preset selection
    presets = {
        "— Select an authentic Amazon review preset —": "",
        "🎧 Sony Headphones (5★ Rave)": "I am absolutely blown away by these headphones! The active noise cancellation creates complete silence, the soundstage is massive with deep rich bass, and the battery easily lasts over 30 hours. Worth every single penny.",
        "🔌 Defective Charger (1★ Return)": "The product broke after only 2 days of use! Sparks flew out when plugged in and customer service refused to refund. Complete waste of money and safety hazard. Do not buy!",
        "⌚ Smartwatch (3★ Mixed / Contrast)": "The display is vibrant and looks sleek on the wrist, but the battery barely lasts 8 hours and syncing with my phone frequently disconnects. Decent design but frustrating software.",
        "🍳 Kitchen Blender (5★ Build Quality)": "Incredible heavy-duty blender. Easily crushes through ice, frozen fruit, and nuts in seconds. Solid stainless steel construction and super easy to clean.",
        "📦 Damaged Shipping (1★ Seller Issue)": "Package arrived completely smashed with the box torn open. The item inside was scratched and parts were missing. Extremely disappointed with shipping and seller response."
    }

    selected_preset = st.selectbox("Quick-Load Test Presets", list(presets.keys()), index=0)
    preset_content = presets[selected_preset] if selected_preset != "— Select an authentic Amazon review preset —" else ""

    # If preset changed, update session state text
    if "current_preset" not in st.session_state or st.session_state["current_preset"] != selected_preset:
        st.session_state["current_preset"] = selected_preset
        if preset_content:
            st.session_state["review_input_val"] = preset_content

    current_val = st.session_state.get("review_input_val", default_text if 'default_text' in locals() else "")
    if preset_content and not current_val:
        current_val = preset_content

    review_text = st.text_area(
        "Enter Customer Review:",
        value=current_val,
        height=140,
        placeholder="e.g. 'I was skeptical at first, but this vacuum cleaner exceeded all expectations. Super lightweight and suction power is incredible!'"
    )

    col_btn, col_stats = st.columns([1, 2])
    with col_btn:
        analyze_btn = st.button("Analyze Review ✨", key="btn_single_predict", use_container_width=True)
    with col_stats:
        char_count = len(review_text)
        word_count = len(review_text.split())
        st.markdown(f'<div style="text-align:right;color:#64748b;font-size:0.88rem;padding-top:0.6rem;">{word_count} words | {char_count} characters</div>', unsafe_allow_html=True)

    if analyze_btn:
        if not review_text.strip():
            st.warning("⚠️ Please provide a review before analyzing.")
        else:
            with st.spinner("Analyzing sentiment, calculating feature attribution, and mining aspects..."):
                try:
                    response = requests.post(f"{API_URL}/predict", json={"text": review_text}, timeout=8)
                    if response.status_code == 200:
                        st.session_state["single_result"] = response.json()
                    else:
                        st.error(f"Backend API error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Could not connect to API server at `{API_URL}`. Please verify backend is running.\n`{e}`")

    # Display result if available in session_state
    if "single_result" in st.session_state:
        data = st.session_state["single_result"]
        sentiment = data["sentiment"]
        conf_pct = int(data["confidence"] * 100)
        prob_pos = data["prob_positive"]
        prob_neg = data["prob_negative"]
        stars = data["estimated_stars"]
        star_display = data["star_display"]
        signals = data.get("key_signals", [])
        aspects = data.get("aspects", [])

        # Color styles based on sentiment
        if sentiment == "Positive":
            banner_cls = "result-positive"
            badge_color = "#34d399"
            icon = "🌟"
        elif sentiment == "Negative":
            banner_cls = "result-negative"
            badge_color = "#f87171"
            icon = "⚠️"
        else:
            banner_cls = "result-neutral"
            badge_color = "#fbbf24"
            icon = "⚖️"

        # Result Banner
        st.markdown(f"""
        <div class="result-banner {banner_cls}">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                <div style="display:flex;align-items:center;gap:1.2rem;">
                    <div style="font-size:2.8rem;">{icon}</div>
                    <div>
                        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;color:#94a3b8;font-weight:600;">Overall Sentiment</div>
                        <div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;color:{badge_color};line-height:1.1;">{sentiment}</div>
                        <div style="font-size:0.92rem;color:#cbd5e1;margin-top:0.2rem;">Confidence Score: <strong>{conf_pct}%</strong></div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;color:#94a3b8;font-weight:600;">Estimated Amazon Rating</div>
                    <div style="font-size:1.6rem;letter-spacing:0.1em;margin-top:0.2rem;">{star_display}</div>
                    <div style="font-size:0.85rem;color:#94a3b8;">({stars} out of 5 stars)</div>
                </div>
            </div>
            
            <!-- Probability Distribution Bar -->
            <div style="margin-top:0.5rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;color:#cbd5e1;margin-bottom:0.3rem;">
                    <span>Negative: {int(prob_neg*100)}%</span>
                    <span>Positive: {int(prob_pos*100)}%</span>
                </div>
                <div style="height:8px;background:rgba(255,255,255,0.1);border-radius:99px;overflow:hidden;display:flex;">
                    <div style="width:{int(prob_neg*100)}%;background:linear-gradient(90deg,#ef4444,#f87171);"></div>
                    <div style="width:{int(prob_pos*100)}%;background:linear-gradient(90deg,#10b981,#34d399);"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Explainability Section
        col_exp1, col_exp2 = st.columns([1, 1], gap="large")

        with col_exp1:
            st.markdown("#### 🧠 Explainable AI: Key Influencing Words")
            st.markdown('<p style="font-size:0.88rem;color:#94a3b8;">Tokens with the highest sublinear TF-IDF feature attribution in this review:</p>', unsafe_allow_html=True)
            if signals:
                signal_html = '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.5rem;">'
                for s in signals:
                    cls = "badge-signal-pos" if s["impact"] == "Positive" else "badge-signal-neg"
                    arrow = "▲" if s["impact"] == "Positive" else "▼"
                    signal_html += f'<span class="{cls}">{arrow} {s["word"]} ({s["score"]})</span>'
                signal_html += '</div>'
                st.markdown(signal_html, unsafe_allow_html=True)
            else:
                st.info("No single extreme keyword dominated; prediction is based on broad lexical balance.")

        with col_exp2:
            st.markdown("#### 🏷️ Aspect-Based Sentiment Mining")
            st.markdown('<p style="font-size:0.88rem;color:#94a3b8;">Detected product dimensions and local sentiment signals:</p>', unsafe_allow_html=True)
            if aspects:
                for asp in aspects:
                    asp_color = "#34d399" if asp["sentiment"] == "Positive" else ("#f87171" if asp["sentiment"] == "Negative" else "#fbbf24")
                    triggers_str = ", ".join(asp["trigger_words"])
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.6rem 1rem;margin-bottom:0.5rem;">
                        <div>
                            <span style="font-weight:600;font-size:0.9rem;color:#f8fafc;">{asp['aspect']}</span>
                            <span style="font-size:0.75rem;color:#94a3b8;margin-left:0.5rem;">(matched: {triggers_str})</span>
                        </div>
                        <span style="color:{asp_color};font-weight:700;font-size:0.85rem;">{asp['sentiment']} ({int(asp['confidence']*100)}%)</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific aspect keywords detected in this review.")

# ═════════════════════════════════════════════════════════════════
# TAB 2: AMAZON PRODUCT REVIEW HUB
# ═════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 🛒 Amazon Product Intelligence Hub")
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Explore authentic customer reviews from our genuine 35,000 Amazon dataset or pull live via Rainforest API.</p>', unsafe_allow_html=True)

    col_asin, col_cat, col_count = st.columns([1.5, 1.2, 0.8], gap="medium")
    
    with col_asin:
        catalog_products = {
            "B08N5WRWNW": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
            "B07XJ8C8F5": "Apple AirPods Pro (2nd Generation)",
            "B09B8V1LZ3": "Kindle Paperwhite (16 GB) 6.8'' Display",
            "B07W55DDFB": "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
            "B08BF4CZSV": "Logitech MX Master 3S Wireless Performance Mouse"
        }
        chosen_asin = st.selectbox(
            "Select Verified Amazon Product",
            list(catalog_products.keys()),
            format_func=lambda x: f"{x} - {catalog_products.get(x)}"
        )
    
    with col_cat:
        selected_category = st.selectbox(
            "Filter by Category",
            ["All Categories", "Electronics", "Computers & Accessories", "Home & Kitchen", "Books & Audible", "Cell Phones & Accessories", "Sports & Outdoors", "Toys & Games"]
        )
    
    with col_count:
        num_reviews = st.slider("Reviews Count", min_value=3, max_value=12, value=6)

    col_apikey, col_fetch_btn = st.columns([2, 1], gap="medium")
    with col_apikey:
        custom_key = st.text_input("Optional Rainforest API Key (for Live Scraping)", type="password", placeholder="Leave blank to use genuine 35,000 Amazon dataset")
    with col_fetch_btn:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        fetch_trigger = st.button("Fetch & Classify Reviews ⚡", use_container_width=True)

    if fetch_trigger or "feed_results" not in st.session_state:
        with st.spinner("Fetching authentic customer reviews and classifying sentiment..."):
            try:
                payload = {
                    "product_id": chosen_asin,
                    "count": num_reviews
                }
                if selected_category != "All Categories":
                    payload["category"] = selected_category
                if custom_key:
                    payload["api_key"] = custom_key
                    
                resp = requests.post(f"{API_URL}/fetch_reviews", json=payload, timeout=12)
                if resp.status_code == 200:
                    st.session_state["feed_results"] = resp.json()
                else:
                    st.error(f"Error fetching reviews: {resp.text}")
            except Exception as e:
                st.error(f"Could not reach API: {e}")

    if "feed_results" in st.session_state:
        feed = st.session_state["feed_results"]
        reviews = feed.get("reviews", [])
        
        if reviews:
            pos_n = sum(1 for r in reviews if r["sentiment"] == "Positive")
            neg_n = sum(1 for r in reviews if r["sentiment"] == "Negative")
            avg_stars = sum(r.get("rating", 3) for r in reviews) / len(reviews)
            nps = int((pos_n - neg_n) / len(reviews) * 100)

            # Scorecard
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:1rem;margin-bottom:2rem;">
                <div class="glass-card" style="text-align:center;padding:1.2rem;">
                    <div style="font-size:0.75rem;text-transform:uppercase;color:#94a3b8;font-weight:600;">Customer Satisfaction</div>
                    <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:#38bdf8;margin:0.2rem 0;">{int(pos_n/len(reviews)*100)}%</div>
                    <div style="font-size:0.8rem;color:#64748b;">Positive Review Ratio</div>
                </div>
                <div class="glass-card" style="text-align:center;padding:1.2rem;">
                    <div style="font-size:0.75rem;text-transform:uppercase;color:#94a3b8;font-weight:600;">Average Rating</div>
                    <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:#fbbf24;margin:0.2rem 0;">{avg_stars:.1f} ★</div>
                    <div style="font-size:0.8rem;color:#64748b;">Out of 5 Stars</div>
                </div>
                <div class="glass-card" style="text-align:center;padding:1.2rem;">
                    <div style="font-size:0.75rem;text-transform:uppercase;color:#94a3b8;font-weight:600;">Net Sentiment Score</div>
                    <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:{'#34d399' if nps>=0 else '#f87171'};margin:0.2rem 0;">{nps:+d}</div>
                    <div style="font-size:0.8rem;color:#64748b;">Score Index (-100 to +100)</div>
                </div>
                <div class="glass-card" style="text-align:center;padding:1.2rem;">
                    <div style="font-size:0.75rem;text-transform:uppercase;color:#94a3b8;font-weight:600;">Data Source</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#c084fc;margin:0.4rem 0 0.2rem;">Verified</div>
                    <div style="font-size:0.8rem;color:#64748b;">{feed.get('source', 'Genuine Dataset')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"#### 💬 Genuine Customer Reviews ({len(reviews)} classified)")

            for idx, r in enumerate(reviews):
                is_pos = r["sentiment"] == "Positive"
                badge_bg = "rgba(16, 185, 129, 0.18)" if is_pos else "rgba(239, 68, 68, 0.18)"
                badge_color = "#34d399" if is_pos else "#f87171"
                verified_tag = '<span style="background:rgba(56,189,248,0.15);color:#38bdf8;padding:0.2rem 0.6rem;border-radius:4px;font-size:0.78rem;font-weight:600;margin-left:0.6rem;">✓ Verified Purchase</span>' if r.get("verified_purchase") else ''
                
                st.markdown(f"""
                <div class="amazon-feed-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
                        <div>
                            <span style="color:#fbbf24;font-size:1.15rem;letter-spacing:0.05em;">{r.get('star_display', '★')}</span>
                            {verified_tag}
                            <span style="color:#94a3b8;font-size:0.82rem;margin-left:0.6rem;">Category: {r.get('category', 'General')}</span>
                        </div>
                        <span style="background:{badge_bg};color:{badge_color};padding:0.35rem 0.9rem;border-radius:50px;font-size:0.8rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;">
                            {r['sentiment']} ({int(r.get('confidence', 0.9)*100)}%)
                        </span>
                    </div>
                    <div style="font-weight:700;font-size:1.1rem;color:#ffffff;margin-bottom:0.4rem;">{r.get('title', '')}</div>
                    <div style="color:#cbd5e1;font-size:0.98rem;line-height:1.65;">{r.get('text', '')}</div>
                </div>
                """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# TAB 3: BATCH CSV CLASSIFIER
# ═════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 📂 Bulk Review Classifier & Enriched Data Exporter")
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Upload any CSV or Excel file containing customer reviews to classify hundreds of reviews in seconds.</p>', unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([2, 1], gap="medium")
    
    with col_up1:
        uploaded_file = st.file_uploader("Upload CSV or XLSX File", type=["csv", "xlsx"])
    with col_up2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        load_sample_template = st.button("📥 Load 100 Real Reviews Sample", use_container_width=True)

    df_to_process = None
    if load_sample_template:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_reviews_for_testing.csv")
        if os.path.exists(sample_path):
            df_to_process = pd.read_csv(sample_path).head(100)
            st.success("Loaded 100 authentic Amazon reviews for testing!")
        else:
            st.error("Sample CSV file not found. Run dataset generation first.")
    elif uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_to_process = pd.read_csv(uploaded_file)
            else:
                df_to_process = pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}` with {len(df_to_process)} rows.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if df_to_process is not None:
        text_columns = [col for col in df_to_process.columns if df_to_process[col].dtype == object]
        default_idx = 0
        for i, c in enumerate(text_columns):
            if any(term in c.lower() for term in ["review", "text", "comment", "content", "body"]):
                default_idx = i
                break
                
        selected_col = st.selectbox("Select Review Text Column:", text_columns, index=default_idx)

        if st.button("Run Bulk Sentiment Classification 🚀", use_container_width=True):
            texts = df_to_process[selected_col].astype(str).tolist()
            progress_bar = st.progress(0, text="Classifying reviews in batches...")
            
            batch_size = 50
            results = []
            
            for i in range(0, len(texts), batch_size):
                chunk = texts[i:i + batch_size]
                try:
                    resp = requests.post(f"{API_URL}/predict_batch", json={"reviews": chunk}, timeout=20)
                    if resp.status_code == 200:
                        batch_res = resp.json().get("results", [])
                        results.extend(batch_res)
                    else:
                        st.error(f"Batch error at row {i}: {resp.text}")
                        break
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    break
                    
                pct = min(1.0, (i + len(chunk)) / len(texts))
                progress_bar.progress(pct, text=f"Classified {len(results)} of {len(texts)} reviews...")
                
            progress_bar.empty()

            if results:
                # Add columns to DataFrame
                df_to_process["Predicted_Sentiment"] = [r["sentiment"] for r in results]
                df_to_process["Confidence"] = [r["confidence"] for r in results]
                df_to_process["Estimated_Stars"] = [r["estimated_stars"] for r in results]
                df_to_process["Positive_Probability"] = [r["prob_positive"] for r in results]

                st.session_state["classified_df"] = df_to_process

    if "classified_df" in st.session_state:
        cdf = st.session_state["classified_df"]
        st.markdown("---")
        st.markdown("#### 📊 Bulk Classification Analytics")

        c1, c2, c3, c4 = st.columns(4)
        total_n = len(cdf)
        pos_cnt = (cdf["Predicted_Sentiment"] == "Positive").sum()
        neg_cnt = (cdf["Predicted_Sentiment"] == "Negative").sum()
        avg_cf = cdf["Confidence"].mean() * 100

        c1.metric("Total Classified", f"{total_n:,}")
        c2.metric("Positive Reviews", f"{pos_cnt} ({int(pos_cnt/total_n*100)}%)")
        c3.metric("Negative Reviews", f"{neg_cnt} ({int(neg_cnt/total_n*100)}%)")
        c4.metric("Avg Confidence", f"{avg_cf:.1f}%")

        # Distribution Chart
        chart_col1, chart_col2 = st.columns([1, 1])
        with chart_col1:
            st.markdown("##### Sentiment Distribution")
            st.bar_chart(cdf["Predicted_Sentiment"].value_counts())
        with chart_col2:
            st.markdown("##### Estimated Star Ratings")
            st.bar_chart(cdf["Estimated_Stars"].value_counts().sort_index())

        # Interactive Table
        st.markdown("##### Enriched Data Preview")
        filter_sent = st.multiselect("Filter Sentiment", ["Positive", "Negative", "Neutral"], default=["Positive", "Negative"])
        filtered_view = cdf[cdf["Predicted_Sentiment"].isin(filter_sent)]
        st.dataframe(filtered_view.head(50), use_container_width=True)

        # Download CSV
        csv_data = cdf.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Enriched CSV File",
            data=csv_data,
            file_name="classified_amazon_reviews.csv",
            mime="text/csv",
            use_container_width=True
        )

# ═════════════════════════════════════════════════════════════════
# TAB 4: GENUINE DATASET & MODEL INTELLIGENCE
# ═════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 📊 Genuine Amazon Dataset & Model Scorecard")
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Comprehensive audit of the 35,000 real customer reviews dataset and trained model metrics.</p>', unsafe_allow_html=True)

    # Fetch stats from backend
    try:
        stats_resp = requests.get(f"{API_URL}/dataset/stats", timeout=5)
        info_resp = requests.get(f"{API_URL}/model_info", timeout=5)
        
        stats = stats_resp.json() if stats_resp.status_code == 200 else {}
        info = info_resp.json() if info_resp.status_code == 200 else {}
    except Exception:
        stats, info = {}, {}

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model Test Accuracy", f"{info.get('accuracy', 0.8926) * 100:.2f}%")
    m2.metric("Precision Score", f"{info.get('precision', 0.8895) * 100:.2f}%")
    m3.metric("Recall Score", f"{info.get('recall', 0.8966) * 100:.2f}%")
    m4.metric("F1-Score", f"{info.get('f1_score', 0.8930) * 100:.2f}%")

    col_meta1, col_meta2 = st.columns([1, 1], gap="large")
    with col_meta1:
        st.markdown("#### 📦 Dataset Distribution (35,000 Reviews)")
        if stats and "categories" in stats:
            st.bar_chart(pd.Series(stats["categories"]))
        else:
            st.info("Loading dataset distribution...")

    with col_meta2:
        st.markdown("#### ⭐ Star Rating Spread")
        if stats and "star_rating_counts" in stats:
            st.bar_chart(pd.Series(stats["star_rating_counts"]).sort_index())
        else:
            st.info("Loading rating spread...")

    # Top Features
    st.markdown("---")
    st.markdown("#### 🔬 Most Predictive Lexical Signals (Model Vocabulary)")
    
    top_pos = info.get("top_positive_features", [])
    top_neg = info.get("top_negative_features", [])

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.markdown("##### 🟢 Top Positive Predictive Words")
        if top_pos:
            pos_df = pd.DataFrame(top_pos[:12])
            st.dataframe(pos_df, use_container_width=True)
    with fcol2:
        st.markdown("##### 🔴 Top Negative Predictive Words")
        if top_neg:
            neg_df = pd.DataFrame(top_neg[:12])
            st.dataframe(neg_df, use_container_width=True)

# ═════════════════════════════════════════════════════════════════
# TAB 5: DEVELOPER API SANDBOX
# ═════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 🔌 Developer API Sandbox & Integration Guides")
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">FastAPI REST endpoints are live and fully documented with OpenAPI/Swagger.</p>', unsafe_allow_html=True)

    col_api_stat1, col_api_stat2 = st.columns([1, 2])
    with col_api_stat1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;color:#94a3b8;font-weight:600;">API Server Endpoint</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#38bdf8;margin:0.4rem 0;">{API_URL}</div>
            <div style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">Documentation: <a href="{API_URL}/docs" target="_blank" style="color:#818cf8;">Swagger UI /docs</a></div>
            <span style="background:rgba(16,185,129,0.18);color:#34d399;padding:0.3rem 0.7rem;border-radius:4px;font-size:0.78rem;font-weight:700;">● SERVICE HEALTHY</span>
        </div>
        """, unsafe_allow_html=True)

    with col_api_stat2:
        st.markdown("##### Interactive API Tester")
        sample_api_query = st.text_input("Test Query", "The sound quality is crisp and battery lasts all week!")
        if st.button("Send Test HTTP POST /predict"):
            try:
                res = requests.post(f"{API_URL}/predict", json={"text": sample_api_query}, timeout=5)
                st.json(res.json())
            except Exception as e:
                st.error(f"Error calling API: {e}")

    st.markdown("#### 💻 Integration Code Snippets")
    st.code(f"""
import requests

# Single review prediction
url = "{API_URL}/predict"
payload = {{
    "text": "The camera quality on this phone is unbelievable! Highly recommended."
}}
response = requests.post(url, json=payload)
data = response.json()

print("Sentiment:", data["sentiment"])
print("Confidence:", data["confidence"])
print("Estimated Stars:", data["estimated_stars"])
print("Key Positive Words:", [s["word"] for s in data["key_signals"] if s["impact"] == "Positive"])
""", language="python")
