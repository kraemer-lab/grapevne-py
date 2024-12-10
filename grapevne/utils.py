from typing import Union


def get_port_spec(port: Union[str, dict, list, None]):
    """Input port specification

    Utility function to convert shorthand input port specifications to their full
    format. Always returns a list.

    Port specification:
        [
            {
                ref: (required; str),       # Port reference (used in Snakefile)
                label: (required; str),
                namespace: (required; str), # Namespace link (incoming)

                # Used for composite modules:
                mapping: [
                    {                       #   Target module
                        module: (str),      #     target module name / reference
                        port: (str),        #     target port reference

                    },
                    ...
                ],
            },
            ...
        ]

    Shorthand specifications:
        null    No input ports
        str     Single input port
        dict    Multiple or named input ports, with port names as keys and
                namespaces as values
    """

    if port is None:
        # No input ports (null)
        return []
    if isinstance(port, str):
        # Single input port (str)
        return [{"ref": "in", "label": "In", "namespace": port}]
    if isinstance(port, dict):
        required_keys = ["ref", "label", "namespace"]
        if all(key in port for key in required_keys):
            # single dict (new format)
            return [port]
        else:
            return [{"ref": k, "label": k, "namespace": v} for k, v in port.items()]
    if isinstance(port, list):
        return port
    raise ValueError(f"Unknown port specification: {port}")


def get_ports(config):
    """Get ports specification from config

    Includes a backwards compatibility check for the legacy 'input_namespace'
    """
    ports = config.get("ports", None)
    if ports is None:  # Shorthand / backwards compatibility
        ports = config.get("input_namespace", None)
    return get_port_spec(ports)


def get_port_namespace(ports, port_ref):
    """Get the namespace for a given port reference"""
    for port in ports:
        if port["ref"] == port_ref:
            return port["namespace"]
    raise ValueError(f"Port not found: {port_ref}")


def get_namespace(config):
    """Return the module's namespace

    Includes a backwards compatibility check for the legacy 'output_namespace'
    """
    namespace = None
    if config:
        namespace = config.get("namespace", None)
        if namespace is None:
            # Backwards compatibility
            namespace = config.get("output_namespace", None)
    return namespace
