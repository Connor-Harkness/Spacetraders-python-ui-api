# SpaceTraders WebUI

A standalone web interface for the SpaceTraders API, providing a clean dashboard view of your agent, fleet, and contracts data.

## Features

- **Dashboard Overview**: View agent information, fleet status, and contract details in one place
- **Rate Limited**: Respects SpaceTraders API rate limits (2 requests per second)
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-refresh**: Dashboard automatically refreshes every 30 seconds
- **Standalone**: Runs independently from the terminal UI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SpaceTraders API token

### Installation

1. Navigate to the webui directory:
   ```bash
   cd webui
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your SpaceTraders API token:
   ```bash
   export SPACETRADERS_TOKEN="your_token_here"
   ```
   
   Or create a `.env` file:
   ```
   SPACETRADERS_TOKEN=your_token_here
   ```

4. Run the web application:
   ```bash
   python run.py
   ```

5. Open your browser and go to: `http://localhost:5000`

## Configuration

You can customize the WebUI behavior using environment variables:

### Required
- `SPACETRADERS_TOKEN`: Your SpaceTraders API token

### Optional
- `HOST`: Server host (default: `127.0.0.1`)
- `PORT`: Server port (default: `5000`)
- `FLASK_DEBUG`: Enable debug mode (default: `False`)
- `SECRET_KEY`: Flask secret key (default: development key)

Example configuration:
```bash
export SPACETRADERS_TOKEN="your_token_here"
export HOST="0.0.0.0"
export PORT="8080"
export FLASK_DEBUG="True"
```

## Dashboard Features

### Agent Information
- Agent symbol and credits
- Headquarters location
- Starting faction
- Total ship count

### Fleet Overview
- Ship status and location
- Fuel and cargo levels
- Ship roles and capabilities
- Visual progress bars

### Contracts Overview
- Contract status (pending, accepted, fulfilled)
- Payment information
- Delivery requirements and progress
- Deadline tracking

### Server Status
- Game server status
- API version information
- Reset dates and statistics

## API Endpoints

The WebUI also provides JSON API endpoints for integration:

- `GET /api/agent` - Agent information
- `GET /api/ships` - Ship list with pagination
- `GET /api/ships/<symbol>` - Individual ship details
- `GET /api/contracts` - Contract list with pagination
- `GET /api/contracts/<id>` - Individual contract details
- `GET /api/status` - Server status

## Rate Limiting

The WebUI implements proper rate limiting to respect the SpaceTraders API limits:
- Maximum 2 requests per second
- Automatic request queuing
- Transparent handling of rate limit enforcement

## Development

### Project Structure
```
webui/
├── run.py                 # Main entry point
├── app.py                 # Flask application
├── config.py              # Configuration settings
├── api_client.py          # Rate-limited API client
├── rate_limiter.py        # Rate limiting implementation
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   └── error.html        # Error page
└── static/               # Static assets
    ├── css/style.css     # Styles
    └── js/app.js         # JavaScript
```

### Running in Development Mode
```bash
export FLASK_DEBUG=True
python run.py
```

### Adding New Features

1. **New API endpoints**: Add methods to `api_client.py`
2. **New routes**: Add routes to `app.py`
3. **New pages**: Create templates in `templates/`
4. **Styling**: Update `static/css/style.css`
5. **Client-side logic**: Update `static/js/app.js`

## Deployment

### Production Setup

1. Set production environment variables:
   ```bash
   export FLASK_DEBUG=False
   export SECRET_KEY="your-secure-secret-key"
   export HOST="0.0.0.0"
   export PORT="80"
   ```

2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:80 app:app
   ```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t spacetraders-webui .
docker run -p 5000:5000 -e SPACETRADERS_TOKEN="your_token" spacetraders-webui
```

## Troubleshooting

### Common Issues

1. **Token not set**: Ensure `SPACETRADERS_TOKEN` environment variable is set
2. **Port in use**: Change the `PORT` environment variable
3. **API errors**: Check your token validity and network connection
4. **Rate limiting**: The app automatically handles rate limits, but high refresh rates may cause delays

### Debug Mode

Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=True
python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the SpaceTraders Python UI API and follows the same license terms.

## Links

- [SpaceTraders Game](https://spacetraders.io/)
- [SpaceTraders API Documentation](https://docs.spacetraders.io/)
- [Main Project Repository](../README.md)