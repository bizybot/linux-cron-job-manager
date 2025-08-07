
# Linux Cron Job Manager

A modern web-based application for managing cron jobs on Linux systems. Built with FastAPI and Docker for easy deployment and management.

## Features

- ✅ **Schedule new cron jobs** - Create and add cron jobs to the system
- ✅ **Capture bash scripts** - Store executable bash scripts for each job execution
- ✅ **Capture cron expressions** - Store and validate cron scheduling expressions
- ✅ **Showcase job list** - Display all scheduled jobs with status and details
- ✅ **Cancel next run** - Temporarily disable jobs to cancel their next execution
- ✅ **Remove cron jobs** - Permanently delete jobs from the system
- ✅ **Modern web interface** - Responsive UI for easy job management
- ✅ **Docker support** - Containerized deployment for consistency
- ✅ **Startup Synchronization** - Automatically syncs jobs between the database and system crontab on startup

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript
- **Container**: Docker
- **Cron Management**: python-crontab

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linux-cron-job-manager
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Jobs Management
- `GET /api/jobs` - List all cron jobs
- `POST /api/jobs` - Create a new cron job
- `GET /api/jobs/{job_id}` - Get specific job details
- `PUT /api/jobs/{job_id}` - Update a job
- `DELETE /api/jobs/{job_id}` - Delete a job

### Job Control
- `POST /api/jobs/{job_id}/enable` - Enable a job
- `POST /api/jobs/{job_id}/disable` - Disable a job (cancel next run)

### System Information
- `GET /api/system/jobs` - Get all jobs from system cron

## Usage Examples

### Creating a Job via API

```bash
curl -X POST "http://localhost:8000/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "backup-database",
    "expression": "0 2 * * *",
    "command": "#!/bin/bash\npg_dump mydb > /backup/db_$(date +%Y%m%d).sql",
    "description": "Daily database backup at 2 AM"
  }'
```

### Cron Expression Examples

| Expression | Description |
|------------|-------------|
| `*/5 * * * *` | Every 5 minutes |
| `0 */2 * * *` | Every 2 hours |
| `0 2 * * *` | Daily at 2 AM |
| `0 9 * * 1` | Every Monday at 9 AM |
| `0 0 1 * *` | First day of every month |

## Project Structure

```
linux-cron-job-manager/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── crud.py             # Database operations
│   ├── cron_service.py     # Cron job management
│   ├── templates/
│   │   └── index.html      # Main web interface
│   └── static/
│       ├── style.css       # Styling
│       └── script.js       # Frontend logic
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
├── test_app.py
└── README.md
```

## Security Considerations

- The application runs as a non-root user in Docker
- Input validation for cron expressions
- Script execution in isolated environment
- XSS protection in the web interface
- SQL injection protection via SQLAlchemy

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database

The application uses SQLite for simplicity. The database file (`cron_manager.db`) is created automatically on first run.

### Logs

Application logs are available in the Docker container:
```bash
docker-compose logs cron-manager
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**
   - Ensure the application has write permissions to the scripts directory
   - Check that the cron service is running on the host system

2. **Jobs not executing**
   - Verify cron daemon is running: `sudo systemctl status cron`
   - Check cron logs: `sudo tail -f /var/log/cron`

3. **Docker container issues**
   - Rebuild the container: `docker-compose build --no-cache`
   - Check container logs: `docker-compose logs`

### Health Checks

The application includes health checks to ensure it's running properly:
```bash
curl http://localhost:8000/api/jobs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

