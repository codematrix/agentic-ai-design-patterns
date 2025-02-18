from pydantic_ai.result import StreamedRunResult

class Utils:
    @staticmethod
    async def stream_result_async(result: StreamedRunResult): 
        async for message in result.stream_text(delta=True):  
            yield message 
