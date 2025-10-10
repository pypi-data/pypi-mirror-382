import os
import sys
from pathlib import Path
from managers.blueprint_manager import PortBlueprintManager
from managers.action_manager import PortActionManager
from managers.mapping_manager import PortMappingManager
from managers.blueprint_tree_manager import BlueprintTreeManager
from managers.widget_manager import PortWidgetManager


def load_env_file(env_file='.env'):
    """Load environment variables from .env file."""
    env_path = Path(env_file)
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


load_env_file()


def get_client_credentials() -> tuple[str, str]:
    """
    Get Port.io client ID and client secret from environment variables or .env file.
    
    Returns:
        Tuple of (client_id, client_secret)
    """
    client_id = os.getenv('PORT_CLIENT_ID')
    client_secret = os.getenv('PORT_CLIENT_SECRET')
    
    return client_id, client_secret


def check_existing_resources(client_id: str, client_secret: str, resource_type: str, resource_dir: str) -> dict:
    """
    Check existing resources in Port environment and compare with local resources.
    
    Args:
        client_id: Port client ID
        client_secret: Port client secret
        resource_type: Type of resource ('blueprints', 'actions', 'mappings', 'widgets')
        resource_dir: Path to local resources directory
        
    Returns:
        Dictionary with comparison results
    """
    print(f"\n🔍 Checking existing {resource_type} in your Port environment...")
    
    # Load local resources
    local_resources = {}
    if Path(resource_dir).exists():
        for filename in os.listdir(resource_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(resource_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        import json
                        resource_data = json.load(f)
                        
                        # Extract identifier based on resource type
                        identifier = None
                        title = None
                        
                        if resource_type == 'blueprints':
                            identifier = resource_data.get('identifier')
                            title = resource_data.get('title', identifier)
                        elif resource_type == 'actions':
                            identifier = resource_data.get('identifier')
                            title = resource_data.get('title', identifier)
                        elif resource_type == 'mappings':
                            identifier = resource_data.get('identifier')
                            title = resource_data.get('title', identifier)
                        elif resource_type == 'widgets':
                            identifier = resource_data.get('identifier')
                            title = resource_data.get('title', identifier)
                        
                        if identifier:
                            local_resources[identifier] = {
                                'filename': filename,
                                'title': title or identifier,
                                'description': resource_data.get('description', 'No description'),
                                'data': resource_data
                            }
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
    
    if not local_resources:
        print(f"❌ No local {resource_type} found!")
        return {'local': {}, 'existing': {}, 'to_create': [], 'to_update': []}
    
    # Check existing resources in Port
    if resource_type == 'blueprints':
        manager = PortBlueprintManager(client_id, client_secret)
        api_endpoint = '/v1/blueprints'
        exists_method = manager.blueprint_exists
    elif resource_type == 'actions':
        manager = PortActionManager(client_id, client_secret)
        api_endpoint = '/v1/actions'
        exists_method = manager.action_exists
    elif resource_type == 'mappings':
        manager = PortMappingManager(client_id, client_secret)
        api_endpoint = '/v1/integration'
        exists_method = manager.integration_exists
    elif resource_type == 'widgets':
        manager = PortWidgetManager(client_id, client_secret)
        api_endpoint = '/v1/pages'
        exists_method = manager.page_exists
    else:
        print(f"❌ Unknown resource type: {resource_type}")
        return {'local': {}, 'existing': {}, 'to_create': [], 'to_update': []}
    
    existing_resources = {}
    to_create = []
    to_update = []
    
    print(f"\n📋 Local {resource_type} found: {len(local_resources)}")
    for identifier, resource_info in local_resources.items():
        print(f"  • {identifier}: {resource_info['title']}")
        
        if exists_method(identifier):
            existing_resources[identifier] = resource_info
            to_update.append(identifier)
            print(f"    ✅ Already exists - will be UPDATED")
        else:
            to_create.append(identifier)
            print(f"    🆕 New {resource_type[:-1]} - will be CREATED")
    
    # Get all existing resources from Port (for reference)
    try:
        all_existing_response = manager.make_api_request('GET', api_endpoint)
        if all_existing_response:
            if resource_type == 'blueprints' and 'blueprints' in all_existing_response:
                all_existing = {bp['identifier']: bp.get('title', bp['identifier']) for bp in all_existing_response['blueprints']}
            elif resource_type == 'actions' and 'actions' in all_existing_response:
                all_existing = {action['identifier']: action.get('title', action['identifier']) for action in all_existing_response['actions']}
            elif resource_type == 'mappings' and isinstance(all_existing_response, list):
                all_existing = {integration['identifier']: integration.get('title', integration['identifier']) for integration in all_existing_response}
            elif resource_type == 'widgets' and 'pages' in all_existing_response:
                all_existing = {page['identifier']: page.get('title', page['identifier']) for page in all_existing_response['pages']}
            else:
                all_existing = {}
            
            other_existing = {k: v for k, v in all_existing.items() if k not in local_resources}
        else:
            other_existing = {}
    except Exception as e:
        print(f"⚠️  Could not fetch all existing {resource_type}: {e}")
        other_existing = {}
    
    return {
        'local': local_resources,
        'existing': existing_resources,
        'other_existing': other_existing,
        'to_create': to_create,
        'to_update': to_update
    }


def get_user_confirmation(comparison_results: dict, resource_type: str) -> bool:
    """
    Get user confirmation before proceeding with resource operations.
    
    Args:
        comparison_results: Results from resource comparison
        resource_type: Type of resource being processed
        
    Returns:
        True if user confirms, False otherwise
    """
    to_create = comparison_results['to_create']
    to_update = comparison_results['to_update']
    other_existing = comparison_results['other_existing']
    
    resource_name = resource_type.title()
    resource_name_singular = resource_type[:-1] if resource_type.endswith('s') else resource_type
    
    print("\n" + "="*60)
    print(f"📊 {resource_name} OPERATION SUMMARY")
    print("="*60)
    
    if to_create:
        print(f"\n🆕 {resource_name.upper()} TO BE CREATED ({len(to_create)}):")
        for identifier in to_create:
            resource_info = comparison_results['local'][identifier]
            print(f"  • {identifier}: {resource_info['title']}")
    
    if to_update:
        print(f"\n🔄 {resource_name.upper()} TO BE UPDATED/MERGED ({len(to_update)}):")
        for identifier in to_update:
            resource_info = comparison_results['local'][identifier]
            print(f"  • {identifier}: {resource_info['title']}")
    
    
    if not to_create and not to_update:
        print(f"\n✅ All {resource_type} are already up to date!")
        return True
    
    print("\n" + "="*60)
    print("⚠️  CONFIRMATION REQUIRED")
    print("="*60)
    
    print(f"\nThis operation will:")
    if to_create:
        print(f"  • CREATE {len(to_create)} new {resource_name_singular}(s)")
    if to_update:
        print(f"  • UPDATE/MERGE {len(to_update)} existing {resource_name_singular}(s)")
    
    print(f"\nThe operation will use the 'merge' strategy")
    print("This means existing resources will be updated with new properties,")
    print("and new properties will be added without removing existing ones.")
    
    while True:
        response = input("\nDo you want to proceed? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def main():
    """Main function to setup blueprints and apply mappings."""
    print("Port One-Click Middleware - Blueprint & Mapping Setup")
    
    client_id, client_secret = get_client_credentials()
    
    blueprints_dir = os.getenv('BLUEPRINTS_DIR', 'setup/blueprints')
    actions_dir = os.getenv('ACTIONS_DIR', 'setup/actions')
    mappings_dir = os.getenv('MAPPINGS_DIR', 'setup/mappings')
    widgets_dir = os.getenv('WIDGETS_DIR', 'setup/widgets')
    
    action = os.getenv('ACTION', 'all').lower()
    
    print(f"\n🔧 Configuration:")
    print(f"  • Processing: {action}")
    print(f"  • Blueprints directory: {blueprints_dir}")
    print(f"  • Actions directory: {actions_dir}")
    print(f"  • Mappings directory: {mappings_dir}")
    print(f"  • Widgets directory: {widgets_dir}")
    
    success = True
    
    if action in ['blueprints', 'all']:
        print(f"\n📋 Setting up blueprints from: {blueprints_dir}")
        
        # Check if blueprints directory exists
        if not Path(blueprints_dir).exists():
            print(f"Error: Blueprints directory '{blueprints_dir}' not found")
            success = False
        else:
            comparison_results = check_existing_resources(client_id, client_secret, 'blueprints', blueprints_dir)
            
            if not comparison_results['local']:
                print("❌ No local blueprints found to process")
                print(f"   Directory contents: {list(Path(blueprints_dir).glob('*.json')) if Path(blueprints_dir).exists() else 'Directory does not exist'}")
                # Don't set success = False for missing resources, just skip
                print("   ⏭️  Skipping blueprint operations")
            else:
                # Get user confirmation before proceeding
                if get_user_confirmation(comparison_results, 'blueprints'):
                    print("\n🚀 Proceeding with blueprint operations...")
                    
                    blueprint_manager = PortBlueprintManager(client_id, client_secret)
                    blueprint_results = blueprint_manager.setup_all_blueprints(blueprints_dir)
                    
                    success_count = 0
                    failed_blueprints = []
                    for identifier, blueprint_success in blueprint_results.items():
                        status = "SUCCESS" if blueprint_success else "FAILED"
                        print(f"{identifier}: {status}")
                        if blueprint_success:
                            success_count += 1
                        else:
                            failed_blueprints.append(identifier)
                    
                    print(f"Blueprint Summary: {success_count}/{len(blueprint_results)} blueprints created successfully")
                    if failed_blueprints:
                        print(f"❌ Failed blueprints: {', '.join(failed_blueprints)}")
                    
                    if success_count != len(blueprint_results):
                        success = False
                else:
                    print("\n❌ Operation cancelled by user")
                    success = False
    
    if action in ['actions', 'all']:
        print(f"\n⚡ Setting up actions from: {actions_dir}")
        
        # Check if actions directory exists
        if not Path(actions_dir).exists():
            print(f"Error: Actions directory '{actions_dir}' not found")
            success = False
        else:
            comparison_results = check_existing_resources(client_id, client_secret, 'actions', actions_dir)
            
            if not comparison_results['local']:
                print("❌ No local actions found to process")
                print(f"   Directory contents: {list(Path(actions_dir).glob('*.json')) if Path(actions_dir).exists() else 'Directory does not exist'}")
                # Don't set success = False for missing resources, just skip
                print("   ⏭️  Skipping action operations")
            else:
                # Get user confirmation before proceeding
                if get_user_confirmation(comparison_results, 'actions'):
                    print("\n🚀 Proceeding with action operations...")
                    
                    action_manager = PortActionManager(client_id, client_secret)
                    action_results = action_manager.setup_all_actions(actions_dir)
                    
                    success_count = 0
                    failed_actions = []
                    for identifier, action_success in action_results.items():
                        status = "SUCCESS" if action_success else "FAILED"
                        print(f"{identifier}: {status}")
                        if action_success:
                            success_count += 1
                        else:
                            failed_actions.append(identifier)
                    
                    print(f"Action Summary: {success_count}/{len(action_results)} actions created successfully")
                    if failed_actions:
                        print(f"❌ Failed actions: {', '.join(failed_actions)}")
                    
                    if success_count != len(action_results):
                        success = False
                else:
                    print("\n❌ Operation cancelled by user")
                    success = False
    
    if action in ['mappings', 'all']:
        print(f"\n🔗 Applying mappings from: {mappings_dir}")
        
        if not Path(mappings_dir).exists():
            print(f"Error: Mappings directory '{mappings_dir}' not found")
            success = False
        else:
            comparison_results = check_existing_resources(client_id, client_secret, 'mappings', mappings_dir)
            
            if not comparison_results['local']:
                print("❌ No local mappings found to process")
                print(f"   Directory contents: {list(Path(mappings_dir).glob('*.json')) if Path(mappings_dir).exists() else 'Directory does not exist'}")
                # Don't set success = False for missing resources, just skip
                print("   ⏭️  Skipping mapping operations")
            else:
                # Get user confirmation before proceeding
                if get_user_confirmation(comparison_results, 'mappings'):
                    print("\n🚀 Proceeding with mapping operations...")
                    
                    mapping_manager = PortMappingManager(client_id, client_secret)
                    mapping_results = mapping_manager.apply_mappings(mappings_dir)
                    
                    success_count = 0
                    failed_mappings = []
                    for identifier, mapping_success in mapping_results.items():
                        status = "SUCCESS" if mapping_success else "FAILED"
                        print(f"{identifier}: {status}")
                        if mapping_success:
                            success_count += 1
                        else:
                            failed_mappings.append(identifier)
                    
                    print(f"Mapping Summary: {success_count}/{len(mapping_results)} mappings applied successfully")
                    if failed_mappings:
                        print(f"❌ Failed mappings: {', '.join(failed_mappings)}")
                    
                    if success_count != len(mapping_results):
                        success = False
                else:
                    print("\n❌ Operation cancelled by user")
                    success = False
    
    if action in ['widgets', 'all']:
        print(f"\n📊 Setting up widgets from: {widgets_dir}")
        
        # Check if widgets directory exists
        if not Path(widgets_dir).exists():
            print(f"Error: Widgets directory '{widgets_dir}' not found")
            success = False
        else:
            comparison_results = check_existing_resources(client_id, client_secret, 'widgets', widgets_dir)
            
            if not comparison_results['local']:
                print("❌ No local widgets found to process")
                print(f"   Directory contents: {list(Path(widgets_dir).glob('*.json')) if Path(widgets_dir).exists() else 'Directory does not exist'}")
                # Don't set success = False for missing resources, just skip
                print("   ⏭️  Skipping widget operations")
            else:
                # Get user confirmation before proceeding
                if get_user_confirmation(comparison_results, 'widgets'):
                    print("\n🚀 Proceeding with widget operations...")
                    
                    widget_manager = PortWidgetManager(client_id, client_secret)
                    widget_results = widget_manager.setup_all_widgets(widgets_dir)
                    
                    success_count = 0
                    failed_widgets = []
                    for identifier, widget_success in widget_results.items():
                        status = "SUCCESS" if widget_success else "FAILED"
                        print(f"{identifier}: {status}")
                        if widget_success:
                            success_count += 1
                        else:
                            failed_widgets.append(identifier)
                    
                    print(f"Widget Summary: {success_count}/{len(widget_results)} widgets created successfully")
                    if failed_widgets:
                        print(f"❌ Failed widgets: {', '.join(failed_widgets)}")
                    
                    if success_count != len(widget_results):
                        success = False
                else:
                    print("\n❌ Operation cancelled by user")
                    success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some operations failed!")
        print("\n🔍 Debug Information:")
        print(f"  • Blueprints directory exists: {Path(blueprints_dir).exists()}")
        print(f"  • Actions directory exists: {Path(actions_dir).exists()}")
        print(f"  • Mappings directory exists: {Path(mappings_dir).exists()}")
        print(f"  • Widgets directory exists: {Path(widgets_dir).exists()}")
        print(f"  • Action filter: {action}")
        print("\n💡 To see detailed error logs, check the console output above for specific failure reasons.")
        sys.exit(1)


if __name__ == '__main__':
    main()
