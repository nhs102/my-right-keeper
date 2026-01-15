# API Usage Guide

## 법제처 법령해석 API

This guide explains how to use the 법제처 (Korea Legislation Research Institute) API for retrieving legal interpretations.

## API Endpoints

### 1. List Search API

**Purpose**: Search for legal interpretations by keyword

**Endpoint**: `http://www.law.go.kr/DRF/lawSearch.do`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `OC` | string | Yes | User email ID (e.g., "test" from test@example.com) |
| `target` | string | Yes | Service target: `moelCgmExpc` |
| `type` | string | Yes | Output format: `JSON`, `XML`, or `HTML` |
| `query` | string | No | Search keyword |
| `display` | int | No | Number of results (default: 20, max: 100) |
| `page` | int | No | Page number (default: 1) |
| `sort` | string | No | Sort option (see below) |

**Sort Options**:
- `lasc`: Case name ascending (default)
- `ldes`: Case name descending
- `dasc`: Interpretation date ascending
- `ddes`: Interpretation date descending
- `nasc`: Case number ascending
- `ndes`: Case number descending

**Example Request**:
```python
import requests

params = {
    "OC": "your_api_id",
    "target": "moelCgmExpc",
    "type": "JSON",
    "query": "퇴직",
    "display": 20
}

response = requests.get(
    "http://www.law.go.kr/DRF/lawSearch.do",
    params=params
)
data = response.json()
```

**Example Response**:
```json
{
  "CgmExpc": {
    "cgmExpc": [
      {
        "법령해석일련번호": "21822",
        "안건명": "퇴직금 관련 질의",
        "안건번호": "12-0123",
        "질의기관명": "서울시청",
        "해석일자": "20240101"
      }
    ]
  }
}
```

---

### 2. Full Text API

**Purpose**: Retrieve full text of a specific legal interpretation

**Endpoint**: `http://www.law.go.kr/DRF/lawService.do`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `OC` | string | Yes | User email ID |
| `target` | string | Yes | Service target: `moelCgmExpc` |
| `type` | string | Yes | Output format: `JSON`, `XML`, or `HTML` |
| `ID` | int | Yes | Legal interpretation serial number |

**Example Request**:
```python
params = {
    "OC": "your_api_id",
    "target": "moelCgmExpc",
    "type": "JSON",
    "ID": "21822"
}

response = requests.get(
    "http://www.law.go.kr/DRF/lawService.do",
    params=params
)
data = response.json()
```

**Example Response**:
```json
{
  "CgmExpcService": {
    "법령해석일련번호": "21822",
    "안건명": "퇴직금 관련 질의",
    "안건번호": "12-0123",
    "해석일자": "20240101",
    "질의요지": "퇴직금 지급 기준에 대한 질의",
    "회답": "근로기준법 제34조에 따라...",
    "이유": "...",
    "관련법령": "근로기준법 제34조"
  }
}
```

---

## Implementation in My Rights Keeper

### API Connector Module

The `api_connector.py` module wraps these APIs with:

1. **Retry Logic**: Automatic retry with exponential backoff
2. **Timeout Handling**: 30-second timeout per request
3. **Error Handling**: Comprehensive error catching and logging
4. **Response Parsing**: Automatic JSON parsing

### Usage Example

```python
from app.api_connector import (
    get_law_interpretations,
    parse_interpretation_list,
    get_full_interpretation_text,
    parse_full_text
)

# Step 1: Search for interpretations
raw_data = get_law_interpretations("퇴직금")

# Step 2: Parse the list
interpretations = parse_interpretation_list(raw_data)

# Step 3: Get full text for first result
if interpretations:
    interp_id = interpretations[0]["interpretation_id"]
    full_text_data = get_full_interpretation_text(interp_id)
    
    # Step 4: Parse full text
    parsed = parse_full_text(full_text_data)
    print(parsed["text"])
```

---

## Error Handling

### Common Errors

1. **Invalid API Key**
   - Error: `LAW_API_ID environment variable not set`
   - Solution: Set `LAW_API_ID` in `.env` file

2. **Request Timeout**
   - Error: Request timeout after retries
   - Solution: Check network connection, API may be slow

3. **HTTP 404/500**
   - Error: Server error
   - Solution: Verify API endpoint and parameters

4. **JSON Parse Error**
   - Error: Failed to parse response
   - Solution: Check API response format

### Retry Behavior

The system automatically retries failed requests:
- **Max Retries**: 3 attempts
- **Retry Delay**: Exponential backoff (1s, 2s, 3s)
- **Timeout**: 30 seconds per request

---

## Rate Limiting

> [!WARNING]
> The 법제처 API may have rate limits. Avoid making excessive requests in short periods.

**Best Practices**:
- Cache results when possible
- Implement request throttling for production use
- Monitor API usage

---

## API Key Registration

To get an API key:

1. Visit [법제처 오픈API](http://www.law.go.kr/DRF/lawService.do)
2. Register for an account
3. Request API access
4. Use your email ID as the `OC` parameter

---

## Testing

Test the API connection:

```bash
python app/api_connector.py
```

This will:
1. Search for "퇴직" interpretations
2. Retrieve the first result's full text
3. Display parsed data

---

## Additional Resources

- [Official API Documentation](http://www.law.go.kr/DRF/lawService.do)
- [법제처 Website](http://www.law.go.kr)
