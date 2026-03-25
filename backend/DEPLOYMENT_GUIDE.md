"""
COMPLETE DEPLOYMENT GUIDE - StudentLabs RAG System

This guide walks through complete setup and deployment.
"""

# ==============================================================================
# QUICK START (Local Development)
# ==============================================================================

"""
1. Backend Setup

# Install Python 3.11+
python --version  # Should be 3.11+

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

# Install dependencies
cd backend
pip install -r requirements_production.txt

# Initialize database
python -c "from app.database import init_db; init_db()"
# Output: ✅ Database initialized successfully

# Test imports
python -c "from app.services.rag_service import get_rag_service; rag = get_rag_service(); print('✅ RAG System ready!')"

2. Start Backend

# Option A: Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option B: Production (with workers)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Option C: Docker
docker build -t studentlabs-backend .
docker run -p 8000:8000 studentlabs-backend

Verify:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

3. Start Celery Workers (In separate terminal)

# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start Flower (monitoring)
celery -A app.celery_app flower

# Verify:
- Flower Dashboard: http://localhost:5555

4. Redis (For Celery)

# Start Redis (if not already running)
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
"""


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

"""
ASSIGNMENT ENDPOINTS:

1. Generate Assignment (Sync)
   POST /api/projects/{project_id}/assignments/generate
   
   Request:
   {
       "user_id": 123,
       "topic": "Machine Learning in Healthcare",
       "async_mode": false,
       "section_types": ["abstract", "introduction", "literature"]
   }
   
   Response:
   {
       "status": "success",
       "assignment": {
           "id": 1,
           "title": "RAG Assignment: Machine Learning in Healthcare",
           "topic": "Machine Learning in Healthcare",
           "word_count": 5234,
           "paper_count": 5,
           "created_at": "2024-01-15T10:30:00",
           "rag_used": true
       }
   }

2. Generate Assignment (Async)
   POST /api/projects/{project_id}/assignments/generate
   
   Request:
   {
       "user_id": 123,
       "topic": "Machine Learning in Healthcare",
       "async_mode": true
   }
   
   Response:
   {
       "status": "queued",
       "job_id": "abc123def456",
       "message": "Assignment generation queued. Check /api/jobs/abc123def456 for status"
   }

3. Get Assignment
   GET /api/projects/{project_id}/assignments
   
   Response:
   {
       "status": "success",
       "assignment": {
           "id": 1,
           "title": "RAG Assignment: Topic",
           "content": {
               "abstract": "...",
               "introduction": "...",
               "literature": "..."
           },
           "citations": [...],
           "word_count": 5234,
           "rag_used": true,
           "created_at": "2024-01-15T10:30:00"
       }
   }

4. Delete Assignment
   DELETE /api/projects/{project_id}/assignments?user_id={user_id}
   
   Response:
   {
       "status": "success",
       "message": "Assignment deleted"
   }

5. Get RAG Statistics
   GET /api/projects/{project_id}/rag-stats
   
   Response:
   {
       "status": "success",
       "stats": {
           "project_id": 123,
           "papers_indexed": 50,
           "assignments_generated": 3,
           "embeddings_stored": 50,
           "index_cached": true
       }
   }

6. Refresh RAG Index
   POST /api/projects/{project_id}/rag-index/refresh
   
   Request:
   {
       "user_id": 123
   }
   
   Response:
   {
       "status": "success",
       "message": "Index refreshed",
       "papers_indexed": 50
   }
"""


# ==============================================================================
# DATABASE MANAGEMENT
# ==============================================================================

"""
Initialize Database:
    python -c "from app.database import init_db; init_db()"

Reset Database (DELETE ALL DATA):
    python -c "from app.database import reset_db; reset_db()"

Drop Database:
    python -c "from app.database import drop_db; drop_db()"

View Database:
    # SQLite
    sqlite3 backend.db
    .tables
    SELECT * FROM projects;
    
    # PostgreSQL
    psql -U user -d studentlabs
    \\dt
    SELECT * FROM projects;
"""


# ==============================================================================
# TESTING
# ==============================================================================

"""
Run All Tests:
    pytest tests/ -v

Run Specific Test:
    pytest tests/test_rag_integration.py::TestRetrieval -v

Run with Coverage:
    pytest tests/ --cov=app --cov-report=html

Run Tests in Parallel:
    pytest tests/ -n auto

Expected Output:
    test_rag_integration.py::TestFAISSPersistence::test_index_creation PASSED
    test_rag_integration.py::TestRetrieval::test_retrieve_relevant_papers PASSED
    test_rag_integration.py::TestDatabaseIntegration::test_embedding_model_creation PASSED
    ...
    ====== 20 passed in 15.23s ======
"""


# ==============================================================================
# PERFORMANCE OPTIMIZATION
# ==============================================================================

"""
1. Index Caching
   - First assignment generation: ~5 minutes (creates FAISS index)
   - Subsequent generations: ~100ms (loads cached index from disk)
   - Location: faiss_indexes/project_{id}.index

2. Async Processing
   - Long tasks queued to Celery
   - User gets immediate job ID
   - Can poll for status
   - UI shows progress

3. Database Optimization
   - Add indexes on frequently queried columns
   - Use connection pooling (SQLAlchemy)
   - Monitor slow queries

4. Model Caching
   - Models loaded once and cached
   - Lazy loading (only when first used)
   - Reused across requests
"""


# ==============================================================================
# PRODUCTION DEPLOYMENT
# ==============================================================================

"""
Docker Deployment:

1. Build Image
   docker build -t studentlabs:latest .

2. Run Container
   docker run -d \\
     -p 8000:8000 \\
     -e DATABASE_URL=postgresql://... \\
     -e REDIS_URL=redis://redis:6379 \\
     -v data:/app/data \\
     studentlabs:latest

3. Docker Compose
   docker-compose up -d

Environment Variables:
   DATABASE_URL=postgresql://user:pass@localhost/studentlabs
   REDIS_URL=redis://localhost:6379
   CORS_ORIGINS=["https://studentlabs.com"]
   DEBUG=false
   ENVIRONMENT=production

Monitoring:
   - Prometheus: /metrics
   - Logs: stdout (or file)
   - Health: /health
   - Flower: http://localhost:5555
"""


# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

"""
Issue: Import errors when starting backend
Solution:
   1. Check Python version: python --version (should be 3.11+)
   2. Activate venv: source venv/Scripts/activate
   3. Reinstall deps: pip install --upgrade -r requirements_production.txt
   4. Test imports: python -c "from app.main import app; print('✅')"

Issue: Database errors
Solution:
   1. Reset database: python -c "from app.database import reset_db; reset_db()"
   2. Check DATABASE_URL in .env
   3. Verify database server running
   4. Check file permissions for SQLite

Issue: FAISS index errors
Solution:
   1. Delete faiss_indexes/ directory
   2. Regenerate by creating new assignment
   3. Check available disk space

Issue: Celery tasks not running
Solution:
   1. Verify Redis running: redis-cli ping
   2. Start worker: celery -A app.celery_app worker
   3. Check Flower dashboard: http://localhost:5555
   4. View logs: celery -A app.celery_app worker --loglevel=debug

Issue: Transformers model errors
Solution:
   1. Pre-download models: python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   2. Check disk space for models (~2GB)
   3. Update transformers: pip install --upgrade transformers
"""


# ==============================================================================
# MONITORING & LOGS
# ==============================================================================

"""
View Logs:
   # Backend logs
   tail -f server.log
   
   # Celery logs
   tail -f celery.log
   
   # All logs
   tail -f *.log

Key Metrics to Monitor:
   - Request latency (should be < 100ms for cached)
   - Task queue depth (Flower)
   - Database connection pool
   - Memory usage
   - Disk space (for models and indexes)
   
Health Checks:
   - API: GET /health
   - Database: SELECT 1
   - Redis: redis-cli ping
   - Celery: celery -A app.celery_app inspect active
"""


# ==============================================================================
# SCALING
# ==============================================================================

"""
Horizontal Scaling:
   1. Run multiple FastAPI workers
   2. Run multiple Celery workers
   3. Use load balancer (nginx)
   4. Share database (PostgreSQL)
   5. Share cache (Redis cluster)

Load Balancing:
   - Nginx upstream with multiple backend servers
   - Auto-scaling based on CPU/memory
   - Session affinity not required (stateless)

Database Scaling:
   - Use PostgreSQL with replication
   - Read replicas for queries
   - Connection pooling (PgBouncer)

Cache Scaling:
   - Redis cluster for high availability
   - Sentinel for failover
"""


# ==============================================================================
# CONFIGURATION
# ==============================================================================

"""
Environment Variables (.env):

DATABASE_URL=sqlite:///./backend.db  # or PostgreSQL
REDIS_URL=redis://localhost:6379
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://example.com"]

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
ENVIRONMENT=production

# AI Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
GENERATION_MODEL=mistralai/Mistral-7B-Instruct
SUMMARIZATION_MODEL=facebook/bart-large-cnn

# Storage
FAISS_INDEXES_DIR=faiss_indexes
TEMP_DIR=/tmp/studentlabs

# Timeouts
GENERATION_TIMEOUT=1800  # 30 minutes
RETRIEVAL_TIMEOUT=30     # 30 seconds
"""


# ==============================================================================
# SUCCESS CHECKLIST
# ==============================================================================

"""
Before deploying to production, verify:

✅ Database: python -c "from app.database import init_db; init_db()"
✅ Imports: python -c "from app.services.rag_service import get_rag_service; print('OK')"
✅ API start: uvicorn app.main:app --reload
✅ Health check: curl http://localhost:8000/health
✅ API docs: http://localhost:8000/docs
✅ Sample request: POST /api/projects/1/assignments/generate
✅ Celery workers: celery -A app.celery_app worker --loglevel=info
✅ Redis running: redis-cli ping
✅ Tests passing: pytest tests/ -v
✅ Logs clean: No errors in application output
✅ Performance: First request < 5 mins, cached < 100ms
"""
