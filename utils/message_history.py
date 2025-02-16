import json
from typing import Annotated, List, Self, get_args, get_origin
from pydantic_ai.messages import (
    ModelRequestPart, 
    ModelResponsePart, 
    ModelMessage, 
    ModelMessagesTypeAdapter,
    ModelRequest, 
    ModelResponse, 
)

# A wrapper around Pydantic AI History

class MessageHistory:
    def __init__(self):
        self.__messages: List[ModelMessage] = []

    def assign(self, messages: List[ModelMessage]) -> Self:
        self.__messages = messages
        return self

    def append(self, part: ModelMessage) -> Self:
        def get_raw_types(annotated_type):
            return get_args(get_args(annotated_type)[0]) if get_origin(annotated_type) is Annotated else get_args(annotated_type)

        model_request_parts = get_raw_types(ModelRequestPart)
        model_response_parts = get_raw_types(ModelResponsePart)

        if isinstance(part, model_request_parts):
            self.__messages.append(ModelRequest([part]))
            return self

        if isinstance(part, model_response_parts):
            self.__messages.append(ModelResponse([part]))
            return self

        raise TypeError(
            f"Invalid part type: {type(part).__name__}. "
            f"Expected one of: {', '.join([t.__name__ for t in model_request_parts + model_response_parts])}."
        )

    def remove_part_kind(self, part_kind:str) -> Self:
        for item in self.__messages:
            parts = item.parts.copy()
            for part in parts:
                if part.part_kind == part_kind:
                    item.parts.remove(part)
                                    
        return self

    def get_all_messages(self) -> List[ModelMessage]:
        return self.__messages

    def to_json(self, indent: int = None) -> str:
        return MessageHistory.messages_to_json(self.__messages, indent=indent)

    @staticmethod
    def messages_to_json(messages: List[ModelMessage], indent: int = None) -> str:
        json_str = ModelMessagesTypeAdapter.dump_json(messages)
        parsed_json = json.loads(json_str)
        pretty_json = json.dumps(parsed_json, indent=indent)
        
        return pretty_json
