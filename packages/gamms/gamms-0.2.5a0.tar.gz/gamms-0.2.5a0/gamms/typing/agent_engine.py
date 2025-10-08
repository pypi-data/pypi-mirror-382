from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Optional, Callable, Tuple
from gamms.typing.sensor_engine import ISensor

from enum import IntEnum

class AgentType(IntEnum):
    """
    Enum representing different types of agents.
    """
    BASIC = 0
    AERIAL = 1

class IAgent(ABC):
    """
    Abstract base class representing an agent in the system.

    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name identifier of the agent.
        """
        pass
    
    @property
    @abstractmethod
    def current_node_id(self) -> int:
        """
        Get the current node ID of the agent.
        """
        pass
    
    @property
    @abstractmethod
    def prev_node_id(self) -> int:
        """
        Get the previous node ID of the agent.
        """
        pass

    @property
    @abstractmethod
    def type(self) -> AgentType:
        """
        Get the type of the agent.
        
        Returns:
            AgentType: The type of the agent (e.g., BASIC, AERIAL).
        """
        pass

    @property
    @abstractmethod
    def orientation(self) -> Tuple[float, float]:
        """
        Get the orientation of the agent.

        Returns:
            Tuple[float, float]: The current orientation of the agent.
        """
        pass
    
    @property
    @abstractmethod
    def state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.

        Returns:
            Dict[str, Any]: The current state data of the agent.
        """
        pass

    @property
    @abstractmethod
    def strategy(self) -> Optional[Callable[[Dict[str, Any]], None]]:
        """
        Get the current strategy of the agent.

        Returns:
            Optional[Callable[[Dict[str, Any]], None]]: The current strategy function or None if no strategy is set.
        """
        pass

    @abstractmethod
    def step(self):
        """
        Execute a single operational step of the agent.

        This method should contain the logic that defines the agent's behavior
        during one iteration or time step in the system.
        """
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Retrieve the current state of the agent.

        Returns:
            Dict[str, Any]: The current state data of the agent, structure depends on implementation.
        """
        pass

    @abstractmethod
    def set_state(self):
        """
        Update the agent's state.

        Raises:
            KeyError: If action is not found in the agent's state.
            KeyError: If action is an int but not a valid node ID.
            TypeError: If action is not an int or dict.
            ValueError: If action dict does not contain 'node_id' key
            ValueError: If orientation is not a tuple of (sin, cos).
        """
        pass

    @abstractmethod
    def register_sensor(self, name: str, sensor: ISensor):
        """
        Register a sensor with the agent.

        Sensors can be used by the agent to perceive the environment or gather data.

        Args:
            name (str): The unique name identifier for the sensor.
            sensor (ISensor): The sensor instance or object to be registered.
        """
        pass

    @abstractmethod
    def deregister_sensor(self, name: str):
        """
        Deregister a sensor from the agent.

        Args:
            name (str): The unique name identifier for the sensor to be deregistered.
        """
        pass

    @abstractmethod
    def register_strategy(self, strategy: Callable[[Dict[str, Any]], None]):
        """
        Register a strategy with the agent.

        Strategies define the decision-making or action-planning mechanisms for the agent.

        Args:
            strategy (Callable[[Dict[str, Any]], None]): The strategy instance or object to be registered.
        """
        pass


class IAerialAgent(IAgent):
    """
    Abstract base class representing an aerial agent in the system.

    This class extends the basic agent functionality to include aerial-specific behaviors.

    Requires a start node ID and speed for initialization.
    """

    @property
    @abstractmethod
    def quat(self) -> Tuple[float, float, float, float]:
        """
        Get the quaternion representation of the agent's orientation.
        Formatted as (w, x, y, z).

        Returns:
            Tuple[float, float, float, float]: The quaternion representing the agent's orientation.
        """
        pass

    @property
    @abstractmethod
    def orientation(self) -> Tuple[float, float]:
        """
        Get the orientation of the agent in the x-y plane.

        Returns:
            Tuple[float, float]: The current orientation of the agent as a tuple (sin, cos).
        """
        pass

    @property
    @abstractmethod
    def position(self) -> Tuple[float, float, float]:
        """
        Get the current position of the agent in 3D space.

        Returns:
            Tuple[float, float, float]: The current position of the agent as a tuple (x, y, z).
        """
        pass

    @abstractmethod
    def set_state(self):
        """
        Update the agent's position and orientation.
        Action should be a 3d direction tuple. It will be normalized to a unit vector and multiplied by the agent's speed.

        Action can also be a dictionary with 'direction' key to specify the direction and have 'quat' key to specify the quaternion orientation.

        Raises:
            KeyError: If action is not found in the agent's state.
            TypeError: If action is not a tuple or dict.
            ValueError: If action dict does not contain 'direction' key
            ValueError: If quat is not a tuple of (w, x, y, z).
        """
        pass


class IAgentEngine(ABC):
    """
    Abstract base class representing the engine that manages agents.

    The engine is responsible for creating, managing, and terminating agents,
    as well as facilitating interactions between them.
    """

    @abstractmethod
    def create_iter(self) -> Iterable[IAgent]:
        """
        Create an iterator for processing agent steps.

        Returns:
            Iterable[IAgent]: An iterator object over all agents.
        """
        pass

    @abstractmethod
    def create_agent(self, name:str, **kwargs: Dict[str, Any]) -> IAgent:
        """
        Instantiate a new agent within the engine.

        Args:
            name (str): The unique name identifier for the agent.
            **kwargs: Additional keyword arguments for agent initialization.

        Returns:
            IAgent: The newly created agent instance.
        
        Raises:
            ValueError: If an agent with the same name already exists.
            KeyError: If start_node_id is not provided in kwargs.
        """
        pass

    @abstractmethod
    def terminate(self):
        """
        Terminate the agent engine and perform necessary cleanup operations.

        This method should ensure that all resources are properly released and
        that agents are gracefully shut down.
        """
        pass

    @abstractmethod
    def get_agent(self, name: str) -> IAgent:
        """
        Retrieve an agent by its name.

        Args:
            name (str): The unique name identifier of the agent to retrieve.

        Returns:
            IAgent: The agent instance corresponding to the provided name.

        Raises:
            KeyError: If no agent with the specified name exists.
        """
        pass

    @abstractmethod
    def delete_agent(self, name: str) -> None:
        """
        Delete an agent by its name.

        Args:
            name (str): The unique name identifier of the agent to retrieve.

        Returns:
            None

        Raises:
            Logs a warning and does nothing if no agent with the specified name exists.
        """
        pass
    




