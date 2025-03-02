import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, data_path: str):
        """Initialize model trainer"""
        self.data_path = data_path
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_data(self) -> tuple:
        """Load and prepare the dataset"""
        try:
            # Load data
            df = pd.read_csv(self.data_path)
            
            # Define features
            categorical_features = ['gender', 'primary_diagnosis', 'discharge_to']
            numerical_features = ['age', 'num_procedures', 'days_in_hospital', 'comorbidity_score']
            
            # Handle categorical features
            X_encoded = df[numerical_features].copy()
            
            for cat_feature in categorical_features:
                # Create and fit label encoder
                le = LabelEncoder()
                X_encoded[cat_feature] = le.fit_transform(df[cat_feature])
                # Store the encoder
                self.label_encoders[cat_feature] = le
                
            # Prepare features and target
            X = X_encoded[numerical_features + categorical_features]
            y = df['readmitted']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Store feature names for later use
            self.feature_names = X.columns.tolist()
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def train(self):
        """Train the model"""
        try:
            # Load and split data
            X_train, X_test, y_train, y_test = self.load_data()
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            logger.info("Training model...")
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
            # Print metrics
            logger.info("\nClassification Report:")
            logger.info(classification_report(y_test, y_pred))
            
            logger.info(f"\nROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
            
            # Feature importance
            importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.info("\nFeature Importance:")
            logger.info(importance)
            
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def save_model(self, output_dir: str):
        """Save the trained model, scaler, and label encoders"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save model
            model_path = os.path.join(output_dir, f"readmission_model_{timestamp}.pkl")
            joblib.dump(self.model, model_path)
            logger.info(f"Model saved to {model_path}")
            
            # Save scaler
            scaler_path = os.path.join(output_dir, f"scaler_{timestamp}.pkl")
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Scaler saved to {scaler_path}")
            
            # Save label encoders
            encoders_path = os.path.join(output_dir, f"label_encoders_{timestamp}.pkl")
            joblib.dump(self.label_encoders, encoders_path)
            logger.info(f"Label encoders saved to {encoders_path}")
            
            # Create symlinks to latest versions
            latest_model_path = os.path.join(output_dir, "readmission_model.pkl")
            latest_scaler_path = os.path.join(output_dir, "scaler.pkl")
            latest_encoders_path = os.path.join(output_dir, "label_encoders.pkl")
            
            if os.path.exists(latest_model_path):
                os.remove(latest_model_path)
            if os.path.exists(latest_scaler_path):
                os.remove(latest_scaler_path)
            if os.path.exists(latest_encoders_path):
                os.remove(latest_encoders_path)
                
            os.symlink(model_path, latest_model_path)
            os.symlink(scaler_path, latest_scaler_path)
            os.symlink(encoders_path, latest_encoders_path)
            
            # Save feature names
            feature_names_path = os.path.join(output_dir, "feature_names.pkl")
            joblib.dump(self.feature_names, feature_names_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

def main():
    """Main function to train and save the model"""
    try:
        # Initialize trainer
        trainer = ModelTrainer("data/hospital_readmissions.csv")
        
        # Train model
        trainer.train()
        
        # Save model and associated objects
        trainer.save_model("app/ml_models")
        
        logger.info("Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 