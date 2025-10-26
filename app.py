from flask import Flask, render_template, request, jsonify
import wikipedia
import os
import warnings
import logging
import database

# Suppress warnings from the Wikipedia API
warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Set the Wikipedia language and user agent
wikipedia.set_lang("en")
wikipedia.set_user_agent("MyWikipediaApp/1.0")

# Define the directory where files will be saved
SAVE_DIR = "downloaded_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize database
database.init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        query = request.form['query']
        results = search_wikipedia(query)  # Search for the query
    downloaded_files = list_downloaded_files()  # List previously downloaded files
    return render_template('index.html', results=results, downloaded_files=downloaded_files)

def search_wikipedia(query):
    try:
        page = wikipedia.page(query)

        # Generate Wikipedia URL
        url = page.url

        # Calculate word and character counts
        word_count = len(page.content.split())
        char_count = len(page.content)

        # Save to database
        try:
            article_id = database.insert_article(
                title=page.title,
                content=page.content,
                url=url,
                word_count=word_count,
                char_count=char_count,
                tags=[]
            )

            return {
                "id": article_id,
                "title": page.title,
                "summary": page.summary,
                "full_content": page.content,
                "url": url,
                "word_count": word_count
            }
        except ValueError as e:
            # Article already exists or validation error
            return {
                "title": page.title,
                "summary": page.summary,
                "full_content": page.content,
                "url": url,
                "error": str(e)
            }

    except wikipedia.exceptions.DisambiguationError as e:
        return {
            "title": "Disambiguation",
            "summary": f"This term may refer to: {', '.join(e.options)}",
            "full_content": None
        }
    except wikipedia.exceptions.PageError:
        return None

def list_downloaded_files():
    """Lists all articles from the database."""
    try:
        articles = database.get_all_articles(limit=100, offset=0)
        return articles
    except Exception as e:
        logging.error(f"Error fetching articles: {e}")
        return []  # Return an empty list on error

@app.errorhandler(500)
def internal_error(error):
    """Handles internal server errors."""
    return f"500 error: {str(error)}", 500

# API Routes
@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    """List all saved articles with pagination."""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Validate and clamp parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0

        articles = database.get_all_articles(limit=limit, offset=offset)

        # Get total count
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM articles')
        total = cursor.fetchone()['count']
        conn.close()

        return jsonify({
            "articles": articles,
            "total": total,
            "limit": limit,
            "offset": offset
        }), 200

    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def api_get_article(article_id):
    """Retrieve a single article by ID."""
    try:
        article = database.get_article_by_id(article_id)

        if article is None:
            return jsonify({"error": "Article not found", "status": 404}), 404

        return jsonify(article), 200

    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/api/search', methods=['POST'])
def api_search_articles():
    """Search across saved article content."""
    try:
        # Check Content-Type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json", "status": 400}), 400

        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({"error": "Query parameter required", "status": 400}), 400

        query = data['query']

        if not query or not query.strip():
            return jsonify({"error": "Query parameter required", "status": 400}), 400

        results = database.search_articles(query)

        return jsonify({
            "results": results,
            "count": len(results)
        }), 200

    except Exception as e:
        logging.error(f"API error: {e}")
        if "JSON" in str(e):
            return jsonify({"error": "Invalid JSON", "status": 400}), 400
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def api_delete_article(article_id):
    """Delete a saved article from database."""
    try:
        rows_deleted = database.delete_article(article_id)

        if rows_deleted == 0:
            return jsonify({"error": "Article not found", "status": 404}), 404

        return '', 204

    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get database statistics."""
    try:
        stats = database.get_stats()
        return jsonify(stats), 200

    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == '__main__':
    app.run(debug=True)
