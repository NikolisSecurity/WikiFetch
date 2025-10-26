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

# Migration Routes
@app.route('/migration-status', methods=['GET'])
def get_migration_status():
    """Get status of txt files vs database articles."""
    try:
        # Get all txt files
        txt_files = []
        if os.path.exists(SAVE_DIR):
            txt_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.txt')]

        # Get all article titles from database
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM articles')
        db_titles = {row['title'] for row in cursor.fetchall()}
        conn.close()

        # Categorize files
        unmigrated_files = []
        migrated_files = []

        for txt_file in txt_files:
            # Parse title from filename (reverse the underscore replacement)
            title = txt_file.replace('.txt', '').replace('_', ' ')

            if title in db_titles:
                migrated_files.append(txt_file)
            else:
                unmigrated_files.append(txt_file)

        return jsonify({
            "unmigrated": unmigrated_files,
            "migrated": migrated_files,
            "total_txt_files": len(txt_files),
            "total_db_articles": len(db_titles)
        }), 200

    except Exception as e:
        logging.error(f"Migration status error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/migrate', methods=['POST'])
def migrate_files():
    """Migrate selected txt files to database."""
    try:
        data = request.get_json()

        if not data or 'files' not in data:
            return jsonify({"error": "Files parameter required", "status": 400}), 400

        files_to_migrate = data['files']
        delete_after = data.get('delete_after', False)

        if not isinstance(files_to_migrate, list):
            return jsonify({"error": "Files must be an array", "status": 400}), 400

        results = []

        for file_name in files_to_migrate:
            result = {"file": file_name, "status": "error", "message": "Unknown error"}

            try:
                file_path = os.path.join(SAVE_DIR, file_name)

                # Check if file exists
                if not os.path.exists(file_path):
                    result["message"] = "File not found"
                    results.append(result)
                    continue

                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse content: First line should be "Title: X"
                if not content.startswith("Title: "):
                    result["message"] = "File malformed (no Title: line)"
                    results.append(result)
                    continue

                # Split on first double newline
                parts = content.split('\n\n', 1)
                if len(parts) < 2:
                    result["message"] = "File malformed (no content after title)"
                    results.append(result)
                    continue

                # Extract title
                title_line = parts[0]
                title = title_line.replace("Title: ", "").strip()

                # Extract content
                article_content = parts[1].strip()

                if not title:
                    result["message"] = "Title is empty"
                    results.append(result)
                    continue

                if len(article_content) < 10:
                    result["message"] = "Content too short"
                    results.append(result)
                    continue

                # Generate Wikipedia URL
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

                # Calculate metrics
                word_count = len(article_content.split())
                char_count = len(article_content)

                # Insert into database
                try:
                    article_id = database.insert_article(
                        title=title,
                        content=article_content,
                        url=url,
                        word_count=word_count,
                        char_count=char_count,
                        tags=[]
                    )

                    result["status"] = "success"
                    result["message"] = f"Imported successfully (ID: {article_id})"
                    result["article_id"] = article_id

                    # Delete file if requested
                    if delete_after:
                        os.remove(file_path)
                        result["message"] += " and file deleted"

                except ValueError as e:
                    if "already saved" in str(e).lower():
                        result["message"] = "Article already exists in database"
                    else:
                        result["message"] = str(e)

            except PermissionError:
                result["message"] = "File read permission error"
            except Exception as e:
                result["message"] = f"Error: {str(e)}"

            results.append(result)

        # Return results
        success_count = sum(1 for r in results if r['status'] == 'success')
        return jsonify({
            "results": results,
            "success_count": success_count,
            "total_count": len(results)
        }), 200

    except Exception as e:
        logging.error(f"Migration error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == '__main__':
    app.run(debug=True)
