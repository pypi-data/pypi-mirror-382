from typing import Any,Dict
import re
import inspect

def parse_google_docstring(docstring: str) -> Dict[str, Any]:
    """
    解析Google风格的docstring
    
    格式示例:
    ```
    这是函数的简短描述。
    
    这里可以有更详细的描述。
    
    Args:
        param1 (str): 参数1的描述
        param2 (int, optional): 参数2的描述. Defaults to 0.
        param3 (str): 参数3的描述. Enum: ["option1", "option2"]
        
    Returns:
        str: 返回值描述
    ```
    
    Args:
        docstring: 要解析的docstring
        
    Returns:
        包含描述和参数信息的字典
    """
    if not docstring:
        return {
            'description': '',
            'args': {},
            'returns': ''
        }
    
    lines = docstring.split('\n')
    
    description_lines = []
    args_section = []
    returns_section = []
    
    current_section = 'description'
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Args:'):
            current_section = 'args'
            continue
        elif line.startswith('Returns:'):
            current_section = 'returns'
            continue
        elif line.startswith('Raises:') or line.startswith('Examples:') or line.startswith('Note:'):
            current_section = 'other'
            continue
        
        if current_section == 'description' and line:
            description_lines.append(line)
        elif current_section == 'args' and line:
            args_section.append(line)
        elif current_section == 'returns' and line:
            returns_section.append(line)
    
    description = ' '.join(description_lines)
    
    args_info = {}
    current_arg = None
    
    for line in args_section:
        param_match = re.match(r'(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+)', line)
        
        if param_match:
            param_name = param_match.group(1)
            param_type = param_match.group(2) or 'any'
            param_desc = param_match.group(3)
            
            enum_match = re.search(r'Enum:\s*\[([^\]]+)\]', param_desc)
            enum_values = None
            if enum_match:
                enum_str = enum_match.group(1)
                enum_values = [v.strip().strip('"\'') for v in enum_str.split(',')]
                param_desc = re.sub(r'\s*Enum:\s*\[[^\]]+\]', '', param_desc)
            
            args_info[param_name] = {
                'type': param_type,
                'description': param_desc.strip(),
                'enum': enum_values
            }
            current_arg = param_name
        elif current_arg and line:
            args_info[current_arg]['description'] += ' ' + line
    
    return {
        'description': description,
        'args': args_info,
        'returns': ' '.join(returns_section)
    }

def python_type_to_json_type(py_type: Any) -> str:
    if py_type == inspect.Parameter.empty:
        return "string"
    
    type_str = str(py_type)
    
    type_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object',
        'List': 'array',
        'Dict': 'object',
    }
    
    for py_name, json_name in type_mapping.items():
        if py_name in type_str:
            return json_name
    
    return "string"