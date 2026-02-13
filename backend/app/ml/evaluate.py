# Model Evaluation Utilities for PoisonSense NLP Model
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
from datetime import datetime


def evaluate_model(
    model,
    test_loader,
    label_encoder,
    device: str = "cpu",
) -> Dict:
    """
    Run full evaluation on the trained model and return structured metrics.

    Args:
        model: Trained DistilBERT model.
        test_loader: DataLoader with test data.
        label_encoder: Fitted LabelEncoder.
        device: 'cuda' or 'cpu'.

    Returns:
        Dictionary with accuracy, precision, recall, f1,
        per-class report, and confusion matrix.
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch[0].to(device)
            attention_mask = batch[1].to(device)
            labels = batch[2]

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)

            all_preds.extend(preds.tolist())
            all_labels.extend(labels.numpy().tolist())
            all_probs.extend(probs.tolist())

    # Overall metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average="weighted", zero_division=0
    )

    # Per-class report
    class_names = list(label_encoder.classes_)
    per_class = classification_report(
        all_labels,
        all_preds,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "per_class_report": per_class,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
        "total_samples": len(all_labels),
        "evaluated_at": datetime.utcnow().isoformat(),
    }


def get_top_k_predictions(
    model,
    tokenizer,
    text: str,
    label_encoder,
    device: str = "cpu",
    k: int = 3,
) -> List[Dict]:
    """
    Get top-k predictions with confidence scores for a single input.

    Args:
        model: Trained model.
        tokenizer: DistilBERT tokenizer.
        text: Symptom text input.
        label_encoder: Fitted LabelEncoder.
        device: 'cuda' or 'cpu'.
        k: Number of top predictions to return.

    Returns:
        List of dicts with poison_name and confidence.
    """
    model.eval()
    tokens = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="pt",
    )
    tokens = {key: val.to(device) for key, val in tokens.items()}

    with torch.no_grad():
        outputs = model(**tokens)
        probs = torch.softmax(outputs.logits, dim=1)

    top_probs, top_indices = torch.topk(probs, min(k, probs.shape[1]))
    top_probs = top_probs.cpu().numpy()[0]
    top_indices = top_indices.cpu().numpy()[0]

    results = []
    for prob, idx in zip(top_probs, top_indices):
        results.append({
            "poison_name": label_encoder.inverse_transform([idx])[0],
            "confidence": round(float(prob), 4),
        })

    return results


def compute_severity_from_confidence(confidence: float) -> str:
    """
    Map model confidence to a severity advisory level.
    Higher confidence in a dangerous poison → higher urgency.
    """
    if confidence >= 0.85:
        return "high"
    elif confidence >= 0.60:
        return "moderate"
    elif confidence >= 0.35:
        return "low"
    else:
        return "uncertain"


def format_evaluation_summary(metrics: Dict) -> str:
    """
    Format evaluation metrics into a human-readable summary string.
    """
    lines = [
        "=" * 50,
        "  PoisonSense NLP Model - Evaluation Summary",
        "=" * 50,
        f"  Accuracy  : {metrics['accuracy']:.4f}",
        f"  Precision : {metrics['precision']:.4f}",
        f"  Recall    : {metrics['recall']:.4f}",
        f"  F1 Score  : {metrics['f1_score']:.4f}",
        f"  Samples   : {metrics['total_samples']}",
        f"  Classes   : {len(metrics['class_names'])}",
        f"  Evaluated : {metrics['evaluated_at']}",
        "=" * 50,
    ]
    return "\n".join(lines)
