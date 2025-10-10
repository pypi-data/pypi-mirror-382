# Port One-Click Middleware Configuration

## Simplified Configuration

The Port One-Click Middleware now uses a simplified configuration approach without external configuration files. All operations use safe defaults:

### Default Behavior

- **Strategy**: Always `merge` - Update existing resources, create new ones
- **Error Handling**: Stop on first error for safety
- **User Confirmation**: Always ask for confirmation before making changes

### Supported Resource Types

- **Blueprints** - Entity schemas and configurations
- **Actions** - Automated actions and workflows  
- **Mappings** - Integration configurations
- **Widgets** - Dashboard widgets and pages

### Operation Flow

1. **Check Existing**: The system checks what already exists in your Port environment
2. **Compare**: Compares local files with existing resources
3. **Confirm**: Shows you what will be created/updated and asks for confirmation
4. **Execute**: Proceeds with the operations only after your approval

### Environment Variables

The only configuration needed is through environment variables:

```bash
# Required
PORT_CLIENT_ID=your_client_id
PORT_CLIENT_SECRET=your_client_secret

# Optional - defaults shown
BLUEPRINTS_DIR=setup/blueprints
ACTIONS_DIR=setup/actions  
MAPPINGS_DIR=setup/mappings
WIDGETS_DIR=setup/widgets
ACTION=all  # or specific: blueprints, actions, mappings, widgets
```

### Usage Examples

```bash
# Setup everything (with confirmation)
python main.py

# Setup only blueprints
ACTION=blueprints python main.py

# Setup only widgets  
ACTION=widgets python main.py
```

### Variable Substitution for Actions

Actions support environment variable substitution using `var__` prefixed keys:

```json
{
  "invocationMethod": {
    "type": "GITHUB",
    "var__org": "SET_UP_NEW_ACTION_ORG",
    "var__repo": "SET_UP_NEW_ACTION_REPO",
    "workflow": "create-port-automation.yml"
  }
}
```

With environment variables:
```bash
SET_UP_NEW_ACTION_ORG=eri_org
SET_UP_NEW_ACTION_REPO=eri_repo
```

Results in:
```json
{
  "invocationMethod": {
    "type": "GITHUB",
    "org": "eri_org",
    "repo": "eri_repo",
    "workflow": "create-port-automation.yml"
  }
}
```

**How it works:**
- Keys prefixed with `var__` are treated as variable substitutions
- The value of the `var__` key should be the environment variable name
- The `var__` prefix is removed from the final key name
- If the environment variable is not found, a warning is logged and the original key/value is preserved

### Safety Features

- **Always asks for confirmation** before making changes
- **Shows exactly what will be created/updated** before proceeding
- **Stops on first error** to prevent partial state
- **Uses merge strategy** to preserve existing configurations
- **Variable substitution** for actions with environment variables
