import sqlite3
import os
from datetime import datetime

# Database configuration
DB_PATH = os.getenv('DATABASE_PATH', './data/wikifetch.db')

def init_db():
    """Initialize database and create tables if they don't exist."""
    # Create data directory if it doesn't exist
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            summary TEXT,
            url TEXT,
            saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fetched_date TIMESTAMP,
            word_count INTEGER,
            character_count INTEGER
        )
    ''')

    # Create tags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create article_tags junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS article_tags (
            article_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (article_id, tag_id),
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')

    # Create favorites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            article_id INTEGER PRIMARY KEY,
            favorited_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
        )
    ''')

    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_saved_date ON articles(saved_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)')

    conn.commit()
    conn.close()

def get_db_connection():
    """Return a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_article(title, content, url, word_count=None, char_count=None, tags=None):
    """
    Insert a new article into the database with optional tags.

    Args:
        title: Article title (required)
        content: Full article text (required)
        url: Wikipedia URL (required)
        word_count: Number of words (optional, will be calculated if not provided)
        char_count: Number of characters (optional, will be calculated if not provided)
        tags: List of tag names (optional)

    Returns:
        Inserted article ID

    Raises:
        sqlite3.IntegrityError: If article with same title already exists
        ValueError: If validation fails
    """
    if tags is None:
        tags = []

    # Validation
    if not title or not title.strip():
        raise ValueError("Title is required")
    if not content or len(content) < 10:
        raise ValueError("Content is required and must be at least 10 characters")
    if len(title) > 500:
        raise ValueError("Title must be less than 500 characters")

    title = title.strip()

    # Calculate summary: First 200 characters, truncated at last complete word
    summary = content[:200]
    if len(content) > 200:
        last_space = summary.rfind(' ')
        if last_space > 0:
            summary = summary[:last_space] + '...'

    # Calculate word and character counts if not provided
    if word_count is None:
        word_count = len(content.split())
    if char_count is None:
        char_count = len(content)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert article
        cursor.execute('''
            INSERT INTO articles (title, content, summary, url, fetched_date, word_count, character_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, summary, url, datetime.now().isoformat(), word_count, char_count))

        article_id = cursor.lastrowid

        # Insert tags if provided
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                # Insert tag if it doesn't exist
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))

                # Get tag ID
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag_row = cursor.fetchone()
                tag_id = tag_row['id']

                # Link article and tag
                cursor.execute('INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)',
                             (article_id, tag_id))

        conn.commit()
        return article_id

    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Article already saved")
        raise
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_article_by_id(article_id):
    """
    Retrieve a single article by ID with its tags.

    Args:
        article_id: Article ID

    Returns:
        Dictionary with article data and tags array, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get article data
    cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
    article = cursor.fetchone()

    if not article:
        conn.close()
        return None

    # Convert row to dictionary
    article_dict = dict(article)

    # Get tags for this article
    cursor.execute('''
        SELECT tags.name
        FROM tags
        JOIN article_tags ON tags.id = article_tags.tag_id
        WHERE article_tags.article_id = ?
    ''', (article_id,))

    tags = [row['name'] for row in cursor.fetchall()]
    article_dict['tags'] = tags

    conn.close()
    return article_dict

def get_all_articles(limit=50, offset=0):
    """
    List all articles with pagination.

    Args:
        limit: Maximum number of articles to return (default 50)
        offset: Number of articles to skip (default 0)

    Returns:
        List of article dictionaries with preview data
    """
    if limit is None or limit > 100:
        limit = 50
    if limit < 1:
        limit = 1
    if offset is None or offset < 0:
        offset = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, saved_date, word_count, substr(summary, 1, 100) as summary
        FROM articles
        ORDER BY saved_date DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))

    articles = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return articles

def search_articles(query):
    """
    Search articles by query string in title and content.

    Args:
        query: Search term

    Returns:
        List of matching articles with relevance score
    """
    if not query or not query.strip():
        return []

    query = query.strip()
    search_pattern = f'%{query}%'

    conn = get_db_connection()
    cursor = conn.cursor()

    # Search with relevance scoring: title matches get score 2, content matches get score 1
    cursor.execute('''
        SELECT
            id,
            title,
            summary,
            url,
            word_count,
            saved_date,
            CASE
                WHEN title LIKE ? THEN 2
                ELSE 1
            END as relevance_score
        FROM articles
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY relevance_score DESC, saved_date DESC
    ''', (search_pattern, search_pattern, search_pattern))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results

def delete_article(article_id):
    """
    Delete an article from the database.

    Args:
        article_id: Article ID to delete

    Returns:
        Number of rows deleted (0 if not found, 1 if deleted)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
    rows_deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return rows_deleted

def get_stats():
    """
    Get database statistics.

    Returns:
        Dictionary with database statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get article statistics
    cursor.execute('''
        SELECT
            COUNT(*) as total_articles,
            COALESCE(SUM(word_count), 0) as total_words,
            MIN(saved_date) as oldest_article_date,
            MAX(saved_date) as newest_article_date
        FROM articles
    ''')

    stats = dict(cursor.fetchone())
    conn.close()

    # Get database file size
    if os.path.exists(DB_PATH):
        db_size_bytes = os.path.getsize(DB_PATH)
        db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
    else:
        db_size_mb = 0.0

    stats['database_size_mb'] = db_size_mb

    # Handle case where there are no articles
    if stats['total_articles'] == 0:
        stats['oldest_article_date'] = None
        stats['newest_article_date'] = None

    return stats

def add_tag(article_id, tag_name):
    """
    Add a tag to an article.

    Args:
        article_id: Article ID
        tag_name: Tag name to add
    """
    tag_name = tag_name.strip()
    if not tag_name:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert tag if it doesn't exist
        cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))

        # Get tag ID
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        tag_row = cursor.fetchone()
        tag_id = tag_row['id']

        # Link article and tag
        cursor.execute('INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)',
                     (article_id, tag_id))

        conn.commit()
    finally:
        conn.close()

def get_article_tags(article_id):
    """
    Get all tags for an article.

    Args:
        article_id: Article ID

    Returns:
        List of tag name strings
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT tags.name
        FROM tags
        JOIN article_tags ON tags.id = article_tags.tag_id
        WHERE article_tags.article_id = ?
    ''', (article_id,))

    tags = [row['name'] for row in cursor.fetchall()]
    conn.close()

    return tags
