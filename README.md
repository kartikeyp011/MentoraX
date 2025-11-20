# MentoraX - AI-Powered Career Guidance Platform

An intelligent career guidance platform for college students powered by Gemini AI, FAISS vector search, and AWS S3.

## 🚀 Features

- **AI Career Guidance**: Personalized career path recommendations using Gemini API
- **Smart Skill Matching**: FAISS-powered semantic search for skills and resources
- **Opportunities Hub**: Real-time internship and job listings from multiple sources
- **Profile Management**: Resume upload to AWS S3, skill tracking
- **Learning Resources**: Curated courses and materials with semantic search

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- MySQL
- FAISS (vector search)
- Gemini API (AI)
- AWS S3 (file storage)
- BeautifulSoup (web scraping)

**Frontend:**
- Vanilla JavaScript
- Tailwind CSS
- Responsive design

## 📋 Prerequisites

- Python 3.11.9+
- MySQL
- AWS Account (S3 access)
- Gemini API key

## ⚙️ Installation

1. Clone the repository:
```
git clone <your-repo-url>
cd mentorax
```

2. Create virtual environment:
```
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET_NAME=your_bucket_name
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=mentorax_db
```

5. Set up MySQL database:
```
mysql -u root -p < schema.sql
```

6. Build FAISS indexes:
```
python backend/faiss_utils.py
```

7. Run scraper (one-time):
```
python backend/scraper.py
python backend/load_data.py
```

## 🚀 Running the Application

Start the server:
```
python backend/main.py
```

Access the application:
- Landing: http://localhost:8000/landing
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
mentorax/
├── backend/          # FastAPI backend
├── frontend/         # HTML/CSS/JS frontend
├── data/            # FAISS indexes, scraped data
├── .env             # Environment variables (not committed)
└── venv/            # Virtual environment (not committed)
```

## 🔒 Security Notes

- Never commit `.env` file
- Keep AWS credentials secure
- Use environment variables for all secrets
- Session tokens expire after 7 days

## 📝 License

MIT License

## 👨‍💻 Author
[Kartikey Narain Prajapati