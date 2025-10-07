# AUTOSAR Automotive Example

This example demonstrates parsing AUTOSAR ARXML files for automotive software generation.

## Files in this example:

- `ecu.arxml` - AUTOSAR ECU configuration file
- `config.yaml` - Template Forge configuration for ARXML processing
- `ecu_config.h.j2` - Template for generating C header files

## Input Data (`ecu.arxml`)

Contains AUTOSAR Electronic Control Unit configuration including:
- ECU metadata and identification
- Software component definitions
- Port interfaces and data types
- Communication matrix and signals

## Usage

```bash
cd examples/autosar
template-forge config.yaml
```

## Expected Output

Generates automotive software artifacts:
- C header files with ECU configuration
- Signal definitions and data types
- Communication interface code
- Configuration tables and constants

## Key Concepts Demonstrated

1. **ARXML Processing**: Parse complex AUTOSAR XML files
2. **Namespace Handling**: Work with XML namespaces
3. **Automotive Standards**: Generate AUTOSAR-compliant code
4. **Signal Processing**: Extract communication signals and data
5. **Code Generation**: Create embedded C code from metadata

## AUTOSAR Concepts

- **ECU**: Electronic Control Unit
- **ARXML**: AUTOSAR XML format
- **SW-C**: Software Component
- **Port Interface**: Communication interface definition