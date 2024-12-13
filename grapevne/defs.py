from typing import List, Union, TypedDict


Namespace = Union[list, None, str, dict]


class SnakefileRemotePath(TypedDict):
    function: str
    args: List[str]
    kwargs: dict


Snakefile = Union[str, SnakefileRemotePath]


# Input port specification
class Port:
    def __init__(
        self,
        ref: str,
        label: str,
        namespace: str,
        mapping: list[dict[str, str]]
    ):
        """Initialise a Port object

        Args:
            ref (str): Port reference (used in Snakefile)
            label (str): Port label (displayed in UI)
            namespace (str): Incoming / input namespace
            mapping (list[dict[str, str]]): Nested structures {module: (str), port: (str)}
        """
        self.ref = ref
        self.label = label
        self.namespace = namespace
        self.mapping = mapping


class Module:
    def __init__(
        self,
        name: str,
        rulename: str,
        nodetype: str,
        snakefile: Snakefile = "",
        config=None,
        ports: [Port] = None,
        namespace: str = "",
        docstring: str = "",  # passthrough (unused in builds)
        # Backwards compatiblity list
        input_namespace: Namespace = None,
        output_namespace: Union[str, None] = None,
    ):
        """Initialise a Node object, the parent class for Modules

        Args:
            name (str): Name of the node
            rulename (str): Name of the rule
            nodetype (str): Type of node (module, connector, etc.)
            snakefile (str|dict): str location or dict representing function call
            config (dict): Configuration (parameters) for the Snakefile
            ports ([Port]): List of input ports
            namespace (str): Module namespace
        """

        self.name = name
        self.rulename = rulename
        self.nodetype = nodetype
        self.snakefile = snakefile
        self.config = {} if not config else config
        self.ports = [] if not ports else ports
        self.namespace = namespace

        # Backwards compatibility (input_namespace -> ports)
        if ports is not None and input_namespace is not None:
            raise ValueError(
                "Cannot specify both 'ports' and (legacy) 'input_namespace' in Module"
            )
        if input_namespace is not None:
            self.ports = get_port_spec(input_namespace)
        if "input_namespace" in self.config.keys():
            del self.config["input_namespace"]

        # Backwards compatibility (output_namespace -> namespace)
        if namespace is not None and output_namespace is not None:
            raise ValueError(
                "Cannot specify both 'namespace' and (legacy) 'output_namespace' in Module"
            )
        if output_namespace is not None:
            self.namespace = output_namespace
        if "output_namespace" in self.config.keys():
            del self.config["output_namespace"]

        if not isinstance(self.ports, list):
            raise ValueError(f"({self.name}): Ports must be a list, not {type(self.ports)}")


def get_port_spec(port: Union[str, dict, list, None]) -> Port:
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
        # Single input port (str)  - convert to dictionary for conversion
        port = {"in": port}
    if isinstance(port, dict):
        # First, check that the dictionary is not a new-form Port definition
        required_keys = ["ref", "label", "namespace"]
        if all(key in port for key in required_keys):
            # single dict (new format)
            return [port]
        new_ports = []
        for k, v in port.items():
            p = {
                "ref": k,
                "label": "In" if k == "in" else k,
                "namespace": v,
            }
            # Check for old-form node mapping and convert to new form
            if "$" in k:
                module, port = k.split('$')  # Only map one-connection deep
                p['mapping'] = [{
                    'module': module,
                    'port': port if port else "in",
                }]
            # Append port
            new_ports.append(p)
        return new_ports
    if isinstance(port, list):
        return port
    raise ValueError(f"Unknown port specification: {port}")


def get_ports(config):
    """Get ports specification from config

    Includes a backwards compatibility check for the legacy 'input_namespace'
    """
    ports = config.get("ports", config.get("input_namespace", None))
    return get_port_spec(ports)


def get_port_namespace(ports, port_ref=None):
    """Get the namespace for a given port reference"""
    ports = get_port_spec(ports)
    if port_ref is None:
        if len(ports) == 0:
            return []
        if len(ports) == 1:
            return ports[0]["namespace"]
        else:
            raise ValueError("Port reference required when multiple ports are present (ports: {ports})")
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
