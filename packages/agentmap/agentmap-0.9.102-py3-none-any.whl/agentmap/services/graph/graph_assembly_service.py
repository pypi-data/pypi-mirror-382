from typing import Any, Callable, Dict, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

from agentmap.models.graph import Graph
from agentmap.services.config.app_config_service import AppConfigService
from agentmap.services.features_registry_service import FeaturesRegistryService
from agentmap.services.function_resolution_service import FunctionResolutionService
from agentmap.services.graph.graph_factory_service import GraphFactoryService
from agentmap.services.logging_service import LoggingService
from agentmap.services.protocols import OrchestrationCapableAgent
from agentmap.services.state_adapter_service import StateAdapterService


class GraphAssemblyService:
    def __init__(
        self,
        app_config_service: AppConfigService,
        logging_service: LoggingService,
        state_adapter_service: StateAdapterService,
        features_registry_service: FeaturesRegistryService,
        function_resolution_service: FunctionResolutionService,
        graph_factory_service: GraphFactoryService,
        orchestrator_service: Any,  # OrchestratorService
    ):
        self.config = app_config_service
        self.logger = logging_service.get_class_logger(self)
        self.functions_dir = self.config.get_functions_path()
        self.state_adapter = state_adapter_service
        self.features_registry = features_registry_service
        self.function_resolution = function_resolution_service
        self.graph_factory_service = graph_factory_service
        self.orchestrator_service = orchestrator_service

        # Get state schema from config or default to dict
        state_schema = self._get_state_schema_from_config()
        self.builder = StateGraph(state_schema=state_schema)
        self.orchestrator_nodes = []
        self.orchestrator_node_registry: Optional[Dict[str, Any]] = None
        self.injection_stats = {
            "orchestrators_found": 0,
            "orchestrators_injected": 0,
            "injection_failures": 0,
        }

    def _get_state_schema_from_config(self):
        """
        Get state schema from configuration.

        Returns:
            State schema type (dict, pydantic model, or other LangGraph-compatible schema)
        """
        try:
            # Try to get state schema configuration
            execution_config = self.config.get_execution_config()
            state_schema_config = execution_config.get("graph", {}).get(
                "state_schema", "dict"
            )

            if state_schema_config == "dict":
                return dict
            elif state_schema_config == "pydantic":
                # Try to import pydantic and return BaseModel or a custom model
                try:
                    from pydantic import BaseModel

                    # Could be configured to use a specific model class
                    model_class = execution_config.get("graph", {}).get(
                        "state_model_class"
                    )
                    if model_class:
                        # Would need to dynamically import the specified class
                        # For now, return BaseModel as a safe default
                        return BaseModel
                    return BaseModel
                except ImportError:
                    self.logger.warning(
                        "Pydantic requested but not available, falling back to dict"
                    )
                    return dict
            else:
                # Custom state schema - would need specific handling
                self.logger.warning(
                    f"Unknown state schema type '{state_schema_config}', falling back to dict"
                )
                return dict

        except Exception as e:
            self.logger.debug(
                f"Could not read state schema from config: {e}, using dict"
            )
            return dict

    def assemble_graph(
        self,
        graph: Graph,
        agent_instances: Dict[str, Any],
        orchestrator_node_registry: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Assemble an executable LangGraph from a Graph domain model.

        Args:
            graph: Graph domain model with nodes and configuration
            agent_instances: Dictionary mapping node names to agent instances
            node_registry: Optional node registry for orchestrator injection

        Returns:
            Compiled executable graph

        Raises:
            ValueError: If graph has no nodes or missing agent instances
        """
        self.logger.info(f"🚀 Starting graph assembly: '{graph.name}'")

        # Validate graph has nodes
        if not graph.nodes:
            raise ValueError(f"Graph '{graph.name}' has no nodes")

        # Create fresh StateGraph builder for each compilation to avoid LangGraph conflicts
        state_schema = self._get_state_schema_from_config()
        self.builder = StateGraph(state_schema=state_schema)
        self.orchestrator_nodes = []
        self.injection_stats = {
            "orchestrators_found": 0,
            "orchestrators_injected": 0,
            "injection_failures": 0,
        }

        self.orchestrator_node_registry = orchestrator_node_registry

        # Add all nodes and process their edges
        node_names = list(graph.nodes.keys())

        self.logger.debug(f"Processing {len(node_names)} nodes: {node_names}")

        # ENSURE consistent entry point using factory (in case graph doesn't have one)
        if not graph.entry_point:
            graph.entry_point = self.graph_factory_service.detect_entry_point(graph)
            self.logger.debug(f"🚪 Factory detected entry point: '{graph.entry_point}'")
        else:
            self.logger.debug(
                f"🚪 Using pre-existing graph entry point: '{graph.entry_point}'"
            )

        for node_name, node in graph.nodes.items():
            # Get agent instance from the provided agent_instances dictionary
            if node_name not in agent_instances:
                raise ValueError(f"No agent instance found for node: {node_name}")
            agent_instance = agent_instances[node_name]
            self.add_node(
                node_name, agent_instance
            )  # detects orchestrator nodes and adds to self.orchestrator_nodes
            self.process_node_edges(node_name, node.edges)

        # Set entry point
        if graph.entry_point:
            self.builder.set_entry_point(graph.entry_point)
            self.logger.debug(f"🚪 Set entry point: '{graph.entry_point}'")

        # Add dynamic routers for orchestrator nodes
        if self.orchestrator_nodes:
            self.logger.debug(
                f"Adding dynamic routers for {len(self.orchestrator_nodes)} orchestrator nodes"
            )
            for orch_node_name in self.orchestrator_nodes:
                # Get the node's failure edge if it exists
                node = graph.nodes.get(orch_node_name)
                failure_target = node.edges.get("failure") if node else None
                self._add_dynamic_router(orch_node_name, failure_target)

        # Compile and return the executable LangGraph
        compiled_graph = self.builder.compile()
        self.logger.debug(f"✅ Graph '{graph.name}' compiled successfully")
        return compiled_graph

    def assemble_with_checkpoint(
        self,
        graph: Graph,
        agent_instances: Dict[str, Any],
        node_definitions: Optional[Dict[str, Any]] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
    ) -> Any:
        """
        Assemble an executable LangGraph with checkpoint support.

        This method creates a graph with checkpoint capability for pause/resume functionality.

        Args:
            graph: Graph domain model with nodes and configuration
            agent_instances: Dictionary mapping node names to agent instances
            node_definitions: Optional node registry for orchestrator injection
            checkpointer: Checkpoint service for state persistence

        Returns:
            Compiled executable graph with checkpoint support

        Raises:
            ValueError: If graph has no nodes or missing agent instances
        """
        self.logger.info(
            f"🚀 Starting checkpoint-enabled graph assembly: '{graph.name}'"
        )

        # Validate graph has nodes
        if not graph.nodes:
            raise ValueError(f"Graph '{graph.name}' has no nodes")

        # Create fresh StateGraph builder for each compilation to avoid LangGraph conflicts
        state_schema = self._get_state_schema_from_config()
        self.builder = StateGraph(state_schema=state_schema)
        self.orchestrator_nodes = []
        self.injection_stats = {
            "orchestrators_found": 0,
            "orchestrators_injected": 0,
            "injection_failures": 0,
        }

        self.orchestrator_node_registry = node_definitions

        # Add all nodes and process their edges (same as standard assembly)
        node_names = list(graph.nodes.keys())
        self.logger.debug(
            f"Processing {len(node_names)} nodes with checkpoint support: {node_names}"
        )

        # ENSURE consistent entry point using factory (in case graph doesn't have one)
        if not graph.entry_point:
            graph.entry_point = self.graph_factory_service.detect_entry_point(graph)
            self.logger.debug(f"🚪 Factory detected entry point: '{graph.entry_point}'")
        else:
            self.logger.debug(
                f"🚪 Using pre-existing graph entry point: '{graph.entry_point}'"
            )

        for node_name, node in graph.nodes.items():
            # Get agent instance from the provided agent_instances dictionary
            if node_name not in agent_instances:
                raise ValueError(f"No agent instance found for node: {node_name}")
            agent_instance = agent_instances[node_name]
            self.add_node(node_name, agent_instance)
            self.process_node_edges(node_name, node.edges)

        # Set entry point
        if graph.entry_point:
            self.builder.set_entry_point(graph.entry_point)
            self.logger.debug(f"🚪 Set entry point: '{graph.entry_point}'")

        # Add dynamic routers for orchestrator nodes
        if self.orchestrator_nodes:
            self.logger.debug(
                f"Adding dynamic routers for {len(self.orchestrator_nodes)} orchestrator nodes"
            )
            for orch_node_name in self.orchestrator_nodes:
                # Get the node's failure edge if it exists
                node = graph.nodes.get(orch_node_name)
                failure_target = node.edges.get("failure") if node else None
                self._add_dynamic_router(orch_node_name, failure_target)

        # Compile with checkpoint support
        if checkpointer:
            compiled_graph = self.builder.compile(checkpointer=checkpointer)
            self.logger.debug(
                f"✅ Graph '{graph.name}' compiled with checkpoint support"
            )
        else:
            compiled_graph = self.builder.compile()
            self.logger.debug(
                f"✅ Graph '{graph.name}' compiled without checkpoint support"
            )

        return compiled_graph

    def add_node(self, name: str, agent_instance: Any) -> None:
        """
        Add a node to the graph with its agent instance.

        Args:
            name: Node name
            agent_instance: Agent instance with run method
        """
        self.builder.add_node(name, agent_instance.run)
        class_name = agent_instance.__class__.__name__

        if isinstance(agent_instance, OrchestrationCapableAgent):
            self.orchestrator_nodes.append(name)
            self.injection_stats["orchestrators_found"] += 1
            try:
                # Configure orchestrator service (always available)
                agent_instance.configure_orchestrator_service(self.orchestrator_service)

                # Configure node registry if available
                if self.orchestrator_node_registry:
                    agent_instance.node_registry = self.orchestrator_node_registry
                    self.logger.debug(
                        f"✅ Injected orchestrator service and node registry into '{name}'"
                    )
                else:
                    self.logger.debug(
                        f"✅ Injected orchestrator service into '{name}' (no node registry available)"
                    )

                self.injection_stats["orchestrators_injected"] += 1
            except Exception as e:
                self.injection_stats["injection_failures"] += 1
                error_msg = f"Failed to inject orchestrator service into '{name}': {e}"
                self.logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg) from e

        self.logger.debug(f"🔹 Added node: '{name}' ({class_name})")

    def process_node_edges(self, node_name: str, edges: Dict[str, str]) -> None:
        """
        Process edges for a node and add them to the graph.

        Args:
            node_name: Source node name
            edges: Dictionary of edge conditions to target nodes
        """
        # For orchestrator nodes, we handle edges differently
        # They use dynamic routing for main flow but may have failure edges
        if node_name in self.orchestrator_nodes:
            # Only process failure edges for orchestrator nodes
            if edges and "failure" in edges:
                failure_target = edges["failure"]
                self.logger.debug(
                    f"Adding failure edge for orchestrator '{node_name}' → {failure_target}"
                )
                # We'll handle this in the dynamic router
            return

        if not edges:
            return

        self.logger.debug(
            f"Processing edges for node '{node_name}': {list(edges.keys())}"
        )

        has_func = False
        for condition, target in edges.items():
            func_ref = self.function_resolution.extract_func_ref(target)
            if func_ref:
                success = edges.get("success")
                failure = edges.get("failure")
                self._add_function_edge(node_name, func_ref, success, failure)
                has_func = True
                break

        if not has_func:
            if "success" in edges and "failure" in edges:
                self._add_success_failure_edge(
                    node_name, edges["success"], edges["failure"]
                )
            elif "success" in edges:

                def success_only(state):
                    return (
                        edges["success"]
                        if state.get("last_action_success", True)
                        else None
                    )

                self._add_conditional_edge(node_name, success_only)
            elif "failure" in edges:

                def failure_only(state):
                    return (
                        edges["failure"]
                        if not state.get("last_action_success", True)
                        else None
                    )

                self._add_conditional_edge(node_name, failure_only)
            elif "default" in edges:
                self.builder.add_edge(node_name, edges["default"])
                self.logger.debug(f"[{node_name}] → default → {edges['default']}")

    def _add_conditional_edge(self, source: str, func: Callable) -> None:
        """Add a conditional edge to the graph."""
        self.builder.add_conditional_edges(source, func)
        self.logger.debug(f"[{source}] → conditional edge added")

    def _add_success_failure_edge(
        self, source: str, success: str, failure: str
    ) -> None:
        """Add success/failure conditional edges."""

        def branch(state):
            return success if state.get("last_action_success", True) else failure

        self.builder.add_conditional_edges(source, branch)
        self.logger.debug(f"[{source}] → success → {success} / failure → {failure}")

    def _add_function_edge(
        self,
        source: str,
        func_name: str,
        success: Optional[str],
        failure: Optional[str],
    ) -> None:
        """Add function-based routing edge."""
        func = self.function_resolution.load_function(func_name)

        def wrapped(state):
            return func(state, success, failure)

        self.builder.add_conditional_edges(source, wrapped)
        self.logger.debug(f"[{source}] → routed by function '{func_name}'")

    def _add_dynamic_router(
        self, node_name: str, failure_target: Optional[str] = None
    ) -> None:
        """Add dynamic routing for orchestrator nodes.

        Args:
            node_name: Name of the orchestrator node
            failure_target: Optional failure target node
        """
        self.logger.debug(f"[{node_name}] → adding dynamic router for orchestrator")
        if failure_target:
            self.logger.debug(f"  Failure target: {failure_target}")

        def dynamic_router(state):
            # First check if there was an error/failure
            if failure_target:
                last_success = self.state_adapter.get_value(
                    state, "last_action_success", True
                )
                if not last_success:
                    self.logger.debug(
                        f"Orchestrator '{node_name}' routing to failure target: {failure_target}"
                    )
                    return failure_target

            # Normal dynamic routing based on __next_node
            next_node = self.state_adapter.get_value(state, "__next_node")
            if next_node:
                # Clear the __next_node to prevent infinite loops
                self.state_adapter.set_value(state, "__next_node", None)
                # Return the next node without validation
                # The orchestrator may route to nodes passed dynamically at runtime
                self.logger.debug(f"Orchestrator '{node_name}' routing to: {next_node}")
                return next_node

            # No next_node set
            return None

        # For orchestrators, we need to handle dynamic routing differently
        # The orchestrator can route to ANY node, including ones passed at runtime
        # So we use a path_map=None to allow any destination
        self.builder.add_conditional_edges(
            node_name, dynamic_router, path_map=None  # Allow any destination
        )

        self.logger.debug(f"[{node_name}] → dynamic router added with open routing")

    def get_injection_summary(self) -> Dict[str, int]:
        """Get summary of registry injection statistics."""
        return self.injection_stats.copy()
