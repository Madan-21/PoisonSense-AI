"""
RAGAS Evaluation Script for PoisonSense RAG Chatbot

Evaluates the RAG pipeline using RAGAS metrics:
  - Faithfulness: Are answers grounded in the retrieved context?
  - Answer Relevancy: Are answers relevant to the question?
  - Context Precision: Are retrieved contexts relevant?
  - Context Recall: Does the retrieved context cover the expected answer?

Usage:
  cd backend
  python -m rag.evaluate_ragas

Requires: ragas, datasets (optional — uses built-in lightweight evaluation by default)
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Ensure backend is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rag.config import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL,
    TOP_K, RELEVANCE_THRESHOLD,
)
from rag import vector_store, agent


# ═══════════════════════════════════════════════════════════════════════
# Test Dataset — domain-specific poisoning/toxicology Q&A pairs
# ═══════════════════════════════════════════════════════════════════════

EVAL_DATASET = [
    {
        "question": "What are the symptoms of organophosphate poisoning?",
        "ground_truth": "Organophosphate poisoning symptoms include excessive salivation, lacrimation, urination, defecation, gastrointestinal distress, emesis (the SLUDGE mnemonic), miosis (constricted pupils), bradycardia, bronchospasm, muscle fasciculations, and in severe cases respiratory failure and seizures.",
    },
    {
        "question": "What is the antidote for paracetamol overdose?",
        "ground_truth": "The antidote for paracetamol (acetaminophen) overdose is N-Acetylcysteine (NAC). It works by replenishing glutathione stores in the liver, which helps neutralize the toxic metabolite NAPQI. It should be administered as early as possible, ideally within 8-10 hours of ingestion.",
    },
    {
        "question": "How should a snake bite be treated as first aid?",
        "ground_truth": "First aid for a snake bite includes: immobilize the affected limb, keep the patient calm and still, remove jewelry or tight clothing near the bite, do not cut the wound or attempt to suck out venom, do not apply a tourniquet, transport the patient to the nearest hospital as quickly as possible for antivenom treatment, and note the time of the bite and appearance of the snake if possible.",
    },
    {
        "question": "What are the dangers of mixing bleach and ammonia?",
        "ground_truth": "Mixing bleach (sodium hypochlorite) and ammonia produces toxic chloramine gases. These gases can cause coughing, shortness of breath, chest pain, nausea, watery eyes, and in severe cases pulmonary edema and death. If exposed, move to fresh air immediately and call emergency services.",
    },
    {
        "question": "How should pesticide poisoning be managed?",
        "ground_truth": "Pesticide poisoning management includes: remove the patient from the source of exposure, remove contaminated clothing, wash the skin with soap and water, if ingested do not induce vomiting unless instructed by a medical professional, call emergency services or poison control, administer atropine and pralidoxime for organophosphate poisoning under medical supervision.",
    },
    {
        "question": "What is activated charcoal used for in poisoning?",
        "ground_truth": "Activated charcoal is used as a gastrointestinal decontaminant in poisoning. It adsorbs many toxins in the GI tract, preventing their absorption into the bloodstream. It is most effective when administered within 1-2 hours of ingestion. It is not effective for all poisons — it does not work well for alcohols, metals (iron, lithium), acids, alkalis, or petroleum products.",
    },
    {
        "question": "What are the symptoms of carbon monoxide poisoning?",
        "ground_truth": "Carbon monoxide poisoning symptoms include headache, dizziness, nausea, vomiting, confusion, weakness, chest pain, blurred vision, and loss of consciousness. Cherry-red skin color may be observed. In severe cases, it can lead to seizures, coma, and death. Exposure to high levels can be rapidly fatal.",
    },
    {
        "question": "How should rat poison ingestion be handled?",
        "ground_truth": "Rat poison (rodenticide) ingestion should be handled by: calling emergency services or poison control immediately, identifying the type of rodenticide if possible (anticoagulant vs non-anticoagulant), not inducing vomiting unless instructed, monitoring for symptoms such as bleeding (anticoagulant type) or neurological symptoms (bromethalin). Treatment for anticoagulant rodenticides is Vitamin K1 under medical supervision.",
    },
    {
        "question": "What is the role of a poison control center?",
        "ground_truth": "Poison control centers provide 24/7 expert guidance on poisoning emergencies. They help identify toxic substances, advise on first aid measures, recommend whether to seek emergency medical care, guide treatment decisions for healthcare providers, track poisoning trends and epidemiology, and provide public education on poison prevention.",
    },
    {
        "question": "How can household chemical poisoning be prevented?",
        "ground_truth": "Household chemical poisoning can be prevented by: storing chemicals in original labeled containers, keeping cleaning products out of reach of children, never mixing cleaning products (especially bleach and ammonia), using products in well-ventilated areas, reading labels and following safety instructions, using child-resistant closures, and keeping the poison control center number accessible.",
    },
]


# ═══════════════════════════════════════════════════════════════════════
# Evaluation Functions
# ═══════════════════════════════════════════════════════════════════════

def run_rag_pipeline(question: str) -> Dict[str, Any]:
    """Run a question through the full RAG pipeline and capture context + answer."""
    # Step 1: Retrieve relevant chunks
    from rag.safety_gate import classify_query
    classification = classify_query(question)
    
    # Get collections to query
    collections = agent._route_collections(question, classification)
    
    # Retrieve from vector store
    existing = set(vector_store.list_collections())
    valid_collections = [c for c in collections if c in existing]
    
    if not valid_collections:
        valid_collections = ["general"]
    
    if len(valid_collections) == 1:
        hits = vector_store.query_collection(question, valid_collections[0], TOP_K)
    else:
        hits = vector_store.query_multiple_collections(question, valid_collections, TOP_K)
    
    filtered = vector_store.filter_by_threshold(hits, RELEVANCE_THRESHOLD)
    
    # Capture the retrieved contexts
    contexts = [h.get("text", "") for h in filtered if h.get("text")]
    
    # Step 2: Generate answer via the full agent pipeline
    result = agent.ask(question)
    answer = result.get("answer", "")
    
    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "source_count": len(filtered),
        "confidence": result.get("confidence", {}),
    }


def compute_faithfulness(answer: str, contexts: List[str]) -> float:
    """
    Compute faithfulness — proportion of answer claims supported by contexts.
    Uses keyword overlap as a proxy for grounding.
    """
    if not answer or not contexts:
        return 0.0
    
    context_text = " ".join(contexts).lower()
    context_words = set(context_text.split())
    
    # Extract meaningful words from answer (ignore common stop words)
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "this", "that", "these",
        "those", "i", "you", "he", "she", "it", "we", "they", "me", "him",
        "her", "us", "them", "my", "your", "his", "its", "our", "their",
        "in", "on", "at", "to", "for", "with", "by", "from", "of", "and",
        "or", "but", "not", "no", "if", "so", "as", "than", "when", "where",
        "how", "what", "which", "who", "whom", "whose", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "any",
        "such", "only", "very", "just", "also", "about", "between", "after",
        "before", "during", "above", "below", "up", "down", "out", "into",
    }
    
    answer_words = set(answer.lower().split()) - stop_words
    answer_words = {w.strip(".,;:!?()[]{}\"'") for w in answer_words if len(w) > 2}
    
    if not answer_words:
        return 0.0
    
    supported = sum(1 for w in answer_words if w in context_words)
    return round(supported / len(answer_words), 4)


def compute_answer_relevancy(question: str, answer: str) -> float:
    """
    Compute answer relevancy — how well the answer addresses the question.
    Uses keyword overlap between question and answer.
    """
    if not answer:
        return 0.0
    
    q_words = set(question.lower().split())
    q_words = {w.strip(".,;:!?") for w in q_words if len(w) > 2}
    
    a_words = set(answer.lower().split())
    a_words = {w.strip(".,;:!?") for w in a_words if len(w) > 2}
    
    if not q_words:
        return 0.0
    
    overlap = len(q_words & a_words)
    return round(min(overlap / len(q_words), 1.0), 4)


def compute_context_precision(question: str, contexts: List[str]) -> float:
    """
    Compute context precision — what fraction of retrieved contexts are relevant.
    A context is relevant if it shares significant keyword overlap with the question.
    """
    if not contexts:
        return 0.0
    
    q_words = set(question.lower().split())
    q_words = {w.strip(".,;:!?") for w in q_words if len(w) > 3}
    
    relevant = 0
    for ctx in contexts:
        ctx_words = set(ctx.lower().split())
        ctx_words = {w.strip(".,;:!?") for w in ctx_words if len(w) > 3}
        overlap = len(q_words & ctx_words)
        if overlap >= 2:  # At least 2 significant shared words
            relevant += 1
    
    return round(relevant / len(contexts), 4)


def compute_context_recall(answer: str, ground_truth: str, contexts: List[str]) -> float:
    """
    Compute context recall — can the ground truth be extracted from contexts?
    Measures how well the retrieved context covers the expected answer.
    """
    if not contexts or not ground_truth:
        return 0.0
    
    context_text = " ".join(contexts).lower()
    
    gt_words = set(ground_truth.lower().split())
    gt_words = {w.strip(".,;:!?()[]") for w in gt_words if len(w) > 3}
    
    if not gt_words:
        return 0.0
    
    covered = sum(1 for w in gt_words if w in context_text)
    return round(covered / len(gt_words), 4)


# ═══════════════════════════════════════════════════════════════════════
# Main Evaluation Loop
# ═══════════════════════════════════════════════════════════════════════

def run_evaluation(dataset: List[Dict] = None, output_file: str = None) -> Dict[str, Any]:
    """
    Run full RAGAS-style evaluation on the dataset.
    Returns aggregate metrics and per-question details.
    """
    if dataset is None:
        dataset = EVAL_DATASET
    
    if output_file is None:
        output_file = str(Path(__file__).parent / "ragas_results.json")
    
    print("=" * 70)
    print("PoisonSense RAG — RAGAS Evaluation")
    print("=" * 70)
    print(f"Questions: {len(dataset)}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"TOP_K: {TOP_K}, Relevance Threshold: {RELEVANCE_THRESHOLD}")
    print()
    
    results = []
    total_latency = 0
    
    for i, item in enumerate(dataset, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        print(f"[{i}/{len(dataset)}] {question[:60]}...")
        
        start = time.time()
        pipeline_result = run_rag_pipeline(question)
        latency = round(time.time() - start, 2)
        total_latency += latency
        
        answer = pipeline_result["answer"]
        contexts = pipeline_result["contexts"]
        
        # Compute metrics
        faithfulness = compute_faithfulness(answer, contexts)
        relevancy = compute_answer_relevancy(question, answer)
        precision = compute_context_precision(question, contexts)
        recall = compute_context_recall(answer, ground_truth, contexts)
        
        result = {
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer[:500],  # Truncate for readability
            "num_contexts": len(contexts),
            "latency_sec": latency,
            "confidence": pipeline_result.get("confidence", {}),
            "metrics": {
                "faithfulness": faithfulness,
                "answer_relevancy": relevancy,
                "context_precision": precision,
                "context_recall": recall,
            },
        }
        results.append(result)
        
        print(f"   ✅ Faith={faithfulness:.2f} | Rel={relevancy:.2f} | "
              f"Prec={precision:.2f} | Recall={recall:.2f} | "
              f"Ctx={len(contexts)} | {latency}s")
    
    # ── Aggregate Metrics ──────────────────────────────────────────
    num = len(results)
    avg = lambda key: round(sum(r["metrics"][key] for r in results) / num, 4) if num else 0
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "llm_provider": LLM_PROVIDER,
            "top_k": TOP_K,
            "relevance_threshold": RELEVANCE_THRESHOLD,
            "num_questions": num,
        },
        "aggregate_metrics": {
            "avg_faithfulness": avg("faithfulness"),
            "avg_answer_relevancy": avg("answer_relevancy"),
            "avg_context_precision": avg("context_precision"),
            "avg_context_recall": avg("context_recall"),
            "avg_latency_sec": round(total_latency / num, 2) if num else 0,
            "total_latency_sec": round(total_latency, 2),
        },
        "per_question": results,
    }
    
    # ── Print Summary ──────────────────────────────────────────────
    print()
    print("=" * 70)
    print("AGGREGATE RESULTS")
    print("=" * 70)
    agg = summary["aggregate_metrics"]
    print(f"  Faithfulness      : {agg['avg_faithfulness']:.4f}")
    print(f"  Answer Relevancy  : {agg['avg_answer_relevancy']:.4f}")
    print(f"  Context Precision : {agg['avg_context_precision']:.4f}")
    print(f"  Context Recall    : {agg['avg_context_recall']:.4f}")
    print(f"  Avg Latency       : {agg['avg_latency_sec']}s")
    print(f"  Total Time        : {agg['total_latency_sec']}s")
    print()
    
    # ── Grade ──────────────────────────────────────────────────────
    overall = (agg['avg_faithfulness'] + agg['avg_answer_relevancy'] + 
               agg['avg_context_precision'] + agg['avg_context_recall']) / 4
    grade = ("A" if overall >= 0.85 else
             "B" if overall >= 0.70 else
             "C" if overall >= 0.55 else
             "D" if overall >= 0.40 else "F")
    
    summary["aggregate_metrics"]["overall_score"] = round(overall, 4)
    summary["aggregate_metrics"]["grade"] = grade
    
    print(f"  Overall Score     : {overall:.4f} (Grade: {grade})")
    print("=" * 70)
    
    # ── Save results ───────────────────────────────────────────────
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n📄 Full results saved to: {output_file}")
    
    return summary


if __name__ == "__main__":
    run_evaluation()
