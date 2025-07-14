"""
Automation manager for coordinating ship and contract automation.
"""

import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from spacetraders_client.models import Ship, Contract, Agent

from .ship_automation import ShipAutomation
from .contract_automation import ContractAutomation
from .navigation import NavigationHelper
from .resource_management import ResourceManager


class AutomationManager:
    """Main automation manager for coordinating all automation activities."""
    
    def __init__(self, client: SpaceTradersClient):
        self.client = client
        self.navigation_helper = NavigationHelper(client)
        self.resource_manager = ResourceManager(client)
        
        # Automation instances
        self.ship_automations: Dict[str, ShipAutomation] = {}
        self.contract_automations: Dict[str, ContractAutomation] = {}
        
        # State tracking
        self.active_ships: Set[str] = set()
        self.active_contracts: Set[str] = set()
        self.last_update = datetime.now()
        
        # Running tasks
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
    
    async def start(self):
        """Start the automation manager."""
        self.is_running = True
        
        # Start main monitoring loop
        self.running_tasks["monitor"] = asyncio.create_task(self._monitor_loop())
        
        print("🤖 Automation Manager started")
    
    async def stop(self):
        """Stop the automation manager."""
        self.is_running = False
        
        # Cancel all running tasks
        for task_name, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.running_tasks.clear()
        print("🛑 Automation Manager stopped")
    
    async def automate_ship(self, ship_symbol: str, automation_type: str = "general") -> bool:
        """Start automating a ship."""
        try:
            # Get ship data
            ship = await self.client.get_ship(ship_symbol)
            
            # Create ship automation
            ship_automation = ShipAutomation(
                client=self.client,
                ship=ship,
                navigation_helper=self.navigation_helper,
                resource_manager=self.resource_manager
            )
            
            self.ship_automations[ship_symbol] = ship_automation
            self.active_ships.add(ship_symbol)
            
            # Start automation task
            task_name = f"ship_{ship_symbol}"
            self.running_tasks[task_name] = asyncio.create_task(
                ship_automation.run_automation(automation_type)
            )
            
            print(f"🚀 Started automation for ship {ship_symbol}")
            return True
            
        except SpaceTradersError as e:
            print(f"❌ Failed to automate ship {ship_symbol}: {e.message}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error automating ship {ship_symbol}: {e}")
            return False
    
    async def stop_ship_automation(self, ship_symbol: str) -> bool:
        """Stop automating a ship."""
        try:
            task_name = f"ship_{ship_symbol}"
            if task_name in self.running_tasks:
                task = self.running_tasks[task_name]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.running_tasks[task_name]
            
            if ship_symbol in self.ship_automations:
                del self.ship_automations[ship_symbol]
            
            self.active_ships.discard(ship_symbol)
            print(f"🛑 Stopped automation for ship {ship_symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping ship automation {ship_symbol}: {e}")
            return False
    
    async def automate_contract(self, contract_id: str) -> bool:
        """Start automating a contract."""
        try:
            # Get contract data
            contract = await self.client.get_contract(contract_id)
            
            # Create contract automation
            contract_automation = ContractAutomation(
                client=self.client,
                contract=contract,
                navigation_helper=self.navigation_helper,
                resource_manager=self.resource_manager
            )
            
            self.contract_automations[contract_id] = contract_automation
            self.active_contracts.add(contract_id)
            
            # Start automation task
            task_name = f"contract_{contract_id}"
            self.running_tasks[task_name] = asyncio.create_task(
                contract_automation.run_automation()
            )
            
            print(f"📋 Started automation for contract {contract_id}")
            return True
            
        except SpaceTradersError as e:
            print(f"❌ Failed to automate contract {contract_id}: {e.message}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error automating contract {contract_id}: {e}")
            return False
    
    async def stop_contract_automation(self, contract_id: str) -> bool:
        """Stop automating a contract."""
        try:
            task_name = f"contract_{contract_id}"
            if task_name in self.running_tasks:
                task = self.running_tasks[task_name]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.running_tasks[task_name]
            
            if contract_id in self.contract_automations:
                del self.contract_automations[contract_id]
            
            self.active_contracts.discard(contract_id)
            print(f"🛑 Stopped automation for contract {contract_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping contract automation {contract_id}: {e}")
            return False
    
    async def get_automation_status(self) -> Dict:
        """Get current automation status."""
        return {
            "active_ships": len(self.active_ships),
            "active_contracts": len(self.active_contracts),
            "running_tasks": len(self.running_tasks),
            "last_update": self.last_update,
            "is_running": self.is_running,
            "ship_details": {
                ship_symbol: {
                    "status": automation.current_status,
                    "last_action": automation.last_action,
                    "errors": automation.error_count
                }
                for ship_symbol, automation in self.ship_automations.items()
            },
            "contract_details": {
                contract_id: {
                    "status": automation.current_status,
                    "progress": automation.progress,
                    "errors": automation.error_count
                }
                for contract_id, automation in self.contract_automations.items()
            }
        }
    
    async def _monitor_loop(self):
        """Main monitoring loop for automation management."""
        while self.is_running:
            try:
                # Update last update time
                self.last_update = datetime.now()
                
                # Check for completed tasks
                await self._cleanup_completed_tasks()
                
                # Monitor ship automations
                await self._monitor_ship_automations()
                
                # Monitor contract automations
                await self._monitor_contract_automations()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in automation monitor loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed automation tasks."""
        completed_tasks = []
        
        for task_name, task in self.running_tasks.items():
            if task.done():
                completed_tasks.append(task_name)
                
                # Handle task completion
                if task_name.startswith("ship_"):
                    ship_symbol = task_name[5:]  # Remove "ship_" prefix
                    self.active_ships.discard(ship_symbol)
                    if ship_symbol in self.ship_automations:
                        del self.ship_automations[ship_symbol]
                
                elif task_name.startswith("contract_"):
                    contract_id = task_name[9:]  # Remove "contract_" prefix
                    self.active_contracts.discard(contract_id)
                    if contract_id in self.contract_automations:
                        del self.contract_automations[contract_id]
        
        # Remove completed tasks
        for task_name in completed_tasks:
            del self.running_tasks[task_name]
    
    async def _monitor_ship_automations(self):
        """Monitor ship automation health."""
        for ship_symbol, automation in list(self.ship_automations.items()):
            try:
                # Check if ship automation is healthy
                if automation.error_count > 5:
                    print(f"⚠️  Ship {ship_symbol} has too many errors, restarting automation")
                    await self.stop_ship_automation(ship_symbol)
                    await asyncio.sleep(5)  # Brief pause before restart
                    await self.automate_ship(ship_symbol)
                    
            except Exception as e:
                print(f"❌ Error monitoring ship {ship_symbol}: {e}")
    
    async def _monitor_contract_automations(self):
        """Monitor contract automation health."""
        for contract_id, automation in list(self.contract_automations.items()):
            try:
                # Check if contract automation is healthy
                if automation.error_count > 5:
                    print(f"⚠️  Contract {contract_id} has too many errors, restarting automation")
                    await self.stop_contract_automation(contract_id)
                    await asyncio.sleep(5)  # Brief pause before restart
                    await self.automate_contract(contract_id)
                    
            except Exception as e:
                print(f"❌ Error monitoring contract {contract_id}: {e}")