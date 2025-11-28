# **MentoraX - AI-Powered Career Guidance Platform**


An intelligent career guidance and upskilling platform for college students, powered by AI and machine learning. MentoraX helps students discover career paths, find opportunities, learn new skills, and get personalized mentorship.

***

## ✨ **Features**

### **🎯 AI Career Guidance**
- Personalized career path recommendations using AI
- Skill gap analysis with actionable insights
- Context-aware suggestions based on user profile

### **💼 Opportunities Hub**
- Real-time internship and job listings
- Advanced filtering (location, skills, date)
- Save/bookmark opportunities

### **📚 Learning Zone**
- AI-powered semantic search for courses
- Free and paid course recommendations
- Personalized learning paths

### **🤖 Upskill Coach**
- Interactive AI chatbot for career advice
- Personalized learning plans
- Real-time mentorship

### **👤 Profile Management**
- Skills portfolio with proficiency tracking
- Resume upload to cloud storage
- Progress tracking and statistics

***

## 🛠️ **Tech Stack**

**Backend:** FastAPI (Python 3.11.9), MySQL 8.0, FAISS (Vector Search)  
**AI/ML:** Google Gemini API, Sentence Transformers  
**Frontend:** Vanilla JavaScript, Tailwind CSS  
**Cloud:** AWS S3  
**Authentication:** Session-based with SHA256 hashing

***

## 🚀 **Installation**

### **Prerequisites**
- Python 3.11.9
- MySQL 8.0+
- Chrome browser
- AWS Account
- Google Gemini API key

### **Quick Start**

```bash
# Clone repository
git clone https://github.com/kartikeyp011/MentoraX.git
cd MentoraX

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p < backend/schema.sql

# Configure environment (.env file)
GEMINI_API=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET_NAME=your_bucket
MYSQL_PASSWORD=your_password

# Build indexes
python backend/faiss_utils.py

# Start server
python -m backend.main
```

Visit: `http://localhost:8000`

***

## 📖 **Usage**

### **For Students**

1. **Sign Up** → Create profile with degree and career goals
2. **Add Skills** → Build your skills portfolio
3. **Get Guidance** → AI analyzes and suggests career paths
4. **Find Opportunities** → Browse and save relevant positions
5. **Learn** → Discover courses with semantic search
6. **Chat with AI** → Get personalized advice anytime

### **For Administrators**

```bash
# Run data collection
python -m backend.scraper

# Rebuild search indexes
python -m backend.faiss_utils

# Monitor logs
SELECT * FROM scraping_logs ORDER BY completed_at DESC LIMIT 10;
```

***

## 📚 **API Endpoints**

**Authentication**
- `POST /auth/signup` - Register user
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout

**Career**
- `POST /career/path` - Get AI recommendations
- `POST /career/skills/analyze` - Analyze skills

**Opportunities**
- `GET /opportunities/all` - List all
- `POST /opportunities/save/{id}` - Save opportunity
- `POST /opportunities/filter` - Filter by criteria

**Resources**
- `POST /resources/search` - Semantic search
- `GET /resources/all` - List all courses

**Coach**
- `POST /coach/chat` - Chat with AI
- `GET /coach/plan` - Get learning plan

**User**
- `GET /user/profile` - Get profile
- `POST /user/update` - Update profile
- `POST /user/upload_resume` - Upload resume

Full docs: `http://localhost:8000/docs`

***

## 📁 **Project Structure**

```
mentorax/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── auth.py              # Authentication
│   ├── career.py            # Career guidance (Gemini)
│   ├── opportunities.py     # Job/internship endpoints
│   ├── resources.py         # Learning resources
│   ├── coach.py             # AI chatbot
│   ├── profile.py           # User management
│   ├── database.py          # MySQL connector
│   ├── faiss_utils.py       # Vector search
│   ├── scraper_utils.py     # Scraping infrastructure
│   └── schema.sql           # Database schema
├── frontend/
│   ├── *.html               # Pages
│   └── js/*.js              # Frontend logic
├── data/
│   └── faiss_indexes/       # Search indexes
├── .env                     # Environment config
└── requirements.txt         # Dependencies
```

***

## 🔧 **Key Features**

### **AI-Powered Recommendations**
Uses Google Gemini API to generate personalized career paths based on:
- Current skills and proficiency
- Academic background
- Career goals
- Market trends

### **Semantic Search**
FAISS-based vector search enables natural language queries:
- "learn machine learning for beginners"
- "python courses for data science"
- Results ranked by relevance score

### **Automated Data Collection**
Intelligent web scrapers with:
- Duplicate detection (SHA256 fingerprinting)
- Automatic retry and rate limiting
- Data validation and cleanup
- Activity logging

### **Smart Duplicate Prevention**
Combines URL + title hashing to ensure:
- No duplicate opportunities
- Updates to existing entries
- Cleanup of outdated data (30+ days)

***

## 📄 **License**

MIT License - see LICENSE file

***

## 📧 **Contact**

- **Repository:** [github.com/kartikeyp011/mentorax](https://github.com/kartikeyp011/mentorax)

***