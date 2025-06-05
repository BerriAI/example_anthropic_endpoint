from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def data_generator():
    response_id = uuid.uuid4().hex
    sentence = "Hello this is a test response from a fixed OpenAI endpoint."
    words = sentence.split(" ")
    for word in words:
        word = word + " "
        chunk = {
                    "id": f"chatcmpl-{response_id}",
                    "object": "chat.completion.chunk",
                    "created": 1677652288,
                    "model": "claude-3-5-sonnet-20241022",
                    "choices": [{"index": 0, "delta": {"content": word}}],
                }
        try:
            yield f"data: {json.dumps(chunk.dict())}\n\n"
        except:
            yield f"data: {json.dumps(chunk)}\n\n"


def large_data_generator():
    """Generate a large streaming response with 100 chunks in Anthropic format"""
    message_id = f"msg_{uuid.uuid4().hex}"
    
    for i in range(100):
        # Create varied content for each chunk
        if i % 50 == 0:
            content = f"\n\n--- Chunk {i+1} of 100 ---\n"
        elif i % 10 == 0:
            content = f" [Milestone {i+1}] "
        else:
            content = f"Chunk_{i+1:03d} "
        content = content * 10
        
        # Anthropic streaming format
        chunk = {
            "type": "content_block_delta",
            "index": 0,
            "delta": {
                "type": "text_delta",
                "text": content
            },
            "model": "claude-3-7-sonnet-latest"
        }
        
        yield f"data: {json.dumps(chunk)}\n\n"
    
    # Send final chunk to indicate completion
    final_chunk = {
        "type": "message_stop"
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"


# for completion
@app.post("/v1/messages")
async def completion(request: Request):
    data = await request.json()
    import time
    time.sleep(55)

    if data.get("stream") == True:
        return StreamingResponse(
            content=data_generator(),
            media_type="text/event-stream",
        )
    else:
        response = {
            "id": "msg_01G7MsdWPT2JZMUuc1UXRavn",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                "type": "text",
                "text": "I'm sorry, but the string of characters \"123450000s0 p kk\" doesn't appear to have any clear meaning or context. It seems to be a random combination of numbers and letters. If you could provide more information or clarify what you're trying to communicate, I'll do my best to assist you."
                }
            ],
            "model": "claude-3-5-sonnet-20241022",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 17,
                "output_tokens": 71
            }
        }

        return response


@app.post("/large-stream/v1/messages")
async def large_stream(request: Request):
    """Endpoint that returns a large streaming response with 450 chunks"""
    data = await request.json()
    
    # Always return streaming response for this large stream endpoint
    # But you could check data.get("stream") if you want to make it conditional
    return StreamingResponse(
        content=large_data_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8093)