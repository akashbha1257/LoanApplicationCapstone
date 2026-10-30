# Setup Guide - Multi-Agent Loan Application System

## Overview
This guide provides step-by-step instructions to set up and run the Multi-Agent Loan Application Analysis System.

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows (WSL2)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 10GB free space

### Dependencies
- Docker & Docker Compose (recommended)
- OR: Python 3.10+, MySQL 8.0+
- Anthropic API Key (get from https://console.anthropic.com)

## Setup Methods

### Method 1: Docker Compose (Recommended)

**Fastest way to get started - everything in one command!**

1. **Prerequisites**
   ```bash
   # Install Docker Desktop from https://docker.com
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Clone/Navigate to project**
   ```bash
   cd /home/ubuntu/Desktop/LoanApplicationCapstone
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   
   # Edit .env and add your Anthropic API key
   # You can use any text editor
   nano .env
   # or
   code .env
   ```

4. **Start the system**
   ```bash
   docker-compose up
   ```

   This will:
   - Pull MySQL 8.0 image
   - Build the Python application image
   - Create and initialize the database
   - Start Streamlit UI
   - Load sample data

5. **Access the application**
   - Open browser to: http://localhost:8501
   - MySQL available at: localhost:3306

6. **Stop the system**
   ```bash
   docker-compose down
   ```

   To also remove data:
   ```bash
   docker-compose down -v
   ```

---

### Method 2: Local Installation (Without Docker)

**For development or custom setup**

1. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install and configure MySQL**
   ```bash
   # macOS
   brew install mysql
   brew services start mysql
   
   # Ubuntu/Debian
   sudo apt-get install mysql-server
   sudo systemctl start mysql
   
   # Windows
   # Download from https://dev.mysql.com/downloads/mysql/
   ```

3. **Create database**
   ```bash
   mysql -u root -p
   > CREATE DATABASE loan_application_db;
   > CREATE USER 'loan_admin'@'localhost' IDENTIFIED BY 'secure_password_123';
   > GRANT ALL PRIVILEGES ON loan_application_db.* TO 'loan_admin'@'localhost';
   > FLUSH PRIVILEGES;
   > EXIT;
   ```

4. **Load schema and sample data**
   ```bash
   mysql -u loan_admin -p loan_application_db < database/schema.sql
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   
   # Edit .env with your credentials and API key
   nano .env
   ```

6. **Verify database connection**
   ```bash
   python -c "from src.database import DatabaseConnection; DatabaseConnection.init_db(); print('✅ Database connected!')"
   ```

7. **Run the application**
   ```bash
   streamlit run ui/app.py
   ```

   The app will open at: http://localhost:8501

---

## First Steps After Setup

### 1. Verify Installation
Check that all components are working:
```bash
# Test database connection
python -c "from src.database import DatabaseConnection; DatabaseConnection.init_db(); print('✅ DB OK')"

# Test agents can initialize
python -c "from src.agents import CreditAnalysisAgent; print('✅ Agents OK')"

# Test MCP server
python -c "from src.mcp_server import get_mcp_server; print('✅ MCP OK')"
```

### 2. Run a Test Evaluation
Using the provided test script:
```bash
python run_evaluation.py 1
```

This will evaluate the first sample applicant and show results.

### 3. Access the UI
1. Open http://localhost:8501
2. Navigate to "Submit Application" tab
3. Fill out a sample application
4. Submit and watch agents evaluate in real-time

---

## Troubleshooting

### Docker Issues

**Container won't start**
```bash
# Check logs
docker-compose logs app

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**MySQL connection timeout**
```bash
# MySQL might not be ready, wait 30 seconds and retry
# Or check if port 3306 is already in use
lsof -i :3306
```

**Port already in use**
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
docker-compose down
sudo lsof -i :8501  # Find what's using Streamlit port
```

### MySQL Issues

**Connection refused**
```bash
# Ensure MySQL is running
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# Check MySQL is listening
sudo netstat -tlnp | grep mysql
```

**Authentication failed**
```bash
# Verify credentials in .env match MySQL setup
# Verify MySQL user exists
mysql -u loan_admin -p -e "SELECT USER();"
```

**Database not found**
```bash
# Reimport schema
mysql -u loan_admin -p loan_application_db < database/schema.sql
```

### Application Issues

**Streamlit won't load**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check for syntax errors
python -m py_compile ui/app.py
python -m py_compile src/orchestrator/orchestrator.py

# Run with verbose output
streamlit run ui/app.py --logger.level=debug
```

**Anthropic API errors**
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test API connection
python -c "import anthropic; print(anthropic.Anthropic(api_key='YOUR_KEY').models.list())"
```

**Agent evaluation fails**
```bash
# Check logs
tail -f logs/base_agent.log
tail -f logs/orchestrator.py.log

# Run single agent test
python -c "
from src.agents import CreditAnalysisAgent
agent = CreditAnalysisAgent()
result = agent.evaluate({'credit_score': 750, 'credit_utilization_percent': 30})
print(result)
"
```

---

## Configuration Reference

### Environment Variables (.env)

```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Your Anthropic API key
MODEL_ID=claude-3-5-sonnet-20241022  # Claude model to use

# MySQL Database Configuration
MYSQL_HOST=mysql          # or 'localhost' for local setup
MYSQL_PORT=3306
MYSQL_USER=loan_admin
MYSQL_PASSWORD=secure_password_123
MYSQL_DATABASE=loan_application_db

# MCP Server Configuration
MCP_HOST=localhost
MCP_PORT=8080

# Application Configuration
DEBUG=False               # Set to True for debug mode
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Data Management

### Backup Database
```bash
# Docker setup
docker exec loan_app_mysql mysqldump -u loan_admin -psecure_password_123 \
  loan_application_db > backup.sql

# Local setup
mysqldump -u loan_admin -p loan_application_db > backup.sql
```

### Restore Database
```bash
# Docker setup
docker exec -i loan_app_mysql mysql -u loan_admin -psecure_password_123 \
  loan_application_db < backup.sql

# Local setup
mysql -u loan_admin -p loan_application_db < backup.sql
```

### Reset to Sample Data
```bash
# Docker setup
docker exec loan_app_mysql mysql -u loan_admin -psecure_password_123 \
  loan_application_db < database/schema.sql

# Local setup
mysql -u loan_admin -p loan_application_db < database/schema.sql
```

---

## Performance Tuning

### For High Volume
1. **Increase MySQL pool size** in `src/database/connection.py`
   ```python
   pool_size=50,      # Increase from 10
   max_overflow=50    # Increase from 20
   ```

2. **Add indexing** for frequently queried fields
   ```sql
   CREATE INDEX idx_applicant_annual_income ON applicants(annual_income);
   ```

3. **Enable MySQL query cache**
   ```ini
   query_cache_size=32M
   query_cache_type=1
   ```

### Memory Optimization
- Run agents with lower concurrency: Modify `_run_agents_parallel()` in orchestrator
- Use connection pooling (already configured)
- Archive old evaluations to separate table

---

## Next Steps

### Development
1. Read [docs/agents.md](docs/agents.md) to understand agent architecture
2. Review [docs/api.md](docs/api.md) for API documentation
3. Check [docs/schema.md](docs/schema.md) for database design

### Production Deployment
1. Review [docs/deployment.md](docs/deployment.md)
2. Set up SSL/TLS for database connections
3. Configure backup and disaster recovery
4. Set up monitoring and alerting

### Customization
1. Add custom agents by extending `BaseAgent`
2. Add new database fields to models
3. Customize Streamlit UI components
4. Add additional regulatory rules

---

## Support

### Debug Mode
Enable debug logging:
```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### View Logs
```bash
# Docker
docker-compose logs -f app
docker-compose logs -f mysql

# Local
tail -f logs/*.log
```

### Common Issues Checklist
- [ ] Anthropic API key is valid and set
- [ ] MySQL is running and accessible
- [ ] All Python dependencies installed
- [ ] Port 8501 (Streamlit) not in use
- [ ] Port 3306 (MySQL) not in use
- [ ] Firewall allows connections to ports
- [ ] At least 4GB RAM available
- [ ] Python version is 3.10+

---

## Quick Reference

| Task | Command |
|------|---------|
| Start system | `docker-compose up` |
| Stop system | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Run tests | `pytest tests/ -v` |
| Test evaluation | `python run_evaluation.py 1` |
| Access UI | http://localhost:8501 |
| Access MySQL | `mysql -u loan_admin -p -h localhost` |
| Rebuild containers | `docker-compose build --no-cache` |
| Reset database | `mysql -u loan_admin -p < database/schema.sql` |

---

**Successfully set up? 🎉 Head to http://localhost:8501 and start evaluating loan applications!**
