# MCP PostgreSQL LLM Server

A comprehensive Model Context Protocol (MCP) server application that integrates PostgreSQL database with OpenAI and Anthropic LLM APIs, providing a business-friendly web interface for database operations and AI-powered analysis.

## 🚀 Features

### Core Capabilities
- **MCP Server Implementation**: Full Model Context Protocol server with PostgreSQL integration
- **Dual LLM Support**: OpenAI (GPT models) and Anthropic (Claude models) integration
- **PostgreSQL Integration**: Direct database connectivity with SQL execution and schema introspection
- **Web Interface**: Modern, responsive web UI for business users
- **Natural Language SQL**: Convert natural language queries to SQL using LLMs
- **Data Analysis**: AI-powered analysis of query results with insights and recommendations
- **Real-time Chat**: Interactive chat interface with LLMs for database-related queries

### Business Features
- **User Management**: Authentication and authorization system
- **Query History**: Track all SQL executions with performance metrics
- **Usage Analytics**: Monitor LLM API usage and costs
- **Schema Browser**: Visual database schema exploration
- **Conversation Tracking**: Maintain chat history and context
- **Multi-tenancy**: Support for multiple users with isolated sessions

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API Key (optional)
- Anthropic API Key (optional)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/mcp_database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mcp_database
POSTGRES_USER=username
POSTGRES_PASSWORD=password

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
MCP_LOG_LEVEL=INFO

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key_here
DEBUG=True

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# Authentication
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb mcp_database

# Initialize database tables
python main.py init-db

# Create an admin user (optional)
python main.py create-user --username admin --email admin@example.com --password admin123 --full-name "Admin User" --admin
```

### 4. Create Required Directories

```bash
mkdir -p static templates
```

## 🚦 Running the Application

### Option 1: Run Both Servers Together (Recommended)

```bash
python run_server.py
```

This starts both the MCP server and web interface simultaneously.

### Option 2: Run Servers Separately

**Terminal 1 - MCP Server:**
```bash
python main.py run-mcp-server
```

**Terminal 2 - Web Interface:**
```bash
python main.py run-web-server
```

### Option 3: Development Mode

```bash
# Check configuration
python main.py check-config

# Run web server only
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Accessing the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📖 Usage Guide

### Web Interface Features

#### 1. SQL Query Tab
- Execute direct SQL queries against PostgreSQL
- View results in formatted tables
- Query history and performance tracking

#### 2. LLM Chat Tab
- Interactive chat with OpenAI or Anthropic models
- Database-specific conversations
- Model and provider selection

#### 3. Natural Language SQL Tab
- Convert natural language to SQL queries
- Automatic query execution
- Context-aware SQL generation

#### 4. Data Analysis Tab
- AI-powered analysis of query results
- Trend identification and insights
- Business recommendations

#### 5. Database Schema Tab
- Visual database schema browser
- Table and column information
- Relationship mapping

### API Endpoints

#### Core Endpoints
- `GET /api/status` - System status and configuration
- `GET /api/database/tables` - List database tables
- `GET /api/database/schema` - Get database schema
- `POST /api/database/query` - Execute SQL query

#### LLM Endpoints
- `POST /api/llm/chat` - Chat with LLM
- `POST /api/llm/sql-generate` - Generate SQL from natural language
- `POST /api/llm/analyze` - Analyze data with LLM

#### User Management
- `GET /api/conversations` - Get user conversations
- `GET /api/query-history` - Get query execution history
- `GET /api/usage-stats` - Get API usage statistics

### MCP Server Tools

The MCP server provides these tools for LLM clients:

1. **execute_sql**: Execute SQL queries on PostgreSQL
2. **chat_with_llm**: Chat with configured LLM providers
3. **sql_with_llm**: Generate and execute SQL using LLM assistance
4. **analyze_data**: Analyze database query results using LLM

### MCP Server Resources

Available resources for MCP clients:

1. **postgresql://tables**: List all database tables
2. **postgresql://schema**: Get complete database schema
3. **llm://models**: List available LLM models
4. **mcp://status**: Get server status and configuration

## 🔧 Configuration

### Database Configuration
- Supports standard PostgreSQL connection parameters
- Connection pooling and retry logic
- Automatic table creation and migration

### LLM Configuration
- Multiple provider support (OpenAI + Anthropic)
- Automatic model selection
- Usage tracking and cost estimation
- Rate limiting and error handling

### Security Configuration
- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration for web interface
- API key management

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI API   │    │   MCP Server    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Core)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   LLM APIs      │
                       │   Database      │    │ (OpenAI/Claude) │
                       └─────────────────┘    └─────────────────┘
```

### Components

1. **MCP Server** (`app/mcp_server.py`): Core Model Context Protocol implementation
2. **Database Layer** (`app/database.py`, `app/models.py`): PostgreSQL integration and ORM
3. **LLM Integration** (`app/llm/`): OpenAI and Anthropic API integration
4. **FastAPI Backend** (`app/api/`): RESTful API and web server
5. **Web Interface** (`templates/index.html`): Modern web UI for business users

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connection
python main.py check-config

# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Check database exists
psql -h localhost -p 5432 -U username -l
```

#### LLM API Issues
```bash
# Verify API keys are set
python main.py check-config

# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Test Anthropic connection
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

#### Port Conflicts
```bash
# Check if ports are in use
netstat -tlnp | grep :8000
netstat -tlnp | grep :8001

# Change ports in .env file if needed
API_PORT=8080
MCP_SERVER_PORT=8002
```

### Logging and Debugging

```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG

# View detailed logs
python main.py run-web-server

# Check application logs
tail -f app.log
```

## 🔐 Security Considerations

- Change default secret key in production
- Use environment variables for sensitive data
- Enable HTTPS in production environments
- Implement proper user access controls
- Monitor API usage and costs
- Regular security updates

## 🚀 Production Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8001

CMD ["python", "run_server.py"]
```

### Using Systemd

```ini
[Unit]
Description=MCP PostgreSQL LLM Server
After=network.target postgresql.service

[Service]
Type=simple
User=mcpuser
WorkingDirectory=/opt/mcp-server
ExecStart=/opt/mcp-server/venv/bin/python run_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Variables for Production

```bash
DEBUG=False
SECRET_KEY=production_secret_key_here
DATABASE_URL=postgresql://user:pass@prod-db:5432/mcp_db
API_HOST=0.0.0.0
FRONTEND_URL=https://yourdomain.com
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`

## 🔄 Version History

- **v1.0.0**: Initial release with MCP server, PostgreSQL integration, and web interface
- Core features: SQL execution, LLM chat, natural language SQL, data analysis
- Support for OpenAI and Anthropic APIs
- Complete web interface for business users