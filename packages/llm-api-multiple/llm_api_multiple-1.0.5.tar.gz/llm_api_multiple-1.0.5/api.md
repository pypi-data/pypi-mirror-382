# Chat

Methods:

- <code title="post /chat/completions">client.chat.<a href="./src/llm_api/resources/chat.py">create_completion</a>(\*\*<a href="src/llm_api/types/chat_create_completion_params.py">params</a>) -> object</code>

# Audio

Methods:

- <code title="post /audio/transcriptions">client.audio.<a href="./src/llm_api/resources/audio.py">create_transcription</a>(\*\*<a href="src/llm_api/types/audio_create_transcription_params.py">params</a>) -> object</code>

# Images

Methods:

- <code title="post /images/generations">client.images.<a href="./src/llm_api/resources/images.py">generate</a>(\*\*<a href="src/llm_api/types/image_generate_params.py">params</a>) -> object</code>

# Models

Methods:

- <code title="get /models/{model_id}">client.models.<a href="./src/llm_api/resources/models.py">retrieve</a>(model_id) -> object</code>
- <code title="get /models">client.models.<a href="./src/llm_api/resources/models.py">list</a>() -> object</code>

# Files

Methods:

- <code title="get /files/{file_id}">client.files.<a href="./src/llm_api/resources/files.py">retrieve</a>(file_id) -> object</code>
- <code title="get /files">client.files.<a href="./src/llm_api/resources/files.py">list</a>(\*\*<a href="src/llm_api/types/file_list_params.py">params</a>) -> object</code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/llm_api/resources/files.py">delete</a>(file_id) -> object</code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/llm_api/resources/files.py">download_content</a>(file_id) -> object</code>
- <code title="post /files">client.files.<a href="./src/llm_api/resources/files.py">upload</a>(\*\*<a href="src/llm_api/types/file_upload_params.py">params</a>) -> object</code>

# Batches

Types:

```python
from llm_api.types import BatchCreateResponse, BatchCancelResponse
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/llm_api/resources/batches.py">create</a>(\*\*<a href="src/llm_api/types/batch_create_params.py">params</a>) -> <a href="./src/llm_api/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batches/{batch_id}">client.batches.<a href="./src/llm_api/resources/batches.py">retrieve</a>(batch_id) -> object</code>
- <code title="get /batches">client.batches.<a href="./src/llm_api/resources/batches.py">list</a>(\*\*<a href="src/llm_api/types/batch_list_params.py">params</a>) -> object</code>
- <code title="post /batches/{batch_id}/cancel">client.batches.<a href="./src/llm_api/resources/batches.py">cancel</a>(batch_id) -> <a href="./src/llm_api/types/batch_cancel_response.py">BatchCancelResponse</a></code>
