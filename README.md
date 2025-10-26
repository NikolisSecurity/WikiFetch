# WikiFetch - Wikipedia Article Manager

WikiFetch is a modern web application for searching, saving, and managing Wikipedia articles offline. It features a SQLite database for article storage, a REST API for programmatic access, and Docker support for easy deployment.

## Features

- **Search Wikipedia**: Search and save Wikipedia articles with full content
- **SQLite Database**: Store articles with metadata (word count, dates, tags)
- **Offline API**: REST API endpoints for accessing saved articles without internet
- **Modern UI**: Split dashboard layout with sidebar navigation
- **Migration Tool**: Import existing text files into the database
- **Docker Support**: Containerized deployment with dev and prod configurations
- **Cross-Platform**: Works on Windows, Linux, and macOS

---

## Prerequisites

### All Platforms

- Git (for cloning repository)
- Internet connection (for initial Wikipedia fetches)

### Docker Method (Recommended)

- **Windows/macOS**: Docker Desktop
- **Linux**: Docker Engine and Docker Compose

### Python Method (Alternative)

- Python 3.9 or higher
- pip (Python package manager)

---

## Installation

### Option A: Docker Setup (Recommended)

#### Windows

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker Desktop from Start menu
3. Open PowerShell and verify installation:
   ```powershell
   docker --version
   docker-compose --version
   ```

#### Linux (Ubuntu/Debian)

```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group changes
docker --version
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
docker --version
```

#### macOS

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Open Docker.app from Applications
3. Verify in Terminal:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Clone and Run

```bash
# Clone repository
git clone https://github.com/NikolisSecurity/WikiFetch.git
cd WikiFetch

# Development mode (with hot reload)
docker-compose up --build

# Production mode
docker-compose -f docker-compose.prod.yml up -d --build
```

**Access the application:**
- Development: http://localhost:5000
- Production: http://localhost:8000

---

### Option B: Python Setup (Traditional)

#### Windows

```powershell
# Check Python version (should be 3.9+)
python --version

# Clone repository
git clone https://github.com/NikolisSecurity/WikiFetch.git
cd WikiFetch

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

#### Linux/macOS

```bash
# Check Python version (should be 3.9+)
python3 --version

# Clone repository
git clone https://github.com/NikolisSecurity/WikiFetch.git
cd WikiFetch

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

**Access the application:**
- http://localhost:5000

---

## First Run Setup

### Database Initialization

On first run, the database file `wikifetch.db` will be created automatically in the `data/` directory (or at the path specified by `DATABASE_PATH` environment variable).

### Migrating Existing Text Files

If you have existing `.txt` files in the `downloaded_data/` directory:

1. Navigate to the application in your browser
2. Look for the "Import from Files" section in the sidebar
3. Select files you want to import
4. Click "Import Selected" or "Import All"
5. Optionally check "Delete files after import" to remove text files after migration

### Verify Installation

1. Open browser to http://localhost:5000 (or :8000 for production)
2. You should see the WikiFetch dashboard
3. Try searching for "Python programming"
4. Article should appear and be saved to database
5. Check sidebar for saved articles list

---

## Environment Configuration

Create a `.env` file in the WikiFetch directory for custom configuration:

```env
FLASK_ENV=development
PORT=5000
DATABASE_PATH=./data/wikifetch.db
```

**Docker environment:**
Set environment variables in `docker-compose.yml` or create a `.env` file.

**Available variables:**
- `FLASK_ENV`: `development` or `production`
- `PORT`: Port number (default: 5000 for dev, 8000 for prod)
- `DATABASE_PATH`: Path to SQLite database file

---

## Usage

### Web Interface

1. **Search Wikipedia**: Enter article name in search box and click "Search"
2. **View Saved Articles**: Click any article in the sidebar to view it
3. **Import Files**: Use the "Import from Files" section to migrate text files
4. **Browse Offline**: All saved articles are accessible without internet

### API Usage

The application provides REST API endpoints for programmatic access.

#### List All Articles

```bash
curl http://localhost:5000/api/articles
curl http://localhost:5000/api/articles?limit=20&offset=0
```

#### Get Specific Article

```bash
curl http://localhost:5000/api/articles/1
```

#### Search Articles

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python"}'
```

#### Get Statistics

```bash
curl http://localhost:5000/api/stats
```

#### Delete Article

```bash
curl -X DELETE http://localhost:5000/api/articles/1
```

---

## Common Issues and Troubleshooting

### Port Already in Use

**Symptom**: Error message about port 5000 or 8000 already in use

**Windows**:
```powershell
netstat -ano | findstr :5000
```

**Linux/macOS**:
```bash
lsof -i :5000
```

**Solution**: Either stop the conflicting service or change the `PORT` environment variable.

### Docker Daemon Not Running

**Symptom**: "Cannot connect to Docker daemon"

**Windows/macOS**: Ensure Docker Desktop is started
**Linux**:
```bash
sudo systemctl start docker
```

### Permission Denied (Linux Docker)

**Symptom**: Permission denied when running Docker commands

**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Module Not Found Errors

**Symptom**: "ModuleNotFoundError" when running Python

**Solution**:
1. Ensure virtual environment is activated:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### Database Locked

**Symptom**: "Database is locked" error

**Solution**:
1. Close any other processes accessing the database
2. Restart the application
3. If using Docker, restart the container

### Wikipedia API Rate Limiting

**Symptom**: Errors when searching multiple articles quickly

**Solution**: Wait a few seconds between requests. The Wikipedia API has rate limits.

---

## Updating the Application

### Docker Method

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build
```

### Python Method

```bash
# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python app.py
```

---

## Uninstallation

### Docker Method

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes database)
docker-compose down -v

# Remove images
docker rmi wikifetch_wikifetch
```

### Python Method

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf WikiFetch  # Linux/macOS
# or: rmdir /s WikiFetch  # Windows
```

---

## Development

### Running in Development Mode

**Docker**:
```bash
docker-compose up
```
Hot reload is enabled - code changes will automatically restart the server.

**Python**:
```bash
source venv/bin/activate
FLASK_ENV=development python app.py
```

### Project Structure

```
WikiFetch/
├── app.py                     # Main Flask application
├── database.py                # SQLite database module
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage Docker configuration
├── docker-compose.yml         # Development Docker Compose
├── docker-compose.prod.yml    # Production Docker Compose
├── .dockerignore             # Docker build exclusions
├── templates/
│   └── index.html            # Web UI template
├── data/
│   └── wikifetch.db          # SQLite database (created at runtime)
└── downloaded_data/          # Legacy text files (optional)
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | List all saved articles (pagination supported) |
| GET | `/api/articles/:id` | Get specific article by ID |
| POST | `/api/search` | Search saved articles |
| DELETE | `/api/articles/:id` | Delete article |
| GET | `/api/stats` | Database statistics |
| GET | `/migration-status` | Check migration status |
| POST | `/migrate` | Migrate text files to database |

---

## Production Deployment

### Recommendations

- Use `docker-compose.prod.yml` for production
- Set `FLASK_ENV=production`
- Use gunicorn (included in production Docker setup)
- Place behind reverse proxy (nginx) for SSL/TLS
- Regular database backups
- Monitor disk space for database growth
- Set up log rotation

### Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Backup

**Docker**:
```bash
docker cp wikifetch_wikifetch_1:/app/data/wikifetch.db ./backup/wikifetch_$(date +%Y%m%d).db
```

**Python**:
```bash
cp data/wikifetch.db backup/wikifetch_$(date +%Y%m%d).db
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test locally (both Docker and Python methods)
5. Commit your changes: `git commit -m "Description"`
6. Push to your fork: `git push origin feature-name`
7. Open a Pull Request

---

## License

This project is provided as-is for educational and personal use.

---

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

---

## Changelog

### Version 2.0 (Current)

- Added SQLite database for article storage
- Implemented REST API for offline access
- Modern split dashboard UI
- Migration tool for importing text files
- Docker support with dev and prod configurations
- Cross-platform setup documentation

### Version 1.0

- Basic Wikipedia search
- Text file storage
- Simple web interface

---

**Enjoy using WikiFetch!**
