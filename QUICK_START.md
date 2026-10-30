# 🚀 Quick Start - 2 Minutes to Running

## Step 1: Prepare Environment (30 seconds)

```bash
cd /home/ubuntu/Desktop/LoanApplicationCapstone
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Step 2: Start Everything (1 minute)

```bash
docker-compose up
```

Wait for: `✓ StreamlitServerAddress_Text <- Streamlit is running...`

## Step 3: Open Browser (30 seconds)

Visit: **http://localhost:8501**

---

## ✅ What You Can Do

### Option A: View Dashboard
1. Click **Dashboard** in sidebar
2. See key metrics and recent applications

### Option B: Submit New Application
1. Click **Submit Application**
2. Fill in sample data:
   - Name: John Doe
   - Email: john@example.com
   - Annual Income: 75000
   - Loan Amount: 50000
3. Click **Submit Application**
4. Watch 5 agents evaluate in real-time!
5. See final decision in seconds

### Option C: View Existing Applications
1. Click **View Applications**
2. See all 10 sample applicants
3. Click **Details** on any application
4. Review agent evaluations, audit trail, final decision

---

## 🧪 Test Individual Evaluation

In a new terminal (while `docker-compose up` is running):

```bash
python run_evaluation.py 1
```

This evaluates applicant #1 (John Doe) and shows:
- Credit Analysis results
- Risk Assessment results
- Compliance check results
- Fraud Detection results
- Final Decision

---

## 🛑 Stop the System

```bash
# In the terminal where docker-compose is running
Ctrl + C

# Or in another terminal
docker-compose down
```

---

## 📊 What Happens Internally

```
1. You submit form → Streamlit captures data
2. Creates application in MySQL
3. Orchestrator triggers 5 agents (in parallel):
   - Credit Analysis Agent → Reviews creditworthiness
   - Risk Assessment Agent → Analyzes financial stability
   - Compliance Agent → Checks regulatory rules
   - Fraud Detection Agent → Identifies red flags
   - Decision Agent → Synthesizes findings
4. Results saved to database + audit trail
5. UI displays:
   - Individual agent assessments
   - Final classification (Approved/Rejected/Manual Review)
   - Confidence score
   - Complete reasoning
```

---

## 🎯 Sample Applicants to Test

| ID | Name | Credit | Expected Result | Notes |
|---|---|---|---|---|
| 1 | John Doe | 720 (Good) | ✅ APPROVED | Stable employment, good credit |
| 2 | Jane Smith | 780 (Very Good) | ✅ APPROVED | Excellent credit, high income |
| 3 | Bob Johnson | 650 (Fair) | ⏳ REVIEW | Self-employed, fair credit |
| 4 | Alice Williams | 550 (Poor) | ❌ REJECTED | Poor credit, lower income |
| 5 | Charlie Brown | Unemployed | ❌ REJECTED | Fraud flag set |
| 6 | Diana Martinez | 750 (Very Good) | ✅ APPROVED | Healthcare professional |
| 7 | Edward Garcia | 800 (Excellent) | ✅ APPROVED | Lawyer, excellent credit |
| 8 | Fiona Rodriguez | 710 (Good) | ✅ APPROVED | Educator, good credit |
| 9 | George Lee | 690 (Good) | ✅ APPROVED | Consultant, good credit |
| 10 | Helen Taylor | 770 (Very Good) | ✅ APPROVED | Tech startup, very good credit |

Try different applicants to see different evaluation paths!

---

## 🎓 Learn the System

### Quick Exploration (5 min)
1. **Dashboard**: Overview of all applications
2. **View Applications**: Filter by status
3. **Application Details**: Deep dive into decisions
4. **Analytics**: View trends and statistics

### Deep Dive (15 min)
1. Look at agent evaluations
2. Review audit trail
3. Check decision justification
4. View confidence scores

### Code Exploration (30 min)
1. Read `README.md` (overview)
2. Read `PROJECT_OVERVIEW.md` (architecture)
3. Check `src/agents/` (agent implementations)
4. Review `ui/app.py` (UI code)

---

## 🔑 Key Files

```
LoanApplicationCapstone/
├── README.md               ← Start here for overview
├── SETUP_GUIDE.md         ← Detailed setup instructions
├── PROJECT_OVERVIEW.md    ← Architecture & design
├── IMPLEMENTATION_SUMMARY.md ← What was built
│
├── docker-compose.yml     ← Start with: docker-compose up
├── Dockerfile             ← Container configuration
│
├── src/agents/            ← 5 AI agents
├── ui/app.py             ← Streamlit dashboard
├── database/schema.sql   ← MySQL setup
│
└── run_evaluation.py     ← Test script
```

---

## 🚨 Troubleshooting

### "Connection refused"
```bash
# MySQL might not be ready - wait 30 seconds
docker-compose logs mysql
```

### "Port 8501 already in use"
```bash
# Kill process on port 8501
lsof -i :8501
kill -9 <PID>
```

### "API key error"
```bash
# Check .env has ANTHROPIC_API_KEY set
cat .env | grep ANTHROPIC_API_KEY

# Verify key format starts with sk-ant-
```

### "Application won't load"
```bash
# Check logs
docker-compose logs -f app

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📞 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Read guides**: See SETUP_GUIDE.md for detailed help
3. **Test directly**: `python run_evaluation.py 1`
4. **Review code**: Check inline comments in Python files

---

## 💡 Pro Tips

### Tip 1: Multiple Terminals
```bash
# Terminal 1: Start system
docker-compose up

# Terminal 2: Run tests while system is running
python run_evaluation.py 2
python run_evaluation.py 3
```

### Tip 2: Database Access
```bash
# Access MySQL directly
mysql -h localhost -u loan_admin -p loan_application_db
# Password: secure_password_123
```

### Tip 3: View Raw Logs
```bash
# See detailed logs
docker-compose logs -f app | tail -50
```

### Tip 4: Reset Everything
```bash
# Remove containers and database
docker-compose down -v

# Start fresh
docker-compose up
```

---

## ✅ You're Ready!

Your Multi-Agent Loan Application Analysis System is ready to use!

**Current Status**:
- ✅ System built and configured
- ✅ Database with 10 sample applicants
- ✅ All 5 agents ready
- ✅ UI ready to use
- ✅ Docker configured

**Next Step**: Run `docker-compose up` and open http://localhost:8501

Happy analyzing! 🎉
