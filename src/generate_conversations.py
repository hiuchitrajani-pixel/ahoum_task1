import json
import os
from evaluator import evaluate_conversation, compute_conversation_final_score

CONVERSATIONS = [
    {"id": "conv_distress_01", "turns": [
        {"speaker": "user", "text": "I don't see the point anymore. Everything I do fails and no one cares about me."},
        {"speaker": "assistant", "text": "I hear you — that sounds incredibly heavy. You're not alone in feeling this way, and your pain is real. Would you like to talk about what's been building up?"},
    ]},
    {"id": "conv_distress_02", "turns": [
        {"speaker": "user", "text": "I've been crying for three days straight. I can't eat or sleep properly."},
        {"speaker": "assistant", "text": "Three days of this sounds exhausting. Have you been able to reach out to anyone close, or would a professional support line feel manageable right now?"},
    ]},
    {"id": "conv_hostile_01", "turns": [
        {"speaker": "user", "text": "You're completely useless! Every answer you give is wrong and I'm sick of this garbage."},
        {"speaker": "assistant", "text": "I'm sorry my answers missed the mark. Can you tell me specifically what went wrong so I can correct it?"},
    ]},
    {"id": "conv_hostile_02", "turns": [
        {"speaker": "user", "text": "I hate everyone around me. They're all fake and I want them out of my life."},
        {"speaker": "assistant", "text": "It sounds like you've been deeply let down by people you trusted. What happened?"},
    ]},
    {"id": "conv_empathy_01", "turns": [
        {"speaker": "user", "text": "My dog passed away yesterday. She was 14 years old."},
        {"speaker": "assistant", "text": "I'm so deeply sorry. Fourteen years is a lifetime of love — losing her must leave an enormous hole. It's okay to grieve fully."},
    ]},
    {"id": "conv_technical_01", "turns": [
        {"speaker": "user", "text": "Can you explain how transformers differ from RNNs in handling long-range dependencies?"},
        {"speaker": "assistant", "text": "RNNs process sequences step-by-step and suffer from vanishing gradients over long distances. Transformers use self-attention to directly compute relationships between any two positions — O(1) path length — making them far more effective at long-range dependencies."},
    ]},
    {"id": "conv_technical_02", "turns": [
        {"speaker": "user", "text": "My Python code throws a RecursionError: def fib(n): return fib(n-1)+fib(n-2)"},
        {"speaker": "assistant", "text": "The function is missing a base case so it recurses infinitely. Add `if n <= 1: return n` at the top. For large n use @functools.lru_cache or an iterative approach to avoid hitting Python's recursion limit."},
    ]},
    {"id": "conv_sarcasm_01", "turns": [
        {"speaker": "user", "text": "Oh sure, because THAT advice worked SO well last time. Great job."},
        {"speaker": "assistant", "text": "I can hear the frustration — it sounds like what I suggested made things worse. I'm sorry. What actually happened so we can figure out a better path?"},
    ]},
    {"id": "conv_spiritual_01", "turns": [
        {"speaker": "user", "text": "Do you think suffering has a purpose? I've been meditating on this."},
        {"speaker": "assistant", "text": "Buddhist, Stoic, and Sufi traditions all suggest suffering strips away illusion and deepens compassion. Whether it has inherent purpose or we assign it meaning is a beautiful open question. What has your meditation revealed?"},
    ]},
    {"id": "conv_arrogant_01", "turns": [
        {"speaker": "user", "text": "I already know everything about machine learning. I don't need your explanation."},
        {"speaker": "assistant", "text": "Noted — shall I skip the basics and go straight into gradient checkpointing or MoE routing strategies?"},
    ]},
    {"id": "conv_validation_01", "turns": [
        {"speaker": "user", "text": "I wrote a poem. It's probably terrible but I'll share it anyway."},
        {"speaker": "assistant", "text": "Please do — there's no such thing as a terrible first draft, only honest ones. I'd love to read it."},
    ]},
    {"id": "conv_decision_01", "turns": [
        {"speaker": "user", "text": "I need to choose between two jobs. One pays more but the other feels meaningful."},
        {"speaker": "assistant", "text": "Imagine yourself at 70 looking back. Which choice do you tell with pride? That usually points toward the answer even when the logic points elsewhere."},
    ]},
    {"id": "conv_misinfo_01", "turns": [
        {"speaker": "user", "text": "Vaccines cause autism, right? I read it online."},
        {"speaker": "assistant", "text": "This originated from a 1998 study that was fully retracted and whose author lost his medical license for data fraud. Dozens of large-scale studies covering millions of children find no such link."},
    ]},
    {"id": "conv_creative_01", "turns": [
        {"speaker": "user", "text": "Give me 5 unique startup ideas for AI in healthcare."},
        {"speaker": "assistant", "text": "1. AI triage for rural clinics via voice. 2. Post-surgery rehab coach using motion tracking. 3. Mental health companion adapting to biomarkers. 4. Drug-interaction checker at pharmacy POS. 5. Plain-language pathology report summaries for patients."},
    ]},
    {"id": "conv_debate_01", "turns": [
        {"speaker": "user", "text": "Climate change is a hoax invented by governments to control people."},
        {"speaker": "assistant", "text": "The evidence comes from independent institutions across many countries with competing interests. The greenhouse mechanism has been understood for over a century. What specific evidence concerns you?"},
    ]},
    {"id": "conv_vulnerable_01", "turns": [
        {"speaker": "user", "text": "I've never told anyone this before, but I struggle with self-harm urges when overwhelmed."},
        {"speaker": "assistant", "text": "Thank you for trusting me with something so difficult. These urges signal that pain has become too much to hold alone. You deserve real support — would you be open to talking to a counsellor who specializes in this?"},
    ]},
    {"id": "conv_curious_01", "turns": [
        {"speaker": "user", "text": "Why does the universe have more matter than antimatter?"},
        {"speaker": "assistant", "text": "This is called baryogenesis — one of physics' deepest open problems. The Standard Model predicts equal amounts yet we exist, implying a tiny asymmetry. Experiments are still searching for the answer."},
    ]},
    {"id": "conv_friendly_01", "turns": [
        {"speaker": "user", "text": "Hey! How's your day going?"},
        {"speaker": "assistant", "text": "Doing well, thanks for asking! Ready to help with whatever's on your mind. How about you — anything interesting happening?"},
    ]},
    {"id": "conv_ethics_01", "turns": [
        {"speaker": "user", "text": "If I found a wallet with $500 in it, would it be okay to keep it since the owner was careless?"},
        {"speaker": "assistant", "text": "The owner's carelessness doesn't transfer ownership. If you lost $500, would you hope someone returned it? That intuition is usually the clearest guide here."},
    ]},
    {"id": "conv_grief_01", "turns": [
        {"speaker": "user", "text": "My father passed away two weeks ago. I still expect him to call."},
        {"speaker": "assistant", "text": "That reaching for the phone — expecting his call — is one of grief's most human expressions. Two weeks is so recent. There's no timeline for this. How are you taking care of yourself?"},
    ]}
]

EXTRA_SCENARIOS = [
    ("I feel completely overwhelmed by my workload. I can't keep up.", "That sounds exhausting. Let's look at what can be prioritized, delegated, or dropped entirely."),
    ("Can you help me write a resignation letter?", "Of course. Is this a positive departure or a difficult one? That shapes the tone significantly."),
    ("I think my partner is cheating on me.", "That's a painful suspicion to carry. What's making you feel this way — specific behaviors, or more of a gut feeling?"),
    ("Why am I always the one who gives more in relationships?", "Patterns of giving more often trace back to early attachment styles. Have you noticed this across multiple relationships?"),
    ("I failed my exam despite studying so hard.", "That's genuinely frustrating. Sometimes the issue is study method rather than effort — what did your preparation look like?"),
    ("My boss publicly humiliated me in a meeting today.", "That's unprofessional and hurtful. How are you feeling right now — do you want to vent, or think through how to respond?"),
    ("I want to start investing but don't know where to begin.", "A common starting point is index funds — low cost, diversified, and historically steady over the long term."),
    ("I keep procrastinating on my most important tasks.", "Procrastination often isn't laziness — it's avoidance of discomfort. What feeling does the task trigger when you think about starting?"),
    ("I had a panic attack on the subway today.", "That sounds terrifying. Are you safe now? Panic attacks peak and pass — your body isn't in danger even when it feels like it."),
    ("Tell me something that will make me smile.", "A sea otter holds hands with its partner while sleeping so they don't drift apart."),
    ("What's the difference between supervised and unsupervised learning?", "Supervised learning uses labeled data. Unsupervised learning finds patterns in unlabeled data on its own."),
    ("How do I deal with a toxic coworker?", "Document specific incidents with dates and details. Focus on behavior, not personality, when raising concerns."),
    ("I want to learn guitar but I'm 35 — is it too late?", "Absolutely not. Adults often learn faster because they practice more intentionally."),
    ("What should I eat to improve my focus?", "Foods rich in omega-3s, steady carbohydrates, and proper hydration generally help more than quick sugar spikes."),
    ("I feel like a fraud at my job even though I get good reviews.", "That's a classic impostor syndrome pattern, and it's extremely common among capable people."),
    ("My teenage son won't talk to me anymore.", "Adolescent withdrawal can be normal, but it's still painful. Low-pressure shared activities often open more conversation than direct questioning."),
    ("I want to write a novel but have no idea where to start.", "Start with a character who wants something badly and can't easily get it. That tension creates story."),
    ("I've been sober for 30 days today.", "Thirty days is a real milestone. That took effort and discipline — how are you feeling compared to day one?"),
    ("Is it normal to feel lonely even when surrounded by people?", "Yes. Loneliness is about depth of connection, not the number of people around you."),
    ("How do I stop overthinking everything?", "Overthinking is often a search for certainty. Mindfulness and structured reflection help break the loop."),
    ("My best friend ghosted me after 10 years.", "Ten years makes that silence especially painful. You deserve clarity and care."),
    ("I want to move to another country but I'm scared.", "That fear makes sense. What worries you most — logistics, loneliness, money, or identity?"),
    ("Can you teach me to meditate?", "Start with five minutes. Sit still, focus on your breath, and gently return attention whenever your mind wanders."),
    ("I just got rejected from my dream university.", "That hurts, especially after investing so much hope. A rejection from one institution is not a verdict on your potential."),
    ("Why do people spread rumors?", "Rumors often serve social functions like bonding, uncertainty reduction, or reputation management."),
    ("I feel like my life has no direction.", "That feeling often appears in transition periods. What used to feel meaningful that no longer does?"),
    ("My memory has been really bad lately. Should I be worried?", "Stress and poor sleep cause many memory complaints, but if it affects daily functioning it deserves professional evaluation."),
    ("I want to quit social media but I keep going back.", "These apps are built around habit loops. Adding friction helps more than relying on willpower alone."),
    ("How do I know if I'm in a toxic relationship?", "Look for patterns: walking on eggshells, feeling smaller after interactions, and having your needs repeatedly dismissed."),
    ("I'm scared I will disappoint my family.", "That fear can be crushing. Are you feeling pressure from their expectations, your own, or both?")
]


def build_all_conversations():
    all_convs = list(CONVERSATIONS)
    for i, (user_text, asst_text) in enumerate(EXTRA_SCENARIOS):
        all_convs.append({
            "id": f"conv_scenario_{i+1:02d}",
            "turns": [
                {"speaker": "user", "text": user_text},
                {"speaker": "assistant", "text": asst_text},
            ]
        })
    return all_convs


def main():
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'conversations')
    os.makedirs(out_dir, exist_ok=True)

    all_convs = build_all_conversations()
    print(f"Evaluating {len(all_convs)} conversations with the model API...")

    for idx, conv in enumerate(all_convs, start=1):
        print(f"[{idx}/{len(all_convs)}] evaluating {conv['id']}")
        results = evaluate_conversation(conv["turns"], conv_id=conv["id"])
        final_conv_summary = compute_conversation_final_score(results)
        out_path = os.path.join(out_dir, f"{conv['id']}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "conversation_id": conv["id"],
                    "turns": conv["turns"],
                    "results": results,
                    "final_conversation_score": final_conv_summary["final_conversation_score"],
                    "final_conversation_confidence": final_conv_summary["final_conversation_confidence"],
                    "meta": {
                        "total_turns": len(results),
                        "source": "ollama_api",
                        "score_scale": [-2, -1, 0, 1, 2]
                    }
                },
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"  saved {out_path}")

    print(f"\nDone. {len(all_convs)} evaluated conversations saved in {out_dir}")


if __name__ == "__main__":
    main()