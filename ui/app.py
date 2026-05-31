import sys
import os
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
  [data-testid="stAppViewContainer"] { background: #f7f6f2; }
  [data-testid="stSidebar"] { background: #1c1b19; }
  [data-testid="stSidebar"] * { color: #cdccca !important; }
  h1 { color: #01696f !important; }
  .stButton>button { background: #01696f; color: white; border: none; border-radius: 8px; }
  .stButton>button:hover { background: #0c4e54; }
  .score-badge { padding: 3px 10px; border-radius: 999px; font-size: 0.85rem; display: inline-block; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Ahoum Conversation Evaluator")
st.caption("300-facet benchmark · Ollama batched inference · final turn and conversation scoring")

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    model = st.selectbox("Model", ["qwen2.5:1.5b", "llama3:8b", "mistral:7b"], index=0)
    batch_size = st.slider("Facets per batch", 10, 50, 20, 5)
    st.markdown("---")
    st.markdown("### Categories")
    all_cats = ["behavioral", "emotion", "pragmatic", "social", "moral", "linguistic", "safety", "clinical", "other"]
    selected_cats = st.multiselect("Include", all_cats, default=all_cats)
    st.markdown("---")
    st.markdown("### Score Scale")
    for score, label, color in [
        (-2, "Strong negative evidence", "#fee2e2"),
        (-1, "Slight negative evidence", "#fecaca"),
        (0, "Unclear / not inferable", "#e5e7eb"),
        (1, "Clear positive evidence", "#d1fae5"),
        (2, "Strong positive evidence", "#bbf7d0")
    ]:
        st.markdown(
            f'<span class="score-badge" style="background:{color};"><b>{score}</b> — {label}</span>',
            unsafe_allow_html=True
        )

tab1, tab2, tab3, tab4 = st.tabs(["📝 Single Turn", "💬 Full Conversation", "📊 Browse Results", "📚 Facet Explorer"])


def build_mock_result(turn_text, speaker):
    random.seed(hash(turn_text) % 100000)
    mock_facets = [
        {"facet_id": 1, "facet_name": "Compassion", "category": "emotion"},
        {"facet_id": 2, "facet_name": "Hostility", "category": "safety"},
        {"facet_id": 3, "facet_name": "Assertiveness", "category": "pragmatic"},
        {"facet_id": 4, "facet_name": "Clarity", "category": "linguistic"},
        {"facet_id": 5, "facet_name": "Empathy", "category": "emotion"},
        {"facet_id": 6, "facet_name": "Helpfulness", "category": "behavioral"},
        {"facet_id": 7, "facet_name": "Honesty", "category": "moral"},
        {"facet_id": 8, "facet_name": "Patience", "category": "behavioral"},
        {"facet_id": 9, "facet_name": "Anxiety", "category": "clinical"},
        {"facet_id": 10, "facet_name": "Warmth", "category": "pragmatic"},
    ]
    mock_scores = []
    for f in mock_facets:
        score = random.choice([-2, -1, 0, 1, 2])
        conf = round(random.uniform(0.55, 0.95), 2)
        mock_scores.append({
            **f,
            "score": score,
            "confidence": conf,
            "evidence": "demo signal"
        })

    if mock_scores:
        weighted = sum(x["score"] * x["confidence"] for x in mock_scores)
        conf_sum = sum(x["confidence"] for x in mock_scores)
        final_turn_score = round(weighted / conf_sum, 3) if conf_sum else 0.0
        final_turn_confidence = round(conf_sum / len(mock_scores), 3)
    else:
        final_turn_score = 0.0
        final_turn_confidence = 0.0

    return {
        "conversation_id": "demo",
        "turn_index": 0,
        "speaker": speaker,
        "turn_text": turn_text,
        "model": "mock",
        "facet_scores": mock_scores,
        "total_facets": len(mock_scores),
        "final_turn_score": final_turn_score,
        "final_turn_confidence": final_turn_confidence
    }


with tab1:
    st.subheader("Score a Single Conversation Turn")
    speaker = st.radio("Speaker", ["user", "assistant"], horizontal=True)
    turn_text = st.text_area(
        "Turn text",
        placeholder='e.g. "I do not see the point anymore. Everything feels hopeless."',
        height=120
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        run_btn = st.button("🚀 Evaluate", type="primary", use_container_width=True)
    with col2:
        st.info(f"~{max(1, 300 // batch_size)} LLM calls may be made. Ensure Ollama is running with `ollama serve`.")

    if run_btn and turn_text.strip():
        with st.spinner("Running inference..."):
            try:
                os.environ["MODEL_NAME"] = model
                os.environ["BATCH_SIZE"] = str(batch_size)
                from evaluator import evaluate_turn, load_facets
                facets = load_facets()
                if selected_cats:
                    facets = [f for f in facets if f["category"] in selected_cats]
                result = evaluate_turn(turn_text, speaker=speaker, facets=facets)
            except Exception as e:
                st.warning(f"Ollama not reachable ({e}). Showing mock scores for demo.")
                result = build_mock_result(turn_text, speaker)

        scores = result["facet_scores"]
        df = pd.DataFrame(scores)

        st.markdown("---")
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Facets Scored", len(scores))
        k2.metric("Final Turn Score", f"{result.get('final_turn_score', 0.0):.3f}")
        k3.metric("Turn Confidence", f"{result.get('final_turn_confidence', 0.0):.3f}")
        k4.metric("Positive (≥1)", int((df["score"] >= 1).sum()) if not df.empty else 0)
        k5.metric("Negative (≤-1)", int((df["score"] <= -1).sum()) if not df.empty else 0)

        if not df.empty:
            st.markdown("#### Category Breakdown")
            cat_df = df.groupby("category").agg(
                mean_score=("score", "mean"),
                mean_confidence=("confidence", "mean"),
                count=("facet_id", "count")
            ).round(3).reset_index().sort_values("mean_score", ascending=False)
            st.dataframe(cat_df, use_container_width=True, hide_index=True)

            st.markdown("#### All Facet Scores")
            show_cols = ["facet_name", "category", "score", "confidence", "evidence"]
            st.dataframe(
                df[show_cols].sort_values(["score", "confidence"], ascending=[False, False]),
                use_container_width=True,
                height=380,
                hide_index=True
            )

        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name=f"eval_{int(time.time())}.json",
            mime="application/json"
        )


with tab2:
    st.subheader("Score a Full Conversation")
    st.info("Prefix each line with `user:` or `assistant:`")
    conv_input = st.text_area(
        "Conversation",
        value="user: I feel really anxious about my interview tomorrow.\nassistant: That's completely understandable. What specifically worries you most?\nuser: I'm afraid I'll blank out on technical questions.",
        height=220
    )
    conv_btn = st.button("🚀 Evaluate Conversation", type="primary")

    if conv_btn and conv_input.strip():
        turns = []
        for line in conv_input.strip().split("\n"):
            line = line.strip()
            if line.lower().startswith("user:"):
                turns.append({"speaker": "user", "text": line[5:].strip()})
            elif line.lower().startswith("assistant:"):
                turns.append({"speaker": "assistant", "text": line[10:].strip()})

        if not turns:
            st.error("No valid turns found. Prefix each line with `user:` or `assistant:`.")
        else:
            with st.spinner("Running conversation evaluation..."):
                try:
                    os.environ["MODEL_NAME"] = model
                    os.environ["BATCH_SIZE"] = str(batch_size)
                    from evaluator import evaluate_conversation, compute_conversation_final_score, load_facets
                    facets = load_facets()
                    if selected_cats:
                        facets = [f for f in facets if f["category"] in selected_cats]

                    results = []
                    from evaluator import evaluate_turn
                    for idx, t in enumerate(turns):
                        results.append(
                            evaluate_turn(
                                turn_text=t["text"],
                                conversation_id="streamlit_conversation",
                                turn_index=idx,
                                speaker=t["speaker"],
                                facets=facets
                            )
                        )
                    conv_summary = compute_conversation_final_score(results)
                    conversation_output = {
                        "conversation_id": "streamlit_conversation",
                        "turns": turns,
                        "results": results,
                        "final_conversation_score": conv_summary["final_conversation_score"],
                        "final_conversation_confidence": conv_summary["final_conversation_confidence"],
                        "meta": {
                            "total_turns": len(results),
                            "source": "streamlit_ui",
                            "score_scale": [-2, -1, 0, 1, 2]
                        }
                    }
                except Exception as e:
                    st.warning(f"Ollama not reachable ({e}). Showing parsed turns only.")
                    conversation_output = {
                        "conversation_id": "streamlit_conversation",
                        "turns": turns,
                        "results": [],
                        "final_conversation_score": 0.0,
                        "final_conversation_confidence": 0.0
                    }

            st.success(f"Parsed **{len(turns)} turns**")
            c1, c2 = st.columns(2)
            c1.metric("Final Conversation Score", f"{conversation_output.get('final_conversation_score', 0.0):.3f}")
            c2.metric("Conversation Confidence", f"{conversation_output.get('final_conversation_confidence', 0.0):.3f}")

            for r in conversation_output.get("results", []):
                label = f"Turn {r['turn_index']} · {r['speaker'].upper()} · {r['turn_text'][:60]}..."
                with st.expander(label):
                    st.write(r["turn_text"])
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Final Turn Score", f"{r.get('final_turn_score', 0.0):.3f}")
                    m2.metric("Turn Confidence", f"{r.get('final_turn_confidence', 0.0):.3f}")
                    m3.metric("Facets", r.get("total_facets", 0))

                    df = pd.DataFrame(r.get("facet_scores", []))
                    if not df.empty:
                        st.dataframe(
                            df[["facet_name", "category", "score", "confidence", "evidence"]].sort_values(
                                ["score", "confidence"], ascending=[False, False]
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

            st.download_button(
                "⬇️ Download Conversation JSON",
                data=json.dumps(conversation_output, indent=2, ensure_ascii=False),
                file_name=f"conversation_eval_{int(time.time())}.json",
                mime="application/json"
            )


with tab3:
    st.subheader("Browse Saved Results")
    conv_dir = os.path.join(os.path.dirname(__file__), '..', 'conversations')

    if os.path.exists(conv_dir):
        files = sorted([f for f in os.listdir(conv_dir) if f.endswith('.json')])
        if files:
            st.success(f"**{len(files)} saved conversations**")
            selected = st.selectbox("Select conversation", files)

            with open(os.path.join(conv_dir, selected), encoding="utf-8") as f:
                data = json.load(f)

            results = data.get("results", [])
            st.write(f"**{len(results)} turn(s)** in this conversation")

            c1, c2 = st.columns(2)
            c1.metric("Final Conversation Score", f"{data.get('final_conversation_score', 0.0):.3f}")
            c2.metric("Conversation Confidence", f"{data.get('final_conversation_confidence', 0.0):.3f}")

            for r in results:
                label = f"Turn {r['turn_index']} · {r['speaker'].upper()} · \"{r['turn_text'][:55]}...\""
                with st.expander(label):
                    df = pd.DataFrame(r["facet_scores"])
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Final Turn Score", f"{r.get('final_turn_score', 0.0):.3f}")
                    m2.metric("Turn Confidence", f"{r.get('final_turn_confidence', 0.0):.3f}")
                    m3.metric("Facets", len(df))

                    if not df.empty:
                        st.dataframe(
                            df[["facet_name", "category", "score", "confidence", "evidence"]].sort_values(
                                ["score", "confidence"], ascending=[False, False]
                            ),
                            use_container_width=True,
                            hide_index=True
                        )
        else:
            st.info("No conversations yet. Run: `python src/generate_conversations.py`")
    else:
        st.info("Conversations folder not found.")


with tab4:
    st.subheader("Facet Dataset Explorer")
    facets_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_benchmark_cleaned.csv')

    if os.path.exists(facets_csv):
        df = pd.read_csv(facets_csv)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Facets", len(df))
        c2.metric("Observable from Text", int(df["observable_from_text"].sum()))
        c3.metric("Categories", df["category"].nunique())
        c4.metric("Score Range", "-2 to 2")

        col1, col2 = st.columns(2)
        with col1:
            cat_filter = st.selectbox("Filter by category", ["All"] + sorted(df["category"].dropna().unique().tolist()))
        with col2:
            dir_filter = st.selectbox("Filter by direction", ["All", "higher_is_better", "lower_is_better"])

        filtered = df.copy()
        if cat_filter != "All":
            filtered = filtered[filtered["category"] == cat_filter]
        if dir_filter != "All":
            filtered = filtered[filtered["scoring_direction"] == dir_filter]

        st.markdown("#### Category Counts")
        st.dataframe(
            df["category"].value_counts().rename_axis("category").reset_index(name="count"),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Facet Table")
        show_cols = [
            "facet_id", "facet_name", "category", "facet_group",
            "scoring_direction", "applicable_to", "evidence_required"
        ]
        st.dataframe(
            filtered[show_cols],
            use_container_width=True,
            height=420,
            hide_index=True
        )
    else:
        st.info("Benchmark facet file not found. Run: `python src/preprocess.py`")