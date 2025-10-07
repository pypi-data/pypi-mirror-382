# Data Extraction - Requirements

## 1. Supported Input Formats

**REQ-EXT-001**: The system shall support the following input file formats:
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)
- XML (`.xml`)
- ARXML (`.arxml`) - AUTOSAR XML format

**REQ-EXT-002**: The system shall automatically detect the input format based on file extension.

**REQ-EXT-003**: The system shall allow explicit format override via the `format` field in configuration.

**REQ-EXT-004**: The system shall provide clear error messages for unsupported file formats.

## 2. JSON Data Extraction

**REQ-EXT-010**: The system shall parse JSON files using the standard Python `json` module.

**REQ-EXT-011**: The system shall support extraction from nested JSON objects using dot notation.

**REQ-EXT-012**: The system shall support extraction from JSON arrays using index notation: `items[0]`

**REQ-EXT-013**: The system shall support extraction from all array elements using wildcard: `items[*]`

**REQ-EXT-014**: The system shall return the entire JSON structure as a dictionary if no tokens are specified.

## 3. YAML Data Extraction

**REQ-EXT-020**: The system shall parse YAML files using the PyYAML library.

**REQ-EXT-021**: The system shall support all YAML data types (strings, numbers, booleans, lists, dictionaries).

**REQ-EXT-022**: The system shall support extraction from nested YAML structures using dot notation.

**REQ-EXT-023**: The system shall support extraction from YAML arrays using index and wildcard notation.

**REQ-EXT-024**: The system shall handle YAML anchors and aliases correctly.

## 4. XML Data Extraction

**REQ-EXT-030**: The system shall parse XML files using Python's `xml.etree.ElementTree` module.

**REQ-EXT-031**: The system shall support extraction using dot notation to navigate XML element hierarchy: `root.parent.child`

**REQ-EXT-032**: The system shall extract XML element text content by specifying the element path: `database.name` extracts text from `<database><name>value</name></database>`

**REQ-EXT-033**: The system shall support extraction of XML attributes using `@attribute` syntax: `database.@host` extracts the `host` attribute from `<database host="localhost">`

**REQ-EXT-034**: The system shall support extraction of all child elements using wildcard notation: `servers.*` extracts all children under `<servers>`

**REQ-EXT-035**: The system shall convert extracted XML elements to Python dictionaries with keys:
- `text`: Element text content (if present)
- `@attributeName`: Attribute values (if present)
- `childName`: Nested child elements (if present)

**REQ-EXT-036**: When extracting an element with both attributes and text, the system shall provide access to both: element text via the element path, attributes via `@attribute` syntax.

**REQ-EXT-037**: When extracting an element with multiple children of the same tag name, the system shall return them as a list accessible via index: `servers.server[0]`, `servers.server[1]`

**REQ-EXT-038**: XML extraction example:
```xml
<config>
  <database host="localhost" port="5432">
    <name>mydb</name>
    <user>admin</user>
  </database>
  <servers>
    <server>web01</server>
    <server>web02</server>
  </servers>
</config>
```
Configuration:
```yaml
inputs:
  - path: config.xml
    namespace: cfg
    format: xml
    tokens:
      - name: db_host
        key: database.@host          # Extracts: "localhost"
      - name: db_port
        key: database.@port          # Extracts: "5432"
      - name: db_name
        key: database.name           # Extracts: "mydb"
      - name: db_user
        key: database.user           # Extracts: "admin"
      - name: first_server
        key: servers.server[0]       # Extracts: "web01"
      - name: all_servers
        key: servers.server[*]       # Extracts: ["web01", "web02"]
```

## 5. ARXML Data Extraction

**REQ-EXT-040**: The system shall parse ARXML (AUTOSAR XML) files as a specialized XML format with AUTOSAR-specific conventions.

**REQ-EXT-041**: The system shall handle ARXML namespace prefixes correctly, stripping or normalizing them for token extraction: `ar:AUTOSAR` becomes `AUTOSAR`

**REQ-EXT-042**: The system shall support extraction of AUTOSAR SHORT-NAME elements using dot notation: `AR-PACKAGES.AR-PACKAGE.SHORT-NAME`

**REQ-EXT-043**: The system shall support extraction of AUTOSAR reference paths (AR-REF) as string values.

**REQ-EXT-044**: The system shall support extraction from deeply nested AUTOSAR element hierarchies common in ECU configurations.

**REQ-EXT-045**: ARXML extraction example:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>ECU_Config</SHORT-NAME>
      <ELEMENTS>
        <ECU-INSTANCE>
          <SHORT-NAME>MainECU</SHORT-NAME>
          <COM-CONFIG-GW-TIME-BASE>0.005</COM-CONFIG-GW-TIME-BASE>
          <COMM-CONTROLLERS>
            <CAN-COMMUNICATION-CONTROLLER>
              <SHORT-NAME>CAN_Ctrl_0</SHORT-NAME>
            </CAN-COMMUNICATION-CONTROLLER>
          </COMM-CONTROLLERS>
        </ECU-INSTANCE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
```
Configuration:
```yaml
inputs:
  - path: ecu_config.arxml
    namespace: ecu
    format: arxml
    tokens:
      - name: package_name
        key: AR-PACKAGES.AR-PACKAGE.SHORT-NAME           # Extracts: "ECU_Config"
      - name: ecu_name
        key: AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.SHORT-NAME  # Extracts: "MainECU"
      - name: time_base
        key: AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.COM-CONFIG-GW-TIME-BASE  # Extracts: "0.005"
      - name: can_controller
        key: AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.COMM-CONTROLLERS.CAN-COMMUNICATION-CONTROLLER.SHORT-NAME  # Extracts: "CAN_Ctrl_0"
```

**REQ-EXT-046**: The system shall treat ARXML as case-sensitive, preserving AUTOSAR's uppercase naming conventions.

## 6. Token Extraction

**REQ-EXT-050**: The system shall extract tokens based on key paths specified in configuration.

**REQ-EXT-051**: The system shall support dot notation for navigating nested structures: `parent.child.grandchild`

**REQ-EXT-052**: The system shall support array indexing: `items[0]`, `items[1]`

**REQ-EXT-053**: The system shall support array wildcard to extract all elements: `items[*]`

**REQ-EXT-054**: The system shall support object wildcard to extract entire objects: `config.*`

**REQ-EXT-055**: The system shall log a warning when a token extraction key cannot be found.

**REQ-EXT-056**: The system shall continue processing other tokens when one token extraction fails.

## 7. Data Transformations

**REQ-EXT-060**: The system shall support the following transformations on extracted values:

### String Case Transformations
- `upper`: Convert string to uppercase
- `lower`: Convert string to lowercase
- `title`: Convert string to title case (first letter of each word)
- `capitalize`: Capitalize first letter only

### String Formatting
- `strip`: Remove leading and trailing whitespace
- `snake_case`: Convert to snake_case (e.g., "MyVariable" → "my_variable")
- `camel_case`: Convert to camelCase (e.g., "my_variable" → "myVariable")

### Type Conversions
- `int`: Convert value to integer
- `float`: Convert value to floating-point number
- `bool`: Convert value to boolean (true/false, 1/0, yes/no, on/off)

### Collection Operations
- `len`: Get length of string, list, or other collection
- `any`: Return True if any element is truthy (for lists/tuples)
- `all`: Return True if all elements are truthy (for lists/tuples)
- `sum`: Sum numeric values in a list/tuple
- `max`: Get maximum value from a list/tuple
- `min`: Get minimum value from a list/tuple
- `unique`: Remove duplicates from a list/tuple, preserving order

**REQ-EXT-061**: Transformations shall be applied after extraction and before regex filtering.

**REQ-EXT-062**: Type conversions shall handle conversion errors gracefully, returning the original value on failure.

**REQ-EXT-063**: Collection operations shall only apply to appropriate data types (lists, tuples, strings) and return the original value for incompatible types.

## 8. Regular Expression Filtering

**REQ-EXT-070**: The system shall support regex filtering on extracted string values.

**REQ-EXT-071**: The regex filter shall extract the first matching group if groups are defined.

**REQ-EXT-072**: The regex filter shall extract the entire match if no groups are defined.

**REQ-EXT-073**: If regex doesn't match, the system shall log a warning and use the original value.

**REQ-EXT-074**: Regex filters shall be applied after transformations.

## 9. Array and Object Handling

**REQ-EXT-080**: When extracting with `[*]` wildcard, the system shall return a list of values.

**REQ-EXT-081**: When extracting with `.*` wildcard, the system shall return the entire object/dictionary.

**REQ-EXT-082**: Array elements shall be accessible by zero-based index.

**REQ-EXT-083**: Nested array access shall be supported: `items[0].subitems[1].name`

## 10. Namespace-Based Token Organization

**REQ-EXT-090**: All tokens extracted from an input file shall be organized under the namespace specified in the input configuration.

**REQ-EXT-091**: The namespace shall create a hierarchical token structure: `namespace.token_name`

**REQ-EXT-092**: If no token extraction rules are specified for an input file, all top-level keys shall be extracted under the namespace.

**REQ-EXT-093**: Namespaces prevent token collisions between different input files by design.

**REQ-EXT-094**: Each input file must specify a unique namespace; duplicate namespaces shall result in a validation error.

**REQ-EXT-095**: Example namespace-based extraction:
```yaml
inputs:
  - path: project.json
    namespace: project        # Creates 'project' namespace
    tokens:
      - name: version         # Accessible as: project.version
        key: app.version
      - name: name            # Accessible as: project.name
        key: app.name
```

## 11. Default Extraction

**REQ-EXT-100**: If no token extraction rules are specified, all top-level keys from the input file shall be extracted under the specified namespace.

**REQ-EXT-101**: Each top-level key shall become a token accessible as `namespace.key_name`.

**REQ-EXT-102**: Complex nested structures shall be preserved as dictionaries and lists within the namespace.

## 12. Error Handling

**REQ-EXT-110**: The system shall continue processing if an input file cannot be read, logging an error.

**REQ-EXT-111**: The system shall provide clear error messages including file path and error details.

**REQ-EXT-112**: The system shall validate file format before attempting to parse.

**REQ-EXT-113**: The system shall handle malformed data files gracefully with descriptive errors.

**REQ-EXT-114**: The system shall validate that all input files specify unique namespaces.

**REQ-EXT-115**: Duplicate namespace error message example:
```
ERROR: Duplicate namespace 'project' found in configuration
  First definition: project.json
  Duplicate definition: project-backup.json
  Solution: Use unique namespaces like 'project' and 'project_backup'
```

## 13. Token Organization

**REQ-EXT-120**: Tokens from all input files shall be organized in a hierarchical structure by namespace.

**REQ-EXT-121**: Namespace-based organization prevents accidental token collisions between input files.

**REQ-EXT-122**: Static tokens and namespaced tokens coexist without collision by using separate hierarchies or different top-level keys.

## 14. Examples

### JSON Extraction with Namespace
```json
{
  "project": {
    "name": "MyApp",
    "version": "1.0.0",
    "modules": [
      {"name": "core", "type": "library"},
      {"name": "ui", "type": "executable"}
    ]
  }
}
```

Configuration with namespace:
```yaml
inputs:
  - path: project.json
    namespace: app              # All tokens under 'app' namespace
    tokens:
      - name: name              # Accessible as: app.name
        key: project.name
      - name: version           # Accessible as: app.version
        key: project.version
      - name: module_names      # Accessible as: app.module_names
        key: project.modules[*].name
      - name: first_module      # Accessible as: app.first_module
        key: project.modules[0].*
```

Template usage:
```jinja2
# Application: {{ app.name }}
Version: {{ app.version }}
Modules: {{ app.module_names | join(', ') }}
```

### XML Extraction with Namespace
```xml
<configuration>
  <database host="localhost" port="5432">
    <name>mydb</name>
    <user>admin</user>
  </database>
</configuration>
```

Configuration with namespace:
```yaml
inputs:
  - path: database.xml
    namespace: db               # All tokens under 'db' namespace
    format: xml
    tokens:
      - name: host              # Accessible as: db.host
        key: database.@host
      - name: port              # Accessible as: db.port
        key: database.@port
      - name: name              # Accessible as: db.name
        key: database.name
      - name: user              # Accessible as: db.user
        key: database.user
```

Template usage:
```jinja2
DATABASE_HOST={{ db.host }}
DATABASE_PORT={{ db.port }}
DATABASE_NAME={{ db.name }}
DATABASE_USER={{ db.user }}
```

### Multiple Input Files Without Collision
```yaml
inputs:
  - path: project.json
    namespace: project
    tokens:
      - name: version           # project.version
        key: application.version
      - name: name              # project.name
        key: application.name

  - path: library.json
    namespace: library
    tokens:
      - name: version           # library.version (no collision!)
        key: library.version
      - name: name              # library.name (no collision!)
        key: library.name

  - path: build.yaml
    namespace: build
    # No tokens specified - extracts all top-level keys under 'build'
```

Template usage:
```jinja2
Project: {{ project.name }} v{{ project.version }}
Library: {{ library.name }} v{{ library.version }}
Build Type: {{ build.type }}
Build Date: {{ build.date }}
```
