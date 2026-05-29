import streamlit as st
import requests
import os

st.set_page_config(page_title="ReviewLens · Sentiment AI", layout="wide", page_icon="🔍")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    /* ── RESET & BASE ── */
    *, *::before, *::after { box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
    }

    /* ── APP BACKGROUND ── */
    .stApp {
        background-color: #080c14;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(14, 165, 233, 0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 110%, rgba(99, 102, 241, 0.10) 0%, transparent 60%);
        color: #e2e8f0;
        min-height: 100vh;
    }

    /* ── HIDE STREAMLIT CHROME ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 2.5rem 3rem 4rem !important;
        max-width: 1100px !important;
    }

    /* ── HERO HEADER ── */
    .hero-wrap {
        text-align: center;
        padding: 3.5rem 0 2.5rem;
        position: relative;
    }
    .hero-eyebrow {
        display: inline-block;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 50px;
        padding: 0.35rem 1rem;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.6rem, 5vw, 3.8rem);
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: #f1f5f9;
        margin: 0 0 1rem;
    }
    .hero-title span {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 60%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #64748b;
        font-weight: 300;
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.6;
    }
    .hero-divider {
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        margin: 2rem auto 0;
        border-radius: 2px;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.07) !important;
        gap: 0 !important;
        padding: 0 !important;
        margin-bottom: 2.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        color: #475569 !important;
        padding: 1rem 2rem !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.25s ease !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #94a3b8 !important;
        background: rgba(255,255,255,0.02) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
        background: transparent !important;
    }

    /* ── SECTION HEADINGS ── */
    h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        color: #f1f5f9 !important;
    }
    h2 { font-size: 1.6rem !important; margin-bottom: 0.4rem !important; }
    h3 { font-size: 1.3rem !important; }

    .section-desc {
        color: #64748b;
        font-size: 1rem;
        font-weight: 300;
        margin-bottom: 1.8rem;
        margin-top: 0.2rem;
        line-height: 1.6;
    }

    /* ── INPUT LABELS ── */
    .stTextInput label p, .stTextArea label p {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: #94a3b8 !important;
        margin-bottom: 0.5rem !important;
    }

    /* ── TEXT INPUTS ── */
    .stTextArea > div > textarea,
    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
        padding: 1rem 1.2rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stTextArea > div > textarea:focus,
    .stTextInput > div > div > input:focus {
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.08) !important;
        outline: none !important;
    }
    .stTextArea > div > textarea::placeholder {
        color: #334155 !important;
        font-style: italic;
    }

    /* ── PRIMARY BUTTON ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.85rem 2rem !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.25) !important;
        margin-top: 0.5rem !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4) !important;
        filter: brightness(1.08) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── RESULT CARDS ── */
    .result-card {
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        border: 1px solid;
        animation: slideUp 0.4s ease forwards;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .result-positive {
        background: rgba(16, 185, 129, 0.08);
        border-color: rgba(16, 185, 129, 0.25);
    }
    .result-negative {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.25);
    }
    .result-icon {
        font-size: 2.2rem;
        flex-shrink: 0;
    }
    .result-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.6;
        margin-bottom: 0.25rem;
    }
    .result-sentiment {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.35rem;
    }
    .result-positive .result-sentiment { color: #34d399; }
    .result-negative .result-sentiment { color: #f87171; }
    .result-confidence {
        font-size: 0.95rem;
        font-weight: 400;
        color: #94a3b8;
    }
    .confidence-bar-track {
        margin-top: 0.6rem;
        height: 5px;
        border-radius: 99px;
        background: rgba(255,255,255,0.08);
        overflow: hidden;
        width: 220px;
        max-width: 100%;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.6s ease;
    }
    .result-positive .confidence-bar-fill { background: linear-gradient(90deg, #10b981, #34d399); }
    .result-negative .confidence-bar-fill { background: linear-gradient(90deg, #ef4444, #f87171); }

    /* ── REVIEW BATCH CARD ── */
    .review-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }
    .review-card:hover { border-color: rgba(255,255,255,0.14); }
    .review-num {
        font-family: 'Syne', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 0.6rem;
    }
    .review-text {
        font-size: 1.02rem;
        line-height: 1.7;
        color: #cbd5e1;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'Syne', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.35rem 0.85rem;
        border-radius: 50px;
    }
    .badge-pos {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .badge-neg {
        background: rgba(239, 68, 68, 0.12);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }

    /* ── INFO BOX ── */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        font-size: 0.95rem !important;
    }

    /* ── SPINNER ── */
    .stSpinner > div {
        border-top-color: #38bdf8 !important;
    }

    /* ── COLUMN GAP ── */
    [data-testid="column"] { gap: 1.5rem; }

    /* ── ASIN HELPER ── */
    .asin-hint {
        font-size: 0.82rem;
        color: #475569;
        margin-top: 0.4rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ── HERO HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">🔍 Powered by Logistic Regression NLP</div>
    <h1 class="hero-title">Decode What Customers<br><span>Really Think</span></h1>
    <p class="hero-sub">Paste any product review and get an instant sentiment signal — or pull live Amazon reviews by ASIN.</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────
tabs = st.tabs(["✍️  Single Review", "🛒  Amazon Reviews"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — SINGLE REVIEW
# ═══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## Analyse a Review")
    st.markdown('<p class="section-desc">Type or paste any product review below. The model returns a sentiment label with a confidence score.</p>', unsafe_allow_html=True)

    user_input = st.text_area(
        "Product review",
        height=160,
        placeholder='e.g. "This headphone has incredible bass and lasts all day on a single charge - totally worth it."',
        label_visibility="visible"
    )

    if st.button("Analyse Sentiment →", key="single_btn"):
        if user_input.strip():
            try:
                with st.spinner("Running inference…"):
                    response = requests.post(f"{API_URL}/predict", json={"text": user_input})
                    if response.status_code == 200:
                        data       = response.json()
                        sentiment  = data["sentiment"]
                        confidence = data["confidence"]
                        pct        = int(confidence * 100)
                        is_pos     = sentiment == "Positive"
                        card_cls   = "result-positive" if is_pos else "result-negative"
                        icon       = "😊" if is_pos else "😞"

                        st.markdown(f"""
                        <div class="result-card {card_cls}">
                            <div class="result-icon">{icon}</div>
                            <div>
                                <div class="result-label">Detected Sentiment</div>
                                <div class="result-sentiment">{sentiment}</div>
                                <div class="result-confidence">Confidence: <strong>{pct}%</strong></div>
                                <div class="confidence-bar-track">
                                    <div class="confidence-bar-fill" style="width:{pct}%"></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"API error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Could not reach the backend. Is it running?  \n`{e}`")
        else:
            st.warning("Please enter a review before analysing.")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — AMAZON REVIEWS
# ═══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## Live Amazon Reviews")
    st.markdown('<p class="section-desc">Enter an Amazon product ASIN and optionally your Rainforest API key to fetch real reviews and classify them in bulk. Without an API key, mock data is returned.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        product_id = st.text_input("Amazon ASIN", value="B08N5WRWNW", placeholder="e.g. B08N5WRWNW")
        st.markdown('<p class="asin-hint">Find the ASIN in any Amazon product URL after <code>/dp/</code></p>', unsafe_allow_html=True)
    with col2:
        api_key = st.text_input("Rainforest API Key (optional)", type="password", placeholder="••••••••••••••••")

    if st.button("Fetch & Classify Reviews →", key="batch_btn"):
        try:
            with st.spinner("Fetching and classifying reviews…"):
                payload = {"product_id": product_id}
                if api_key:
                    payload["api_key"] = api_key

                response = requests.post(f"{API_URL}/fetch_reviews", json=payload)
                if response.status_code == 200:
                    data    = response.json()
                    reviews = data.get("reviews", [])

                    if "note" in data:
                        st.info(f"ℹ️  {data['note']}")

                    if not reviews:
                        st.warning("No reviews returned for this ASIN.")
                    else:
                        # Summary strip
                        pos_count = sum(1 for r in reviews if r["sentiment"] == "Positive")
                        neg_count = len(reviews) - pos_count
                        st.markdown(f"""
                        <div style="display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;">
                            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.9rem 1.4rem;min-width:130px;text-align:center;">
                                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#34d399;">{pos_count}</div>
                                <div style="font-size:0.8rem;color:#64748b;letter-spacing:0.08em;text-transform:uppercase;font-weight:500;">Positive</div>
                            </div>
                            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.9rem 1.4rem;min-width:130px;text-align:center;">
                                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#f87171;">{neg_count}</div>
                                <div style="font-size:0.8rem;color:#64748b;letter-spacing:0.08em;text-transform:uppercase;font-weight:500;">Negative</div>
                            </div>
                            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:10px;padding:0.9rem 1.4rem;min-width:130px;text-align:center;">
                                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#818cf8;">{len(reviews)}</div>
                                <div style="font-size:0.8rem;color:#64748b;letter-spacing:0.08em;text-transform:uppercase;font-weight:500;">Total</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        for i, rev in enumerate(reviews):
                            is_pos     = rev["sentiment"] == "Positive"
                            badge_cls  = "badge-pos" if is_pos else "badge-neg"
                            badge_icon = "✅" if is_pos else "❌"
                            st.markdown(f"""
                            <div class="review-card">
                                <div class="review-num">Review {i + 1}</div>
                                <div class="review-text">{rev["text"]}</div>
                                <span class="badge {badge_cls}">{badge_icon} {rev["sentiment"]}</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Could not reach the backend. Is it running?  \n`{e}`")
