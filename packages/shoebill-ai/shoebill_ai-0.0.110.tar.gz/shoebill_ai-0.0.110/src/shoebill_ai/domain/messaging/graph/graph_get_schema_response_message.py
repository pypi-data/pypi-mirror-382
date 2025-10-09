from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphGetSchemaResponseMessage(HaiMessage):
    """Response message containing the graph database schema"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(
        cls,
        schema: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None
    ) -> 'GraphGetSchemaResponseMessage':
        """Create a response message with the graph schema"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_SCHEMA_RESPONSE,
            payload={
                "schema": schema,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def schema(self) -> Dict[str, Any]:
        """Get the schema from the payload"""
        return self.payload.get("schema", {})

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetSchemaResponseMessage':
        payload = message.payload
        return cls.create_message(
            schema=payload.get("schema", {}),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )
