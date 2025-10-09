from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindOpinionsOnNodeResponseMessage(HaiMessage):
    """Message containing opinions found on a specific node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, opinion_nodes: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphFindOpinionsOnNodeResponseMessage':
        """Create a message with opinions found on a specific node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_OPINIONS_ON_NODE_RESPONSE,
            payload={
                "node_id": node_id,
                "opinion_nodes": opinion_nodes,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @property
    def opinion_nodes(self) -> List[Dict]:
        """Get the list of opinion nodes from the payload"""
        return self.payload.get("opinion_nodes", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindOpinionsOnNodeResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            opinion_nodes=payload.get("opinion_nodes", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )