from backend.scraper_utils import ScraperBase, OpportunityInserter
from datetime import datetime, timedelta


def test_fingerprinting():
    """Test fingerprint creation"""
    scraper = ScraperBase("Test")

    # Same URL and title should give same hash
    hash1 = scraper.create_fingerprint(
        "https://example.com/job/123",
        "Software Engineer"
    )
    hash2 = scraper.create_fingerprint(
        "https://example.com/job/123",
        "Software Engineer"
    )

    assert hash1 == hash2, "Same URL+title should produce same hash"
    print("✅ Fingerprinting test passed")

    # Different URL should give different hash
    hash3 = scraper.create_fingerprint(
        "https://example.com/job/456",
        "Software Engineer"
    )

    assert hash1 != hash3, "Different URLs should produce different hashes"
    print("✅ Duplicate detection test passed")


def test_opportunity_insertion():
    """Test inserting opportunity with duplicate handling"""
    scraper = ScraperBase("Test")

    # Test data
    opp_data = {
        'title': 'Test Software Engineer Position',
        'description': 'Test description for Python and JavaScript role',
        'link': 'https://example.com/test-job-12345',
        'url_hash': scraper.create_fingerprint(
            'https://example.com/test-job-12345',
            'Test Software Engineer Position'
        ),
        'source': 'Test',
        'location': 'Remote',
        'deadline': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        'company_name': 'Test Company',
        'job_type': 'Full-time',
        'skill_ids': [1, 3]  # Python, JavaScript
    }

    # First insertion - should add
    opp_id1, status1 = OpportunityInserter.insert_or_update(opp_data)
    print(f"First insert: ID={opp_id1}, Status={status1}")
    assert status1 == 'added', "First insertion should be 'added'"

    # Second insertion with same data - should be duplicate
    opp_id2, status2 = OpportunityInserter.insert_or_update(opp_data)
    print(f"Second insert: ID={opp_id2}, Status={status2}")
    assert status2 == 'duplicate', "Second insertion should be 'duplicate'"
    assert opp_id1 == opp_id2, "Should return same ID"

    # Third insertion with updated description - should update
    opp_data['description'] = 'Updated description with React and Node.js'
    opp_id3, status3 = OpportunityInserter.insert_or_update(opp_data)
    print(f"Third insert: ID={opp_id3}, Status={status3}")
    assert status3 == 'updated', "Third insertion should be 'updated'"

    print("✅ Opportunity insertion test passed")


if __name__ == "__main__":
    print("🧪 Testing Scraper Utilities...\n")

    test_fingerprinting()
    test_opportunity_insertion()

    print("\n🎉 All tests passed!")