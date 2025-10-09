from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphGetSchemaRequestMessage(HaiMessage):
    """Message to request the graph database schema"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'GraphGetSchemaRequestMessage':
        """Create a message requesting to get the graph schema"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_SCHEMA,
            payload={}
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetSchemaRequestMessage':
        """Create a GraphGetSchemaRequestMessage from a HaiMessage"""
        return cls.create_message()
