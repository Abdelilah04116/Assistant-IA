# Intelligent Research Assistant

A production-ready, multi-agent RAG-powered research assistant that answers complex questions by retrieving and synthesizing information from reliable sources.

## 🏗️ Architecture Overview

This system combines **Retrieval-Augmented Generation (RAG)** with a **multi-agent architecture** to provide intelligent, well-researched answers with proper citations.

### Core Components

1. **Multi-Agent System**
   - **Research Agent**: Retrieves information from internal documents and external sources
   - **Reasoning Agent**: Analyzes queries, decomposes complex questions, and builds logical understanding
   - **Writer Agent**: Synthesizes final answers with clear structure and proper citations

2. **RAG Pipeline**
   - **Document Ingestion**: PDF, TXT, and MD file processing with intelligent chunking
   - **Embeddings**: SentenceTransformers-based text embeddings with model flexibility
   - **Vector Store**: ChromaDB (persistent) or FAISS (high-performance) for similarity search
   - **Retrieval**: Top-k retrieval with optional reranking

3. **FastAPI Backend**
   - RESTful API with comprehensive endpoints
   - Async-ready architecture with proper error handling
   - Pydantic schemas for request/response validation
   - Health monitoring and logging

4. **React Frontend**
   - Modern chat interface with real-time responses
   - Document upload and management
   - Search and collection statistics
   - Responsive design with TailwindCSS

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- Google Gemini API key

### Using Docker Compose (Recommended)

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd intelligent-research-assistant
   cp .env.example .env
   ```

2. **Configure Environment**
   Edit `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Start Services**
   ```bash
   docker-compose up --build
   ```

4. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend**
   ```bash
   npm start
   ```

## 📖 Usage Guide

### 1. Document Upload

Upload documents through the web interface or API:

- **Supported formats**: PDF, TXT, MD
- **Max file size**: 50MB per file
- **Processing**: Automatic chunking and embedding generation

### 2. Chat Interface

Ask questions in natural language:

- The system retrieves relevant documents
- Multi-agent workflow processes your query
- Responses include citations and quality scores
- Real-time streaming responses available

### 3. Document Search

Search through uploaded documents:

- Semantic search with similarity scoring
- Optional reranking for better results
- Filter by document type or metadata

## 🔧 Configuration

### Environment Variables

#### Backend Configuration
```bash
# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key

# Vector Store
VECTOR_STORE_TYPE=chroma  # chroma or faiss
CHROMA_PERSIST_DIRECTORY=./data/vector_store
FAISS_INDEX_PATH=./data/vector_store/faiss.index

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_DOCUMENTS_PER_QUERY=5

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Frontend Configuration
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Vector Store Options

#### ChromaDB (Default)
- Persistent storage
- Built-in metadata handling
- Easy setup and management
- Recommended for production

#### FAISS
- High-performance similarity search
- Memory-efficient for large datasets
- Requires manual metadata management
- Best for large-scale deployments

## 🏛️ API Documentation

### Core Endpoints

#### Chat
```http
POST /chat/
Content-Type: application/json

{
  "query": "What are the latest developments in quantum computing?",
  "max_documents": 5,
  "include_web_search": true
}
```

#### Document Upload
```http
POST /ingestion/upload
Content-Type: multipart/form-data

file: [document]
chunk_size: 1000
chunk_overlap: 200
```

#### Document Search
```http
POST /ingestion/search
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "k": 10,
  "rerank": true
}
```

#### Health Check
```http
GET /health/
```

### Full API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🧠 Multi-Agent Workflow

### 1. Research Agent
- **Purpose**: Information retrieval and source gathering
- **Capabilities**:
  - Internal document search using RAG
  - External web search integration
  - Source validation and ranking
  - Metadata extraction

### 2. Reasoning Agent
- **Purpose**: Query analysis and logical decomposition
- **Capabilities**:
  - Complex query decomposition
  - Sub-question generation
  - Logical reasoning over sources
  - Insight extraction

### 3. Writer Agent
- **Purpose**: Answer synthesis and presentation
- **Capabilities**:
  - Structured answer generation
  - Proper citation formatting
  - Quality assessment
  - Style adaptation

### Orchestration with LangGraph

The system uses **LangGraph** for agent orchestration because:

- **Superior State Management**: Better workflow state tracking and checkpointing
- **Flexible Routing**: Conditional workflow paths based on intermediate results
- **Error Recovery**: Robust error handling and retry mechanisms
- **LangChain Integration**: Seamless integration with the LangChain ecosystem
- **Scalability**: Designed for complex, multi-step reasoning workflows

## 🔄 RAG Pipeline Details

### Document Processing

1. **Ingestion**: Files are uploaded and validated
2. **Parsing**: PDF text extraction, markdown/text reading
3. **Chunking**: Intelligent text splitting with overlap
4. **Embedding**: Vector representation using SentenceTransformers
5. **Storage**: Persistent vector database with metadata

### Retrieval Process

1. **Query Embedding**: Convert user query to vector
2. **Similarity Search**: Find top-k similar document chunks
3. **Reranking** (optional): Improve relevance with cross-encoder
4. **Context Assembly**: Prepare retrieved documents for agents

### Quality Assurance

- **Relevance Filtering**: Remove low-similarity results
- **Deduplication**: Eliminate redundant content
- **Source Validation**: Verify document integrity
- **Performance Monitoring**: Track retrieval metrics

## 📊 Performance & Scaling

### Optimization Features

- **Async Processing**: Non-blocking I/O throughout the stack
- **Batch Operations**: Efficient bulk document processing
- **Caching**: Embedding and query result caching
- **Connection Pooling**: Database connection optimization

### Scaling Considerations

- **Horizontal Scaling**: Multiple backend instances behind load balancer
- **Vector Store Scaling**: Distributed ChromaDB or FAISS clusters
- **Caching Layer**: Redis for session and result caching
- **Monitoring**: Health checks and performance metrics

### Resource Requirements

#### Minimum (Development)
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 10GB
- **Network**: Standard broadband

#### Production (Small-Medium)
- **CPU**: 4-8 cores
- **Memory**: 16-32GB RAM
- **Storage**: 100GB+ SSD
- **Network**: High-speed internet

## 🔒 Security Considerations

### API Security
- **CORS Configuration**: Restricted origins
- **Input Validation**: Pydantic schema validation
- **Rate Limiting**: Request throttling (implement as needed)
- **API Keys**: Secure environment variable storage

### Data Security
- **File Validation**: Type and size restrictions
- **Sandboxing**: Isolated document processing
- **Temporary Files**: Automatic cleanup
- **Access Control**: User-based document access (extend as needed)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Monitoring & Logging

### Application Logs
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Performance Metrics**: Request timing and success rates
- **Error Tracking**: Detailed error context and stack traces

### Health Monitoring
- **Service Health**: `/health/` endpoint
- **Component Status**: Database, LLM, and vector store checks
- **Resource Usage**: CPU, memory, and storage monitoring
- **Alerting**: Health-based alerting (implement as needed)

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Production environment variables
   export OPENAI_API_KEY=prod_key
   export DEBUG=false
   export LOG_LEVEL=WARNING
   ```

2. **Docker Deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Load Balancer Configuration**
   - Configure reverse proxy (nginx/traefik)
   - SSL/TLS termination
   - Health check endpoints

### Cloud Deployment Options

- **AWS**: ECS/EKS with RDS and ElastiCache
- **Google Cloud**: GKE with Cloud SQL and Memorystore
- **Azure**: AKS with Azure Database and Redis Cache
- **Vercel/Railway**: Managed platform deployment

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes with tests
4. **Document** your changes
5. **Submit** a pull request

### Development Guidelines

- **Code Style**: Follow PEP 8 (Python) and ESLint rules (JavaScript)
- **Testing**: Maintain test coverage above 80%
- **Documentation**: Update docs for API changes
- **Performance**: Profile changes that affect performance

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Check environment variables
export OPENAI_API_KEY=your_key
```

#### Frontend Build Errors
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

#### Vector Store Issues
```bash
# Clear vector store
rm -rf ./data/vector_store/*

# Rebuild embeddings
# Upload documents again
```

#### Memory Issues
- Reduce `MAX_DOCUMENTS_PER_QUERY`
- Use smaller embedding models
- Increase system RAM
- Switch to FAISS for large datasets

### Getting Help

1. **Check Logs**: Review application logs for errors
2. **Health Check**: Verify service status at `/health/`
3. **Documentation**: Review this README and API docs
4. **Issues**: Check GitHub issues for known problems
5. **Support**: Create new issue with detailed information

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Advanced Web Search**: Multiple search engine integration
- [ ] **User Management**: Authentication and authorization
- [ ] **Document Collaboration**: Shared collections and annotations
- [ ] **Advanced Analytics**: Usage metrics and insights
- [ ] **Custom Models**: Support for local LLM models
- [ ] **Real-time Collaboration**: Multi-user chat sessions
- [ ] **Advanced Reranking**: Cross-encoder and learning-to-rank
- [ ] **Document Versioning**: Track document changes over time

### Performance Improvements

- [ ] **Streaming Responses**: Real-time answer generation
- [ ] **Parallel Processing**: Concurrent agent execution
- [ ] **Smart Caching**: Intelligent result caching
- [ ] **Database Optimization**: Query performance improvements

## 📚 Additional Resources

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [React Documentation](https://react.dev/)

### Related Projects
- [LangChain](https://github.com/langchain-ai/langchain)
- [SentenceTransformers](https://github.com/UKPLab/sentence-transformers)
- [FAISS](https://github.com/facebookresearch/faiss)

---

**Built with ❤️ using modern AI and web technologies**
