"""
SpaceTraders WebUI Flask Application
"""

import asyncio
import os
from threading import Thread
from typing import Dict, Any, Optional
from flask import Flask, render_template, jsonify, request
from .config import Config
from .api_client import SpaceTradersAPIClient

app = Flask(__name__)
app.config.from_object(Config)

# Global API client instance
api_client: Optional[SpaceTradersAPIClient] = None

def run_async(coro):
    """Helper function to run async code in Flask routes."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def initialize_client():
    """Initialize the API client."""
    global api_client
    Config.validate()
    api_client = SpaceTradersAPIClient(Config.SPACETRADERS_TOKEN)

@app.before_first_request
def setup():
    """Setup the application before the first request."""
    initialize_client()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Get basic data for the dashboard
        agent_data = run_async(api_client.get_agent())
        ships_data = run_async(api_client.get_ships(limit=10))
        contracts_data = run_async(api_client.get_contracts(limit=10))
        server_status = run_async(api_client.get_server_status())
        
        return render_template('dashboard.html',
                             agent=agent_data.get('data', {}),
                             ships=ships_data.get('data', []),
                             ships_meta=ships_data.get('meta', {}),
                             contracts=contracts_data.get('data', []),
                             contracts_meta=contracts_data.get('meta', {}),
                             server_status=server_status,
                             config=Config)
    
    except Exception as e:
        return render_template('error.html', 
                             error=str(e),
                             error_type="API Error")

@app.route('/api/agent')
def api_agent():
    """API endpoint to get agent data."""
    try:
        data = run_async(api_client.get_agent())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ships')
def api_ships():
    """API endpoint to get ships data."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        data = run_async(api_client.get_ships(page=page, limit=limit))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ships/<ship_symbol>')
def api_ship_detail(ship_symbol: str):
    """API endpoint to get specific ship data."""
    try:
        data = run_async(api_client.get_ship(ship_symbol))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contracts')
def api_contracts():
    """API endpoint to get contracts data."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        data = run_async(api_client.get_contracts(page=page, limit=limit))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contracts/<contract_id>')
def api_contract_detail(contract_id: str):
    """API endpoint to get specific contract data."""
    try:
        data = run_async(api_client.get_contract(contract_id))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint to get server status."""
    try:
        data = run_async(api_client.get_server_status())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error="Page not found",
                         error_type="404 Not Found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', 
                         error="Internal server error",
                         error_type="500 Internal Server Error"), 500

def create_app() -> Flask:
    """Application factory function."""
    return app

if __name__ == '__main__':
    Config.validate()
    initialize_client()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)