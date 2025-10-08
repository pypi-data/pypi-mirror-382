# Streamlit Kanban Board Component

A powerful, interactive Kanban board component for Streamlit applications, designed for deal pipeline management, project tracking, and workflow visualization. Features drag-and-drop functionality, role-based permissions, business rules engine, smart search filters, and detailed dialogs with source-based styling.

![Kanban Board Preview](https://via.placeholder.com/800x400?text=Kanban+Board+Component)

## ✨ Features

### Core Functionality
- **Drag & Drop Interface**: Native HTML5 drag-and-drop with smooth animations
- **Interactive Deal Cards**: Click cards to open detailed dialogs with full Streamlit widget support
- **Customizable Stages**: Define pipeline stages with custom names and colors
- **Source-Based Styling**: Automatic card styling based on data source (VV=blue, OF=orange)
- **Role-Based Permissions**: Control drag/drop access and stage visibility by user role

### Advanced Capabilities
- **Permission System**: Granular control over user actions (drag, approve, reject, edit)
- **Business Rules Engine**: Configurable rules for deal transitions and validations
- **Smart Search Filters**: Real-time search with autocomplete for company names and tenant IDs
- **Visual Feedback**: Dynamic column highlighting and lock icons during drag operations
- **Responsive Design**: Mobile-friendly layout with touch support
- **Custom HTML**: Embed custom HTML content in deal cards
- **Session State Integration**: Seamless integration with Streamlit's session state

### User Experience
- **Smooth Animations**: CSS transitions for professional feel
- **Loading States**: Visual feedback during operations
- **Error Prevention**: Permission validation before allowing actions
- **Accessibility**: Keyboard navigation and screen reader support
- **Smart Dialog Management**: Automatic detection of external dialog closure (ESC/click outside)

## 🚀 Installation

### From PyPI
```bash
pip install streamlit-kanban-board-goviceversa
```

### From Test PyPI (for testing)
```bash
pip install -i https://test.pypi.org/simple/ streamlit-kanban-board-goviceversa
```

### From Source
```bash
git clone https://github.com/goviceversa-com/streamlit_kanban_board.git
cd streamlit_kanban_board
pip install -e .
```

## 🎯 Quick Start

### Basic Usage

```python
import streamlit as st
from streamlit_kanban_board_goviceversa import kanban_board

# Define your pipeline stages
stages = [
    {"id": "todo", "name": "To Do", "color": "#3498db"},
    {"id": "in_progress", "name": "In Progress", "color": "#f39c12"},
    {"id": "done", "name": "Done", "color": "#27ae60"}
]

# Define your deals/items
deals = [
    {
        "id": "deal_001",
        "stage": "todo",
        "deal_id": "D-2024-001",
        "company_name": "Acme Corp",
        "product_type": "Term Loan",
        "date": "2024-01-15",
        "underwriter": "John Smith",
        "source": "VV"
    }
]

# Display the kanban board
result = kanban_board(
    stages=stages,
    deals=deals,
    key="my_kanban_board"
)

# Handle interactions
if result:
    if result.get("moved_deal"):
        st.success(f"Deal moved to: {result['moved_deal']['to_stage']}")
    elif result.get("clicked_deal"):
        st.info(f"Deal clicked: {result['clicked_deal']['company_name']}")
```

### Advanced Usage with Business Rules

```python
from config_helpers import DealtPipelineConfigBuilder, create_user_info

# Create configuration with business rules
builder = DealtPipelineConfigBuilder()
config = builder.create_complete_deal_pipeline_config()

# Create user info
user_info = create_user_info(
    role="riskManager",
    email="risk@company.com",
    approval_limits={"VV": {"EUR": 100000}, "OF": {"EUR": 150000}}
)

# Display enhanced kanban board
result = kanban_board(
    stages=config['stages'],
    deals=deals,
    user_info=user_info,
    permission_matrix=config['permission_matrix'],
    business_rules=config['business_rules'],
    key="advanced_kanban"
)
```

## 📋 API Reference

### `kanban_board()`

Creates a Kanban board component with drag-and-drop functionality.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stages` | `list[dict]` | Required | Stage definitions with id, name, and color |
| `deals` | `list[dict]` | Required | Deal/item data with required fields |
| `key` | `str` | `None` | Unique component key for Streamlit |
| `height` | `int` | `600` | Height of the kanban board in pixels |
| `allow_empty_stages` | `bool` | `True` | Whether to show stages with no deals |
| `draggable_stages` | `list[str]` | `None` | Stages user can drag to (None = all) |
| `user_info` | `dict` | `None` | Current user information for permissions |
| `permission_matrix` | `dict` | `None` | Role-based permission matrix |
| `business_rules` | `list` | `None` | Business rules for deal transitions |
| `show_tooltips` | `bool` | `True` | Whether to show tooltips with feedback |

#### Stage Format

Stages are defined as dictionaries with id, name, and optional color:

```python
stages = [
    {"id": "todo", "name": "To Do", "color": "#3498db"},
    {"id": "in_progress", "name": "In Progress", "color": "#f39c12"},
    {"id": "done", "name": "Done", "color": "#27ae60"}
]
```

#### Data Format

Each item must include these required fields:

```python
item = {
    "id": "unique_item_id",           # Required: Unique identifier
    "stage": "current_stage_id",      # Required: Current stage
    "deal_id": "D-2024-001",         # Required: Display ID
    "company_name": "Company Name",   # Required: Company name
    
    # Optional fields
    "product_type": "Term Loan",      # Product type (shown as badge)
    "date": "2024-01-15",            # Relevant date
    "underwriter": "John Smith",      # Underwriter name
    "amount": 1000000,               # Deal amount
    "currency": "EUR",               # Currency
    "risk_rating": "A",              # Risk rating
    "source": "VV",                  # Source (VV=blue, OF=orange)
    "priority": "high",              # Priority level
    "custom_html": "<div>...</div>"   # Custom HTML content
}
```

#### Return Value

Returns a dictionary with interaction data:

```python
{
    "moved_deal": {                   # Info about moved deal (if any)
        "deal_id": "deal_123",
        "from_stage": "todo",
        "to_stage": "in_progress"
    },
    "clicked_deal": {...},            # Info about clicked deal (if any)
    "validation_error": {             # Info about blocked moves (if any)
        "reason": "Amount exceeds approval limit",
        "suggestions": ["Contact risk manager"]
    }
}
```

## 🔐 Role-Based Permissions

### Permission Matrix

Define comprehensive role-based permissions:

```python
permission_matrix = {
    "riskManager": {
        "stages": {
            "risk_review": {
                "view": True,
                "drag_to": True,
                "drag_from": True,
                "approve": True,
                "reject": True,
                "edit": True
            }
        },
        "actions": {
            "create_deal": True,
            "delete_deal": False,
            "edit_deal": True,
            "approve_deal": True,
            "reject_deal": True,
            "request_info": True
        },
        "approval_limits": {
            "VV": {"EUR": 100000},
            "OF": {"EUR": 150000}
        }
    }
}
```

### User Info Format

```python
user_info = {
    "role": "riskManager",
    "email": "risk@company.com",
    "permissions": ["risk_approval", "management_approval"],
    "approval_limits": {"VV": {"EUR": 100000}, "OF": {"EUR": 150000}},
    "department": "Risk Management",
    "is_active": True
}
```

## 🏗️ Business Rules Engine

### Business Rules Format

Define complex business logic for deal transitions:

```python
business_rules = [
    {
        "id": "vv_high_amount",
        "name": "VV High Amount Rule",
        "description": "VV deals >= 100k EUR require risk manager approval",
        "conditions": [
            {"field": "source", "operator": "equals", "value": "VV"},
            {"field": "amount", "operator": "greater_than", "value": 100000}
        ],
        "actions": [
            {"type": "deny", "message": "Requires risk manager approval"}
        ],
        "priority": 100,
        "is_active": True
    }
]
```

### Configuration Helpers

Use the built-in configuration helpers for common scenarios:

```python
from config_helpers import DealtPipelineConfigBuilder

# Create complete deal pipeline configuration
builder = DealtPipelineConfigBuilder()
config = builder.create_complete_deal_pipeline_config()

# Access configuration components
stages = config['stages']
permission_matrix = config['permission_matrix']
business_rules = config['business_rules']
```

## 🔍 Smart Search Filters

The component includes built-in smart search functionality:

- **Real-time search**: Filter deals as you type
- **Autocomplete suggestions**: Dropdown with matching company names and tenant IDs
- **Multi-field search**: Search across company names, deal IDs, and other fields
- **Case-insensitive**: Automatic case normalization
- **Instant filtering**: No need to press enter or click search

### Search Features

- **Company name search**: Type company names to filter deals
- **Tenant ID search**: Search by deal IDs or tenant identifiers
- **Smart suggestions**: Dropdown shows matching options as you type
- **Clear filters**: Easy reset of search criteria
- **Visual feedback**: Clear indication of active filters

## 🎨 Styling and Customization

### Source-Based Card Colors

Cards automatically style based on the `source` field:

- **VV Source**: Light blue background (`#dbeafe`)
- **OF Source**: Light orange background (`#fed7aa`)
- **Default**: Standard white background

### Custom HTML Content

Add rich content to deal cards:

```python
deal = {
    "id": "deal_001",
    "stage": "review",
    "deal_id": "D-2024-001",
    "company_name": "Acme Corp",
    "custom_html": '''
        <div class="priority-high">High Priority</div>
        <div class="status-urgent">Urgent Review</div>
        <div>Additional custom content</div>
    '''
}
```

### CSS Classes

The component includes these CSS classes for styling:

- `.kanban-board` - Main container
- `.kanban-column` - Stage columns
- `.kanban-card` - Individual deal cards
- `.kanban-card[data-source="VV"]` - VV source cards
- `.kanban-card[data-source="OF"]` - OF source cards
- `.drop-disabled` - Disabled drop zones
- `.not-draggable` - Non-draggable cards
- `.search-filter` - Search input styling
- `.suggestions-dropdown` - Autocomplete dropdown

## 🔄 Advanced Usage

### Dialog Integration

Handle card clicks to show detailed dialogs:

```python
# Handle card clicks
if result and result.get("clicked_deal"):
    st.session_state.selected_deal = result["clicked_deal"]
    st.session_state.show_deal_dialog = True

# Show dialog with external closure detection
if st.session_state.get("show_deal_dialog") and st.session_state.get("selected_deal"):
    @st.dialog(f"Deal Details: {st.session_state.selected_deal['deal_id']}")
    def show_deal_details():
        deal = st.session_state.selected_deal
        
        # Display deal information
        st.write(f"**Company:** {deal['company_name']}")
        st.write(f"**Product:** {deal['product_type']}")
        st.write(f"**Amount:** ${deal.get('amount', 0):,.2f}")
        
        # Add interactive elements
        if st.button("Approve Deal"):
            # Handle approval logic
            pass
            
        if st.button("Close"):
            st.session_state.show_deal_dialog = False
            st.rerun()
    
    show_deal_details()
```

### Real-time Updates

Integrate with session state for real-time updates:

```python
# Initialize deals in session state
if "deals" not in st.session_state:
    st.session_state.deals = load_deals_from_database()

# Handle deal movements
if result and result.get("moved_deal"):
    moved_data = result["moved_deal"]
    
    # Update database
    update_deal_stage(moved_data["deal_id"], moved_data["to_stage"])
    
    # Update session state
    for deal in st.session_state.deals:
        if deal["id"] == moved_data["deal_id"]:
            deal["stage"] = moved_data["to_stage"]
            break
```

### Filtering and Search

Combine with Streamlit widgets for advanced filtering:

```python
# Filter controls
col1, col2, col3 = st.columns(3)

with col1:
    selected_stages = st.multiselect("Stages", stage_options)

with col2:
    search_term = st.text_input("Search companies")

with col3:
    selected_sources = st.multiselect("Sources", ["VV", "OF"])

# Apply filters
filtered_deals = [
    deal for deal in st.session_state.deals
    if (not selected_stages or deal["stage"] in selected_stages)
    and (not search_term or search_term.lower() in deal["company_name"].lower())
    and (not selected_sources or deal.get("source") in selected_sources)
]

# Display filtered board
result = kanban_board(
    stages=stages,
    deals=filtered_deals,
    key="filtered_kanban"
)
```

## 📊 Example Use Cases

### Deal Pipeline Management
- Track loan applications through approval stages
- Role-based access for underwriters, risk managers, and administrators
- Source-specific workflows (VV vs OF deals)
- Business rules for amount-based approvals

### Project Management
- Kanban-style project tracking
- Team member assignments and permissions
- Custom project metadata
- Workflow automation

### Sales Pipeline
- Lead qualification and progression
- Sales team collaboration
- Customer interaction tracking
- Revenue forecasting

### Content Workflow
- Editorial content approval process
- Multi-stage review workflows
- Publication pipeline management
- Content lifecycle tracking

## 🧪 Testing

### Quick Test
Run the simple demo to test basic functionality:

```bash
streamlit run simple_demo.py
```

### Advanced Demo
Run the comprehensive sample application with business rules:

```bash
streamlit run sample_advanced_pipeline.py
```

### Basic Demo
Run the intermediate demo:

```bash
streamlit run sample.py
```

## 🔧 Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/goviceversa-com/streamlit_kanban_board.git
cd streamlit_kanban_board

# Install development dependencies
cd streamlit_kanban_board_goviceversa/frontend
npm install

# Build component
npm run build

# Install Python package
cd ../..
pip install -e .
```

### Project Structure

```
streamlit_kanban_board/
├── streamlit_kanban_board_goviceversa/
│   ├── __init__.py              # Python component wrapper
│   └── frontend/
│       ├── src/
│       │   ├── KanbanComponent.tsx  # Main React component
│       │   ├── DealCard.tsx         # Individual card component
│       │   ├── FilterPanel.tsx      # Search and filter panel
│       │   ├── KanbanComponent.css  # Styling
│       │   ├── types.ts             # TypeScript types
│       │   └── index.tsx            # Entry point
│       ├── public/
│       ├── package.json
│       └── build/               # Built component files
├── config_helpers.py           # Business logic and configuration helpers
├── sample_advanced_pipeline.py # Advanced demo with business rules
├── sample.py                   # Intermediate demo
├── simple_demo.py              # Simple demo
├── pyproject.toml             # Python package configuration
├── setup.py                   # Package setup
└── README.md
```

## 🚀 Deployment

### GitHub Actions Workflow

The project includes automated deployment via GitHub Actions:

- **Push to main branch** → Publishes to Test PyPI
- **Push of version tag** (e.g., `v1.1.3`) → Publishes to Production PyPI
- **GitHub release published** → Publishes to Production PyPI

### Version Management

```bash
# Create and push a new version tag
git tag v1.1.3
git push origin v1.1.3
```

This will automatically trigger the GitHub Actions workflow and publish to PyPI.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines
1. Follow TypeScript best practices for React components
2. Maintain backwards compatibility for Python API
3. Add tests for new features
4. Update documentation for API changes
5. Use the configuration helpers for business logic

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 Check the API documentation above
- 🧪 Run the sample applications for examples
- 🐛 Report issues on GitHub
- 💬 Ask questions in discussions

## 🙏 Acknowledgments

- Built with [Streamlit Components](https://docs.streamlit.io/library/components)
- Drag and drop functionality using native HTML5 APIs
- Styled with modern CSS animations and transitions
- Business rules engine for complex workflow validation
