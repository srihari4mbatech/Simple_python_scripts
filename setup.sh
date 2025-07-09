#!/bin/bash

# MCP PostgreSQL LLM Server Setup Script
set -e

echo "🚀 MCP PostgreSQL LLM Server Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3.8+ is installed
echo -e "${BLUE}Checking Python version...${NC}"
python3 --version || {
    echo -e "${RED}Error: Python 3.8+ is required${NC}"
    exit 1
}

# Check if PostgreSQL is installed
echo -e "${BLUE}Checking PostgreSQL...${NC}"
which psql > /dev/null || {
    echo -e "${YELLOW}Warning: PostgreSQL client (psql) not found in PATH${NC}"
    echo -e "${YELLOW}Please ensure PostgreSQL is installed and accessible${NC}"
}

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your database and API credentials${NC}"
else
    echo -e "${GREEN}.env file already exists${NC}"
fi

# Create required directories
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p static templates

# Make scripts executable
chmod +x main.py
chmod +x run_server.py

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your configuration:"
echo "   - Database credentials"
echo "   - OpenAI API key (optional)"
echo "   - Anthropic API key (optional)"
echo ""
echo "2. Create and setup database:"
echo "   createdb mcp_database"
echo "   python main.py init-db"
echo ""
echo "3. Create admin user (optional):"
echo "   python main.py create-user --username admin --email admin@example.com --password admin123 --admin"
echo ""
echo "4. Run the application:"
echo "   python run_server.py"
echo ""
echo "5. Access the web interface:"
echo "   http://localhost:8000"
echo ""
echo -e "${BLUE}For more information, see MCP_SERVER_README.md${NC}"