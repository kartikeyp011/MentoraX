from app.services.gemini_service import gemini_service

def test_gemini():
    print("Testing Gemini AI Service...\n")
    
    # Test 1: Career Path Generation
    print("1. Testing Career Path Generation...")
    paths = gemini_service.generate_career_paths(
        degree="Computer Science",
        skills=["Python", "JavaScript", "SQL"],
        interests=["AI", "Web Development"],
        career_goals="Want to work in tech industry"
    )
    if paths:
        print(f"✓ Generated {len(paths)} career paths")
        print(f"  First path: {paths[0].get('role_title')}")
    else:
        print("✗ Failed to generate career paths")
    
    # Test 2: Skill Gap Analysis
    print("\n2. Testing Skill Gap Analysis...")
    gap = gemini_service.analyze_skill_gap(
        current_skills=["Python", "HTML", "CSS"],
        target_role="Full Stack Developer"
    )
    if gap:
        print("✓ Skill gap analysis completed")
        print(f"  Missing skills: {len(gap.get('missing_skills', []))}")
    else:
        print("✗ Failed to analyze skill gap")
    
    # Test 3: Interview Questions
    print("\n3. Testing Interview Questions...")
    questions = gemini_service.generate_interview_questions(
        role="Software Engineer",
        count=5
    )
    if questions:
        print(f"✓ Generated {len(questions)} questions")
        print(f"  First question: {questions[0].get('question')[:60]}...")
    else:
        print("✗ Failed to generate questions")
    
    # Test 4: Sentiment Analysis
    print("\n4. Testing Sentiment Analysis...")
    sentiment = gemini_service.analyze_sentiment(
        "I'm feeling overwhelmed with job search but excited about opportunities"
    )
    if sentiment:
        print("✓ Sentiment analyzed")
        print(f"  Sentiment: {sentiment.get('sentiment')}")
        print(f"  Score: {sentiment.get('sentiment_score')}")
    else:
        print("✗ Failed to analyze sentiment")
    
    print("\n✅ Gemini integration tests complete!")

if __name__ == "__main__":
    test_gemini()
