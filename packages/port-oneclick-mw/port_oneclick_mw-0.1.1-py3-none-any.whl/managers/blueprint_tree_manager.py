from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os

from managers import BasePortManager


class PriorityLevel(Enum):
    """Priority levels for blueprint properties."""
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


@dataclass
class BlueprintNode:
    """Simple blueprint node with properties and dependencies."""
    identifier: str
    properties: Dict[str, Any]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class BlueprintTreeManager(BasePortManager):
    """Simplified blueprint manager with priority-based creation."""
    
    PROPERTY_PRIORITY_MAP = {
        'identifier': PriorityLevel.LEVEL_1,
        'description': PriorityLevel.LEVEL_1,
        'title': PriorityLevel.LEVEL_1,
        'icon': PriorityLevel.LEVEL_1,
        'schema': PriorityLevel.LEVEL_1,
        
        'mirrorProperties': PriorityLevel.LEVEL_2,
        'relations': PriorityLevel.LEVEL_2,

        'calculationProperties': PriorityLevel.LEVEL_3,
        'aggregationProperties': PriorityLevel.LEVEL_3,
        'ownership': PriorityLevel.LEVEL_3,
    }
    
    def __init__(self, client_id: str, client_secret: str, port_host: str = "api.port.io"):
        """Initialize the Blueprint Tree Manager."""
        super().__init__(client_id, client_secret, port_host, "BlueprintTreeManager")
        self.blueprint_nodes: Dict[str, BlueprintNode] = {}
        self.created_blueprints: set = set()
    
    def setup_all_blueprints(self, blueprints_dir: str) -> Dict[str, bool]:
        """
        Setup all blueprints using simple priority-based approach.
        
        Args:
            blueprints_dir: Path to the blueprints directory
            
        Returns:
            Dictionary mapping blueprint identifiers to success status
        """
        results = {}
        
        self._load_blueprints(blueprints_dir)
        
        if not self.blueprint_nodes:
            self.logger.warning("No blueprints found to setup")
            return results
        
        self.logger.info(f"Setting up {len(self.blueprint_nodes)} blueprints...")
        
        # Create blueprints one by one, handling dependencies as we go
        for identifier in self.blueprint_nodes:
            if identifier not in self.created_blueprints:
                success = self._create_blueprint_recursive(identifier)
                results[identifier] = success
                
                if not success:
                    self.logger.error(f"Failed to create blueprint: {identifier}")
                    if not self.should_continue_on_error():
                        break
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"Blueprint setup completed: {successful}/{total} successful")
        
        return results
    
    def _load_blueprints(self, blueprints_dir: str) -> None:
        """Load all blueprint files and analyze dependencies."""
        self.logger.info("Loading blueprints...")
        
        if not os.path.exists(blueprints_dir):
            self.logger.error(f"Blueprints directory does not exist: {blueprints_dir}")
            return
        
        for filename in os.listdir(blueprints_dir):
            # Load .json files but skip .extra.json files
            if filename.endswith('.json') and not filename.endswith('.extra.json'):
                filepath = os.path.join(blueprints_dir, filename)
                blueprint_data = self._load_blueprint_file(filepath)
                
                if blueprint_data:
                    identifier = blueprint_data['identifier']
                    
                    self.blueprint_nodes[identifier] = BlueprintNode(
                        identifier=identifier,
                        properties=blueprint_data,
                        dependencies=[]
                    )

                    self.logger.info(f"Loaded blueprint: {identifier}")
        
        self.logger.info(f"Loaded {len(self.blueprint_nodes)} blueprints: {list(self.blueprint_nodes.keys())}")
        # Second pass: Extract dependencies now that all blueprints are loaded
        for identifier, node in self.blueprint_nodes.items():
            dependencies = self._extract_dependencies(node.properties)
            node.dependencies = dependencies
            self.logger.info(f"Blueprint {identifier} dependencies: {dependencies}")
    
    def _load_blueprint_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load and validate a blueprint file."""
        try:
            with open(filepath, 'r') as f:
                blueprint_data = json.load(f)
            
            if 'identifier' not in blueprint_data:
                self.logger.error(f"Missing identifier in {filepath}")
                return None
                
            return blueprint_data
                
        except Exception as e:
            self.logger.error(f"Error loading blueprint file {filepath}: {str(e)}")
            return None
    
    def _extract_dependencies(self, blueprint_data: Dict[str, Any]) -> List[str]:
        """Extract dependencies from blueprint data."""
        dependencies = set()
        identifier = blueprint_data['identifier']
        
        relations = blueprint_data.get('relations', {})
        for relation_config in relations.values():
            target = relation_config.get('target')
            if target and target != identifier:
                dependencies.add(target)
        
        aggregation_props = blueprint_data.get('aggregationProperties', {})
        for prop_config in aggregation_props.values():
            target = prop_config.get('target')
            if target and target != identifier:
                dependencies.add(target)
        
        return [dep for dep in dependencies if dep in self.blueprint_nodes]
    
    def _create_blueprint_recursive(self, identifier: str) -> bool:
        """
        Create a blueprint, creating its dependencies first if needed.
        
        Args:
            identifier: Blueprint identifier to create
            
        Returns:
            True if successful, False otherwise
        """
        if identifier in self.created_blueprints:
            self.logger.info(f"Blueprint {identifier} already created, skipping")
            return True
        
        if identifier not in self.blueprint_nodes:
            self.logger.error(f"Blueprint {identifier} not found")
            return False
        
        blueprint_node = self.blueprint_nodes[identifier]
        
        for dependency in blueprint_node.dependencies:
            if dependency not in self.created_blueprints:
                self.logger.info(f"Creating dependency {dependency} for {identifier}")
                if not self._create_blueprint_recursive(dependency):
                    self.logger.error(f"Failed to create dependency {dependency} for {identifier}")
                    return False
        
        return self._create_blueprint_with_priority(identifier)
    
    def _create_blueprint_with_priority(self, identifier: str) -> bool:
        """
        Create a blueprint using priority levels.
        
        Args:
            identifier: Blueprint identifier
            
        Returns:
            True if successful, False otherwise
        """
        blueprint_node = self.blueprint_nodes[identifier]
        blueprint_data = blueprint_node.properties
        
        # Check if blueprint already exists
        if self.blueprint_exists(identifier):
            self.logger.info(f"Updating existing blueprint '{identifier}' with all properties...")
            return self._update_blueprint_with_priority(identifier, blueprint_data)
        else:
            self.logger.info(f"Creating new blueprint '{identifier}' with priority levels...")
            return self._create_new_blueprint_with_priority(identifier, blueprint_data)
    
    def _create_new_blueprint_with_priority(self, identifier: str, blueprint_data: Dict[str, Any]) -> bool:
        """Create a new blueprint with priority levels."""
        # Level 1: Core properties
        level_1_props = self._get_properties_by_level(blueprint_data, PriorityLevel.LEVEL_1)
        
        # Create blueprint with Level 1 properties
        success = self._create_blueprint_core(level_1_props)
        if not success:
            return False
        
        # Level 2: Relations
        level_2_props = self._get_properties_by_level(blueprint_data, PriorityLevel.LEVEL_2)
        if level_2_props:
            self.logger.info(f"Adding Level 2 properties to {identifier}")
            success = self._update_blueprint_properties(identifier, level_2_props)
            if not success:
                return False
        
        # Level 3: Computed properties
        level_3_props = self._get_properties_by_level(blueprint_data, PriorityLevel.LEVEL_3)
        if level_3_props:
            self.logger.info(f"Adding Level 3 properties to {identifier}")
            success = self._update_blueprint_properties(identifier, level_3_props)
            if not success:
                return False
        
        self.created_blueprints.add(identifier)
        self.logger.info(f"Successfully created blueprint {identifier}")
        return True
    
    def _update_blueprint_with_priority(self, identifier: str, blueprint_data: Dict[str, Any]) -> bool:
        """Update existing blueprint with all properties."""
        # Get current blueprint
        current_blueprint = self.make_api_request('GET', f'/v1/blueprints/{identifier}')
        if not current_blueprint:
            self.logger.error(f"Failed to fetch current blueprint: {identifier}")
            return False
        
        # Merge all properties
        merged_blueprint = self._deep_merge(current_blueprint, blueprint_data)
        
        # Update blueprint
        response = self.make_api_request('PATCH', f'/v1/blueprints/{identifier}', merged_blueprint)
        
        if response:
            self.created_blueprints.add(identifier)
            self.logger.info(f"Successfully updated blueprint {identifier}")
            return True
        else:
            self.logger.error(f"Failed to update blueprint {identifier}")
            return False
    
    def _get_properties_by_level(self, blueprint_data: Dict[str, Any], level: PriorityLevel) -> Dict[str, Any]:
        """Get properties for a specific priority level."""
        properties = {}
        
        for prop_name, prop_value in blueprint_data.items():
            if self.PROPERTY_PRIORITY_MAP.get(prop_name) == level:
                properties[prop_name] = prop_value
        
        return properties
    
    def _create_blueprint_core(self, blueprint_data: Dict[str, Any]) -> bool:
        """Create the core blueprint."""
        identifier = blueprint_data.get('identifier')
        if not identifier:
            self.logger.error("Blueprint identifier is required")
            return False
        
        self.logger.info(f"Creating blueprint core: {identifier}")
        response = self.make_api_request('POST', '/v1/blueprints', blueprint_data)
        
        if response:
            return True
        else:
            self.logger.error(f"Failed to create blueprint core: {identifier}")
            return False
    
    def _update_blueprint_properties(self, identifier: str, properties: Dict[str, Any]) -> bool:
        """Update blueprint with additional properties."""
        self.logger.info(f"Updating blueprint properties: {identifier}")
        response = self.make_api_request('PATCH', f'/v1/blueprints/{identifier}', properties)
        
        if response:
            return True
        else:
            self.logger.error(f"Failed to update blueprint properties: {identifier}")
            return False
    
    def blueprint_exists(self, identifier: str) -> bool:
        """Check if a blueprint exists."""
        response = self.make_api_request('GET', f'/v1/blueprints/{identifier}', silent_404=True)
        exists = response is not None
        
        if exists:
            self.logger.info(f"Blueprint '{identifier}' found in portal")
        else:
            self.logger.info(f"Blueprint '{identifier}' not found in portal - will create it")
        
        return exists
    
    def _deep_merge(self, base_dict: Dict[str, Any], extra_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base_dict.copy()
        
        for key, value in extra_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result