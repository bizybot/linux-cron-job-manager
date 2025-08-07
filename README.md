
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

### Connecting to the Host Crontab (SSH Mode)

By default, the application manages the cron jobs inside the Docker container. To manage the cron jobs on the host machine, you need to enable SSH mode. This allows the application to securely connect to the host and manage its crontab.

**1. Generate an SSH Key Pair**

If you don't already have an SSH key, create a new one on your host machine:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/cron_manager_id_rsa
```

**2. Authorize the Public Key**

Add the public key to your user's `authorized_keys` file on the host. This allows the application to log in without a password.

```bash
cat ~/.ssh/cron_manager_id_rsa.pub >> ~/.ssh/authorized_keys
```

**3. Configure `docker-compose.yml`**

Update the `docker-compose.yml` file with your host's details:

- **`USE_SSH`**: Set to `true` to enable SSH mode.
- **`CRON_HOST`**: The IP address of your host machine. From within a Docker container, this is typically the IP of the Docker bridge network gateway (e.g., `172.17.0.1`). You can find it by running `ip addr show docker0` on your host.
- **`CRON_USER`**: Your username on the host machine.
- **`CRON_SSH_KEY_PATH`**: The path to the private key inside the container. The default is `/app/ssh/id_rsa`.
- **`HOST_SCRIPTS_DIR`**: The absolute path to the `scripts` directory on your host machine (e.g., `/home/myuser/linux-cron-job-manager/scripts`).
- **Volume Mount**: Make sure the volume mount for the SSH key points to the correct private key file on your host.

Example `docker-compose.yml` configuration:

```yaml
services:
  cron-manager:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./scripts:/app/scripts
      # Mount your SSH private key.
      - ~/.ssh/cron_manager_id_rsa:/app/ssh/id_rsa:ro
    environment:
      - PYTHONPATH=/app
      - USE_SSH=true
      - CRON_HOST=172.17.0.1
      - CRON_USER=your_username
      - CRON_SSH_KEY_PATH=/app/ssh/id_rsa
      - HOST_SCRIPTS_DIR=/home/your_username/linux-cron-job-manager/scripts
```

**4. Start the Application**

Now, build and run the container with the new configuration:

```bash
docker-compose up --build
```

The application will now connect to your host's crontab via SSH.

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
- `GET /api/jobs/{id}` - Get specific job details
- `PUT /api/jobs/{id}` - Update a job
- `DELETE /api/jobs/{id}` - Delete a job

### Job Control
- `POST /api/jobs/{id}/enable` - Enable a job
- `POST /api/jobs/{id}/disable` - Disable a job (cancel next run)

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

