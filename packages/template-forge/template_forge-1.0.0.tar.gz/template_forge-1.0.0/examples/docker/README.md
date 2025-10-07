# Docker and Container Example

This example demonstrates generating Docker Compose files from deployment YAML configuration.

## Files in this example:

- `deploy.yaml` - YAML deployment configuration
- `docker-compose.yml.j2` - Jinja2 template for Docker Compose
- `config.yaml` - Template Forge configuration

## Input Data (`deploy.yaml`)

Contains deployment configuration including:
- Environment settings (development, staging, production)
- Container specifications and resource limits
- Service dependencies and networking
- Volume mounts and configuration

## Usage

```bash
cd examples/docker
template-forge config.yaml
```

## Expected Output

Generates a complete Docker Compose file with:
- Service definitions based on deployment config
- Environment-specific variables
- Volume and network configurations
- Resource constraints and health checks

## Key Concepts Demonstrated

1. **YAML Processing**: Parse complex YAML deployment configurations
2. **Environment Variables**: Generate environment-specific configurations
3. **Service Orchestration**: Template container service definitions
4. **Resource Management**: Configure memory and CPU limits
5. **Network Configuration**: Define service interconnections