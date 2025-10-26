# WikiFetch Offline Features Guide

## Overview
WikiFetch now works **completely offline** for all saved articles with enhanced features for managing your local Wikipedia database.

---

## ✅ What's Been Fixed and Added

### 1. **Full Offline Mode Support**
- ✅ **Automatic offline detection**: When you search without internet, WikiFetch automatically searches your local database
- ✅ **Graceful error handling**: No more crashes when Wikipedia is unavailable
- ✅ **Local search results**: Shows matching articles from your saved database
- ✅ **Clear UI indicators**: Orange warning shows when in offline mode

**How it works:**
- Try to search for "Cristiano Ronaldo" without internet
- You'll see: "Offline Mode - Cannot connect to Wikipedia"
- If you have similar articles saved, they'll be displayed as clickable results

---

### 2. **Enhanced Database Schema**
- ✅ Added **Favorites** table for bookmarking articles
- ✅ All CRUD operations work offline
- ✅ Better indexing for faster searches

---

### 3. **New API Endpoints (All Work Offline)**

#### **Favorites Management**
```bash
# Get all favorites
GET /api/favorites

# Add to favorites
POST /api/favorites/1

# Remove from favorites
DELETE /api/favorites/1
```

#### **Tags Management**
```bash
# Get all tags with article counts
GET /api/tags

# Get articles by tag
GET /api/tags/python/articles

# Add tag to article
POST /api/articles/1/tags
Body: {"tag": "programming"}
```

#### **Bulk Operations**
```bash
# Delete multiple articles at once
POST /api/bulk/delete
Body: {"ids": [1, 2, 3]}
```

#### **Export Functionality**
```bash
# Export as TXT
GET /api/export/1?format=txt

# Export as Markdown
GET /api/export/1?format=md

# Export as HTML
GET /api/export/1?format=html
```

---

## 🚀 How to Test Offline Mode

### Test 1: Disconnect and Search
1. **Disconnect from internet** (turn off WiFi/unplug ethernet)
2. Start the application: `python app.py`
3. Search for "Cristiano Ronaldo"
4. **Expected result**:
   - Shows "Offline Mode" warning
   - If "SQL injection" article exists in database, it should appear as a search result
   - You can click it to view the full article

### Test 2: Import Existing Files
1. You have `SQL_injection.txt` in `downloaded_data/`
2. Open WikiFetch in browser
3. Go to "Import from Files" section
4. Check "SQL_injection.txt"
5. Click "Import Selected"
6. **Expected result**: Article imported to database and appears in sidebar

### Test 3: Browse Saved Articles Offline
1. Click any article in the sidebar
2. **Expected result**: Loads instantly from local database, no internet needed

---

## 📊 New Features You Can Use

### 1. **Favorites (Coming in UI)**
```javascript
// Add to favorites via API
fetch('/api/favorites/1', {method: 'POST'})

// Get all favorites
fetch('/api/favorites')
```

### 2. **Tags (Coming in UI)**
```javascript
// Add tag to article
fetch('/api/articles/1/tags', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({tag: 'programming'})
})
```

### 3. **Bulk Delete (Coming in UI)**
```javascript
// Delete multiple articles
fetch('/api/bulk/delete', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ids: [1, 2, 3]})
})
```

### 4. **Export Articles**
```javascript
// Download as file
window.location.href = '/api/export/1?format=md'
```

---

## 🎯 What Works Now

| Feature | Online | Offline | Status |
|---------|--------|---------|--------|
| Search Wikipedia | ✅ | ❌ | Working |
| Search Local DB | ✅ | ✅ | **NEW!** |
| View Saved Articles | ✅ | ✅ | Working |
| Import TXT Files | ✅ | ✅ | Working |
| Delete Articles | ✅ | ✅ | Working |
| Export Articles | ✅ | ✅ | **NEW!** |
| Add/Remove Favorites | ✅ | ✅ | **NEW! (API Only)** |
| Manage Tags | ✅ | ✅ | **NEW! (API Only)** |
| Bulk Operations | ✅ | ✅ | **NEW! (API Only)** |

---

## 🔧 Advanced Usage

### Using the API for Automation

**Example 1: Batch import and tag articles**
```bash
# Import an article
curl http://localhost:5000/migrate -X POST \
  -H "Content-Type: application/json" \
  -d '{"files": ["SQL_injection.txt"], "delete_after": false}'

# Add tags to it (assuming it gets ID 1)
curl http://localhost:5000/api/articles/1/tags -X POST \
  -H "Content-Type: application/json" \
  -d '{"tag": "security"}'
```

**Example 2: Search and export**
```bash
# Search local database
curl http://localhost:5000/api/search -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "SQL"}'

# Export found article
curl http://localhost:5000/api/export/1?format=md -o article.md
```

---

## 📝 Next Steps for Full UI Integration

The backend is **fully functional** for offline operation. To get the complete UI with dark mode, statistics, etc., you can:

1. **Use the API directly** (as shown above) for all features
2. **Build a custom frontend** using the REST API
3. **Request additional UI enhancements** for visual controls

---

## 🐛 Known Limitations

1. **Search from Wikipedia requires internet** - This is expected; offline mode kicks in automatically
2. **Migration UI is basic** - Functional but minimal styling
3. **No dark mode toggle yet** - Coming in future UI update
4. **Favorites/Tags UI pending** - Use API endpoints for now

---

## 📞 Support

If you encounter issues:
1. Check console for JavaScript errors (F12 in browser)
2. Check Flask logs in terminal
3. Verify database file exists: `ls -la data/wikifetch.db`
4. Test API endpoints directly with curl/Postman

---

**Your WikiFetch is now a powerful offline Wikipedia manager!** 🎉
