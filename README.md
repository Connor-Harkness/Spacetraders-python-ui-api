# SpaceTraders Terminal UI

A comprehensive terminal user interface for the SpaceTraders Python API client, providing interactive fleet management, contract automation, and resource management capabilities.

## Features

### 🎯 Interactive Dashboard
- Real-time account overview with credits, ships, and contracts
- Quick statistics and recent activity summaries
- Visual progress indicators and status displays

### 🚀 Fleet Management
- Comprehensive ship information display
- Individual ship status monitoring (fuel, cargo, location)
- Ship automation capabilities
- Navigation controls with orbit/dock requirements

### 📋 Contract Management
- Contract overview with progress tracking
- Automated contract fulfillment
- Delivery tracking and deadline monitoring
- Contract acceptance and completion

### 🤖 Automation System
- Ship automation for mining, trading, and transport
- Contract automation with resource procurement
- Smart navigation (orbit before navigate, dock for markets/shipyards)
- Resource management and cargo optimization
- Auto-refuel system for long journeys
- Cooldown handling and error recovery

### 🗺️ Navigation & Pathfinding
- Coordinate-based pathfinding for closest destinations
- Fuel calculation and route optimization
- Market and shipyard location finding
- Mining location discovery for resource procurement

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r spacetraders_client/requirements.txt
   ```

2. Set your SpaceTraders API token:
   ```bash
   export SPACETRADERS_TOKEN="your_token_here"
   ```

3. Run the terminal UI:
   ```bash
   python main.py
   ```

## Usage

### Basic Navigation
- **Tab**: Switch between Dashboard, Ships, Contracts, and Agent views
- **d**: Jump to Dashboard
- **s**: Jump to Ships
- **c**: Jump to Contracts  
- **a**: Jump to Agent
- **r**: Refresh all data
- **q**: Quit application

### Ship Operations
- View detailed ship information including fuel, cargo, and location
- Navigate ships with automatic orbit/dock status management
- Automate ships for specific tasks (mining, trading, transport)
- Monitor ship status and automation progress

### Contract Management
- View all available and active contracts
- Accept contracts with payment information
- Track delivery progress and deadlines
- Automate contract fulfillment with suitable ships

### Automation Features

#### Ship Automation
Ships can be automated for different roles:
- **Mining**: Automatically find and mine resources
- **Trading**: Navigate between markets for profitable trades
- **Transport**: Handle cargo delivery and logistics
- **Contract**: Focus on fulfilling specific contract requirements

#### Contract Automation
Contracts are automatically handled with:
- Ship assignment based on capabilities
- Resource procurement through mining or trading
- Delivery coordination and tracking
- Progress monitoring and error handling

#### Smart Navigation
The system handles navigation requirements:
- Ships must be orbiting before navigating to new locations
- Ships must be docked to access markets and shipyards
- Fuel calculations and automatic refueling
- Closest destination finding using coordinate systems

## Configuration

### Environment Variables
- `SPACETRADERS_TOKEN`: Your API token (required)

### Automation Settings
The automation system can be configured for:
- Maximum ships per contract
- Fuel threshold for refueling
- Cargo management priorities
- Error retry limits

## Architecture

### Core Components

#### Terminal UI (`terminal_ui/`)
- `app.py`: Main application with Textual framework
- `widgets/`: UI components for different views
- `app.tcss`: Styling and theme configuration

#### Automation (`automation/`)
- `manager.py`: Main automation coordinator
- `ship_automation.py`: Individual ship automation
- `contract_automation.py`: Contract fulfillment automation
- `navigation.py`: Smart navigation and pathfinding
- `resource_management.py`: Cargo and fuel management

#### Utilities (`utils/`)
- `coordinates.py`: Coordinate calculations and pathfinding
- `formatting.py`: Display formatting helpers
- `validation.py`: Ship and contract validation

### Key Features Implementation

#### Navigation Requirements
- Ships automatically orbit before navigation
- Ships automatically dock for market/shipyard access
- Fuel requirements calculated before journeys
- Closest destination finding using coordinate math

#### Resource Management
- Cargo space optimization for contract items
- Non-essential item selling when cargo is full
- Item jettisoning when selling fails
- Fuel monitoring and automatic refueling

#### Contract Automation
- Only mining-capable ships for procurement contracts
- Engineered asteroid discovery for resources
- Delivery coordination to contract destinations
- Progress tracking and completion handling

#### Error Handling
- Cooldown detection and waiting
- API error recovery and retry logic
- Automation health monitoring
- Graceful degradation on failures

## API Integration

The terminal UI integrates with the SpaceTraders Python client:

```python
from spacetraders_client import SpaceTradersClient
from terminal_ui import SpaceTradersApp

# Initialize and run
client = SpaceTradersClient(token="your_token")
app = SpaceTradersApp(token="your_token")
app.run()
```

## Development

### Adding New Features
1. Create new widgets in `terminal_ui/widgets/`
2. Add automation logic in `automation/`
3. Update styling in `terminal_ui/app.tcss`
4. Add utility functions in `utils/`

### Testing
Run the application with a test token:
```bash
SPACETRADERS_TOKEN="test_token" python main.py
```

## Troubleshooting

### Common Issues

1. **Token Authentication**: Ensure `SPACETRADERS_TOKEN` is set correctly
2. **API Errors**: Check network connection and API status
3. **Automation Failures**: Monitor error logs and check ship capabilities
4. **Display Issues**: Ensure terminal supports Unicode characters

### Debug Mode
Enable debug logging for troubleshooting:
```bash
SPACETRADERS_DEBUG=1 python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Update documentation
5. Submit a pull request

## License

This project is open source under the MIT License.

## Links

- [SpaceTraders Game](https://spacetraders.io/)
- [SpaceTraders API Documentation](https://docs.spacetraders.io/)
- [Python Client Documentation](./spacetraders_client/README.md)