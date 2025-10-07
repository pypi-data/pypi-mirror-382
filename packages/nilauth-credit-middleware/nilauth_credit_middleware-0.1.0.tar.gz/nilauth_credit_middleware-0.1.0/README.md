# FastAPI Credit Locking Middleware

A comprehensive middleware solution for FastAPI that integrates with the nilauth-credit service to implement pay-per-request functionality.

## Features

- 🔒 **Automatic credit locking** before request processing
- 💰 **Dynamic cost calculation** based on actual resource usage
- 🎯 **Selective metering** - only affect specific endpoints
- 🔄 **Automatic rollback** on request failures
- 🛠️ **Flexible configuration** - multiple user ID extraction methods
- 📊 **Built-in cost calculators** for common scenarios

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Setup

```python
from fastapi import FastAPI, Request
from credit_middleware import (
    CreditLockingClient,
    CreditLockingMiddleware,
    metered
)

app = FastAPI()

# Initialize credit client
credit_client = CreditLockingClient(
    base_url="http://localhost:3000",
    api_token="your-api-token"
)

# Add middleware
app.add_middleware(CreditLockingMiddleware, credit_client=credit_client)

# Clean up on shutdown
@app.on_event("shutdown")
async def shutdown():
    await credit_client.close()
```

### 2. Create a User ID Extractor

```python
async def get_user_id(request: Request) -> str:
    """Extract user ID from request header"""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise ValueError("User ID header not found")
    return user_id
```

### 3. Decorate Your Endpoints

```python
@app.get("/api/expensive-operation")
@metered(
    user_id_extractor=get_user_id,
    estimated_cost=5.0
)
async def expensive_operation(request: Request):
    return {"result": "success"}
```

## Usage Examples

### Example 1: Fixed Cost Endpoint

Charge a fixed amount regardless of processing:

```python
@app.get("/api/simple")
@metered(
    user_id_extractor=get_user_id,
    estimated_cost=1.0  # Will charge exactly 1.0 credit
)
async def simple_endpoint(request: Request):
    return {"message": "Fixed cost endpoint"}
```

### Example 2: Dynamic Cost Based on Response Size

```python
from credit_middleware import CostCalculators

@app.post("/api/data")
@metered(
    user_id_extractor=get_user_id,
    estimated_cost=5.0,  # Lock 5.0 credits upfront
    cost_calculator=CostCalculators.by_response_size(
        base_cost=0.5,    # Base cost
        per_kb=0.1        # Additional cost per KB
    )
)
async def get_data(request: Request):
    # Return large data
    return {"data": [...]}  # Cost = 0.5 + (size_in_kb * 0.1)
```

### Example 3: Cost Based on Processing Time

```python
@app.post("/api/process")
@metered(
    user_id_extractor=get_user_id,
    estimated_cost=10.0,
    cost_calculator=CostCalculators.by_processing_time(
        base_cost=1.0,     # Base cost
        per_second=2.0     # Cost per second
    )
)
async def process_data(request: Request):
    request.state.start_time = time.time()
    # Do processing...
    return {"result": "done"}  # Cost = 1.0 + (duration * 2.0)
```

### Example 4: Custom Cost Calculation

```python
async def custom_calculator(request: Request, response: Response) -> float:
    """Calculate cost based on custom business logic"""
    base_cost = 1.0
    
    # Factor 1: Response size
    if hasattr(response, 'body'):
        size_cost = len(response.body) / 1024.0 * 0.05
    else:
        size_cost = 0.0
    
    # Factor 2: Processing time
    start_time = getattr(request.state, 'start_time', None)
    if start_time:
        duration = time.time() - start_time
        time_cost = duration * 1.0
    else:
        time_cost = 0.0
    
    # Factor 3: Success/failure penalty
    error_penalty = 0.5 if response.status_code >= 400 else 0.0
    
    return base_cost + size_cost + time_cost + error_penalty

@app.post("/api/advanced")
@metered(
    user_id_extractor=get_user_id,
    estimated_cost=15.0,
    cost_calculator=custom_calculator
)
async def advanced_endpoint(request: Request):
    request.state.start_time = time.time()
    # Process request...
    return {"result": "processed"}
```

## User ID Extraction Methods

### From Header

```python
async def from_header(request: Request) -> str:
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise ValueError("X-User-ID header required")
    return user_id
```

### From Query Parameter

```python
async def from_query(request: Request) -> str:
    user_id = request.query_params.get("user_id")
    if not user_id:
        raise ValueError("user_id parameter required")
    return user_id
```

### From JWT Token

```python
async def from_jwt(request: Request) -> str:
    import jwt
    
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise ValueError("Bearer token required")
    
    token = auth.split(" ")[1]
    payload = jwt.decode(token, options={"verify_signature": False})
    return payload.get("sub")
```

### From Request Body

```python
from pydantic import BaseModel

class RequestWithUser(BaseModel):
    user_id: str
    data: dict

async def from_body(request: Request) -> str:
    body = await request.json()
    user_id = body.get("user_id")
    if not user_id:
        raise ValueError("user_id not found in body")
    return user_id
```

## Built-in Cost Calculators

### Fixed Cost

```python
CostCalculators.fixed_cost(amount=2.5)
# Always charges 2.5 credits
```

### By Response Size

```python
CostCalculators.by_response_size(
    base_cost=0.1,  # Base cost
    per_kb=0.01     # Cost per kilobyte
)
# Cost = base_cost + (response_size_kb * per_kb)
```

### By Processing Time

```python
CostCalculators.by_processing_time(
    base_cost=0.1,   # Base cost
    per_second=0.5   # Cost per second
)
# Cost = base_cost + (duration_seconds * per_second)
# Requires: request.state.start_time = time.time()
```

## Error Handling

The middleware automatically handles errors:

1. **Lock fails** (insufficient balance, user not found, etc.)
   - Request is rejected immediately
   - No processing occurs
   - Client receives appropriate error

2. **Processing fails** (exception during request handling)
   - Funds are unlocked with 0 cost (full refund)
   - Original exception is propagated

3. **Unlock fails** (network error, etc.)
   - Error is logged
   - Original response is still returned
   - Manual intervention may be needed

## Running the Example

1. **Start the nilauth-credit service:**

```bash
# From the main project directory
docker-compose up -d
cargo run
```

2. **Start the Python example app:**

```bash
cd python_middleware
python example_app.py
```

3. **Test the endpoints:**

```bash
# Simple endpoint (1.0 credit)
curl -H "X-User-ID: test-user-1" http://localhost:8000/api/simple

# Variable response size
curl -X POST -H "X-User-ID: test-user-1" \
  -H "Content-Type: application/json" \
  -d '{"size": 1000}' \
  http://localhost:8000/api/data

# Processing time-based
curl -X POST -H "X-User-ID: test-user-1" \
  "http://localhost:8000/api/process?duration=0.5"

# Check balance
curl "http://localhost:8000/api/test/balance?user_id=test-user-1"
```

## API Documentation

Once running, visit:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration Options

### CreditLockingClient

```python
CreditLockingClient(
    base_url="http://localhost:3000",  # Credit service URL
    api_token="your-token",            # API authentication token
    timeout=10.0                       # Request timeout in seconds
)
```

### @metered Decorator

```python
@metered(
    user_id_extractor=callable,  # Required: async function to get user_id
    estimated_cost=1.0,          # Required: upfront lock amount
    cost_calculator=callable     # Optional: async function for actual cost
)
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (if available)
pytest
```

## Best Practices

1. **Estimate conservatively**: Set `estimated_cost` high enough to cover most cases
2. **Calculate accurately**: Use cost calculators to charge fair amounts
3. **Handle errors gracefully**: Always validate user IDs and handle missing data
4. **Monitor closely**: Log cost calculations for debugging
5. **Secure tokens**: Never commit API tokens to version control
6. **Use environment variables**: Load configuration from env vars in production

## Integration with Your Service

### Environment Variables

```bash
export CREDIT_SERVICE_URL="http://localhost:3000"
export CREDIT_API_TOKEN="your-api-token-here"
```

### Production Configuration

```python
import os
from credit_middleware import CreditLockingClient

credit_client = CreditLockingClient(
    base_url=os.getenv("CREDIT_SERVICE_URL", "http://localhost:3000"),
    api_token=os.getenv("CREDIT_API_TOKEN"),
    timeout=float(os.getenv("CREDIT_TIMEOUT", "10.0"))
)
```

## Troubleshooting

### "Credit service unavailable"
- Ensure nilauth-credit service is running
- Check `base_url` is correct
- Verify network connectivity

### "User not found"
- Verify user exists in database
- Check user ID extraction logic
- Review API token permissions

### "Insufficient balance"
- User needs to top up credits
- Check current balance via `/v1/summary` endpoint
- Consider reducing estimated costs

### "Lock not found"
- May indicate timing issue
- Check for race conditions
- Review unlock error logs

## License

Same as the nilauth-credit project.

## Support

For issues and questions, please refer to the main nilauth-credit project documentation.


