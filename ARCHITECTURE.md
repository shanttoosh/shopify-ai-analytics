# Shopify Analytics App - Architecture Diagrams

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        USER[User/API Client]
    end
    
    subgraph "Rails API Gateway :3000"
        API[API Controller<br/>/api/v1/questions]
        AUTH[OAuth Controller<br/>/auth/shopify]
        DB[(PostgreSQL<br/>Store Credentials<br/>Query Logs)]
        RAILSVC[Python AI Client Service]
    end
    
    subgraph "Python AI Service :8000"
        AGENT[Agent Orchestrator]
        INTENT[Intent Classifier]
        PLANNER[Query Planner]
        QGEN[ShopifyQL Generator]
        EXEC[Query Executor]
        PROC[Result Processor]
        EXPL[Explainer]
        LLM[LLM Client<br/>OpenAI/Claude]
    end
    
    subgraph "Shopify Platform"
        SHOPIFY[Shopify Admin API<br/>GraphQL + REST]
        OAUTH[Shopify OAuth]
    end
    
    USER -->|POST question| API
    API -->|Forward| RAILSVC
    RAILSVC -->|HTTP Request| AGENT
    
    AGENT -->|1. Classify| INTENT
    INTENT -->|2. Plan| PLANNER
    PLANNER -->|3. Generate| QGEN
    QGEN -->|4. Execute| EXEC
    EXEC -->|5. Process| PROC
    PROC -->|6. Explain| EXPL
    
    INTENT -.->|LLM Call| LLM
    QGEN -.->|LLM Call| LLM
    EXPL -.->|LLM Call| LLM
    
    EXEC -->|Query Data| SHOPIFY
    SHOPIFY -->|Results| EXEC
    
    AGENT -->|Response| RAILSVC
    RAILSVC -->|Format| API
    API -->|JSON Response| USER
    
    AUTH -->|OAuth Flow| OAUTH
    OAUTH -->|Access Token| AUTH
    AUTH -->|Store Token| DB
    API -.->|Get Token| DB
    RAILSVC -.->|Include Token| AGENT
```

## Agentic Workflow - Detailed Flow

```mermaid
flowchart TD
    START([User Question]) --> RECEIVE[Receive Question<br/>in Python Service]
    
    RECEIVE --> STEP1[Step 1: Intent Classification]
    STEP1 --> LLM1[LLM: Analyze Question]
    LLM1 --> CLASSIFY{Classify Intent}
    
    CLASSIFY -->|Inventory| INTENT1[Projection/Reorder]
    CLASSIFY -->|Sales| INTENT2[Trends/Top Products]
    CLASSIFY -->|Customer| INTENT3[Behavior/Repeat]
    CLASSIFY -->|Ambiguous| INTENT4[Clarification Needed]
    
    INTENT1 --> STEP2
    INTENT2 --> STEP2
    INTENT3 --> STEP2
    INTENT4 --> ERROR1[Return Low Confidence<br/>Request Clarification]
    
    STEP2[Step 2: Query Planning] --> PLAN[Determine Required Data]
    PLAN --> RESOURCES{Select Resources}
    
    RESOURCES -->|Products| R1[products table]
    RESOURCES -->|Orders| R2[orders table]
    RESOURCES -->|Inventory| R3[inventory_levels table]
    RESOURCES -->|Customers| R4[customers table]
    
    R1 --> STEP3
    R2 --> STEP3
    R3 --> STEP3
    R4 --> STEP3
    
    STEP3[Step 3: ShopifyQL Generation] --> LLM2[LLM: Generate Query]
    LLM2 --> VALIDATE{Validate Syntax}
    VALIDATE -->|Invalid| FIX[Regenerate with Feedback]
    FIX --> LLM2
    VALIDATE -->|Valid| CONVERT[Convert to API Calls]
    
    CONVERT --> STEP4[Step 4: Execute Queries]
    STEP4 --> CALL[Call Shopify Admin API]
    CALL --> HANDLE{Handle Response}
    
    HANDLE -->|Success| DATA[Receive Data]
    HANDLE -->|Rate Limit| RETRY[Wait & Retry]
    HANDLE -->|Error| ERROR2[Log Error<br/>Return Gracefully]
    RETRY --> CALL
    
    DATA --> CHECK{Data Complete?}
    CHECK -->|No| PARTIAL[Note Partial Data]
    CHECK -->|Yes| STEP5
    PARTIAL --> STEP5
    
    STEP5[Step 5: Result Processing] --> ANALYZE[Analyze Data]
    ANALYZE --> STATS[Calculate Statistics]
    STATS --> INSIGHTS[Extract Insights]
    
    INSIGHTS --> STEP6[Step 6: Explain Results]
    STEP6 --> LLM3[LLM: Generate Explanation]
    LLM3 --> SIMPLIFY[Convert to Business Language]
    SIMPLIFY --> CONFIDENCE[Calculate Confidence Score]
    
    CONFIDENCE --> RESPONSE[Format Final Response]
    RESPONSE --> END([Return to Rails API])
    
    ERROR1 --> END
    ERROR2 --> END
    
    style STEP1 fill:#e1f5ff
    style STEP2 fill:#e1f5ff
    style STEP3 fill:#e1f5ff
    style STEP4 fill:#e1f5ff
    style STEP5 fill:#e1f5ff
    style STEP6 fill:#e1f5ff
    style LLM1 fill:#fff4e6
    style LLM2 fill:#fff4e6
    style LLM3 fill:#fff4e6
```

## Data Flow Example: "How much inventory to reorder?"

```mermaid
sequenceDiagram
    participant U as User
    participant R as Rails API
    participant P as Python Agent
    participant L as LLM
    participant S as Shopify API
    
    U->>R: POST /api/v1/questions<br/>{"question": "How much inventory<br/>should I reorder for next week?"}
    
    R->>R: Validate request
    R->>R: Get store access token from DB
    
    R->>P: POST /analyze<br/>{question, access_token}
    
    rect rgb(225, 245, 255)
        Note over P: Agent Workflow Starts
        
        P->>L: Classify intent
        L-->>P: Intent: inventory_reorder<br/>Time: next_week
        
        P->>L: Generate ShopifyQL
        L-->>P: Query plan for:<br/>- Sales history (30d)<br/>- Current inventory<br/>- Product variants
        
        P->>P: Convert to API calls
        
        P->>S: GraphQL: Get products<br/>& inventory levels
        S-->>P: Current stock: 15 units
        
        P->>S: REST: Get orders<br/>(last 30 days)
        S-->>P: 300 units sold
        
        P->>P: Calculate:<br/>Daily avg = 10 units/day<br/>Weekly need = 70 units<br/>Shortage = 55 units
        
        P->>L: Explain results in<br/>business language
        L-->>P: "You sell ~10 units/day.<br/>Reorder at least 70 units<br/>for next week."
        
        Note over P: Agent Workflow Complete
    end
    
    P-->>R: {answer, confidence, query, metadata}
    
    R->>R: Log query (optional)
    R-->>U: JSON response with<br/>business-friendly answer
```

## OAuth Flow

```mermaid
sequenceDiagram
    participant U as Store Owner
    participant R as Rails API
    participant S as Shopify OAuth
    
    U->>R: Visit /auth/shopify
    R->>R: Generate state token
    R->>S: Redirect to Shopify<br/>with app credentials & scopes
    
    S->>U: Show permission screen
    U->>S: Approve permissions
    
    S->>R: Redirect to /auth/shopify/callback<br/>with authorization code
    
    R->>S: Exchange code for<br/>access token
    S-->>R: Return access token
    
    R->>R: Encrypt & store token in DB<br/>with shop domain
    R-->>U: Installation complete
```

## Component Responsibilities

### Rails API Gateway
- **Primary Role**: Entry point and orchestrator
- **Responsibilities**:
  - Accept and validate user questions
  - Manage Shopify OAuth and tokens
  - Forward requests to Python service
  - Format and return responses
  - Optional: Log queries for analytics

### Python AI Service
- **Primary Role**: LLM-powered agent system
- **Responsibilities**:
  - Interpret natural language questions
  - Generate appropriate Shopify queries
  - Execute queries against Shopify API
  - Process and analyze results
  - Generate human-friendly explanations

### Shopify Platform
- **Primary Role**: Data source
- **Provides**:
  - OAuth authentication
  - Admin API (GraphQL & REST)
  - Store data (products, orders, customers, inventory)

## Technology Stack Summary

| Layer | Technology | Port | Purpose |
|-------|-----------|------|---------|
| API Gateway | Ruby on Rails 7 | 3000 | Request handling, auth, orchestration |
| AI Service | Python FastAPI | 8000 | LLM agent, ShopifyQL generation |
| Database | PostgreSQL | 5432 | Store credentials, query logs |
| LLM Provider | OpenAI GPT-4 | N/A | Natural language processing |
| Data Source | Shopify Admin API | N/A | Store data access |

## Key Design Decisions

### Why Rails + Python?
- **Rails**: Mature OAuth support, great for API gateway patterns, strong ecosystem for Shopify
- **Python**: Superior LLM libraries, better AI/ML tooling, easier prompt engineering

### Why Separate Services?
- **Separation of Concerns**: Business logic (Rails) vs AI logic (Python)
- **Independent Scaling**: Can scale AI service independently
- **Technology Strengths**: Use each language for what it does best
- **Development**: Teams can work independently

### ShopifyQL Approach
- **Challenge**: ShopifyQL is primarily for Shopify Admin UI
- **Solution**: LLM generates ShopifyQL-like intent, we convert to Admin API calls
- **Benefit**: Leverage LLM's understanding of query languages while using supported APIs

### Agent Architecture
- **Multi-step Pipeline**: Clear separation of intent, planning, execution, explanation
- **LLM Integration Points**: Only where reasoning is needed (intent, query gen, explanation)
- **Deterministic Steps**: Data fetching and processing use standard code
- **Validation**: Multiple checkpoints ensure quality
