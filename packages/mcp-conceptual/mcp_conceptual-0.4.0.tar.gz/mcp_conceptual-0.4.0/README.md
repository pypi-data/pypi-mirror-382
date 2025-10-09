# MCP Conceptual

An MCP (Model Context Protocol) server for the Conceptual Keywords & Creative Performance API. This server provides access to keyword and creative performance data from Google Ads and Meta advertising platforms.

## Features

- **Keywords Performance**: Get keyword metrics, CAC analysis, and performance data
- **Search Terms**: Retrieve search terms that triggered your ads
- **Creative Performance**: Access Meta and Google Ads creative performance data
- **Creative Management**: Get and update creative status (pause/activate)
- **Account Metrics**: Get account-level performance metrics by campaign type (Google Ads)
- **Campaign Metrics**: Get campaign-level performance metrics for Google Ads and Meta
- **Budget Efficiency**: Get automated budget and efficiency checks
- **Weekly Metrics**: Comprehensive weekly marketing performance report with insights
- **CRM Tools**: Access contacts, attribution logs, and export functionality
- **Multi-Client Support**: Manage multiple client API keys and switch between them
- **Admin API**: Fetch client configurations from admin API (for admin users)
- **Rate Limiting**: Built-in awareness of API rate limits
- **Error Handling**: Comprehensive error handling with helpful messages

## Installation

### Using uvx (Recommended)

```bash
uvx mcp-conceptual
```

### From Source

```bash
git clone <repository-url>
cd mcp-conceptual
pip install -e .
```

## Configuration

### Environment Variables

The server supports three configuration methods:

#### Option 1: Single Client (Basic)

```bash
# Required
CONCEPTUAL_API_KEY=your_api_key_here

# Optional (defaults to production)
CONCEPTUAL_BASE_URL=https://api.conceptualhq.com/api
```

#### Option 2: Multi-Client (Environment Variables)

```bash
# Multiple client keys (format: ClientName:key,ClientName2:key2)
CONCEPTUAL_CLIENT_API_KEYS=ClientA:key123,ClientB:key456,ClientC:key789

# Optional default key (used when no client is active)
CONCEPTUAL_API_KEY=default_key_here

# Optional (defaults to production)
CONCEPTUAL_BASE_URL=https://api.conceptualhq.com/api
```

#### Option 3: Multi-Client (Admin API)

```bash
# Admin credentials to fetch client keys from API
CONCEPTUAL_ADMIN_USERNAME=admin@conceptualhq.com
CONCEPTUAL_ADMIN_PASSWORD=your_admin_password

# Optional default key (used when no client is active)
CONCEPTUAL_API_KEY=default_key_here

# Optional (defaults to production)
CONCEPTUAL_BASE_URL=https://api.conceptualhq.com/api
```

When using admin credentials, the server will fetch all available client keys from the admin API on startup.

### Getting an API Key

1. Log into your Conceptual account
2. Go to Account Settings
3. Generate an API key for your customer account
4. Set the `CONCEPTUAL_API_KEY` environment variable

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration:

#### Single Client Configuration
```json
{
  "mcpServers": {
    "conceptual": {
      "command": "uvx",
      "args": ["mcp-conceptual"],
      "env": {
        "CONCEPTUAL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Multi-Client Configuration (Admin API)
```json
{
  "mcpServers": {
    "conceptual": {
      "command": "uvx",
      "args": ["mcp-conceptual"],
      "env": {
        "CONCEPTUAL_ADMIN_USERNAME": "admin@conceptualhq.com",
        "CONCEPTUAL_ADMIN_PASSWORD": "your_admin_password",
        "CONCEPTUAL_API_KEY": "optional_default_key"
      }
    }
  }
}
```

#### Local Development Configuration
```json
{
  "mcpServers": {
    "conceptual": {
      "command": "uvx",
      "args": ["--from", "/path/to/mcp-conceptual", "mcp-conceptual"],
      "env": {
        "CONCEPTUAL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Standalone

```bash
# Run the server (from PyPI)
mcp-conceptual

# Or with uvx (from PyPI)
uvx mcp-conceptual

# Run from local directory (for development/testing)
uvx --from /path/to/mcp-conceptual mcp-conceptual

# Or from current directory
uvx --from . mcp-conceptual
```

## Available Tools

### Keywords Tools

#### `get_keyword_performance`
Get keyword performance data including cost, clicks, conversions, and CAC analysis.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `view_type`: keywords, search_terms, manual, or campaign_content (default: keywords)
- `advanced_mode`: Include advanced metrics (default: false)
- `limit`: Max records to return (1-1000, default: 100)
- `offset`: Records to skip for pagination (default: 0)
- `sort_by`: Field to sort by (cost, clicks, impressions, conversions, cac, ctr, cpc, conversion_rate)
- `sort_direction`: asc or desc (default: desc)

**Rate limit:** 60 requests per minute

#### `get_search_terms_performance`
Get search terms that triggered your ads with performance metrics.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `advanced_mode`: Include advanced metrics (default: false)
- `limit`: Max records to return (1-1000, default: 100)
- `offset`: Records to skip for pagination (default: 0)
- `sort_by`: Field to sort by
- `sort_direction`: asc or desc (default: desc)

**Rate limit:** 60 requests per minute  
**Note:** May be slower due to large volume of search terms data

#### `get_manual_keywords_info`
Get information about manual keywords functionality.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

#### `get_campaign_content_info`
Get information about campaign content functionality.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

### Creative Tools

#### `get_meta_creative_performance`
Get Meta (Facebook/Instagram) creative performance data.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `platform`: meta, google, or all (default: all)
- `status`: active, paused, or all (default: all)
- `limit`: Max records to return (1-500, default: 100)
- `offset`: Records to skip for pagination (default: 0)
- `include_images`: Include creative image URLs (default: true)
- `sort_by`: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
- `sort_direction`: asc or desc (default: desc)

**Rate limit:** 30 requests per minute

#### `get_google_creative_performance`
Get Google Ads creative performance data.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `limit`: Max records to return (1-500, default: 100)
- `offset`: Records to skip for pagination (default: 0)
- `sort_by`: Field to sort by
- `sort_direction`: asc or desc (default: desc)

**Rate limit:** 30 requests per minute

#### `get_creative_status`
Get the current status of a specific creative/ad.

**Parameters:**
- `creative_id` (required): Creative/Ad ID

#### `update_creative_status`
Update the status of a creative/ad (pause or activate).

**Parameters:**
- `creative_id` (required): Creative/Ad ID
- `status` (required): New status (ACTIVE, PAUSED, active, or paused)

**Rate limit:** 10 requests per minute  
**Note:** Requires Meta OAuth permissions for the customer account

### Metrics Tools

#### `get_account_metrics`
Get account-level performance metrics by campaign type (Google Ads only).

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `advanced_mode`: Include advanced metrics and analysis (default: false)

**Rate limit:** 60 requests per minute

#### `get_campaign_metrics`
Get campaign-level performance metrics for Google Ads and/or Meta platforms.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `platform`: google, meta, or all (default: all)
- `advanced_mode`: Include advanced metrics and analysis (default: false)
- `limit`: Max records to return (1-1000, default: 100)
- `offset`: Records to skip for pagination (default: 0)
- `sort_by`: Field to sort by (cost, campaign_name, conversions, cac, roas)
- `sort_direction`: asc or desc (default: desc)

**Rate limit:** 60 requests per minute

#### `get_budget_efficiency_metrics`
Get automated budget and efficiency checks.

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

**Rate limit:** 60 requests per minute

#### `get_weekly_metrics`
Get comprehensive weekly marketing performance report (identical to /slack endpoint).

**Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `comparison_start_date`: Comparison period start date (auto-generated if not provided)
- `comparison_end_date`: Comparison period end date (auto-generated if not provided)
- `comparison_label`: Label for the comparison period (default: "vs. previous period")
- `platform`: Platform filter - google, meta, or all (default: all)
- `include_insights`: Include performance insights and analysis (default: true)
- `include_budget_pacing`: Include budget pacing analysis (default: true)

**Rate limit:** 60 requests per minute

### CRM Tools

#### `get_crm_contacts`
Get CRM contacts list with search and sort functionality.

**Parameters:**
- `search`: Search term to filter contacts (email, name, company)
- `sort_by`: Field to sort contacts by
- `per_page`: Records per page (1-500, default 50)

**Rate limit:** 60 requests per minute

#### `get_crm_contact`
Get single contact with attribution history.

**Parameters:**
- `contact_id` (required): Contact ID to retrieve

#### `get_crm_attribution_logs`
Get attribution logs with search and sort functionality.

**Parameters:**
- `search`: Search term to filter attribution logs
- `sort_by`: Field to sort attribution logs by
- `per_page`: Records per page (1-500, default 200)

**Rate limit:** 60 requests per minute

#### `get_crm_analytics`
Get comprehensive CRM analytics overview.

**Rate limit:** 60 requests per minute

#### `export_crm_contacts`
Export contacts as CSV.

**Parameters:**
- `search`: Search term to filter exported contacts

**Rate limit:** 10 requests per minute (lower due to resource intensity)

### Multi-Client Management Tools

#### `set_active_client`
Set the active client for all subsequent API calls.

**Parameters:**
- `client_name` (required): Name of the client to activate

#### `clear_active_client`
Clear the active client and revert to using the default API key.

#### `get_current_client_info`
Get information about the currently active client and available options.

#### `list_available_clients`
List all available client configurations.

### Admin Tools

#### `list_client_api_keys`
List all client API keys (admin only).

**Parameters:**
- `username` (required): Admin user email address
- `password` (required): Admin user password

**Rate limit:** 5 requests per minute

**Security Requirements:**
- Valid admin user credentials
- User must have is_admin = true privilege
- All access attempts are logged

## Rate Limits

- Keywords endpoints: 60 requests per minute
- Creative endpoints: 30 requests per minute
- Creative status updates: 10 requests per minute
- Metrics endpoints: 60 requests per minute
- Weekly metrics endpoint: 60 requests per minute
- CRM endpoints: 60 requests per minute (export: 10 requests per minute)
- Admin endpoints: 5 requests per minute

## Data Caching

Data is cached for 120 minutes to ensure optimal performance. Cache expiration times are included in response metadata.

## Error Handling

The server handles various error conditions:

- **401 Unauthorized**: Invalid or missing API key
- **400 Bad Request**: Missing platform configuration or invalid parameters
- **422 Validation Error**: Invalid date formats or parameter values
- **429 Rate Limit**: Rate limit exceeded (includes retry suggestions)
- **500 Server Error**: Internal API errors
- **504 Timeout**: Query timeout (for search terms with large datasets)

## Development

### Setup

```bash
git clone <repository-url>
cd mcp-conceptual
pip install -e ".[dev]"
```

### Local Testing

When developing or testing changes locally, you can run the MCP server from your local directory:

```bash
# Using uvx with --from flag
uvx --from . mcp-conceptual

# Or with absolute path
uvx --from /Users/manav/Workspace/mcp-conceptual mcp-conceptual

# Or run directly with Python
python -m mcp_conceptual.server
```

For testing with Claude Desktop, update your configuration to point to your local directory:

```json
{
  "mcpServers": {
    "conceptual": {
      "command": "uvx",
      "args": ["--from", "/Users/manav/Workspace/mcp-conceptual", "mcp-conceptual"],
      "env": {
        "CONCEPTUAL_ADMIN_USERNAME": "admin@conceptualhq.com",
        "CONCEPTUAL_ADMIN_PASSWORD": "your_admin_password"
      }
    }
  }
}
```

### Code Formatting

```bash
black src/
isort src/
```

### Type Checking

```bash
mypy src/
```

### Testing

```bash
pytest
```

## License

MIT License - see LICENSE file for details.

## Support

For API support, contact: support@conceptualhq.com

For issues with this MCP server, please file an issue in the repository.