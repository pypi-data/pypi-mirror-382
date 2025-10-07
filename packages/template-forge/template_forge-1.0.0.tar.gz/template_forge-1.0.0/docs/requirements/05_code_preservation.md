# Code Preservation - Requirements

## 1. Purpose

**REQ-PRV-001**: The system shall support preserving custom code sections when regenerating files.

**REQ-PRV-002**: Preserved sections shall allow developers to add custom logic that survives regeneration.

**REQ-PRV-003**: The preservation mechanism shall work with any text-based output format.

## 2. Preservation Markers

**REQ-PRV-010**: The system shall use `@PRESERVE_START` as the start marker for preserved content.

**REQ-PRV-011**: The system shall use `@PRESERVE_END` as the end marker for preserved content.

**REQ-PRV-012**: Preservation markers shall be language-agnostic and work with any comment style.

**REQ-PRV-013**: Markers shall be case-sensitive: only `@PRESERVE_START` and `@PRESERVE_END` are recognized.

**REQ-PRV-014**: Each preserved block shall have a unique identifier: `@PRESERVE_START identifier`

## 3. Marker Syntax

**REQ-PRV-020**: Start markers shall follow the format: `@PRESERVE_START identifier`
- `identifier`: Unique name for the preserved block

**REQ-PRV-021**: End markers shall follow the format: `@PRESERVE_END identifier`
- `identifier`: Must match the start marker

**REQ-PRV-022**: Markers can be embedded in any comment syntax:
```
// @PRESERVE_START custom_logic     (C++, Java, JavaScript)
/* @PRESERVE_START custom_logic */  (C, CSS)
# @PRESERVE_START custom_logic      (Python, Shell, YAML)
<!-- @PRESERVE_START custom_logic -->(XML, HTML)
```

**REQ-PRV-023**: Whitespace around markers shall be ignored.

**REQ-PRV-024**: Markers shall appear on their own line (not inline with other code).

## 4. Content Preservation

**REQ-PRV-030**: When an output file already exists, the system shall extract all preserved content before regeneration.

**REQ-PRV-031**: Preserved content shall include everything between `@PRESERVE_START` and `@PRESERVE_END` markers, including the markers themselves.

**REQ-PRV-032**: Multiple preserved blocks can exist in a single file, each with a unique identifier.

**REQ-PRV-033**: Each preserved block identifier shall be unique within a file.

## 5. Content Injection

**REQ-PRV-040**: After template rendering, the system shall inject preserved content back into the new output.

**REQ-PRV-041**: Preserved content shall be injected into matching `@PRESERVE_START`/`@PRESERVE_END` blocks in the new output.

**REQ-PRV-042**: If a preserved block exists in the old file but not in the new template, it shall be discarded with a warning.

**REQ-PRV-043**: If a preserved block exists in the new template but not in the old file, it shall remain empty (template default).

**REQ-PRV-044**: Preserved content shall replace the entire block in the new output, including any template-generated placeholder content.

## 6. Block Matching

**REQ-PRV-050**: Preserved blocks shall be matched by their identifier marker.

**REQ-PRV-051**: A `@PRESERVE_START identifier` marker in the old file shall match the same `@PRESERVE_START identifier` marker in the new file.

**REQ-PRV-052**: Block identifiers shall be case-sensitive for matching purposes.

**REQ-PRV-053**: If a preserved block identifier exists in the old file but not in the new template, the system shall log a warning indicating the block will be lost.

## 7. Validation

**REQ-PRV-060**: The system shall validate that every `@PRESERVE_START` has a matching `@PRESERVE_END`.

**REQ-PRV-061**: The system shall reject nested preserved blocks with an error.

**REQ-PRV-062**: The system shall reject unmatched `@PRESERVE_END` markers (end without start).

**REQ-PRV-063**: The system shall reject unclosed `@PRESERVE_START` markers (start without end).

**REQ-PRV-064**: Validation errors shall include file path and line numbers.

## 8. Error Handling

**REQ-PRV-070**: If the existing file cannot be read, the system shall log a warning and proceed without preservation.

**REQ-PRV-071**: If preservation markers are malformed in the existing file, the system shall log an error and skip preservation.

**REQ-PRV-072**: Preservation errors shall not prevent template processing and file generation.

**REQ-PRV-073**: All preservation warnings and errors shall be logged with clear descriptions.

## 9. Template Guidelines

**REQ-PRV-080**: Templates should include empty preserved blocks where custom code is expected.

**REQ-PRV-081**: Preserved blocks should include helpful comments indicating their purpose.

**REQ-PRV-082**: Block identifiers must be descriptive and unique within the file: `custom_imports`, `user_methods`, `config_overrides`

**REQ-PRV-083**: Templates should not generate code inside preserved blocks that must be maintained.

**REQ-PRV-084**: When renaming a preserved block identifier in a template, users must manually update their existing files or content will be lost.

## 10. Use Cases

**REQ-PRV-090**: Support custom imports in generated source files.

**REQ-PRV-091**: Support custom methods/functions in generated classes.

**REQ-PRV-092**: Support custom configuration overrides in generated config files.

**REQ-PRV-093**: Support custom validation logic in generated code.

**REQ-PRV-094**: Support custom documentation sections in generated docs.

## 11. Examples

### Python Example

Template (`class.py.j2`):
```python
#!/usr/bin/env python3
"""{{ class_description }}"""

# Standard imports
import sys
import os

# @PRESERVE_START custom_imports
# Add your custom imports here
# @PRESERVE_END custom_imports

class {{ class_name }}:
    """{{ class_description }}"""
    
    def __init__(self):
        """Initialize {{ class_name }}."""
        self.name = "{{ class_name }}"
    
    # @PRESERVE_START custom_methods
    # Add your custom methods here
    # @PRESERVE_END custom_methods
```

First generation (output):
```python
#!/usr/bin/env python3
"""User management class"""

# Standard imports
import sys
import os

# @PRESERVE_START custom_imports
# Add your custom imports here
# @PRESERVE_END custom_imports

class UserManager:
    """User management class"""
    
    def __init__(self):
        """Initialize UserManager."""
        self.name = "UserManager"
    
    # @PRESERVE_START custom_methods
    # Add your custom methods here
    # @PRESERVE_END custom_methods
```

User adds custom code:
```python
#!/usr/bin/env python3
"""User management class"""

# Standard imports
import sys
import os

# @PRESERVE_START custom_imports
import json
import hashlib
from datetime import datetime
# @PRESERVE_END custom_imports

class UserManager:
    """User management class"""
    
    def __init__(self):
        """Initialize UserManager."""
        self.name = "UserManager"
    
    # @PRESERVE_START custom_methods
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_user(self, username: str) -> bool:
        """Validate username format."""
        return len(username) >= 3 and username.isalnum()
    # @PRESERVE_END custom_methods
```

Regeneration preserves custom code:
```python
#!/usr/bin/env python3
"""User management class - Updated"""  # Description changed

# Standard imports
import sys
import os

# @PRESERVE_START custom_imports
import json
import hashlib
from datetime import datetime
# @PRESERVE_END custom_imports
# ^ Custom imports preserved ^

class UserManager:
    """User management class - Updated"""
    
    def __init__(self):
        """Initialize UserManager."""
        self.name = "UserManager"
        self.version = "2.0"  # New field added by template
    
    # @PRESERVE_START custom_methods
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_user(self, username: str) -> bool:
        """Validate username format."""
        return len(username) >= 3 and username.isalnum()
    # @PRESERVE_END custom_methods
    # ^ Custom methods preserved ^
```

### C++ Example

Template:
```cpp
// {{ file_header }}

#include <iostream>
#include <string>

/* @PRESERVE_START custom_includes */
// Custom includes
/* @PRESERVE_END custom_includes */

class {{ class_name }} {
public:
    {{ class_name }}();
    ~{{ class_name }}();
    
    /* @PRESERVE_START custom_public_methods */
    // Custom public methods
    /* @PRESERVE_END custom_public_methods */

private:
    /* @PRESERVE_START custom_private_members */
    // Custom private members
    /* @PRESERVE_END custom_private_members */
};
```

### Configuration File Example

Template (`config.ini.j2`):
```ini
[application]
name = {{ app_name }}
version = {{ version }}

[database]
host = {{ db_host }}
port = {{ db_port }}

# @PRESERVE_START custom_config
# Add custom configuration here
# @PRESERVE_END custom_config
```

## 12. Limitations and Conditional Support

**REQ-PRV-100**: Preserved content cannot span across multiple files.

**REQ-PRV-101**: Preserved blocks may be conditionally included in templates using Jinja2 control structures.

**REQ-PRV-102**: When a preserved block is conditionally included, it shall only be processed when the condition evaluates to true.

**REQ-PRV-103**: If a conditional preserved block exists in the old file but the condition is false in the new generation, the system shall log a warning that the preserved content will be lost.

**REQ-PRV-104**: Example of conditional preserved blocks:
```jinja2
{% if deployment_type == 'docker' %}
# @PRESERVE_START docker_config
# Custom Docker configuration
# @PRESERVE_END docker_config
{% endif %}
```

**REQ-PRV-105**: Renaming preserved block identifiers requires manual updates to existing files to prevent content loss.
