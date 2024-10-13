# 🌐 WikiFetch 📚  
**Your Personal Wikipedia Content Fetcher**

**WikiFetch** is a powerful, easy-to-use Flask web app that enables you to search and download Wikipedia articles directly to your machine for offline access. It's your personal knowledge repository in one click!

<p align="center">
  <img src="https://img.shields.io/badge/Flask-Backend-informational?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Wikipedia-API-blue?style=for-the-badge&logo=wikipedia" />
  <img src="https://img.shields.io/badge/Python-3.10-green?style=for-the-badge&logo=python" />
</p>

---

### ✨ **Key Features**

- 🔍 **Search Wikipedia Effortlessly:** Search and fetch detailed articles directly from Wikipedia.
- 📥 **Download Articles:** Save full article content as `.txt` files for offline reading.
- 📄 **View Saved Articles:** Keep track of previously downloaded articles in one place.
- 🌐 **Wikipedia API:** Integrated with the Wikipedia API for seamless search experiences.
- 🛠️ **Error Handling:** Handles disambiguation and page errors with friendly responses.

---

### 🚀 **How It Works**
1. 📝 **Search**: Enter a search term in the form to find Wikipedia articles.
2. 🔍 **View**: The app displays a summary, full content, and related pages.
3. 💾 **Download**: Save the article content as a `.txt` file.
4. 🗂️ **Browse**: View all previously downloaded articles.

---

### 🛠️ **Tech Stack**

- **Backend**: [Flask](https://flask.palletsprojects.com/) 
- **API**: [Wikipedia API](https://pypi.org/project/wikipedia/)
- **Languages**: Python, HTML, CSS

---

### 🚀 **Getting Started**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/NikolisSecurity/WikiFetch.git
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Run the App**
   ```bash
   python app.py
4. **Open in Browser**
   ```bash
   Visit: http://127.0.0.1:5000/
   
---
### 📂 **Project Structure**

   ```bash
   WikiFetch/
  ├── app.py                 # Main Flask app
  ├── templates/
  │   └── index.html         # Front-end HTML
  ├── downloaded_data/       # Folder for saved articles
  └── requirements.txt       # Required dependencies
  ```
With WikiFetch, you can easily create your own knowledge base powered by Wikipedia, all in one place! 💡
