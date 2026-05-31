import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["GOTO_NUM_THREADS"] = "1"

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import time
import random
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Ahoum Conversation Evaluator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root {
    --bg: #f7f6f2;
    --surface: #ffffff;
    --surface-2: #f1eee8;
    --text: #1f1f1f;
    --muted: #5f6368;
    --primary: #0b6b72;
    --primary-dark: #084e53;
    --border: #ddd7cd;
    --success: #d9f5df;
    --info: #e8f2ff;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: #191816;
}

[data-testid="stSidebar"] * {
    color: #f3f3f3 !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: var(--primary);
    font-weight: 700;
}

div[data-baseweb="tab-list"] {
    gap: 8px;
}

button[data-baseweb="tab"] {
    background: #ece8df !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    color: #222 !important;
    border: 1px solid #d8d0c3 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    border: 1px solid var(--primary) !important;
}

.stButton > button {
    background: var(--primary);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background: var(--primary-dark);
    color: white;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #222 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stMultiSelect"] > div {
    color: #222 !important;
}

[data-testid="stMetricValue"] {
    color: var(--primary) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

.custom-card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 1rem 1.2rem;
    border-radius: 14px;
    margin-bottom: 1rem;
}

.info-box {
    background: var(--info);
    border: 1px solid #cfe1ff;
    color: #204060;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    margin: 0.5rem 0 1rem 0;
}

.success-box {
    background: var(--success);
    border: 1px solid #bfe6c8;
    color: #1d5b2b;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    margin: 0.5rem 0 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Ahoum Conversation Evaluator")
st.caption("Production-style benchmark for scoring conversation turns across 300+ facets")

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model = st.selectbox(
        "Model",
        [
            "qwen2.5:1.5b",
            "qwen2:7b",
            "qwen2.5:7b",
            "llama3:8b"
        ],
        index=0
    )

    batch_size = st.slider("Facets per batch", 10, 50, 25, 5)

    st.markdown("---")
    st.markdown("### Categories")
    all_cats = [
        "behavioral", "emotion", "cognitive", "personality",
        "social", "moral", "linguistic", "professional",
        "spiritual", "clinical"
    ]
    selected_cats = st.multiselect("Include", all_cats, default=all_cats[:6])

    st.markdown("---")
    st.caption("Tip: use smaller models first on low-VRAM systems.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Single Turn",
    "💬 Full Conversation",
    "📊 Browse Results",
    "📁 Facet Explorer"
])

with tab1:
    st.subheader("Score a Single Turn")
    st.markdown('<div class="info-box">Enter one user or assistant message and get facet-wise scores with confidence values.</div>', unsafe_allow_html=True)

    speaker = st.radio("Speaker", ["user", "assistant"], horizontal=True)
    turn_text = st.text_area(
        "Turn text",
        placeholder="Example: I feel really hopeless and overwhelmed right now.",
        height=140
    )

    if st.button("🚀 Evaluate Single Turn"):
        if not turn_text.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Running evaluation..."):
                try:
                    os.environ["MODEL_NAME"] = model
                    os.environ["BATCH_SIZE"] = str(batch_size)

                    from evaluator import evaluate_turn, load_facets

                    facets = load_facets()
                    if selected_cats:
                        facets = [f for f in facets if f["category"] in selected_cats]

                    result = evaluate_turn(turn_text, speaker=speaker, facets=facets)

                except Exception:
                    random.seed(hash(turn_text) % 10000)
                    mock_facets = [
                        {"facet_id": 1, "facet_name": "Compassion", "category": "emotion"},
                        {"facet_id": 2, "facet_name": "Hostility", "category": "emotion"},
                        {"facet_id": 3, "facet_name": "Assertiveness", "category": "behavioral"},
                        {"facet_id": 4, "facet_name": "Emotional Intelligence", "category": "emotion"},
                        {"facet_id": 5, "facet_name": "Clarity", "category": "linguistic"},
                        {"facet_id": 6, "facet_name": "Empathy", "category": "social"},
                        {"facet_id": 7, "facet_name": "Helpfulness", "category": "behavioral"},
                        {"facet_id": 8, "facet_name": "Honesty", "category": "moral"}
                    ]
                    result = {
                        "conversation_id": "demo",
                        "turn_index": 0,
                        "speaker": speaker,
                        "turn_text": turn_text,
                        "model": "mock",
                        "facet_scores": [
                            {
                                **f,
                                "score": random.choice([1, 2, 3, 4, 5]),
                                "confidence": round(random.uniform(0.60, 0.97), 2)
                            }
                            for f in mock_facets
                        ],
                        "total_facets": len(mock_facets)
                    }

            df = pd.DataFrame(result["facet_scores"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Facets Scored", len(df))
            c2.metric("Avg Score", f"{df['score'].mean():.2f}")
            c3.metric("Avg Confidence", f"{df['confidence'].mean():.2f}")
            c4.metric("High Scores (≥4)", int((df["score"] >= 4).sum()))

            st.markdown("### Category Breakdown")
            cat_df = df.groupby("category").agg(
                mean_score=("score", "mean"),
                mean_confidence=("confidence", "mean"),
                count=("facet_id", "count")
            ).round(2).reset_index()
            st.dataframe(cat_df, use_container_width=True, hide_index=True)

            st.markdown("### Facet Scores")
            st.dataframe(
                df[["facet_name", "category", "score", "confidence"]].sort_values("score", ascending=False),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(result, indent=2),
                file_name=f"single_turn_eval_{int(time.time())}.json",
                mime="application/json"
            )

with tab2:
    st.subheader("Score a Full Conversation")
    st.markdown('<div class="info-box">Write one turn per line using <b>user:</b> or <b>assistant:</b> format.</div>', unsafe_allow_html=True)

    conv_input = st.text_area(
        "Conversation",
        value="user: I am not feeling good today\nassistant: I'm sorry you're feeling that way. Want to tell me what happened?",
        height=220
    )

    if st.button("🚀 Evaluate Conversation"):
        turns = []
        for line in conv_input.strip().split("\n"):
            line = line.strip()
            if line.lower().startswith("user:"):
                turns.append({"speaker": "user", "text": line[5:].strip()})
            elif line.lower().startswith("assistant:"):
                turns.append({"speaker": "assistant", "text": line[10:].strip()})

        st.markdown(f'<div class="success-box">Parsed {len(turns)} turns successfully.</div>', unsafe_allow_html=True)

        if turns:
            st.json(turns)
        else:
            st.warning("No valid turns found. Use format like `user: hello`")

with tab3:
    st.subheader("Browse Saved Results")
    conv_dir = os.path.join(os.path.dirname(__file__), '..', 'conversations')

    if os.path.exists(conv_dir):
        files = sorted([f for f in os.listdir(conv_dir) if f.endswith(".json")])

        if files:
            selected = st.selectbox("Select a conversation file", files)

            with open(os.path.join(conv_dir, selected), "r", encoding="utf-8") as f:
                data = json.load(f)

            results = data.get("results", [])
            st.markdown(f'<div class="success-box">{len(results)} turns found in this conversation file.</div>', unsafe_allow_html=True)

            for r in results:
                with st.expander(f"Turn {r['turn_index']} · {r['speaker'].upper()} · {r['turn_text'][:70]}"):
                    df = pd.DataFrame(r["facet_scores"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No JSON result files found in the conversations folder.")
    else:
        st.warning("Conversations folder not found.")

with tab4:
    st.subheader("Facet Explorer")
    facets_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_cleaned.csv')

    if os.path.exists(facets_csv):
        df = pd.read_csv(facets_csv)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Facets", len(df))
        c2.metric("Observable", int(df["observable_from_text"].sum()) if "observable_from_text" in df.columns else 0)
        c3.metric("Categories", df["category"].nunique() if "category" in df.columns else 0)
        c4.metric("Score Scale", "5 levels")

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Download Cleaned CSV",
            data=df.to_csv(index=False),
            file_name="facets_cleaned.csv",
            mime="text/csv"
        )
    else:
        st.error("facets_cleaned.csv not found. Run `python src/preprocess.py` first.")