# export_api_docs.py - Export complete API documentation
import requests
import json
import yaml
from datetime import datetime
import os

def download_openapi_spec():
    """Download OpenAPI specification from FastAPI"""
    try:
        print("📥 Downloading OpenAPI specification...")
        
        # Get OpenAPI JSON from your running FastAPI server
        response = requests.get("http://localhost:8000/openapi.json")
        
        if response.status_code == 200:
            openapi_spec = response.json()
            
            # Save as JSON
            with open("rewear_api_openapi.json", "w") as f:
                json.dump(openapi_spec, f, indent=2)
            print("✅ Saved: rewear_api_openapi.json")
            
            # Save as YAML (more readable)
            with open("rewear_api_openapi.yaml", "w") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
            print("✅ Saved: rewear_api_openapi.yaml")
            
            return openapi_spec
        else:
            print(f"❌ Failed to download OpenAPI spec: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading OpenAPI spec: {e}")
        return None

def generate_markdown_docs(openapi_spec):
    """Generate comprehensive markdown documentation"""
    
    if not openapi_spec:
        print("❌ No OpenAPI spec to generate docs from")
        return
    
    print("📝 Generating markdown documentation...")
    
    md_content = f"""# ReWear API Documentation

**Version:** {openapi_spec.get('info', {}).get('version', '1.0.0')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{openapi_spec.get('info', {}).get('description', 'Community Clothing Exchange Platform')}

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <your_jwt_token>
```

---

"""

    # Group endpoints by tags
    paths = openapi_spec.get('paths', {})
    tags_info = openapi_spec.get('tags', [])
    
    # Create tag mapping
    tag_descriptions = {tag.get('name', ''): tag.get('description', '') for tag in tags_info}
    
    # Group paths by tags
    endpoints_by_tag = {}
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                tags = details.get('tags', ['Other'])
                tag = tags[0] if tags else 'Other'
                
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                
                endpoints_by_tag[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'details': details
                })
    
    # Generate documentation for each tag
    for tag, endpoints in endpoints_by_tag.items():
        md_content += f"## {tag}\n\n"
        
        if tag in tag_descriptions and tag_descriptions[tag]:
            md_content += f"{tag_descriptions[tag]}\n\n"
        
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method']
            details = endpoint['details']
            
            # Endpoint header
            md_content += f"### {method} {path}\n\n"
            
            # Summary and description
            if details.get('summary'):
                md_content += f"**{details['summary']}**\n\n"
            
            if details.get('description'):
                md_content += f"{details['description']}\n\n"
            
            # Parameters
            parameters = details.get('parameters', [])
            if parameters:
                md_content += "#### Parameters\n\n"
                md_content += "| Name | Type | Location | Required | Description |\n"
                md_content += "|------|------|----------|----------|-------------|\n"
                
                for param in parameters:
                    name = param.get('name', '')
                    param_type = param.get('schema', {}).get('type', 'string')
                    location = param.get('in', '')
                    required = '✅' if param.get('required', False) else '❌'
                    description = param.get('description', '')
                    
                    md_content += f"| `{name}` | {param_type} | {location} | {required} | {description} |\n"
                
                md_content += "\n"
            
            # Request body
            request_body = details.get('requestBody', {})
            if request_body:
                md_content += "#### Request Body\n\n"
                content = request_body.get('content', {})
                
                for content_type, schema_info in content.items():
                    md_content += f"**Content-Type:** `{content_type}`\n\n"
                    
                    schema = schema_info.get('schema', {})
                    if schema:
                        md_content += "```json\n"
                        md_content += json.dumps(generate_example_from_schema(schema, openapi_spec), indent=2)
                        md_content += "\n```\n\n"
            
            # Responses
            responses = details.get('responses', {})
            if responses:
                md_content += "#### Responses\n\n"
                
                for status_code, response_info in responses.items():
                    description = response_info.get('description', '')
                    md_content += f"**{status_code}** - {description}\n\n"
                    
                    content = response_info.get('content', {})
                    for content_type, schema_info in content.items():
                        schema = schema_info.get('schema', {})
                        if schema:
                            md_content += "```json\n"
                            md_content += json.dumps(generate_example_from_schema(schema, openapi_spec), indent=2)
                            md_content += "\n```\n\n"
            
            # Example curl command
            md_content += "#### Example\n\n"
            md_content += generate_curl_example(path, method, details)
            md_content += "\n---\n\n"
    
    # Add schemas section
    components = openapi_spec.get('components', {})
    schemas = components.get('schemas', {})
    
    if schemas:
        md_content += "## Data Models\n\n"
        
        for schema_name, schema_def in schemas.items():
            md_content += f"### {schema_name}\n\n"
            
            if schema_def.get('description'):
                md_content += f"{schema_def['description']}\n\n"
            
            properties = schema_def.get('properties', {})
            if properties:
                md_content += "| Field | Type | Required | Description |\n"
                md_content += "|-------|------|----------|-------------|\n"
                
                required_fields = schema_def.get('required', [])
                
                for field_name, field_def in properties.items():
                    field_type = field_def.get('type', 'string')
                    is_required = '✅' if field_name in required_fields else '❌'
                    description = field_def.get('description', '')
                    
                    md_content += f"| `{field_name}` | {field_type} | {is_required} | {description} |\n"
                
                md_content += "\n"
    
    # Save markdown documentation
    with open("rewear_api_docs.md", "w") as f:
        f.write(md_content)
    
    print("✅ Saved: rewear_api_docs.md")

def generate_example_from_schema(schema, openapi_spec, depth=0):
    """Generate example JSON from schema"""
    if depth > 3:  # Prevent infinite recursion
        return "..."
    
    schema_type = schema.get('type')
    
    if schema_type == 'object':
        example = {}
        properties = schema.get('properties', {})
        
        for prop_name, prop_schema in properties.items():
            example[prop_name] = generate_example_from_schema(prop_schema, openapi_spec, depth + 1)
        
        return example
    
    elif schema_type == 'array':
        items_schema = schema.get('items', {})
        return [generate_example_from_schema(items_schema, openapi_spec, depth + 1)]
    
    elif schema_type == 'string':
        if schema.get('format') == 'email':
            return "user@example.com"
        elif schema.get('format') == 'date-time':
            return "2023-12-01T10:00:00Z"
        elif 'example' in schema:
            return schema['example']
        else:
            return "string"
    
    elif schema_type == 'integer':
        return schema.get('example', 123)
    
    elif schema_type == 'number':
        return schema.get('example', 123.45)
    
    elif schema_type == 'boolean':
        return schema.get('example', True)
    
    # Handle $ref
    elif '$ref' in schema:
        ref_path = schema['$ref']
        if ref_path.startswith('#/components/schemas/'):
            schema_name = ref_path.split('/')[-1]
            referenced_schema = openapi_spec.get('components', {}).get('schemas', {}).get(schema_name, {})
            return generate_example_from_schema(referenced_schema, openapi_spec, depth + 1)
    
    return "example_value"

def generate_curl_example(path, method, details):
    """Generate curl command example"""
    
    # Replace path parameters with example values
    example_path = path
    parameters = details.get('parameters', [])
    
    for param in parameters:
        if param.get('in') == 'path':
            param_name = param.get('name', '')
            example_path = example_path.replace(f'{{{param_name}}}', '123')
    
    curl_cmd = f'curl -X {method} "http://localhost:8000{example_path}"'
    
    # Add headers
    headers = []
    
    # Check if authentication is required
    security = details.get('security', [])
    if security:
        headers.append('-H "Authorization: Bearer YOUR_JWT_TOKEN"')
    
    # Add content-type for POST/PUT requests
    if method in ['POST', 'PUT', 'PATCH']:
        headers.append('-H "Content-Type: application/json"')
    
    if headers:
        curl_cmd += ' \\\n  ' + ' \\\n  '.join(headers)
    
    # Add request body for POST/PUT requests
    request_body = details.get('requestBody', {})
    if request_body and method in ['POST', 'PUT', 'PATCH']:
        curl_cmd += ' \\\n  -d \'{\n    "example": "data"\n  }\''
    
    return f"```bash\n{curl_cmd}\n```"

def generate_postman_collection(openapi_spec):
    """Generate Postman collection"""
    
    if not openapi_spec:
        return
    
    print("📦 Generating Postman collection...")
    
    collection = {
        "info": {
            "name": "ReWear API",
            "description": openapi_spec.get('info', {}).get('description', ''),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "token",
                "value": "YOUR_JWT_TOKEN",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group by tags
    paths = openapi_spec.get('paths', {})
    tags_items = {}
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                tags = details.get('tags', ['Other'])
                tag = tags[0] if tags else 'Other'
                
                if tag not in tags_items:
                    tags_items[tag] = []
                
                # Create Postman request
                request = {
                    "name": details.get('summary', f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}" + path,
                            "host": ["{{baseUrl}}"],
                            "path": path.strip('/').split('/')
                        }
                    }
                }
                
                # Add auth header if needed
                security = details.get('security', [])
                if security:
                    request["request"]["header"].append({
                        "key": "Authorization",
                        "value": "Bearer {{token}}",
                        "type": "text"
                    })
                
                # Add request body
                request_body = details.get('requestBody', {})
                if request_body:
                    request["request"]["header"].append({
                        "key": "Content-Type",
                        "value": "application/json",
                        "type": "text"
                    })
                    
                    content = request_body.get('content', {}).get('application/json', {})
                    schema = content.get('schema', {})
                    
                    if schema:
                        example_body = generate_example_from_schema(schema, openapi_spec)
                        request["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example_body, indent=2)
                        }
                
                tags_items[tag].append(request)
    
    # Create folder structure
    for tag, items in tags_items.items():
        folder = {
            "name": tag,
            "item": items
        }
        collection["item"].append(folder)
    
    # Save Postman collection
    with open("rewear_api_postman.json", "w") as f:
        json.dump(collection, f, indent=2)
    
    print("✅ Saved: rewear_api_postman.json")

def main():
    """Main function to export all API documentation"""
    print("🚀 ReWear API Documentation Exporter")
    print("=" * 50)
    
    print("📋 Make sure your FastAPI server is running on http://localhost:8000")
    input("Press Enter to continue...")
    
    # Download OpenAPI spec
    openapi_spec = download_openapi_spec()
    
    if openapi_spec:
        # Generate different formats
        generate_markdown_docs(openapi_spec)
        generate_postman_collection(openapi_spec)
        
        print("\n🎉 API Documentation Generated!")
        print("=" * 50)
        print("📄 Files created:")
        print("  - rewear_api_openapi.json (OpenAPI JSON)")
        print("  - rewear_api_openapi.yaml (OpenAPI YAML)")
        print("  - rewear_api_docs.md (Markdown docs)")
        print("  - rewear_api_postman.json (Postman collection)")
        
        print("\n📖 How to use:")
        print("  - Open rewear_api_docs.md for complete documentation")
        print("  - Import rewear_api_postman.json into Postman")
        print("  - Use OpenAPI files with Swagger UI or other tools")
        
    else:
        print("❌ Failed to export documentation")
        print("💡 Make sure FastAPI server is running: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()