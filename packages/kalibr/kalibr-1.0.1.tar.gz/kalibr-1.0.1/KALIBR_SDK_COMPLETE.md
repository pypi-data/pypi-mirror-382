# Kalibr SDK - Complete Multi-Model AI Integration Framework 🚀

## Overview

**Kalibr** is an enhanced SDK that enables developers to build AI-integrated applications that automatically work with **all major AI models** from a single codebase. Write once, deploy anywhere, connect to any AI model.

### The Problem Kalibr Solves

**Before Kalibr:**
```
Developer needs AI integration →
├── Build GPT Action (OpenAPI + auth + deployment)
├── Build Claude MCP (WebSocket + JSON-RPC + hosting)  
├── Build Gemini Extension (Google format + infrastructure)
├── Build Copilot Plugin (Microsoft schema + servers)
└── Build Future Model X (Unknown requirements + research)
= Months of work, 5+ codebases, complex infrastructure
```

**With Kalibr SDK:**
```python
# Write once
from kalibr import KalibrApp

app = KalibrApp("My Business API")

@app.action("analyze_data", "Analyze business data")
def analyze(data: str) -> dict:
    return {"analysis": my_business_logic(data)}

# Deploy once
kalibr deploy my_app.py --platform fly --name my-api

# All AI models supported automatically:
✅ GPT Actions: https://my-api.fly.dev/openapi.json
✅ Claude MCP: https://my-api.fly.dev/mcp.json
✅ Gemini: https://my-api.fly.dev/schemas/gemini
✅ Copilot: https://my-api.fly.dev/schemas/copilot
```

## 🎯 Key Features

### ✅ 1. Multi-Model AI Integration
- **GPT Actions** - Automatic OpenAPI 3.0 schema generation
- **Claude MCP** - WebSocket-compatible JSON-RPC manifests
- **Gemini Extensions** - Google's extension format
- **Microsoft Copilot** - Plugin schema generation
- **Future Models** - Extensible architecture for new AI platforms

### ✅ 2. Enhanced App-Level Capabilities
- **File Upload Handling** - Multi-format validation and processing
- **Session Management** - Stateful interactions across requests
- **Streaming Responses** - Real-time data streaming
- **Complex Workflows** - Multi-step processing with state tracking
- **Advanced Data Types** - Files, images, tables, custom objects

### ✅ 3. Built-in Authentication System
- **JWT Token Management** - Secure authentication helpers
- **User Management** - Built-in user stores (in-memory, database)
- **Protected Routes** - Easy auth decorators and middleware
- **Multiple Backends** - MongoDB, PostgreSQL, or custom implementations

### ✅ 4. Deployment Automation
- **Fly.io Integration** - One-command deployment to Fly.io
- **AWS Lambda** - Serverless deployment support
- **Docker Generation** - Automatic Dockerfile creation
- **Environment Management** - Configuration and secrets handling

### ✅ 5. Built-in Analytics & Logging
- **Automatic Tracking** - Every API call logged automatically
- **Performance Metrics** - Response times, success rates, error tracking
- **Custom Events** - Track business-specific analytics
- **Multiple Storage** - File, memory, or database backends

## 🚀 Quick Start

### Installation
```bash
pip install kalibr
```

### Create Your First App
```bash
# Generate a starter app
kalibr init --template basic --name "My API"

# Or create enhanced app with all features
kalibr init --template enhanced --name "My Enhanced API"
```

### Basic Example
```python
from kalibr import Kalibr

app = Kalibr(title="My Business API")

@app.action("hello", "Greet someone")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}

@app.action("analyze_sentiment", "Analyze text sentiment")
def analyze_sentiment(text: str):
    # Your business logic here
    sentiment = "positive" if "good" in text.lower() else "negative"
    return {"text": text, "sentiment": sentiment, "confidence": 0.95}
```

### Enhanced Example with All Features
```python
from kalibr import KalibrApp
from kalibr.types import FileUpload, Session, StreamingResponse
from kalibr.auth_helpers import kalibr_auth, KalibrAuth, InMemoryUserStore
from kalibr.analytics import kalibr_analytics

@kalibr_auth("your-secret-key")
@kalibr_analytics(storage="file", auto_track=True)
class MyEnhancedApp(KalibrApp):
    def __init__(self):
        super().__init__(title="Enhanced Business API")
        
        # Setup authentication
        self.auth = KalibrAuth("your-secret-key")
        self.user_store = InMemoryUserStore()

app = MyEnhancedApp()

# File upload handler
@app.file_handler("analyze_document", [".txt", ".pdf", ".docx"])
async def analyze_document(file: FileUpload):
    content = file.content.decode('utf-8')
    
    # Your document analysis logic
    word_count = len(content.split())
    
    return {
        "filename": file.filename,
        "word_count": word_count,
        "analysis": "Document processed successfully",
        "upload_id": file.upload_id
    }

# Session-aware action
@app.session_action("save_analysis", "Save analysis to user session")
async def save_analysis(session: Session, analysis_result: dict):
    session.set("last_analysis", analysis_result)
    session.set("analysis_count", session.get("analysis_count", 0) + 1)
    
    return {
        "saved": True,
        "session_id": session.session_id,
        "total_analyses": session.get("analysis_count")
    }

# Streaming action
@app.stream_action("process_large_dataset", "Process large dataset with progress")
async def process_large_dataset(dataset_size: int = 100):
    for i in range(dataset_size):
        # Simulate processing
        processed_item = {"item_id": i, "processed_at": "2024-01-01T00:00:00Z"}
        
        yield {
            "progress": (i + 1) / dataset_size * 100,
            "item": processed_item,
            "remaining": dataset_size - i - 1
        }
        
        await asyncio.sleep(0.1)  # Simulate processing time

# Protected action requiring authentication
@app.action("get_private_data", "Get user's private data")
async def get_private_data(current_user = Depends(app.auth.create_auth_dependency(app.user_store.get_user))):
    return {
        "message": f"Private data for {current_user.username}",
        "user_id": current_user.id,
        "account_type": "premium"
    }
```

## 📦 Development Workflow

### 1. Local Development
```bash
# Test your app locally
kalibr serve my_app.py

# Available at:
# • http://localhost:8000/docs (Swagger UI)
# • http://localhost:8000/mcp.json (Claude MCP)
# • http://localhost:8000/openapi.json (GPT Actions)
# • http://localhost:8000/schemas/gemini (Gemini)
# • http://localhost:8000/schemas/copilot (Copilot)
```

### 2. Platform Setup
```bash
# Setup deployment platform
kalibr setup fly
kalibr setup aws

# Or list available platforms
kalibr list-platforms
```

### 3. Deployment
```bash
# Deploy to Fly.io
kalibr deploy my_app.py --platform fly --name my-api

# Deploy to AWS Lambda
kalibr deploy my_app.py --platform aws-lambda --name my-api

# Deploy with environment variables
kalibr deploy my_app.py --platform fly --name my-api --env-file .env
```

### 4. Monitoring
```bash
# Check deployment status
kalibr status https://my-api.fly.dev

# Test all endpoints
kalibr test --url https://my-api.fly.dev
```

## 🤖 AI Model Integration

Once deployed, your Kalibr app automatically provides schemas for all major AI models:

### GPT Actions Integration
```json
GET https://your-app.fly.dev/openapi.json

{
  "openapi": "3.0.0",
  "info": {"title": "My API", "version": "1.0.0"},
  "servers": [{"url": "https://your-app.fly.dev"}],
  "paths": {
    "/proxy/analyze_sentiment": {
      "post": {
        "operationId": "analyze_sentiment",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
              }
            }
          }
        }
      }
    }
  }
}
```

### Claude MCP Integration
```json
GET https://your-app.fly.dev/mcp.json

{
  "mcp": "1.0",
  "name": "my-api",
  "tools": [{
    "name": "analyze_sentiment",
    "description": "Analyze text sentiment",
    "input_schema": {
      "type": "object",
      "properties": {"text": {"type": "string"}},
      "required": ["text"]
    },
    "server": {"url": "https://your-app.fly.dev/proxy/analyze_sentiment"}
  }]
}
```

### Usage in AI Models
**GPT Custom Actions:**
1. Copy OpenAPI schema from `/openapi.json`
2. Create new GPT Action
3. Paste schema and set base URL

**Claude Desktop MCP:**
```json
{
  "mcp": {
    "servers": {
      "my-business-api": {
        "command": "curl",
        "args": ["https://your-app.fly.dev/mcp.json"]
      }
    }
  }
}
```

## 🔒 Authentication & Security

### Built-in Authentication
```python
from kalibr.auth_helpers import KalibrAuth, InMemoryUserStore

# Initialize authentication
auth = KalibrAuth(secret_key="your-secret-key")
user_store = InMemoryUserStore()

# Create auth dependency
get_current_user = auth.create_auth_dependency(user_store.get_user)

@app.action("protected_action", "Requires authentication")
async def protected_action(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

### User Management
```python
# Register users
@app.action("register", "Register new user")
async def register(username: str, email: str, password: str):
    user = user_store.create_user(username, email, password)
    token = auth.create_access_token({"sub": user.id})
    return {"user": user, "token": token}

# Login
@app.action("login", "User login")
async def login(email: str, password: str):
    user = user_store.get_user_by_email(email)
    if user and user_store.verify_password(user.id, password):
        token = auth.create_access_token({"sub": user.id})
        return {"token": token}
    raise HTTPException(401, "Invalid credentials")
```

### Database Integration
```python
from kalibr.auth_helpers import MongoUserStore

# Use MongoDB for user storage
user_store = MongoUserStore(database)

# Or implement your own
class CustomUserStore(DatabaseUserStore):
    async def create_user(self, username, email, hashed_password):
        # Your implementation
        pass
```

## 📊 Analytics & Monitoring

### Automatic Analytics
```python
from kalibr.analytics import kalibr_analytics

@kalibr_analytics(storage="file", auto_track=True)
class MyApp(KalibrApp):
    pass

app = MyApp()

# All actions automatically tracked for:
# • Response times
# • Success/error rates  
# • Usage patterns
# • User analytics
```

### Custom Analytics
```python
@app.action("business_action", "Track custom business metrics")
def business_action(data: str):
    # Your business logic
    result = process_data(data)
    
    # Record custom analytics
    app.record_custom_event("business_process", 
                           data_size=len(data),
                           result_type=result.get("type"),
                           processing_time=result.get("duration"))
    
    return result

# Get analytics
@app.action("get_analytics", "View app analytics")
def get_analytics():
    return app.get_analytics()
```

### Analytics Backends
```python
# File storage (default)
@kalibr_analytics(storage="file")

# Memory storage (development)
@kalibr_analytics(storage="memory")

# Database storage
from kalibr.analytics import MongoAnalyticsBackend
analytics_backend = MongoAnalyticsBackend(database)
```

## 🏗️ Advanced Features

### Complex Workflows
```python
@app.workflow("data_pipeline", "Multi-step data processing pipeline")
async def data_pipeline(input_data: dict, workflow_state):
    # Step 1: Validation
    workflow_state.step = "validation"
    if not validate_input(input_data):
        workflow_state.status = "error"
        return {"error": "Invalid input"}
    
    # Step 2: Processing
    workflow_state.step = "processing"
    processed = await process_data_async(input_data)
    workflow_state.data["processed_records"] = len(processed)
    
    # Step 3: Output
    workflow_state.step = "output_generation"
    result = generate_output(processed)
    
    workflow_state.step = "completed"
    workflow_state.status = "success"
    
    return {
        "workflow_id": workflow_state.workflow_id,
        "result": result,
        "records_processed": len(processed)
    }
```

### File Processing
```python
@app.file_handler("process_csv", [".csv", ".xlsx"])
async def process_csv(file: FileUpload):
    import pandas as pd
    import io
    
    # Read file content
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(file.content.decode('utf-8')))
    else:
        df = pd.read_excel(io.BytesIO(file.content))
    
    # Process data
    summary = {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": df.dtypes.to_dict(),
        "summary_stats": df.describe().to_dict()
    }
    
    return summary
```

### Real-time Streaming
```python
@app.stream_action("live_data_feed", "Stream live data updates")
async def live_data_feed(source: str = "default"):
    import asyncio
    
    for i in range(100):
        # Simulate real-time data
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "value": random.random() * 100,
            "sequence": i
        }
        
        yield data_point
        await asyncio.sleep(0.5)
```

## 🚀 Deployment Options

### Fly.io (Recommended)
```bash
# Setup
kalibr setup fly

# Deploy
kalibr deploy my_app.py --platform fly --name my-api

# Results in:
# ✅ https://my-api.fly.dev/openapi.json
# ✅ https://my-api.fly.dev/mcp.json
# ✅ Automatic SSL, global CDN, scaling
```

### AWS Lambda
```bash
# Setup
kalibr setup aws

# Deploy
kalibr deploy my_app.py --platform aws-lambda --name my-api

# Results in:
# ✅ https://my-api.lambda-url.us-east-1.on.aws/
# ✅ Serverless, pay-per-use, automatic scaling
```

### Docker (Self-hosted)
```python
# Kalibr automatically generates Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install kalibr
COPY my_app.py .
EXPOSE 8000
CMD ["kalibr", "serve", "my_app.py", "--host", "0.0.0.0"]
```

## 📚 CLI Reference

```bash
# App Creation
kalibr init                          # Basic app
kalibr init --template enhanced      # Enhanced app with all features
kalibr init --template auth          # App with authentication
kalibr init --template analytics     # App with built-in analytics

# Development
kalibr serve my_app.py              # Run locally
kalibr test --url http://localhost:8000  # Test endpoints

# Deployment
kalibr setup fly                    # Setup Fly.io
kalibr setup aws                    # Setup AWS
kalibr list-platforms               # Show available platforms
kalibr deploy my_app.py --platform fly --name my-api
kalibr status https://my-api.fly.dev
kalibr version                      # Show SDK version
```

## 🎯 Use Cases

### Business API Integration
```python
# Customer service chatbot backend
@app.action("get_customer_info", "Get customer information")
def get_customer_info(customer_id: str):
    return database.get_customer(customer_id)

@app.action("create_support_ticket", "Create support ticket")
def create_support_ticket(customer_id: str, issue: str, priority: str = "medium"):
    return support_system.create_ticket(customer_id, issue, priority)
```

### Data Analysis Service
```python
# Data analysis API for AI models
@app.action("analyze_sales_data", "Analyze sales performance")
def analyze_sales_data(start_date: str, end_date: str, region: str = "all"):
    data = get_sales_data(start_date, end_date, region)
    return {
        "revenue": calculate_revenue(data),
        "growth": calculate_growth(data),
        "trends": identify_trends(data)
    }
```

### Document Processing
```python
# Document processing service
@app.file_handler("analyze_contract", [".pdf", ".docx"])
async def analyze_contract(file: FileUpload):
    text = extract_text(file.content)
    return {
        "key_terms": extract_terms(text),
        "risks": identify_risks(text),
        "summary": generate_summary(text)
    }
```

### Workflow Automation
```python
# Multi-step business process
@app.workflow("order_processing", "Complete order processing workflow")
async def order_processing(order_data: dict, workflow_state):
    # Validate → Payment → Inventory → Shipping → Notification
    # Full workflow with state tracking and error handling
    pass
```

## 🔮 Roadmap

### Current Version (2.0.0)
- ✅ Multi-model AI integration (GPT, Claude, Gemini, Copilot)
- ✅ Enhanced app-level framework
- ✅ Built-in authentication system
- ✅ Deployment automation (Fly.io, AWS)
- ✅ Analytics and logging
- ✅ Comprehensive CLI tools

### Coming Soon
- 🔄 **More AI Models**: Anthropic Computer Use, Mistral, Local models
- 🔄 **Advanced Auth**: OAuth, SSO, API key management
- 🔄 **More Platforms**: Google Cloud Run, Azure Functions, Railway
- 🔄 **Enhanced Analytics**: Real-time dashboards, billing integration
- 🔄 **Developer Tools**: VS Code extension, debugging tools

## 💝 Why Choose Kalibr SDK?

### ✅ **Developer Experience First**
- **Single Codebase** → All AI models supported
- **Zero Configuration** → Works out of the box
- **Production Ready** → Authentication, analytics, deployment included
- **Type Safe** → Full Python type hints and auto-completion

### ✅ **Future Proof**
- **Extensible Architecture** → Easy to add new AI models
- **Backward Compatible** → Your apps keep working as we add features
- **Open Source** → Community-driven development
- **Active Development** → Regular updates and new features

### ✅ **Production Scale**
- **Performance Optimized** → Async/await throughout
- **Secure by Default** → Built-in auth, input validation, error handling
- **Monitoring Included** → Analytics, logging, health checks
- **Deployment Ready** → One command to production

---

## 🚀 Get Started Now

```bash
# Install the SDK
pip install kalibr

# Create your first app
kalibr init --template enhanced --name "My AI API"

# Test locally
kalibr serve enhanced_app.py

# Deploy to production
kalibr deploy enhanced_app.py --platform fly --name my-ai-api

# Connect to any AI model instantly! 
```

**Transform how you build AI-integrated applications with Kalibr SDK! 🎯**