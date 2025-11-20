import json
from database import execute_query, fetch_one


def load_opportunities():
    """Load opportunities from JSON into database"""
    print("📂 Loading opportunities from data/opportunities.json...")

    # Read JSON file
    with open('data/opportunities.json', 'r', encoding='utf-8') as f:
        opportunities = json.load(f)

    print(f"📊 Found {len(opportunities)} opportunities to load")

    loaded_count = 0

    for opp in opportunities:
        try:
            # Check if opportunity already exists (by title and source)
            existing = fetch_one(
                "SELECT opportunity_id FROM opportunities WHERE title = %s AND source = %s",
                (opp['title'], opp['source'])
            )

            if existing:
                print(f"⏭️  Skipping (already exists): {opp['title']}")
                continue

            # Insert opportunity
            query = """
                    INSERT INTO opportunities (title, description, link, source, location, deadline)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            opp_id = execute_query(
                query,
                (opp['title'], opp['description'], opp['link'],
                 opp['source'], opp['location'], opp['deadline'])
            )

            # Insert skill mappings
            for skill_id in opp['skill_ids']:
                try:
                    execute_query(
                        "INSERT INTO opportunity_skills (opportunity_id, skill_id) VALUES (%s, %s)",
                        (opp_id, skill_id)
                    )
                except:
                    pass  # Ignore duplicates

            loaded_count += 1
            print(f"✅ Loaded: {opp['title']}")

        except Exception as e:
            print(f"❌ Error loading {opp['title']}: {e}")

    print(f"\n🎉 Successfully loaded {loaded_count} new opportunities!")


if __name__ == "__main__":
    load_opportunities()