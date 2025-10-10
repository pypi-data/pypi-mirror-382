
<img width="999" height="562" alt="20250925_2353_Futuristic Knowrithm Logo_simple_compose_01k616ywakf1r91ekdeb54xy9p - Edited" src="https://github.com/user-attachments/assets/ceb44de0-3d1e-435a-b9df-075e7a535ecb" />

# Knowrithm Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI version](https://badge.fury.io/py/knowrithm-py.svg)](https://badge.fury.io/py/knowrithm-py)

**Knowrithm** is a comprehensive Python SDK for building, training, and deploying intelligent AI agents with advanced analytics capabilities. Create custom chatbots and virtual assistants that can be seamlessly integrated into websites, manage leads, process documents, and provide detailed performance analytics.

## 🎯 Project Overview

Knowrithm enables businesses to:
- **Build Custom AI Agents**: Create specialized chatbots tailored to your business needs
- **Process & Analyze Documents**: Upload and analyze various document types for knowledge extraction
- **Manage Leads**: Track and convert leads through intelligent conversation flows  
- **Monitor Performance**: Comprehensive analytics for agents, conversations, and business metrics
- **Scale Operations**: Handle multiple conversations simultaneously with detailed monitoring

## 🚀 Core Features

- **Agent Management**: Create, configure, and deploy AI agents with custom personalities
- **Document Processing**: Advanced document upload, processing, and search capabilities
- **Conversation Handling**: Real-time chat with context management and history tracking
- **Lead Management**: Complete CRM integration with lead tracking and conversion analytics
- **Analytics Dashboard**: Detailed metrics on agent performance, user engagement, and business outcomes
- **Database Connectivity**: Connect and query external databases for dynamic responses
- **Multi-format Export**: Export analytics and conversation data in JSON/CSV formats

## 📦 Installation

### Using pip

```bash
pip install knowrithm-py
```

### From Source

```bash
git clone https://github.com/Knowrithm/knowrithm-py.git
cd knowrithm-py
pip install -e .
```

## 🏃‍♂️ Quick Start

### 1. Initialize the Client

```python
from knowrithm_py.knowrithm.client import KnowrithmClient

# Initialize with API credentials
client = KnowrithmClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://app.knowrithm.org"
)
```

### 2. Create and Configure an AI Agent

```python
from knowrithm_py.services.agent import AgentService

agent_service = AgentService(client)

# Create a new agent
agent = agent_service.create({
    "name": "Customer Support Bot",
    "description": "AI agent for customer support",
    "personality": "friendly and helpful",
    "model_name": "gpt-4",
    "max_response_length": 500
})

print(f"Agent created with ID: {agent['id']}")
```

### 3. Upload and Process Documents

```python
from knowrithm_py.services.document import DocumentService

document_service = DocumentService(client)

# Upload training documents
doc_response = document_service.upload(
    file_path="path/to/faq.pdf",
    agent_id=agent['id']
)

# Check processing status
status = document_service.get_processing_status(doc_response['id'])
print(f"Processing status: {status['status']}")
```

### 4. Start Conversations

```python
from knowrithm_py.services.conversation import ConversationService, MessageService

conversation_service = ConversationService(client)
message_service = MessageService(client)

# Start a conversation
conversation = conversation_service.create(
    agent_id=agent['id'],
    entity_type="USER"
)

# Send a message
response = message_service.send_message(
    conversation_id=conversation['id'],
    content="How can I reset my password?",
    role="user"
)

print(f"Agent response: {response['content']}")
```

## 📊 Analytics and Monitoring

### Dashboard Analytics

```python
from knowrithm_py.services.analytics import AnalyticsService

analytics = AnalyticsService(client)

# Get comprehensive dashboard metrics
dashboard_data = analytics.get_dashboard()
print(f"Total agents: {dashboard_data['agents']['total']}")
print(f"Active conversations: {dashboard_data['conversations']['active']}")
```

### Agent Performance Metrics

```python
# Get detailed agent metrics
agent_metrics = analytics.get_agent_metrics(
    agent_id=agent['id'],
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z"
)

print(f"Total conversations: {agent_metrics['conversation_metrics']['total_conversations']}")
print(f"Average satisfaction: {agent_metrics['quality_metrics']['avg_satisfaction_rating']}")
print(f"Response time: {agent_metrics['performance_metrics']['avg_response_time_seconds']}s")
```

### Conversation Analytics

```python
# Analyze specific conversations
conversation_analytics = analytics.get_conversation_analytics(conversation['id'])

print(f"Message count: {conversation_analytics['message_statistics']['total_messages']}")
print(f"Duration: {conversation_analytics['conversation_flow']['duration_minutes']} minutes")
```

## 📈 Lead Management

### Lead Registration and Tracking

```python
from knowrithm_py.services.lead import LeadService

lead_service = LeadService(client)

# Create a lead
lead = lead_service.create({
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john@example.com",
    "phone": "+1234567890",
    "source": "website_chat"
})

# Update lead status
lead_service.update_status(
    lead_id=lead['id'],
    status="qualified",
    notes="Showed interest in premium features"
)
```

### Lead Analytics

```python
# Get comprehensive lead analytics
lead_analytics = analytics.get_lead_analytics(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z"
)

print(f"Total leads: {lead_analytics['lead_summary']['total_leads']}")
print(f"Conversion rate: {lead_analytics['conversion_funnel']['overall_conversion_rate_percent']}%")
print(f"Top source: {lead_analytics['top_performing_sources'][0]['source']}")
```

## 🗄️ Database Integration

### Connect External Databases

```python
from knowrithm_py.services.database import DatabaseService

db_service = DatabaseService(client)

# Create database connection
db_connection = db_service.create_connection({
    "url": "postgresql://user:password@host:port/db",
    "type": "postgresql",
    "agent_id": "agent-id"
})

# Test connection
test_result = db_service.test_connection(db_connection['id'])
print(f"Connection status: {test_result['status']}")

# Search across connected databases  
search_results = db_service.search(
    query="customer orders last month",
    connection_ids=[db_connection['id']]
)
```

## 📄 Document Management

### Advanced Document Operations

```python
# Search within documents
search_results = document_service.search(
    query="refund policy",
    filters={"agent_id": agent['id']}
)

# List document chunks
chunks = document_service.list_chunks(doc_response['id'])

# Reprocess documents if needed
reprocess_result = document_service.reprocess(doc_response['id'])
```

## 🔧 User and Company Management

### User Operations

```python
from knowrithm_py.services.auth import UserService

user_service = UserService(client)

# Get user profile
profile = user_service.get_profile()
print(f"User: {profile['first_name']} {profile['last_name']}")

# Update preferences
user_service.update_preferences({
    "notifications": True,
    "theme": "dark"
})
```

### Company Statistics

```python
from knowrithm_py.services.company import CompanyService

company_service = CompanyService(client)

# Get company details
company = company_service.get()
print(f"Company: {company['name']}")

# Get company statistics
stats = company_service.get_statistics(days=30)
print(f"Monthly conversations: {stats['conversations']['count']}")
```

## 📊 Data Export and Reporting

### Export Analytics Data

```python
# Export conversation data
export_data = analytics.export_analytics_data({
    "type": "conversations",
    "format": "json", 
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
})

print(f"Exported {export_data['count']} conversations")

# Export leads as CSV
lead_export = analytics.export_analytics_data({
    "type": "leads",
    "format": "csv",
    "start_date": "2024-01-01T00:00:00Z", 
    "end_date": "2024-01-31T23:59:59Z"
})
```

## 🔐 Authentication and Security

### API Key Management

```python
from knowrithm_py.services.auth import AuthService

auth_service = AuthService(client)

# Validate current credentials
validation = auth_service.validate_credentials()
print(f"API key valid: {validation['valid']}")

# Get API key info
key_info = auth_service.get_api_key_info()
print(f"Key permissions: {key_info['permissions']}")

# Create new API key
new_key = auth_service.create_api_key(
    name="Analytics Key",
    permissions={"read": True, "write": False}
)
```

## 🌍 Geographic Data Management

### Address and Location Services

```python
from knowrithm_py.services.address import AddressService

address_service = AddressService(client)

# Create country, state, city hierarchy
country = address_service.create_country("United States", "US")
state = address_service.create_state("California", country['id'])
city = address_service.create_city("San Francisco", state['id'], "94")

# Create address
address = address_service.create_address(
    street_address="123 Main St",
    city_id=city['id'],
    state_id=state['id'],
    country_id=country['id'],
    postal_code="94105"
)
```

## 📝 Complete API Reference

### AgentService
- `create(agent_data)` - Create new AI agent
- `list(company_id)` - List all agents
- `get(agent_id)` - Get agent details
- `update(agent_id, agent_data)` - Update agent configuration
- `delete(agent_id)` - Soft delete agent
- `restore(agent_id)` - Restore deleted agent

### DocumentService  
- `upload(file_path, agent_id)` - Upload document for processing
- `list(agent_id, status)` - List documents with filters
- `search(query, filters)` - Search within documents
- `get_processing_status(document_id)` - Check processing status
- `reprocess(document_id)` - Reprocess document

### ConversationService
- `create(agent_id, entity_type)` - Start new conversation
- `list(agent_id, status)` - List conversations
- `update(conversation_id, data)` - Update conversation metadata
- `end_conversation(conversation_id, rating)` - End conversation

### MessageService
- `send_message(conversation_id, content, role)` - Send message
- `list_messages(conversation_id)` - Get conversation history
- `rate_message(message_id, rating)` - Rate message quality

### AnalyticsService
- `get_dashboard()` - Comprehensive dashboard metrics
- `get_agent_metrics(agent_id, dates)` - Agent performance metrics
- `get_conversation_analytics(conversation_id)` - Conversation analysis
- `get_lead_analytics(dates)` - Lead conversion metrics
- `get_usage_metrics(dates)` - Platform usage statistics
- `export_analytics_data(export_config)` - Export data in various formats

### LeadService
- `create(lead_data)` - Create new lead
- `list(filters)` - List leads with filters
- `update_status(lead_id, status)` - Update lead status
- `add_notes(lead_id, notes)` - Add notes to lead

### DatabaseService
- `create_connection(connection_data)` - Connect external database
- `test_connection(connection_id)` - Test database connection
- `search(query, connection_ids)` - Search across databases
- `get_tables(connection_id)` - List database tables
- `get_semantic_snapshot(connection_id)` - List semantic snapshot
- `get_knowledge_graph(connection_id)` - List knowledge graph
- `get_sample_queries(connection_id)` - List sample queries
- `text_to_sql(connection_id, payload)` - Get suggested SQL query



## 🌐 Website Integration

### HTML/JavaScript Widget

```html
<!-- Add to your website's <head> section -->
<script 
    src="https://app.knowrithm.org/api/widget.js"
    data-agent-id="your-agent-id"
    data-company-id="your-company-id"
    data-api-url="https://app.knowrithm.org/api"
    data-color="#007bff"
    data-position="bottom-right"
    data-welcome="Hi! How can I help you today?"
    data-title="Support Chat"
    async>
</script>
```

## 🛠️ Advanced Configuration

### Custom Response Configuration

```python
# Configure agent response behavior
agent_service.update(agent['id'], {
    "response_config": {
        "max_length": 300,
        "tone": "professional",
        "include_sources": True,
        "fallback_message": "I need more information to help you with that."
    }
})
```

### Performance Monitoring

```python
# Compare agent performance
comparison = analytics.get_agent_performance_comparison(
    agent_id=agent['id'],
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z"
)

print(f"Performance vs company average:")
print(f"Conversations: {comparison['performance_comparison']['conversations']['performance_vs_average_percent']}%")
print(f"Satisfaction: {comparison['performance_comparison']['satisfaction_rating']['performance_vs_average_percent']}%")
```

## 🔍 Error Handling

```python
try:
    response = message_service.send_message(
        conversation_id=conversation['id'],
        content="Hello"
    )
except Exception as e:
    print(f"Error sending message: {e}")
    # Handle error appropriately
```

## 📊 Usage Analytics

```python
# Get platform usage metrics
usage_metrics = analytics.get_usage_metrics(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z"
)

print(f"Total API calls: {usage_metrics['api_usage']['total_api_calls']}")
print(f"Average response time: {usage_metrics['api_usage']['avg_response_time_ms']}ms")
print(f"Error rate: {usage_metrics['api_usage']['error_rate_percent']}%")
```

## 🚀 Production Best Practices

### 1. Environment Configuration
```python
import os
from knowrithm_py.knowrithm.client import KnowrithmClient

client = KnowrithmClient(
    api_key=os.getenv('KNOWRITHM_API_KEY'),
    api_secret=os.getenv('KNOWRITHM_API_SECRET'),
    base_url=os.getenv('KNOWRITHM_BASE_URL', 'https://app.knowrithm.org')
)
```

### 2. Error Handling and Retries
```python
import time
from typing import Dict, Any

def safe_api_call(func, *args, max_retries=3, **kwargs) -> Dict[str, Any]:
    """Safely make API calls with retries"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
    raise Exception("Max retries exceeded")
```

### 3. Monitoring and Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monitor agent performance
def monitor_agent_health(agent_id: str):
    metrics = analytics.get_agent_metrics(agent_id)
    
    # Check response time
    if metrics['performance_metrics']['avg_response_time_seconds'] > 5.0:
        logger.warning(f"Agent {agent_id} has high response time")
    
    # Check satisfaction
    if metrics['quality_metrics']['avg_satisfaction_rating'] < 3.0:
        logger.warning(f"Agent {agent_id} has low satisfaction rating")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.knowrithm.org](https://docs.knowrithm.org)
- **Discord Community**: [https://discord.gg/cHHWfghJrR](https://discord.gg/cHHWfghJrR)
- **Email Support**: support@knowrithm.org
- **GitHub Issues**: [https://github.com/Knowrithm/knowrithm-py/issues](https://github.com/Knowrithm/knowrithm-py/issues)

## 🏆 Real-World Applications

- **E-commerce**: Product recommendation bots with sales analytics
- **SaaS Platforms**: Onboarding assistants with user engagement tracking  
- **Healthcare**: Patient inquiry systems with HIPAA compliance
- **Education**: Course assistants with learning analytics
- **Financial Services**: Support bots with transaction insights
- **Real Estate**: Property inquiry systems with lead qualification

## 🔮 Roadmap

- Voice integration capabilities
- Multi-language support with translation analytics
- Advanced machine learning model fine-tuning
- Real-time collaboration features
- Mobile SDK for iOS and Android
- Advanced webhook integrations
- Custom dashboard builder
- A/B testing framework for agent responses

---

**Made with ❤️ by the Knowrithm Team**

*Build intelligent AI agents that understand your business, engage your customers, and provide actionable insights for growth.*
