# ML Prediction Service - Integrates the DistilBERT model
import os
import torch
import pandas as pd
from typing import Dict, List, Optional, Tuple
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime
from app.core.config import settings

class PoisonMLService:
    """Service for ML-based poison prediction using DistilBERT"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.model = None
        self.tokenizer = None
        self.label_encoder = None
        self.df = None  # Dataset for additional info
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_loaded = False
        
        # Paths
        self.model_path = os.path.join(settings.ML_MODEL_PATH, "poison_model")
        self.encoder_path = os.path.join(settings.ML_MODEL_PATH, "label_encoder.pkl")
        self.dataset_path = os.path.join(settings.ML_DATA_PATH, "symptom_based_poison_dataset_1200.csv")
        
        self._initialized = True
    
    def load_model(self) -> bool:
        """Load the trained model, tokenizer, and label encoder"""
        try:
            # Check if saved model exists
            if os.path.exists(self.model_path):
                print(f"Loading saved model from {self.model_path}")
                self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
                self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
                
                # Load label encoder
                if os.path.exists(self.encoder_path):
                    with open(self.encoder_path, 'rb') as f:
                        self.label_encoder = pickle.load(f)
            else:
                # Load base model (will need training)
                print("Loading base DistilBERT model...")
                self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
                
                # Try to load dataset to get number of labels
                if os.path.exists(self.dataset_path):
                    self.df = pd.read_csv(self.dataset_path)
                    self.label_encoder = LabelEncoder()
                    self.label_encoder.fit(self.df['poison_name'])
                    num_labels = len(self.label_encoder.classes_)
                    
                    self.model = DistilBertForSequenceClassification.from_pretrained(
                        'distilbert-base-uncased', 
                        num_labels=num_labels
                    )
                else:
                    print("Warning: Dataset not found, using default 10 labels")
                    self.model = DistilBertForSequenceClassification.from_pretrained(
                        'distilbert-base-uncased', 
                        num_labels=10
                    )
            
            # Load dataset for additional info lookup
            if os.path.exists(self.dataset_path) and self.df is None:
                self.df = pd.read_csv(self.dataset_path)
            
            self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            print(f"Model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def predict(self, symptoms_text: str) -> Dict:
        """
        Predict poison from symptoms text
        Returns prediction with confidence and additional info
        """
        if not self.model_loaded:
            if not self.load_model():
                return {
                    "error": "Model not loaded",
                    "predictions": []
                }
        
        try:
            # Tokenize input
            tokens = self.tokenizer(
                symptoms_text, 
                padding='max_length', 
                truncation=True, 
                max_length=64, 
                return_tensors='pt'
            )
            tokens = {k: v.to(self.device) for k, v in tokens.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**tokens)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
                
                # Get top predictions
                top_probs, top_indices = torch.topk(probabilities, min(5, probabilities.shape[1]))
                top_probs = top_probs.cpu().numpy()[0]
                top_indices = top_indices.cpu().numpy()[0]
            
            # Decode predictions
            predictions = []
            for prob, idx in zip(top_probs, top_indices):
                if self.label_encoder:
                    poison_name = self.label_encoder.inverse_transform([idx])[0]
                else:
                    poison_name = f"Poison_{idx}"
                
                pred = {
                    "poison_name": poison_name,
                    "confidence": float(prob),
                    "additional_info": self._get_poison_info(poison_name)
                }
                predictions.append(pred)
            
            return {
                "success": True,
                "predictions": predictions,
                "primary_prediction": predictions[0] if predictions else None,
                "model_version": "DistilBERT-v1.0",
                "device": self.device
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }
    
    def _get_poison_info(self, poison_name: str) -> Optional[Dict]:
        """Get additional info about poison from dataset"""
        if self.df is None:
            return None
        
        try:
            rows = self.df[self.df['poison_name'] == poison_name]
            if len(rows) > 0:
                row = rows.iloc[0]
                return {
                    "category": row.get('poison_category', 'Unknown'),
                    "antidote": row.get('antidote', 'Consult medical professional'),
                    "management_protocol": row.get('management_protocol', 'Seek immediate medical attention')
                }
        except Exception:
            pass
        return None
    
    def save_model(self):
        """Save trained model and encoder"""
        if self.model and self.tokenizer:
            os.makedirs(self.model_path, exist_ok=True)
            self.model.save_pretrained(self.model_path)
            self.tokenizer.save_pretrained(self.model_path)
            
            if self.label_encoder:
                with open(self.encoder_path, 'wb') as f:
                    pickle.dump(self.label_encoder, f)
            
            print(f"Model saved to {self.model_path}")
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "loaded": self.model_loaded,
            "device": self.device,
            "model_type": "DistilBERT for Sequence Classification",
            "num_labels": len(self.label_encoder.classes_) if self.label_encoder else None,
            "dataset_loaded": self.df is not None,
            "dataset_size": len(self.df) if self.df is not None else 0
        }


# Singleton instance
ml_service = PoisonMLService()
