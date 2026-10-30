# 🏦 Multi-Agent Loan Application Analysis System

A sophisticated AI-powered loan application analysis system that uses multiple specialized agents to evaluate loan applications and classify them as **Approved**, **Rejected**, or **Requires Manual Review**.

## 🎯 Features

- **Multi-Agent Architecture**: 5 specialized AI agents evaluating different dimensions
  - 💳 **Credit Analysis Agent**: Evaluates creditworthiness
  - 📊 **Risk Assessment Agent**: Analyzes financial stability
  - ⚖️ **Compliance Agent**: Verifies regulatory requirements
  - 🚨 **Fraud Detection Agent**: Identifies suspicious patterns
  - 🎓 **Decision Agent**: Synthesizes findings into final classification

- **Parallel Processing**: All agents run simultaneously for fast evaluation
- **MySQL Database**: Persistent storage of applications and evaluations
- **MCP Server**: Tool integration for database queries and compliance verification
- **Streamlit UI**: User-friendly dashboard for loan officers
- **Audit Trail**: Complete logging of all decisions for compliance
- **Docker Support**: One-command deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (if running without Docker)
- Anthropic API Key

### Installation

1. **Clone the repository**
   ```bash
   cd /home/ubuntu/Desktop/LoanApplicationCapstone
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up
   ```

   The application will be available at:
   - Streamlit UI: http://localhost:8501
   - MySQL: localhost:3306

### Manual Setup (Without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL**
   - Install MySQL 8.0+
   - Create database: `loan_application_db`
   - Import schema: `mysql -u root -p loan_application_db < database/schema.sql`

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL and API credentials
   ```

4. **Initialize database**
   ```bash
   python -c "from src.database import DatabaseConnection, Base; DatabaseConnection.init_db(); Base.metadata.create_all(DatabaseConnection.get_engine())"
   ```

5. **Run Streamlit**
   ```bash
   streamlit run ui/app.py
   ```

## 📋 Usage

### Dashboard
View key metrics and recent applications at a glance.

### Submit Application
- Fill out applicant and loan details
- System automatically evaluates using all 5 agents
- Receives instant classification and decision explanation

### View Applications
- Filter by status, loan amount, or date
- Quick overview of all applications

### Application Details
- View complete applicant profile
- See individual agent evaluations
- Review audit trail
- View final decision and confidence score

### Analytics
- Approval rate metrics
- Distribution by status
- Average loan amounts
- Trends and patterns

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│       Streamlit UI Dashboard             │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌──────────────────┐  ┌────────────────────┐
│  Orchestrator    │  │   MCP Server       │
│  (Parallel)      │  │  (Tool Execution)  │
└─────┬────┬───┬──┘  └────────────────────┘
      │    │   │              │
  ┌───▼─┬──▼─┬─▼──┬──────────▼──┐
  │     │    │    │             │
  ▼     ▼    ▼    ▼             ▼
Credit Risk Comp Fraud Decision MySQL
Agent  Agent Agent Agent Agent  Database

Evaluation Results → Audit Log
Final Decision → Application Status
```

## 🤖 Agent Details

### Credit Analysis Agent
**Inputs**: Credit score, payment history, credit utilization, defaults
**Outputs**: Credit rating (A/B/C/D/F), risk score, recommendation

### Risk Assessment Agent
**Inputs**: Income, debt, employment, collateral, assets
**Outputs**: Risk level (Low/Medium/High), financial cushion assessment

### Compliance Agent
**Inputs**: Age, location, income, regulations
**Outputs**: Compliance status (Pass/Fail), regulatory violations

### Fraud Detection Agent
**Inputs**: Income consistency, credit patterns, employment verification
**Outputs**: Fraud risk level (Low/Medium/High), fraud indicators

### Decision Agent
**Inputs**: All agent findings
**Outputs**: Final classification (Approved/Rejected/Manual Review), confidence, justification

## 📊 Database Schema

### Core Tables
- **applicants**: Personal/business information
- **loan_applications**: Loan request details
- **credit_history**: Credit profile and payment history
- **risk_indicators**: Financial stability metrics
- **regulatory_rules**: Compliance requirements
- **application_evaluations**: Agent assessments and final decision
- **audit_log**: Complete decision trail

## 🔒 Security

- API key management via environment variables
- Database connection encryption
- Complete audit trail for compliance
- PII handling (SSN masked in logs)
- Role-based access control ready

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Test agents independently:
```bash
python -m pytest tests/test_agents.py -v
```

Test database integration:
```bash
python -m pytest tests/test_database.py -v
```

## 🛠️ Configuration

All configuration is managed through `.env` file:

```env
# API
ANTHROPIC_API_KEY=your_key_here
MODEL_ID=claude-3-5-sonnet-20241022

# Database
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=loan_admin
MYSQL_PASSWORD=secure_password_123
MYSQL_DATABASE=loan_application_db

# Application
DEBUG=False
LOG_LEVEL=INFO
```

## 📈 Performance

- **Evaluation Time**: ~15-30 seconds (parallel agent execution)
- **Database Operations**: Sub-second queries with indexing
- **Concurrent Users**: Supports multiple simultaneous evaluations
- **Scalability**: Ready for Kubernetes deployment

## 🐛 Troubleshooting

### MySQL Connection Error
- Ensure MySQL is running on the specified host/port
- Verify credentials in `.env`
- Check firewall rules for port 3306

### API Key Error
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Ensure key has valid permissions
- Check for typos or trailing spaces

### Streamlit Not Loading
- Check firewall allows port 8501
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check logs: `logs/app.log`

## 📝 Sample Applicants

The schema includes 10 sample applicants with varying profiles:
1. John Doe - Good credit, stable employment
2. Jane Smith - Excellent credit, high income
3. Bob Johnson - Fair credit, self-employed
4. Alice Williams - Poor credit, lower income
5. Charlie Brown - Unemployed, high fraud risk
6. Diana Martinez - Good credit, healthcare professional
7. Edward Garcia - Excellent credit, lawyer
8. Fiona Rodriguez - Good credit, educator
9. George Lee - Good credit, consultant
10. Helen Taylor - Very good credit, tech startup

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Kubernetes Deployment
Helm charts and K8s manifests available in `/k8s` directory.

### Cloud Deployment
- AWS: Use RDS for MySQL, ECS for containers
- GCP: Cloud SQL + Cloud Run
- Azure: Azure Database for MySQL + Container Instances

## 📚 Documentation

- [Agent Documentation](docs/agents.md)
- [API Reference](docs/api.md)
- [Database Schema](docs/schema.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude API](https://anthropic.com)
- [Streamlit](https://streamlit.io)
- [SQLAlchemy](https://sqlalchemy.org)
- [MySQL](https://mysql.com)

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: support@example.com
- Documentation: https://docs.example.com

---

**🚀 Happy lending!**
