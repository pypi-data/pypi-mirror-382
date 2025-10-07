"""
Advanced Similarity Metrics Module for HalluNox

This module implements multiple similarity metrics and averaging approaches
for improved confidence estimation using BAAI embeddings.
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Union, Tuple


class MultiSimilarityCalculator:
    """
    Calculate multiple similarity metrics and combine them for robust confidence estimation.
    
    Supports:
    - Cosine similarity
    - Dot product similarity
    - Manhattan (L1) distance-based similarity
    - Euclidean (L2) distance-based similarity
    - Weighted averaging of multiple metrics
    """
    
    def __init__(self, 
                 weights: Dict[str, float] = None,
                 normalize_before_metrics: bool = True,
                 use_temperature_scaling: bool = True,
                 temperature: float = 1.0):
        """
        Initialize the multi-similarity calculator.
        
        Args:
            weights: Dictionary mapping metric names to weights for averaging
            normalize_before_metrics: Whether to normalize embeddings before calculating metrics
            use_temperature_scaling: Whether to apply temperature scaling to similarities
            temperature: Temperature parameter for scaling
        """
        # Default weights - cosine gets highest weight as it's most robust
        self.weights = weights or {
            'cosine': 0.4,
            'dot_product': 0.3,
            'manhattan': 0.15,
            'euclidean': 0.15
        }
        
        # Normalize weights to sum to 1
        total_weight = sum(self.weights.values())
        self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
        self.normalize_before_metrics = normalize_before_metrics
        self.use_temperature_scaling = use_temperature_scaling
        self.temperature = temperature
        
    def cosine_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Calculate cosine similarity between two embedding tensors."""
        if self.normalize_before_metrics:
            x1_norm = F.normalize(x1, p=2, dim=1, eps=1e-8)
            x2_norm = F.normalize(x2, p=2, dim=1, eps=1e-8)
        else:
            x1_norm, x2_norm = x1, x2
        
        return F.cosine_similarity(x1_norm, x2_norm, dim=1, eps=1e-8)
    
    def dot_product_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Calculate normalized dot product similarity."""
        # Normalize to unit vectors first if requested
        if self.normalize_before_metrics:
            x1_norm = F.normalize(x1, p=2, dim=1, eps=1e-8)
            x2_norm = F.normalize(x2, p=2, dim=1, eps=1e-8)
        else:
            x1_norm, x2_norm = x1, x2
        
        # Calculate dot product
        dot_product = torch.sum(x1_norm * x2_norm, dim=1)
        
        # Apply sigmoid to map to [0, 1] range
        return torch.sigmoid(dot_product)
    
    def manhattan_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Calculate similarity based on Manhattan (L1) distance."""
        # Calculate L1 distance with numerical stability
        l1_distance = torch.sum(torch.abs(x1 - x2), dim=1)
        
        # Clamp distance to prevent extreme values
        l1_distance = torch.clamp(l1_distance, min=1e-8, max=1e4)
        
        # Convert distance to similarity using more stable formula
        # Use max distance for normalization instead of std for stability
        max_distance = torch.max(l1_distance) + 1e-8
        normalized_distance = l1_distance / max_distance
        
        # Use stable similarity: 1 / (1 + distance)
        similarity = 1.0 / (1.0 + normalized_distance)
        
        # Ensure output is in valid range
        similarity = torch.clamp(similarity, min=1e-8, max=1.0)
        
        return similarity
    
    def euclidean_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Calculate similarity based on Euclidean (L2) distance."""
        # Calculate L2 distance with numerical stability
        squared_diff = (x1 - x2) ** 2
        l2_distance = torch.sqrt(torch.sum(squared_diff, dim=1) + 1e-8)
        
        # Clamp distance to prevent extreme values
        l2_distance = torch.clamp(l2_distance, min=1e-8, max=1e4)
        
        # Convert distance to similarity using more stable formula
        # Use max distance for normalization instead of std for stability
        max_distance = torch.max(l2_distance) + 1e-8
        normalized_distance = l2_distance / max_distance
        
        # Use stable similarity: 1 / (1 + distance)
        similarity = 1.0 / (1.0 + normalized_distance)
        
        # Ensure output is in valid range
        similarity = torch.clamp(similarity, min=1e-8, max=1.0)
        
        return similarity
    
    def calculate_all_similarities(self, x1: torch.Tensor, x2: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Calculate all similarity metrics between two embedding tensors.
        
        Args:
            x1: First embedding tensor [batch_size, embedding_dim]
            x2: Second embedding tensor [batch_size, embedding_dim]
            
        Returns:
            Dictionary mapping metric names to similarity tensors
        """
        similarities = {}
        
        # Ensure tensors are on the same device and dtype
        x1 = x1.float()
        x2 = x2.float()
        
        # Check for NaN/Inf and replace with fallback
        if torch.isnan(x1).any() or torch.isinf(x1).any():
            print("⚠️ Warning: NaN/Inf in x1, using fallback")
            x1 = torch.randn_like(x1) * 0.01
        
        if torch.isnan(x2).any() or torch.isinf(x2).any():
            print("⚠️ Warning: NaN/Inf in x2, using fallback")
            x2 = torch.randn_like(x2) * 0.01
        
        # Calculate each similarity metric
        similarities['cosine'] = self.cosine_similarity(x1, x2)
        similarities['dot_product'] = self.dot_product_similarity(x1, x2)
        similarities['manhattan'] = self.manhattan_similarity(x1, x2)
        similarities['euclidean'] = self.euclidean_similarity(x1, x2)
        
        # Apply temperature scaling if enabled
        if self.use_temperature_scaling:
            for key in similarities:
                similarities[key] = similarities[key] / self.temperature
        
        # Check for NaN in results and replace with default values
        for key, sim in similarities.items():
            if torch.isnan(sim).any():
                print(f"⚠️ Warning: NaN in {key} similarity, using default")
                similarities[key] = torch.full_like(sim, 0.1)  # Low confidence default
        
        return similarities
    
    def weighted_average(self, similarities: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Calculate weighted average of multiple similarity metrics.
        
        Args:
            similarities: Dictionary mapping metric names to similarity tensors
            
        Returns:
            Weighted average similarity tensor
        """
        weighted_sum = torch.zeros_like(list(similarities.values())[0])
        
        for metric_name, similarity in similarities.items():
            weight = self.weights.get(metric_name, 0.0)
            weighted_sum += weight * similarity
        
        return weighted_sum
    
    def calculate_combined_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Calculate combined similarity using multiple metrics and weighted averaging.
        
        Args:
            x1: First embedding tensor [batch_size, embedding_dim]
            x2: Second embedding tensor [batch_size, embedding_dim]
            
        Returns:
            Tuple of (combined_similarity, individual_similarities)
        """
        # Calculate all individual similarities
        similarities = self.calculate_all_similarities(x1, x2)
        
        # Calculate weighted average
        combined = self.weighted_average(similarities)
        
        # Clamp to reasonable range
        combined = torch.clamp(combined, min=0.0, max=1.0)
        
        return combined, similarities


class EnhancedEmbeddingProcessor:
    """
    Enhanced embedding processor that combines query and context using BAAI embeddings
    with multiple similarity metrics.
    """
    
    def __init__(self, 
                 embed_model,
                 multi_sim_calculator: MultiSimilarityCalculator = None,
                 max_length: int = 512,
                 use_query_context_fusion: bool = True):
        """
        Initialize the enhanced embedding processor.
        
        Args:
            embed_model: The BAAI embedding model (BGE-M3)
            multi_sim_calculator: Calculator for multiple similarity metrics
            max_length: Maximum sequence length for embeddings
            use_query_context_fusion: Whether to use advanced query-context fusion
        """
        self.embed_model = embed_model
        self.multi_sim_calculator = multi_sim_calculator or MultiSimilarityCalculator()
        self.max_length = max_length
        self.use_query_context_fusion = use_query_context_fusion
    
    def format_query_context_for_embedding(self, 
                                         query: str, 
                                         context: str, 
                                         fusion_strategy: str = "structured") -> str:
        """
        Format query and context for optimal BAAI embedding.
        
        Args:
            query: The query text
            context: The context text
            fusion_strategy: Strategy for combining query and context
                           ("structured", "concatenated", "marked")
            
        Returns:
            Formatted text for embedding
        """
        if fusion_strategy == "structured":
            # Structured format with clear sections
            return f"Query: {query}\nContext: {context}\nRelevance: How well does the context support answering the query?"
        
        elif fusion_strategy == "concatenated":
            # Simple concatenation
            return f"{query} {context}"
        
        elif fusion_strategy == "marked":
            # Marked sections with special tokens
            return f"[QUERY] {query} [CONTEXT] {context} [ASSESSMENT]"
        
        else:
            return f"{query} {context}"
    
    def detect_contradictions(self, query: str, context: str) -> Tuple[bool, float]:
        """
        Detect potential contradictions between query and context using semantic analysis.
        
        Args:
            query: The query text
            context: The context text
            
        Returns:
            Tuple of (has_contradiction, contradiction_strength)
        """
        # Use multi-signal semantic approach for better contradiction detection
        
        try:
            # 1. Direct negation detection - check if context is similar to negation patterns
            negation_patterns = [
                "This does not exist and is not real",
                "This is false information",
                "This never existed", 
                "This is made up",
                "This is fictional"
            ]
            
            # Embed context and negation patterns
            texts_to_embed = [context.strip()] + negation_patterns
            embeddings = self.embed_model.encode(
                texts_to_embed,
                batch_size=len(texts_to_embed),
                max_length=self.max_length,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False,
            )
            
            context_emb = torch.tensor(embeddings['dense_vecs'][0], dtype=torch.float32)
            negation_embs = [torch.tensor(embeddings['dense_vecs'][i+1], dtype=torch.float32) 
                           for i in range(len(negation_patterns))]
            
            # Calculate maximum similarity to negation patterns
            max_negation_similarity = 0.0
            best_negation_pattern = ""
            
            for i, neg_emb in enumerate(negation_embs):
                neg_sim = torch.cosine_similarity(
                    context_emb.unsqueeze(0), neg_emb.unsqueeze(0), dim=1
                ).item()
                if neg_sim > max_negation_similarity:
                    max_negation_similarity = neg_sim
                    best_negation_pattern = negation_patterns[i]
            
            # 2. Query-context semantic contradiction check
            query_assumption = f"The concept mentioned in this query exists and is real: {query}"
            assumption_emb = torch.tensor(
                self.embed_model.encode([query_assumption], return_dense=True)['dense_vecs'][0],
                dtype=torch.float32
            )
            
            assumption_context_similarity = torch.cosine_similarity(
                assumption_emb.unsqueeze(0), context_emb.unsqueeze(0), dim=1
            ).item()
            
            # Debug logging
            print(f"🔍 Enhanced Contradiction Analysis:")
            print(f"   Context: {context.strip()}")
            print(f"   Max negation similarity: {max_negation_similarity:.4f} (pattern: {best_negation_pattern})")
            print(f"   Query-context similarity: {assumption_context_similarity:.4f}")
            
            # 3. Context relevance check - does context actually address the query?
            context_query_relevance = torch.cosine_similarity(
                context_emb.unsqueeze(0), 
                torch.tensor(self.embed_model.encode([query], return_dense=True)['dense_vecs'][0], dtype=torch.float32).unsqueeze(0), 
                dim=1
            ).item()
            
            print(f"   Context-query relevance: {context_query_relevance:.4f}")
            
            # Enhanced contradiction detection with false positive prevention
            negation_threshold = 0.50  # Higher threshold to avoid false positives
            semantic_threshold = 0.20   # Keep lower for actual contradictions
            relevance_threshold = 0.40  # If context is relevant to query, be more careful
            
            # Signal 1: High similarity to negation patterns
            strong_negation = max_negation_similarity > negation_threshold
            
            # Signal 2: Low semantic similarity between query assumption and context
            semantic_contradiction = assumption_context_similarity < semantic_threshold
            
            # Signal 3: Context is relevant to query (reduces false positive risk)
            context_is_relevant = context_query_relevance > relevance_threshold
            
            # Contradiction logic with false positive prevention
            if strong_negation and not context_is_relevant:
                # Strong negation and context is not relevant to query
                has_contradiction = True
                contradiction_strength = min(max_negation_similarity * 1.5, 1.0)
                print(f"   ✅ Strong negation-based contradiction detected (strength: {contradiction_strength:.4f})")
            
            elif strong_negation and context_is_relevant:
                # Negation detected but context seems relevant - likely contradiction about existence
                has_contradiction = True
                contradiction_strength = min(max_negation_similarity * 1.2, 0.9)
                print(f"   ✅ Existence contradiction detected (relevant but negating) (strength: {contradiction_strength:.4f})")
            
            elif max_negation_similarity > 0.42 and context_is_relevant:
                # CRITICAL: Context is relevant to query BUT has significant negation similarity
                # This catches cases like "X is not a recognized disease" when asking about X
                has_contradiction = True
                contradiction_strength = min(max_negation_similarity * 1.3, 0.85)
                print(f"   ✅ Relevant contradiction detected (negating while relevant) (strength: {contradiction_strength:.4f})")
            
            elif semantic_contradiction and not context_is_relevant:
                # Low semantic similarity and context not relevant
                has_contradiction = True
                contradiction_strength = min((semantic_threshold - assumption_context_similarity) / semantic_threshold * 0.7, 0.7)
                print(f"   ⚠️ Semantic contradiction detected (strength: {contradiction_strength:.4f})")
            
            elif max_negation_similarity > 0.40 and assumption_context_similarity < 0.15:
                # Moderate negation + very low semantic similarity
                has_contradiction = True
                contradiction_strength = max_negation_similarity * 0.5
                print(f"   ⚠️ Moderate contradiction detected (strength: {contradiction_strength:.4f})")
            
            else:
                has_contradiction = False
                contradiction_strength = 0.0
                print(f"   ✅ No contradiction detected (context appears supportive or neutral)")
                
        except Exception as e:
            print(f"⚠️ Error in semantic contradiction detection: {e}")
            # Fallback to simple text analysis
            context_lower = context.lower()
            simple_negations = ['not', 'no', 'false', 'wrong', 'fake']
            negation_count = sum(1 for neg in simple_negations if neg in context_lower)
            
            has_contradiction = negation_count > 0
            contradiction_strength = min(negation_count / len(simple_negations), 0.8)
        
        return has_contradiction, contradiction_strength
    
    def create_enhanced_embeddings(self, 
                                 texts: List[str],
                                 query_context_pairs: List[Dict] = None) -> Tuple[torch.Tensor, Dict]:
        """
        Create enhanced embeddings using BAAI with query-context fusion.
        
        Args:
            texts: List of texts to embed
            query_context_pairs: Optional list of query-context pairs
            
        Returns:
            Tuple of (embeddings_tensor, metadata_dict)
        """
        embedding_texts = []
        metadata = {
            'has_context': [],
            'contradictions': [],
            'fusion_strategies': []
        }
        
        for i, text in enumerate(texts):
            if query_context_pairs and i < len(query_context_pairs) and query_context_pairs[i]:
                pair = query_context_pairs[i]
                query = pair.get('query', text)
                context = pair.get('context', '')
                
                if context and self.use_query_context_fusion:
                    # Detect contradictions
                    has_contradiction, contradiction_strength = self.detect_contradictions(query, context)
                    
                    # Choose fusion strategy based on contradiction
                    if has_contradiction:
                        fusion_strategy = "structured"  # More explicit for contradictions
                        formatted_text = f"Question: {query}\nClaim: {context}\nEvaluation: Does the claim contradict known facts about the question?"
                    else:
                        fusion_strategy = "structured"
                        formatted_text = self.format_query_context_for_embedding(query, context, fusion_strategy)
                    
                    metadata['has_context'].append(True)
                    metadata['contradictions'].append({
                        'detected': has_contradiction,
                        'strength': contradiction_strength
                    })
                    metadata['fusion_strategies'].append(fusion_strategy)
                    
                    embedding_texts.append(formatted_text)
                else:
                    metadata['has_context'].append(False)
                    metadata['contradictions'].append({'detected': False, 'strength': 0.0})
                    metadata['fusion_strategies'].append('none')
                    embedding_texts.append(text)
            else:
                metadata['has_context'].append(False)
                metadata['contradictions'].append({'detected': False, 'strength': 0.0})
                metadata['fusion_strategies'].append('none')
                embedding_texts.append(text)
        
        # Generate embeddings using BAAI model
        try:
            bge_outputs = self.embed_model.encode(
                embedding_texts,
                batch_size=len(embedding_texts),
                max_length=self.max_length,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False,
            )
            
            embeddings = torch.tensor(
                bge_outputs['dense_vecs'], 
                dtype=torch.float32
            )
            
            # Check for NaN/Inf and replace with fallback
            if torch.isnan(embeddings).any() or torch.isinf(embeddings).any():
                print("⚠️ Warning: NaN/Inf in BAAI embeddings, using fallback")
                embeddings = torch.randn_like(embeddings) * 0.01
            
        except Exception as e:
            print(f"⚠️ Error in BAAI embedding generation: {e}")
            # Fallback embeddings
            embeddings = torch.randn(len(embedding_texts), 1024) * 0.01
        
        return embeddings, metadata
    
    def calculate_enhanced_similarity(self, 
                                    projected_embeddings: torch.Tensor,
                                    reference_embeddings: torch.Tensor,
                                    metadata: Dict) -> Tuple[torch.Tensor, Dict]:
        """
        Calculate enhanced similarity using multiple metrics and context awareness.
        
        Args:
            projected_embeddings: Projected LLM embeddings
            reference_embeddings: BAAI reference embeddings
            metadata: Metadata from embedding creation
            
        Returns:
            Tuple of (final_similarities, detailed_results)
        """
        # Calculate multiple similarities
        combined_similarity, individual_similarities = self.multi_sim_calculator.calculate_combined_similarity(
            projected_embeddings, reference_embeddings
        )
        
        # Apply context-aware adjustments
        final_similarities = combined_similarity.clone()
        
        for i, (has_context, contradiction_info) in enumerate(
            zip(metadata['has_context'], metadata['contradictions'])
        ):
            if contradiction_info['detected']:
                # Apply strong contradiction penalty - semantic contradiction should heavily reduce confidence
                base_penalty = 0.7  # Base 70% reduction
                strength_multiplier = contradiction_info['strength']
                total_penalty = base_penalty + (0.2 * strength_multiplier)  # Up to 90% penalty
                
                original_similarity = final_similarities[i].item()
                
                # Apply penalty by multiplying similarity
                final_similarities[i] = final_similarities[i] * (1 - total_penalty)
                
                # Ensure minimum low confidence for contradictions
                final_similarities[i] = torch.clamp(final_similarities[i], max=0.3)
                
                print(f"🔧 Applying contradiction penalty:")
                print(f"   Original similarity: {original_similarity:.4f}")
                print(f"   Contradiction strength: {strength_multiplier:.4f}")
                print(f"   Total penalty: {total_penalty:.4f}")
                print(f"   Final similarity: {final_similarities[i].item():.4f}")
            
            elif has_context:
                # Small boost for having supportive context
                boost = 0.05
                final_similarities[i] = torch.clamp(final_similarities[i] + boost, max=1.0)
        
        # Prepare detailed results
        detailed_results = {
            'individual_similarities': individual_similarities,
            'combined_similarity': combined_similarity,
            'context_adjusted_similarity': final_similarities,
            'metadata': metadata,
            'weights_used': self.multi_sim_calculator.weights
        }
        
        return final_similarities, detailed_results


def create_multi_similarity_detector_patch():
    """
    Create a patch function that can be applied to existing HallucinationDetector
    to use multiple similarity metrics.
    """
    def enhanced_predict(self, texts: Union[str, List[str]], query_context_pairs: List[Dict] = None) -> Dict:
        """
        Enhanced predict method using multiple similarity metrics.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Initialize enhanced embedding processor if not exists
        if not hasattr(self, 'enhanced_embedding_processor'):
            self.enhanced_embedding_processor = EnhancedEmbeddingProcessor(
                embed_model=self.embed_model,
                max_length=self.bge_max_length
            )
        
        # Check if LLM is loaded
        if not self.load_llm or self.llm is None:
            raise RuntimeError("LLM not loaded. Set load_llm=True for hallucination detection.")
        
        # Get LLM embeddings for projection (use query only for better comparison)
        projection_texts = texts
        if query_context_pairs:
            projection_texts = [
                pair.get('query', text) if i < len(query_context_pairs) and query_context_pairs[i] else text 
                for i, (text, pair) in enumerate(zip(texts, query_context_pairs + [None] * len(texts)))
            ]
        
        # Use the existing get_pooled_embeddings function
        from .detector import get_pooled_embeddings
        model_for_embeddings = getattr(self, 'llm_text', self.llm)
        llm_embeddings = get_pooled_embeddings(
            model_for_embeddings,
            self.tokenizer,
            projection_texts,
            self.device,
            self.max_length,
        ).to(self.device)
        
        # Create enhanced BAAI embeddings with query-context fusion
        ref_embeddings, metadata = self.enhanced_embedding_processor.create_enhanced_embeddings(
            texts, query_context_pairs
        )
        ref_embeddings = ref_embeddings.to(self.device)
        
        # Project LLM embeddings
        with torch.no_grad():
            llm_embeddings = llm_embeddings.float().to(self.device)
            projected = self.projector(llm_embeddings)
            
            # Calculate enhanced similarity using multiple metrics
            similarities, detailed_results = self.enhanced_embedding_processor.calculate_enhanced_similarity(
                projected, ref_embeddings, metadata
            )
            
            # Convert to confidence scores
            confidence_scores = torch.sigmoid(similarities)
        
        # Convert to numpy for result processing
        confidence_scores = confidence_scores.cpu().numpy()
        similarities_np = similarities.cpu().numpy()
        
        # Create results using existing interpretation logic
        results = []
        for i, (text, conf_score, sim_score) in enumerate(zip(texts, confidence_scores, similarities_np)):
            # Use existing threshold logic from original predict method
            if self.is_medgemma_4b:
                if conf_score >= 0.60:
                    interpretation = "HIGH_MEDICAL_CONFIDENCE"
                    risk_level = "LOW_MEDICAL_RISK"
                    routing_action = "LOCAL_GENERATION"
                    description = "This medical response appears to be factual and reliable."
                elif conf_score >= 0.55:
                    interpretation = "MEDIUM_MEDICAL_CONFIDENCE"
                    risk_level = "MEDIUM_MEDICAL_RISK"
                    routing_action = "RAG_RETRIEVAL"
                    description = "This medical response may contain uncertainties. Verify with authoritative sources."
                elif conf_score >= 0.50:
                    interpretation = "LOW_MEDICAL_CONFIDENCE"
                    risk_level = "HIGH_MEDICAL_RISK"
                    routing_action = "LARGER_MODEL"
                    description = "This medical response is likely unreliable. Professional verification required."
                else:
                    interpretation = "VERY_LOW_MEDICAL_CONFIDENCE"
                    risk_level = "VERY_HIGH_MEDICAL_RISK"
                    routing_action = "HUMAN_REVIEW"
                    description = "This medical response appears highly unreliable. Seek professional medical advice."
            else:
                if conf_score >= 0.65:
                    interpretation = "HIGH_CONFIDENCE"
                    risk_level = "LOW_RISK"
                    routing_action = "LOCAL_GENERATION"
                    description = "This response appears to be factual and reliable."
                elif conf_score >= 0.60:
                    interpretation = "MEDIUM_CONFIDENCE"
                    risk_level = "MEDIUM_RISK"
                    routing_action = "RAG_RETRIEVAL"
                    description = "This response may contain uncertainties. Consider retrieval augmentation."
                elif conf_score >= 0.4:
                    interpretation = "LOW_CONFIDENCE"
                    risk_level = "HIGH_RISK"
                    routing_action = "LARGER_MODEL"
                    description = "This response is likely unreliable. Route to larger model."
                else:
                    interpretation = "VERY_LOW_CONFIDENCE"
                    risk_level = "VERY_HIGH_RISK"
                    routing_action = "HUMAN_REVIEW"
                    description = "This response appears to be highly unreliable. Human review required."
            
            result = {
                "text": text,
                "confidence_score": float(conf_score),
                "similarity_score": float(sim_score),
                "interpretation": interpretation,
                "risk_level": risk_level,
                "routing_action": routing_action,
                "description": description,
            }
            
            # Add enhanced metrics info
            if hasattr(self, 'verbose') and self.verbose:
                individual_sims = {k: v[i].item() for k, v in detailed_results['individual_similarities'].items()}
                result["detailed_similarities"] = individual_sims
                result["context_metadata"] = metadata['contradictions'][i] if i < len(metadata['contradictions']) else {}
            
            results.append(result)
        
        return {
            "predictions": results,
            "summary": {
                "total_texts": len(texts),
                "avg_confidence": float(confidence_scores.mean()),
                "high_confidence_count": sum(1 for score in confidence_scores if score >= 0.65),
                "medium_confidence_count": sum(1 for score in confidence_scores if 0.60 <= score < 0.65),
                "low_confidence_count": sum(1 for score in confidence_scores if 0.4 <= score < 0.6),
                "very_low_confidence_count": sum(1 for score in confidence_scores if score < 0.4),
            }
        }
    
    return enhanced_predict