import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import pickle
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FAISSService:
    """
    Service for FAISS vector search
    Handles embeddings and semantic similarity search
    """
    
    def __init__(self):
        # Initialize sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
        self.dimension = 384
        
        # Storage paths
        self.storage_dir = Path("data/faiss")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize indexes
        self.skill_index = None
        self.resource_index = None
        self.skill_metadata = []
        self.resource_metadata = []
        
        # Load existing indexes if available
        self._load_indexes()
    
    def _load_indexes(self):
        """Load existing FAISS indexes from disk"""
        try:
            # Load skill index
            skill_index_path = self.storage_dir / "skill_index.faiss"
            skill_meta_path = self.storage_dir / "skill_metadata.pkl"
            
            if skill_index_path.exists() and skill_meta_path.exists():
                self.skill_index = faiss.read_index(str(skill_index_path))
                with open(skill_meta_path, 'rb') as f:
                    self.skill_metadata = pickle.load(f)
                logger.info(f"Loaded skill index with {len(self.skill_metadata)} items")
            
            # Load resource index
            resource_index_path = self.storage_dir / "resource_index.faiss"
            resource_meta_path = self.storage_dir / "resource_metadata.pkl"
            
            if resource_index_path.exists() and resource_meta_path.exists():
                self.resource_index = faiss.read_index(str(resource_index_path))
                with open(resource_meta_path, 'rb') as f:
                    self.resource_metadata = pickle.load(f)
                logger.info(f"Loaded resource index with {len(self.resource_metadata)} items")
                
        except Exception as e:
            logger.error(f"Failed to load indexes: {str(e)}")
    
    def _save_indexes(self):
        """Save FAISS indexes to disk"""
        try:
            # Save skill index
            if self.skill_index is not None:
                faiss.write_index(self.skill_index, str(self.storage_dir / "skill_index.faiss"))
                with open(self.storage_dir / "skill_metadata.pkl", 'wb') as f:
                    pickle.dump(self.skill_metadata, f)
            
            # Save resource index
            if self.resource_index is not None:
                faiss.write_index(self.resource_index, str(self.storage_dir / "resource_index.faiss"))
                with open(self.storage_dir / "resource_metadata.pkl", 'wb') as f:
                    pickle.dump(self.resource_metadata, f)
                    
            logger.info("Indexes saved successfully")
        except Exception as e:
            logger.error(f"Failed to save indexes: {str(e)}")
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding vector for text"""
        embedding = self.model.encode([text])[0]
        return embedding.astype('float32')
    
    def add_skills(self, skills: List[Dict]):
        """
        Add skills to FAISS index
        skills: [{"skill_id": 1, "skill_name": "Python", "description": "..."}]
        """
        if not skills:
            return
        
        # Create new index if doesn't exist
        if self.skill_index is None:
            self.skill_index = faiss.IndexFlatL2(self.dimension)
        
        # Generate embeddings
        texts = [f"{s['skill_name']} {s.get('description', '')}" for s in skills]
        embeddings = self.model.encode(texts).astype('float32')
        
        # Add to index
        self.skill_index.add(embeddings)
        self.skill_metadata.extend(skills)
        
        # Save to disk
        self._save_indexes()
        
        logger.info(f"Added {len(skills)} skills to index")
    
    def add_resources(self, resources: List[Dict]):
        """
        Add learning resources to FAISS index
        resources: [{"resource_id": 1, "title": "...", "description": "..."}]
        """
        if not resources:
            return
        
        # Create new index if doesn't exist
        if self.resource_index is None:
            self.resource_index = faiss.IndexFlatL2(self.dimension)
        
        # Generate embeddings
        texts = [f"{r['title']} {r.get('description', '')}" for r in resources]
        embeddings = self.model.encode(texts).astype('float32')
        
        # Add to index
        self.resource_index.add(embeddings)
        self.resource_metadata.extend(resources)
        
        # Save to disk
        self._save_indexes()
        
        logger.info(f"Added {len(resources)} resources to index")
    
    def search_similar_skills(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Dict]:
        """
        Find similar skills based on query
        Returns top k most similar skills
        """
        if self.skill_index is None or len(self.skill_metadata) == 0:
            return []
        
        # Create query embedding
        query_embedding = self.create_embedding(query).reshape(1, -1)
        
        # Search
        k = min(k, len(self.skill_metadata))
        distances, indices = self.skill_index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.skill_metadata):
                result = self.skill_metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def search_similar_resources(
        self, 
        query: str, 
        k: int = 10
    ) -> List[Dict]:
        """
        Find similar learning resources based on query
        Returns top k most relevant resources
        """
        if self.resource_index is None or len(self.resource_metadata) == 0:
            return []
        
        # Create query embedding
        query_embedding = self.create_embedding(query).reshape(1, -1)
        
        # Search
        k = min(k, len(self.resource_metadata))
        distances, indices = self.resource_index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.resource_metadata):
                result = self.resource_metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distances[0][i]))
                results.append(result)
        
        return results
    
    def rebuild_skill_index(self, skills: List[Dict]):
        """
        Rebuild entire skill index from scratch
        Use this when you need to refresh the index
        """
        self.skill_index = None
        self.skill_metadata = []
        self.add_skills(skills)
    
    def rebuild_resource_index(self, resources: List[Dict]):
        """
        Rebuild entire resource index from scratch
        """
        self.resource_index = None
        self.resource_metadata = []
        self.add_resources(resources)
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the indexes"""
        return {
            "skill_index_size": len(self.skill_metadata) if self.skill_metadata else 0,
            "resource_index_size": len(self.resource_metadata) if self.resource_metadata else 0,
            "dimension": self.dimension,
            "model": "all-MiniLM-L6-v2"
        }

# Initialize service
faiss_service = FAISSService()
