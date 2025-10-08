from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
import os
import logging
import warnings

logger = logging.getLogger(__name__)


class WhosePIIGuardian:
    """
    Detects and masks PII in text using a hybrid approach.
    
    Supports both cloud-based inference (default) and local inference (fallback).
    Model: whose-pii-guardian-v2
    """
    
    def __init__(
        self, 
        user_api_key: Optional[str] = None,
        local_mode: bool = False,
        local_fallback: bool = True,
        config_path: Optional[str] = None
    ):
        """
        Initialize the PII Guardian.
        
        Args:
            user_api_key: User's JWT API key for authentication and usage tracking
            local_mode: Force local inference (requires heavy dependencies)
            local_fallback: Fall back to local models if cloud fails
            config_path: Path to configuration file
        """
        self._model_version = "whose-pii-guardian-v2"
        self.user_api_key = user_api_key
        self.local_mode = local_mode
        self.local_fallback = local_fallback
        
        # Hardcoded RunPod credentials for AnotiAI service
        self.runpod_api_key = "rpa_YDFRCFG9R883HO8IKLBIWGRZKV3P4D8B5301WFAM17ivxs"
        self.endpoint_id = "r2ol4vgslj001p"
        
        # Initialize cloud client
        self.api_client = None
        if not local_mode:
            try:
                from .client import RunPodAPIClient, ClientConfig
                
                if config_path:
                    config = ClientConfig.from_file(config_path)
                else:
                    config = ClientConfig.from_env()
                
                # Use hardcoded credentials
                config.runpod_api_key = self.runpod_api_key
                config.endpoint_id = self.endpoint_id
                config.local_fallback = local_fallback
                
                if config.is_valid():
                    self.api_client = RunPodAPIClient(config)
                    logger.info("PII Guardian initialized with cloud inference")
                else:
                    if not local_fallback:
                        raise ValueError(
                            "Cloud inference requires a valid user API key. "
                            "Provide user_api_key or enable local_fallback=True"
                        )
                    logger.warning("Cloud credentials not available, using local mode")
                    self.local_mode = True
                    
            except ImportError as e:
                logger.warning(f"Cloud dependencies not available: {e}")
                if not local_fallback:
                    raise ImportError(
                        "Cloud inference dependencies not available. "
                        "Install with: pip install anotiai-pii-masker[cloud]"
                    )
                self.local_mode = True
        
        # Initialize local models if needed
        if self.local_mode or (local_fallback and self.api_client is None):
            self._init_local_models()
        
        logger.info(f"PII Guardian initialized with model: {self._model_version}")
    
    def _init_local_models(self):
        """Initialize local models (heavy dependencies required)."""
        try:
            from .Classification import config
            from .Classification.inference import PiiContextClassifier
            from .Classification.inference_baseline import BaselineClassifier
            from .extraction_engine.presidio_pii import PresidioPiiDetector
            from .extraction_engine.spacy_pii import SpacyPiiDetector
            from .extraction_engine.qa_pii import QaPiiDetector
            
            # Get the directory where this package is located
            package_dir = os.path.dirname(os.path.abspath(__file__))
            models_dir = os.path.join(package_dir, "MODELS")
            
            if not os.path.exists(models_dir):
                raise FileNotFoundError(
                    f"Local models not found at {models_dir}. "
                    "For local inference, install the full package with models."
                )
            
            self.presidio_detector = PresidioPiiDetector()
            self.spacy_detector = SpacyPiiDetector()
            self.qa_detector = QaPiiDetector(model_name="deepset/deberta-v3-large-squad2")
            self.qa_detector2 = QaPiiDetector(model_name="deepset/xlm-roberta-large-squad2")
            self.roberta_classifier = PiiContextClassifier(model_path=os.path.join(models_dir, "roberta_large"))
            self.debarta_classifier = PiiContextClassifier(model_path=os.path.join(models_dir, "debarta_large"))
            self.baseline_classifier = BaselineClassifier(model_path=os.path.join(models_dir, "baseline_model"))
            self.tracker = defaultdict(int)
            self.config = config

            self._supported_entities = set(self.presidio_detector.get_supported_entities()) | set(self.spacy_detector.get_supported_entities())
            logger.info("Local models initialized successfully")
            
        except ImportError as e:
            if self.local_mode:
                raise ImportError(
                    f"Local inference dependencies not available: {e}. "
                    "Install with: pip install anotiai-pii-masker[local]"
                )
            logger.warning(f"Local models not available for fallback: {e}")
            self.local_fallback = False
    
    def _use_cloud_inference(self) -> bool:
        """Determine whether to use cloud inference."""
        return not self.local_mode and self.api_client is not None
    
    def mask_text(self, text: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Mask PII in the provided text.
        
        Args:
            text: The text to process
            confidence_threshold: Minimum confidence threshold for PII detection
            
        Returns:
            Dictionary containing masked_text, pii_map, and usage data
        """
        if self._use_cloud_inference():
            if not self.user_api_key:
                raise ValueError("User API key is required for cloud inference")
            try:
                return self.api_client.mask_text(text, self.user_api_key, confidence_threshold)
            except Exception as e:
                logger.warning(f"Cloud inference failed: {e}")
                if self.local_fallback:
                    logger.info("Falling back to local inference")
                    return self._mask_text_local(text, confidence_threshold)
                else:
                    raise
        else:
            return self._mask_text_local(text, confidence_threshold)
    
    def unmask_text(self, masked_text: str, pii_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore the original text from a masked version and a PII map.
        
        Args:
            masked_text: The masked text
            pii_map: The PII mapping dictionary
            
        Returns:
            Dictionary containing unmasked_text and usage data
        """
        if self._use_cloud_inference():
            if not self.user_api_key:
                raise ValueError("User API key is required for cloud inference")
            try:
                return self.api_client.unmask_text(masked_text, pii_map, self.user_api_key)
            except Exception as e:
                logger.warning(f"Cloud inference failed: {e}")
                if self.local_fallback:
                    logger.info("Falling back to local inference")
                    return self._unmask_text_local(masked_text, pii_map)
                else:
                    raise
        else:
            return self._unmask_text_local(masked_text, pii_map)
    
    def detect_pii(self, text: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Detect PII entities without masking.
        
        Args:
            text: The text to analyze
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            Dictionary with detection results and usage data
        """
        if self._use_cloud_inference():
            if not self.user_api_key:
                raise ValueError("User API key is required for cloud inference")
            try:
                return self.api_client.detect_pii(text, self.user_api_key, confidence_threshold)
            except Exception as e:
                logger.warning(f"Cloud inference failed: {e}")
                if self.local_fallback:
                    logger.info("Falling back to local inference")
                    pii_entities = self._detect_local(text)
                    return {
                        "entities_found": len(pii_entities['pii_results']),
                        "pii_results": pii_entities['pii_results'],
                        "classification": pii_entities['classification'],
                        "confidence": pii_entities['confidence'],
                        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
                    }
                else:
                    raise
        else:
            pii_entities = self._detect_local(text)
            return {
                "entities_found": len(pii_entities['pii_results']),
                "pii_results": pii_entities['pii_results'],
                "classification": pii_entities['classification'],
                "confidence": pii_entities['confidence'],
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            }
    
    def get_model_version(self) -> str:
        """
        Return the version of the loaded PII detection model.
        """
        if self._use_cloud_inference():
            if not self.user_api_key:
                raise ValueError("User API key is required for cloud inference")
            try:
                result = self.api_client.get_model_version(self.user_api_key)
                return result.get("model_version", self._model_version)
            except Exception as e:
                logger.warning(f"Failed to get cloud model version: {e}")
        
        return self._model_version
    
    def get_supported_entities(self) -> List[str]:
        """
        Return a list of PII entity types supported by the detector.
        """
        if hasattr(self, '_supported_entities'):
            return list(self._supported_entities)
        else:
            # Default supported entities for cloud mode
            return [
                "email", "phone", "person", "credit_card", "ssn", 
                "passport", "license", "address", "url", "ip_address"
            ]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the service.
        """
        if self._use_cloud_inference():
            try:
                return self.api_client.health_check()
            except Exception as e:
                return {
                    "status": "unhealthy", 
                    "error": str(e),
                    "service": "anotiai-pii-guardian"
                }
        else:
            return {
                "status": "healthy",
                "mode": "local",
                "service": "anotiai-pii-guardian"
            }
    
    def _mask_text_local(self, text: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Local implementation of text masking."""
        if not hasattr(self, 'presidio_detector'):
            raise RuntimeError("Local models not initialized")
        
        logger.info(f"Starting text masking for text of length: {len(text)}")
        pii_entities = self._detect_local(text)
        masked_text = text
        pii_map = {}

        entities = pii_entities['pii_results']

        if not entities:
            logger.info("No PII entities found - returning original text")
            from .utils import count_tokens
            return {
                "masked_text": text,
                "pii_map": {},
                "entities_found": 0,
                "confidence_threshold": confidence_threshold,
                "usage": {
                    "input_tokens": count_tokens(text),
                    "output_tokens": count_tokens(text),
                    "total_tokens": count_tokens(text) * 2
                }
            }
        
        logger.info(f"Masking {len(entities)} PII entities")
        sorted_pii = sorted(entities, key=lambda x: x['start'], reverse=True)
        for i, entity in enumerate(sorted_pii):
            if entity['confidence'] < confidence_threshold:
                pii_map[f"__TOKEN_{i+1}__"] = {
                    'value': entity['value'],
                    'label': entity['type'],
                    'confidence': entity['confidence'],
                    'placeholder': entity['value'],
                }
                continue
            self.tracker[entity['type']] += 1
            placeholder = f"[REDACTED_{entity['type'].upper()}_{self.tracker[entity['type']]}]"
            masked_text = masked_text[:entity['start']] + placeholder + masked_text[entity['end']:]
        
            pii_map[f"__TOKEN_{i+1}__"] = {
                'value': entity['value'],
                'label': entity['type'],
                'confidence': entity['confidence'],
                'placeholder': placeholder,
            }
            logger.debug(f"Masked entity {i+1}: {entity['type']} -> {placeholder}")
            
        logger.info(f"Text masking completed. Created {len(pii_map)} masked entities")
        
        from .utils import count_tokens
        return {
            "masked_text": masked_text,
            "pii_map": pii_map,
            "entities_found": len(pii_map),
            "confidence_threshold": confidence_threshold,
            "usage": {
                "input_tokens": count_tokens(text),
                "output_tokens": count_tokens(masked_text) + count_tokens(pii_map),
                "total_tokens": count_tokens(text) + count_tokens(masked_text) + count_tokens(pii_map)
            }
        }
    
    def _unmask_text_local(self, masked_text: str, pii_map: Dict[str, Any]) -> Dict[str, Any]:
        """Local implementation of text unmasking."""
        unmasked_text = masked_text
        for key, value in pii_map.items():
            # Handle both dict and PIIEntity object formats
            if hasattr(value, 'placeholder') and hasattr(value, 'value'):
                # PIIEntity object (from FastAPI)
                placeholder = value.placeholder
                original_value = value.value
            else:
                # Dictionary format
                placeholder = value['placeholder']
                original_value = value['value']
            
            unmasked_text = unmasked_text.replace(placeholder, original_value)
        
        from .utils import count_tokens
        return {
            "unmasked_text": unmasked_text,
            "entities_restored": len(pii_map),
            "usage": {
                "input_tokens": count_tokens(masked_text) + count_tokens(pii_map),
                "output_tokens": count_tokens(unmasked_text),
                "total_tokens": count_tokens(masked_text) + count_tokens(pii_map) + count_tokens(unmasked_text)
            }
        }
    
    def _detect_local(self, text: str) -> Dict[str, Any]:
        """Local implementation of PII detection."""
        if not hasattr(self, 'roberta_classifier'):
            raise RuntimeError("Local models not initialized")
            
        rb_results = self.roberta_classifier.predict_single(text)
        db_results = self.debarta_classifier.predict_single(text)
        bl_results = self.baseline_classifier.predict_single(text)

        classification, confidence, method = self._aggregate_predictions(rb_results, db_results, bl_results)
        classification = self.config.ID_TO_LABEL[classification]

        if not classification:
            return {
                "classification": "ERROR",
                "confidence": 0.0,
                "pii_results": []
            }

        logger.info(f"Result: Text classified as '{classification}' with {confidence:.2f} confidence.")

        if classification != "pii_disclosure":
            logger.info("Skipping PII extraction - text not classified as PII disclosure")
            return {
                "classification": classification,
                "confidence": confidence,
                "pii_results": []
            }

        logger.info("Proceeding to PII extraction - text classified as PII disclosure")
        all_pii = []
        
        # Run all detectors
        presidio_results = self.presidio_detector.detect(text)
        spacy_results = self.spacy_detector.detect(text)
        qa_results = self.qa_detector.detect(text, confidence_threshold=0.5/1000)
        qa_results2 = self.qa_detector2.detect(text, confidence_threshold=0.5/1000)
        
        all_pii.extend(presidio_results)
        all_pii.extend(spacy_results)
        all_pii.extend(qa_results)
        all_pii.extend(qa_results2)
        
        logger.info(f"Raw detection results - Presidio: {len(presidio_results)}, spaCy: {len(spacy_results)}, QA1: {len(qa_results)}, QA2: {len(qa_results2)}")

        # Consolidate and Deduplicate Results
        final_pii = self._consolidate_and_deduplicate(all_pii)
        logger.info(f"Found {len(final_pii)} unique PII entities after deduplication")
        
        # Log entity types found
        entity_types = [entity.get('type', 'unknown') for entity in final_pii]
        logger.info(f"Entity types found: {dict(Counter(entity_types))}")

        return {
            "classification": classification,
            "confidence": confidence,
            "pii_results": final_pii
        }
    
    def _aggregate_predictions(self, rb_results, db_results, bl_results):
        """Aggregate predictions from multiple models."""
        predictions = [
            rb_results['predicted_class_id'],
            db_results['predicted_class_id'], 
            bl_results['predicted_class_id']
        ]
        confidences = [
            rb_results['confidence'],
            db_results['confidence'],
            bl_results['confidence']
        ]
        
        # Count votes
        vote_counts = Counter(predictions)
        max_votes = max(vote_counts.values())
        
        # If there's a clear majority, return it with average confidence of winning votes
        if max_votes > 1:
            winning_class = max(vote_counts, key=vote_counts.get)
            # Calculate average confidence of the winning votes
            winning_confidences = [conf for pred, conf in zip(predictions, confidences) if pred == winning_class]
            aggregate_confidence = sum(winning_confidences) / len(winning_confidences)
            return winning_class, aggregate_confidence, "majority_vote"
        
        # Otherwise, use confidence-weighted voting for ties
        confidence_scores = {0: 0, 1: 0, 2: 0}
        for pred, conf in zip(predictions, confidences):
            confidence_scores[pred] += conf
        
        winning_class = max(confidence_scores, key=confidence_scores.get)
        # For confidence-weighted voting, use the confidence of the winning model
        winning_confidence = max(confidences)
        return winning_class, winning_confidence, "confidence_weighted"

    def _consolidate_and_deduplicate(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove overlapping entities from multiple detector sources, keeping the one
        with the highest confidence score.
        """
        if not entities:
            return []

        # Sort by confidence score in descending order to prioritize high-confidence entities
        entities.sort(key=lambda x: x.get('confidence', 0.0), reverse=True)

        unique_entities = []
        seen_ranges = set()

        for entity in entities:
            start, end = entity['start'], entity['end']
            # Check if the range of this entity overlaps with an already added entity
            if not any(start < seen_end and end > seen_start for seen_start, seen_end in seen_ranges):
                unique_entities.append(entity)
                seen_ranges.add((start, end))
        
        # Sort by start position for readability
        unique_entities.sort(key=lambda x: x['start'])
        return unique_entities