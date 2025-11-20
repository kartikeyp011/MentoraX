import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from .database import fetch_all

# Initialize embedding model (will be loaded once)
model = None


def get_model():
    """Get or initialize the embedding model"""
    global model
    if model is None:
        print("🔄 Loading sentence-transformers model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")
    return model


def build_skill_embeddings():
    """Build FAISS index for skills"""
    print("🔨 Building skill embeddings...")

    # Get all skills from database
    skills = fetch_all("SELECT skill_id, skill_name, description FROM skills ORDER BY skill_id")

    if not skills:
        print("❌ No skills found in database")
        return

    # Create text representations
    skill_texts = []
    skill_map = {}

    for skill in skills:
        # Combine name and description for better embeddings
        text = skill['skill_name']
        if skill['description']:
            text += ". " + skill['description']
        skill_texts.append(text)
        skill_map[skill['skill_id']] = {
            'skill_name': skill['skill_name'],
            'description': skill['description']
        }

    # Generate embeddings
    embedding_model = get_model()
    embeddings = embedding_model.encode(skill_texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index
    os.makedirs('data/faiss_indexes', exist_ok=True)
    faiss.write_index(index, 'data/faiss_indexes/skills.index')

    # Save mapping
    with open('data/faiss_indexes/skills_map.json', 'w') as f:
        json.dump(skill_map, f, indent=2)

    print(f"✅ Skill embeddings built: {len(skills)} skills indexed")
    return index, skill_map


def build_resource_embeddings():
    """Build FAISS index for learning resources"""
    print("🔨 Building resource embeddings...")

    # Create sample resources
    sample_resources = [
        {
            "title": "Python for Beginners - Full Course",
            "description": "Complete Python programming course covering basics to advanced topics. Learn data structures, OOP, and more.",
            "url": "https://www.youtube.com/watch?v=python-course"
        },
        {
            "title": "Machine Learning Specialization",
            "description": "Andrew Ng's complete ML course. Covers supervised learning, neural networks, and deep learning fundamentals.",
            "url": "https://www.coursera.org/specializations/machine-learning"
        },
        {
            "title": "React - The Complete Guide",
            "description": "Master React.js from basics to advanced. Build modern web applications with hooks, context, and Redux.",
            "url": "https://www.udemy.com/course/react-the-complete-guide"
        },
        {
            "title": "SQL for Data Analysis",
            "description": "Learn SQL queries, joins, aggregations, and database design. Perfect for data analysts and developers.",
            "url": "https://mode.com/sql-tutorial"
        },
        {
            "title": "Deep Learning Specialization",
            "description": "Advanced deep learning course covering CNNs, RNNs, transformers. Build neural networks from scratch.",
            "url": "https://www.coursera.org/specializations/deep-learning"
        },
        {
            "title": "JavaScript - The Complete Guide",
            "description": "Modern JavaScript ES6+ course. Learn async programming, DOM manipulation, and web APIs.",
            "url": "https://javascript.info"
        },
        {
            "title": "Node.js Backend Development",
            "description": "Build scalable backend APIs with Node.js and Express. Learn authentication, databases, and deployment.",
            "url": "https://www.udemy.com/course/nodejs-express-mongodb"
        },
        {
            "title": "AWS Cloud Practitioner",
            "description": "Introduction to AWS cloud services. Learn EC2, S3, Lambda, and cloud architecture fundamentals.",
            "url": "https://aws.amazon.com/training"
        },
        {
            "title": "Data Structures and Algorithms",
            "description": "Master DSA for coding interviews. Arrays, trees, graphs, dynamic programming with Python/Java.",
            "url": "https://www.leetcode.com"
        },
        {
            "title": "Web Development Bootcamp",
            "description": "Full stack web development course. HTML, CSS, JavaScript, React, Node.js, MongoDB.",
            "url": "https://www.udemy.com/course/web-development-bootcamp"
        },
        {
            "title": "DevOps with Docker and Kubernetes",
            "description": "Learn containerization with Docker and orchestration with Kubernetes. CI/CD pipelines and deployment.",
            "url": "https://www.udemy.com/course/docker-kubernetes"
        },
        {
            "title": "UI/UX Design Fundamentals",
            "description": "Learn user interface and experience design. Figma, wireframing, prototyping, and user research.",
            "url": "https://www.coursera.org/learn/ui-ux-design"
        },
        {
            "title": "Cybersecurity Basics",
            "description": "Introduction to information security. Network security, encryption, ethical hacking, and best practices.",
            "url": "https://www.cybrary.it"
        },
        {
            "title": "Java Programming Masterclass",
            "description": "Complete Java course from basics to advanced. OOP, collections, multithreading, and Spring framework.",
            "url": "https://www.udemy.com/course/java-programming-masterclass"
        },
        {
            "title": "Data Science with Python",
            "description": "Learn data analysis with Pandas, NumPy, Matplotlib. Statistical analysis and machine learning basics.",
            "url": "https://www.datacamp.com/courses/intro-to-python-for-data-science"
        }
    ]

    # Insert resources into database
    from database import execute_query

    resource_map = {}
    resource_texts = []

    for idx, resource in enumerate(sample_resources, start=1):
        # Check if exists
        existing = fetch_all(
            "SELECT resource_id FROM resources WHERE title = %s",
            (resource['title'],)
        )

        if not existing:
            resource_id = execute_query(
                "INSERT INTO resources (title, description, url) VALUES (%s, %s, %s)",
                (resource['title'], resource['description'], resource['url'])
            )
        else:
            resource_id = existing[0]['resource_id']

        # Create text representation
        text = resource['title'] + ". " + resource['description']
        resource_texts.append(text)
        resource_map[str(resource_id)] = {
            'title': resource['title'],
            'description': resource['description'],
            'url': resource['url']
        }

    # Generate embeddings
    embedding_model = get_model()
    embeddings = embedding_model.encode(resource_texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, 'data/faiss_indexes/resources.index')

    # Save mapping
    with open('data/faiss_indexes/resources_map.json', 'w') as f:
        json.dump(resource_map, f, indent=2)

    print(f"✅ Resource embeddings built: {len(sample_resources)} resources indexed")
    return index, resource_map


def search_faiss(query, index_type='skills', top_k=5):
    """Search FAISS index for similar items"""
    try:
        # Load index and mapping
        index_path = f'data/faiss_indexes/{index_type}.index'
        map_path = f'data/faiss_indexes/{index_type}_map.json'

        if not os.path.exists(index_path):
            return []

        index = faiss.read_index(index_path)

        with open(map_path, 'r') as f:
            item_map = json.load(f)

        # Generate query embedding
        embedding_model = get_model()
        query_embedding = embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # Search
        distances, indices = index.search(query_embedding, top_k)

        # Get results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(item_map):
                item_id = list(item_map.keys())[idx]
                results.append({
                    'id': item_id,
                    'distance': float(distance),
                    **item_map[item_id]
                })

        return results

    except Exception as e:
        print(f"Error searching FAISS: {e}")
        return []


def build_all_indexes():
    """Build all FAISS indexes"""
    print("🚀 Building all FAISS indexes...\n")
    build_skill_embeddings()
    print()
    build_resource_embeddings()
    print("\n✅ All indexes built successfully!")


if __name__ == "__main__":
    build_all_indexes()