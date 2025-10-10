# Port OneClick Middleware - Examples

This directory contains example configurations for Port.io resources. Use these as templates when creating your own `setup/` directory.

## Directory Structure

```
examples/
├── blueprints/          # Blueprint definition examples
│   └── service-example.json
├── actions/             # Action definition examples
│   └── deploy-example.json
└── widgets/             # Widget/Dashboard examples
    └── services-dashboard-example.json
```

## Getting Started

### 1. Copy Examples to Your Setup Directory

```bash
# From your project root, create setup directories
mkdir -p setup/blueprints setup/actions setup/mappings setup/widgets

# Copy example files (rename to remove -example suffix)
cp examples/blueprints/service-example.json setup/blueprints/service.json
cp examples/actions/deploy-example.json setup/actions/deploy.json
cp examples/widgets/services-dashboard-example.json setup/widgets/dashboard.json
```

### 2. Customize for Your Needs

Edit the JSON files in your `setup/` directory to match your organization's requirements:

- Update identifiers to match your naming conventions
- Modify properties and schemas for your use cases
- Add or remove fields as needed
- Configure actions for your workflows

### 3. Run the Middleware

```bash
# Make sure you have a .env file with your credentials
python main.py
```

## Example Files Explained

### Blueprint Example

The blueprint example (`blueprints/service-example.json`) shows:
- Basic blueprint structure
- Property definitions
- Schema validation
- Required fields

Blueprints are the foundation of your Port.io data model.

### Action Example

The action example (`actions/deploy-example.json`) shows:
- Self-service action configuration
- User input definitions
- Trigger configuration
- Blueprint association

Actions allow users to trigger workflows from the Port.io UI.

### Widget Example

The widget example (`widgets/services-dashboard-example.json`) shows:
- Dashboard widget configuration
- Data visualization setup
- Blueprint connections
- Widget properties

Widgets create visual dashboards in Port.io.

## Resource Types

### Blueprints
Define your data model entities (e.g., Service, Deployment, Team)

**Key fields:**
- `identifier`: Unique ID for the blueprint
- `title`: Display name
- `icon`: Icon name from Port.io's icon library
- `schema`: JSON Schema defining properties

### Actions
Define self-service actions users can trigger

**Key fields:**
- `identifier`: Unique ID for the action
- `title`: Display name
- `trigger`: Configuration for when/how the action runs
- `blueprintIdentifier`: Which blueprint this action applies to

### Mappings
Define how external data maps to Port.io entities

**Key fields:**
- `identifier`: Unique ID for the mapping
- `blueprint`: Target blueprint identifier
- `filter`: Query to select entities
- `entity`: Mapping configuration

### Widgets
Define dashboard visualizations

**Key fields:**
- `identifier`: Unique ID for the widget
- `title`: Display name
- `type`: Widget type (e.g., table, chart)
- `blueprint`: Source blueprint for data

## Best Practices

1. **Use Descriptive Identifiers**: Make identifiers clear and meaningful
2. **Follow Naming Conventions**: Use consistent naming across resources
3. **Document Properties**: Add descriptions to all properties
4. **Start Simple**: Begin with basic configurations, then add complexity
5. **Test Incrementally**: Test each resource type separately using `ACTION` env var

## Testing Individual Resource Types

You can test one resource type at a time:

```bash
# Test only blueprints
ACTION=blueprints python main.py

# Test only actions
ACTION=actions python main.py

# Test only widgets
ACTION=widgets python main.py

# Test all (default)
ACTION=all python main.py
```

## Additional Resources

- [Port.io Documentation](https://docs.getport.io/)
- [Blueprint Schema Reference](https://docs.getport.io/build-your-software-catalog/define-your-data-model/setup-blueprint/)
- [Self-Service Actions Guide](https://docs.getport.io/create-self-service-experiences/)
- [Dashboard Widgets Guide](https://docs.getport.io/customize-pages-dashboards-and-plugins/)

## Need Help?

If you have questions about the example configurations:
1. Check the Port.io documentation
2. Review the `CONFIG.md` file in the package root
3. Open an issue on GitHub

