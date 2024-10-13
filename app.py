from flask import Flask, render_template, request
import wikipedia
import os
import warnings
import logging

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
        file_name = f"{SAVE_DIR}/{page.title.replace(' ', '_')}.txt"
        # Save the page content to a text file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(f"Title: {page.title}\n\n")
            f.write(page.content)
        return {
            "title": page.title,
            "summary": page.summary,
            "full_content": page.content,
            "file_name": file_name
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
    """Lists all files in the downloaded_data directory."""
    try:
        return os.listdir(SAVE_DIR)
    except FileNotFoundError:
        return []  # Return an empty list if the directory does not exist

@app.errorhandler(500)
def internal_error(error):
    """Handles internal server errors."""
    return f"500 error: {str(error)}", 500

if __name__ == '__main__':
    app.run(debug=True)
