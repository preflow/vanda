from jinja2 import Environment, nodes, meta

def extract_jinja2_variables_with_defaults(template_content):
    """
    Extract all variables and their default values from a Jinja2 template.

    Args:
        template_content (str): The Jinja2 template as a string.

    Returns:
        dict: A dictionary with keys:
            - 'all_variables': A set of all variable names found in the template.
            - 'variables_with_defaults': A dictionary of variables with their default values.
    """
    # Create a Jinja2 environment
    env = Environment()

    # Parse the template
    parsed_content = env.parse(template_content)

    # Extract all variables
    all_variables = meta.find_undeclared_variables(parsed_content)

    # Extract variables with default values
    variables_with_defaults = {}

    def extract_defaults(node):
        """
        Recursively extract variables with default filters and their values.
        """
        if isinstance(node, nodes.Filter) and node.name == 'default':
            # Extract variable name and default value
            var_name = node.node.name if isinstance(node.node, nodes.Name) else None
            default_value = (
                node.args[0].as_const() if node.args and isinstance(node.args[0], nodes.Const) else None
            )
            if var_name and default_value is not None:
                variables_with_defaults[var_name] = default_value
        elif hasattr(node, 'body'):  # Recursively check child nodes
            for child_node in node.body:
                extract_defaults(child_node)
        elif hasattr(node, 'nodes'):  # For nodes with nested child nodes
            for child_node in node.nodes:
                extract_defaults(child_node)

    # Start extracting defaults from the parsed template
    extract_defaults(parsed_content)

    return {
        'all_variables': all_variables,
        'variables_with_defaults': variables_with_defaults
    }

# Example usage
template_content = """
services:
    api:
        image: python:3.8
        container_name: vanda_client_redis
        environment:
            - REDIS_HOST={{ redis_host | default('localhost') }}
            - REDIS_PORT={{ redis_port | default(6379) }}
            - REDIS_DB={{ redis_db | default(0) }}
            - REDIS_PASSWORD={{ redis_password }}
{% if redis_network %}
networks:
    default:
        external:
            name: {{ redis_network }}
{% endif %}
"""

result = extract_jinja2_variables_with_defaults(template_content)

print("All Variables:", result['all_variables'])
print("Variables with Defaults:", result['variables_with_defaults'])

print("------")
print(list(result['all_variables']))
