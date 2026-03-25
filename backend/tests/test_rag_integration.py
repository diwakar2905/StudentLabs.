"""
Integration Tests - RAG System

Comprehensive tests for the complete RAG pipeline:
1. Index creation and persistence
2. Paper retrieval
3. Assignment generation
4. Database integration
5. Error handling

Run tests:
    pytest tests/test_rag_integration.py -v
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Mock data fixtures
@pytest.fixture
def sample_papers():
    """Sample papers for testing"""
    return [
        {
            "id": 1,
            "paper_id": "2024.01.001",
            "title": "Machine Learning in Healthcare",
            "abstract": "This paper explores the application of machine learning techniques in clinical diagnostics and treatment planning.",
            "authors": "John Smith, Jane Doe",
            "year": 2024,
            "url": "https://arxiv.org/abs/2024.01.001"
        },
        {
            "id": 2,
            "paper_id": "2024.01.002",
            "title": "Deep Learning for Medical Imaging",
            "abstract": "Deep neural networks have shown remarkable performance in analyzing medical images and improving diagnostic accuracy.",
            "authors": "Alice Johnson, Bob Wilson",
            "year": 2023,
            "url": "https://arxiv.org/abs/2024.01.002"
        },
        {
            "id": 3,
            "paper_id": "2024.01.003",
            "title": "AI Ethics in Healthcare",
            "abstract": "This work addresses ethical considerations and bias in AI systems used for healthcare applications.",
            "authors": "Carol Davis, David Brown",
            "year": 2024,
            "url": "https://arxiv.org/abs/2024.01.003"
        }
    ]


@pytest.fixture
def temp_faiss_dir():
    """Create temporary directory for FAISS indexes"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_db():
    """Mock database session"""
    # This would be replaced with actual test DB
    pass


class TestFAISSPersistence:
    """Test FAISS index persistence"""
    
    def test_index_creation(self, sample_papers):
        """Test creating FAISS index from papers"""
        from ai_engine.retriever import index_papers
        
        num_indexed = index_papers(sample_papers, project_id=None, save_to_disk=False)
        
        assert num_indexed == len(sample_papers)
        assert num_indexed == 3
    
    def test_index_save_to_disk(self, sample_papers, temp_faiss_dir):
        """Test saving FAISS index to disk"""
        from ai_engine.retriever import index_papers, save_index
        import os
        
        # Index papers
        num_indexed = index_papers(sample_papers, project_id=None, save_to_disk=False)
        assert num_indexed == 3
        
        # Manually change FAISS dir for testing
        project_id = 123
        saved = save_index(project_id)
        
        # Verify files exist
        assert saved == True
    
    def test_index_load_from_disk(self, sample_papers):
        """Test loading FAISS index from disk"""
        from ai_engine.retriever import (
            index_papers,
            save_index,
            load_index,
            retrieve_relevant_content
        )
        
        project_id = 456
        
        # Index and save
        index_papers(sample_papers, project_id=project_id, save_to_disk=True)
        
        # Load from disk
        loaded = load_index(project_id)
        assert loaded == True
        
        # Should be able to retrieve now
        results = retrieve_relevant_content(
            "machine learning healthcare",
            top_k=2,
            project_id=project_id
        )
        assert len(results) > 0


class TestRetrieval:
    """Test paper retrieval"""
    
    def test_retrieve_relevant_papers(self, sample_papers):
        """Test retrieving papers for query"""
        from ai_engine.retriever import index_papers, retrieve_relevant_content
        
        # Index papers
        index_papers(sample_papers, save_to_disk=False)
        
        # Retrieve for query
        results = retrieve_relevant_content(
            query="machine learning medical imaging",
            top_k=2
        )
        
        assert len(results) > 0
        assert len(results) <= 2
        assert isinstance(results, list)
    
    def test_retrieve_with_different_queries(self, sample_papers):
        """Test retrieval with different queries"""
        from ai_engine.retriever import index_papers, retrieve_relevant_content
        
        index_papers(sample_papers, save_to_disk=False)
        
        queries = [
            "machine learning",
            "medical imaging",
            "artificial intelligence ethics"
        ]
        
        for query in queries:
            results = retrieve_relevant_content(query, top_k=1)
            assert len(results) > 0


class TestAssignmentGeneration:
    """Test assignment generation with RAG"""
    
    def test_generate_assignment_basic(self, sample_papers):
        """Test basic assignment generation"""
        from app.services.rag_service import RAGService
        from ai_engine.retriever import index_papers, retrieve_relevant_content
        
        # Index papers first
        index_papers(sample_papers, save_to_disk=False)
        
        # Create RAG service
        rag_service = RAGService()
        
        # Generate section
        section = rag_service.generate_assignment_section(
            section_type="abstract",
            topic="AI in Healthcare",
            context="Retrieved paper content"
        )
        
        assert isinstance(section, str)
        # Section should have some content (or be empty if model not available)
    
    def test_assignment_service_validates_project(self):
        """Test that assignment service validates project ownership"""
        from app.services.assignment_service import AssignmentService
        
        # This would test with mock DB
        # Ensure it validates project existence


class TestDatabaseIntegration:
    """Test database integration"""
    
    def test_embedding_model_creation(self):
        """Test Embedding model can be created"""
        from app.models import Embedding
        
        # Just verify the model exists and is properly defined
        assert hasattr(Embedding, '__tablename__')
        assert Embedding.__tablename__ == 'embeddings'
    
    def test_assignment_model_fields(self):
        """Test Assignment model has required fields"""
        from app.models import Assignment
        
        required_fields = ['id', 'project_id', 'title', 'content', 'citations', 
                          'word_count', 'rag_used', 'created_at']
        
        for field in required_fields:
            assert hasattr(Assignment, field)
    
    def test_all_models_have_tablename(self):
        """Test all models have __tablename__"""
        from app.models import (
            User, Project, Paper, Summary, Assignment,
            Presentation, Export, Embedding
        )
        
        models = [User, Project, Paper, Summary, Assignment, 
                  Presentation, Export, Embedding]
        
        for model in models:
            assert hasattr(model, '__tablename__')
            assert isinstance(model.__tablename__, str)


class TestPrompts:
    """Test prompt templates"""
    
    def test_prompt_template_exists(self):
        """Test prompt templates are defined"""
        from app.ai.prompts import SECTION_PROMPTS, get_prompt
        
        assert len(SECTION_PROMPTS) > 0
    
    def test_get_prompt_formatting(self):
        """Test prompt formatting"""
        from app.ai.prompts import get_prompt
        
        prompt = get_prompt(
            "abstract",
            topic="Climate Change",
            context="Environmental research papers",
            papers_summary="5 papers reviewed"
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Climate Change" in prompt


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_papers_list(self):
        """Test handling of empty papers list"""
        from ai_engine.retriever import index_papers
        
        num_indexed = index_papers([])
        assert num_indexed == 0
    
    def test_retrieve_with_no_indexed_papers(self):
        """Test retrieval when no papers indexed"""
        from ai_engine.retriever import retrieve_relevant_content, clear_index
        
        clear_index()
        
        results = retrieve_relevant_content("test query")
        assert results == []
    
    def test_invalid_project_id_handling(self):
        """Test handling of invalid project ID"""
        from app.services.assignment_service import AssignmentService
        
        # Would test with mock DB that project doesn't exist


class TestPerformance:
    """Test performance characteristics"""
    
    def test_index_loading_speed(self, sample_papers):
        """Test that index loading is fast (from cache)"""
        import time
        from ai_engine.retriever import (
            index_papers,
            save_index,
            load_index
        )
        
        project_id = 999
        
        # Index and save
        index_papers(sample_papers, project_id=project_id, save_to_disk=True)
        
        # Time the load
        start = time.time()
        loaded = load_index(project_id)
        elapsed = time.time() - start
        
        assert loaded == True
        # Loading from disk should be fast (< 1 second for small index)
        assert elapsed < 1.0
    
    def test_retrieval_speed(self, sample_papers):
        """Test retrieval performance"""
        import time
        from ai_engine.retriever import index_papers, retrieve_relevant_content
        
        # Index papers
        index_papers(sample_papers, save_to_disk=False)
        
        # Time retrieval
        start = time.time()
        results = retrieve_relevant_content("query", top_k=2)
        elapsed = time.time() - start
        
        assert len(results) > 0
        # Retrieval should be fast (< 100ms for small index)
        assert elapsed < 0.1


class TestEndToEnd:
    """End-to-end tests for complete workflow"""
    
    def test_complete_rag_pipeline(self, sample_papers):
        """Test complete RAG pipeline from papers to assignment"""
        from ai_engine.retriever import (
            index_papers,
            retrieve_relevant_content,
            build_retrieval_context
        )
        
        # Step 1: Index papers
        num_indexed = index_papers(sample_papers, save_to_disk=False)
        assert num_indexed == 3
        
        # Step 2: Build retrieval context
        context = build_retrieval_context(
            sample_papers,
            query="machine learning in healthcare"
        )
        
        assert len(context) > 0
        assert "Research Context" in context
        
        # Step 3: Could generate assignment here (if models available)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
