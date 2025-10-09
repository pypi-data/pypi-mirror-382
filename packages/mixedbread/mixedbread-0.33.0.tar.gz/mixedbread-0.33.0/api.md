# Shared Types

```python
from mixedbread.types import SearchFilter, SearchFilterCondition, Usage
```

# Mixedbread

Types:

```python
from mixedbread.types import (
    Embedding,
    EmbeddingCreateResponse,
    MultiEncodingEmbedding,
    InfoResponse,
    RerankResponse,
)
```

Methods:

- <code title="post /v1/embeddings">client.<a href="./src/mixedbread/_client.py">embed</a>(\*\*<a href="src/mixedbread/types/client_embed_params.py">params</a>) -> <a href="./src/mixedbread/types/embedding_create_response.py">EmbeddingCreateResponse</a></code>
- <code title="get /">client.<a href="./src/mixedbread/_client.py">info</a>() -> <a href="./src/mixedbread/types/info_response.py">InfoResponse</a></code>
- <code title="post /v1/reranking">client.<a href="./src/mixedbread/_client.py">rerank</a>(\*\*<a href="src/mixedbread/types/client_rerank_params.py">params</a>) -> <a href="./src/mixedbread/types/rerank_response.py">RerankResponse</a></code>

# VectorStores

Types:

```python
from mixedbread.types import (
    ExpiresAfter,
    ScoredAudioURLInputChunk,
    ScoredImageURLInputChunk,
    ScoredTextInputChunk,
    ScoredVideoURLInputChunk,
    VectorStore,
    VectorStoreChunkSearchOptions,
    VectorStoreDeleteResponse,
    VectorStoreQuestionAnsweringResponse,
    VectorStoreSearchResponse,
)
```

Methods:

- <code title="post /v1/vector_stores">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">create</a>(\*\*<a href="src/mixedbread/types/vector_store_create_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_store.py">VectorStore</a></code>
- <code title="get /v1/vector_stores/{vector_store_identifier}">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">retrieve</a>(vector_store_identifier) -> <a href="./src/mixedbread/types/vector_store.py">VectorStore</a></code>
- <code title="put /v1/vector_stores/{vector_store_identifier}">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">update</a>(vector_store_identifier, \*\*<a href="src/mixedbread/types/vector_store_update_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_store.py">VectorStore</a></code>
- <code title="get /v1/vector_stores">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">list</a>(\*\*<a href="src/mixedbread/types/vector_store_list_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_store.py">SyncCursor[VectorStore]</a></code>
- <code title="delete /v1/vector_stores/{vector_store_identifier}">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">delete</a>(vector_store_identifier) -> <a href="./src/mixedbread/types/vector_store_delete_response.py">VectorStoreDeleteResponse</a></code>
- <code title="post /v1/vector_stores/question-answering">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">question_answering</a>(\*\*<a href="src/mixedbread/types/vector_store_question_answering_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_store_question_answering_response.py">VectorStoreQuestionAnsweringResponse</a></code>
- <code title="post /v1/vector_stores/search">client.vector_stores.<a href="./src/mixedbread/resources/vector_stores/vector_stores.py">search</a>(\*\*<a href="src/mixedbread/types/vector_store_search_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_store_search_response.py">VectorStoreSearchResponse</a></code>

## Files

Types:

```python
from mixedbread.types.vector_stores import (
    RerankConfig,
    ScoredVectorStoreFile,
    VectorStoreFileStatus,
    VectorStoreFile,
    FileListResponse,
    FileDeleteResponse,
    FileSearchResponse,
)
```

Methods:

- <code title="post /v1/vector_stores/{vector_store_identifier}/files">client.vector_stores.files.<a href="./src/mixedbread/resources/vector_stores/files.py">create</a>(vector_store_identifier, \*\*<a href="src/mixedbread/types/vector_stores/file_create_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /v1/vector_stores/{vector_store_identifier}/files/{file_id}">client.vector_stores.files.<a href="./src/mixedbread/resources/vector_stores/files.py">retrieve</a>(file_id, \*, vector_store_identifier, \*\*<a href="src/mixedbread/types/vector_stores/file_retrieve_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="post /v1/vector_stores/{vector_store_identifier}/files/list">client.vector_stores.files.<a href="./src/mixedbread/resources/vector_stores/files.py">list</a>(vector_store_identifier, \*\*<a href="src/mixedbread/types/vector_stores/file_list_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_stores/file_list_response.py">FileListResponse</a></code>
- <code title="delete /v1/vector_stores/{vector_store_identifier}/files/{file_id}">client.vector_stores.files.<a href="./src/mixedbread/resources/vector_stores/files.py">delete</a>(file_id, \*, vector_store_identifier) -> <a href="./src/mixedbread/types/vector_stores/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="post /v1/vector_stores/files/search">client.vector_stores.files.<a href="./src/mixedbread/resources/vector_stores/files.py">search</a>(\*\*<a href="src/mixedbread/types/vector_stores/file_search_params.py">params</a>) -> <a href="./src/mixedbread/types/vector_stores/file_search_response.py">FileSearchResponse</a></code>

# Stores

Types:

```python
from mixedbread.types import (
    Store,
    StoreChunkSearchOptions,
    StoreDeleteResponse,
    StoreQuestionAnsweringResponse,
    StoreSearchResponse,
)
```

Methods:

- <code title="post /v1/stores">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">create</a>(\*\*<a href="src/mixedbread/types/store_create_params.py">params</a>) -> <a href="./src/mixedbread/types/store.py">Store</a></code>
- <code title="get /v1/stores/{store_identifier}">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">retrieve</a>(store_identifier) -> <a href="./src/mixedbread/types/store.py">Store</a></code>
- <code title="put /v1/stores/{store_identifier}">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">update</a>(store_identifier, \*\*<a href="src/mixedbread/types/store_update_params.py">params</a>) -> <a href="./src/mixedbread/types/store.py">Store</a></code>
- <code title="get /v1/stores">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">list</a>(\*\*<a href="src/mixedbread/types/store_list_params.py">params</a>) -> <a href="./src/mixedbread/types/store.py">SyncCursor[Store]</a></code>
- <code title="delete /v1/stores/{store_identifier}">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">delete</a>(store_identifier) -> <a href="./src/mixedbread/types/store_delete_response.py">StoreDeleteResponse</a></code>
- <code title="post /v1/stores/question-answering">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">question_answering</a>(\*\*<a href="src/mixedbread/types/store_question_answering_params.py">params</a>) -> <a href="./src/mixedbread/types/store_question_answering_response.py">StoreQuestionAnsweringResponse</a></code>
- <code title="post /v1/stores/search">client.stores.<a href="./src/mixedbread/resources/stores/stores.py">search</a>(\*\*<a href="src/mixedbread/types/store_search_params.py">params</a>) -> <a href="./src/mixedbread/types/store_search_response.py">StoreSearchResponse</a></code>

## Files

Types:

```python
from mixedbread.types.stores import (
    ScoredStoreFile,
    StoreFileStatus,
    StoreFile,
    FileListResponse,
    FileDeleteResponse,
    FileSearchResponse,
)
```

Methods:

- <code title="post /v1/stores/{store_identifier}/files">client.stores.files.<a href="./src/mixedbread/resources/stores/files.py">create</a>(store_identifier, \*\*<a href="src/mixedbread/types/stores/file_create_params.py">params</a>) -> <a href="./src/mixedbread/types/stores/store_file.py">StoreFile</a></code>
- <code title="get /v1/stores/{store_identifier}/files/{file_id}">client.stores.files.<a href="./src/mixedbread/resources/stores/files.py">retrieve</a>(file_id, \*, store_identifier, \*\*<a href="src/mixedbread/types/stores/file_retrieve_params.py">params</a>) -> <a href="./src/mixedbread/types/stores/store_file.py">StoreFile</a></code>
- <code title="post /v1/stores/{store_identifier}/files/list">client.stores.files.<a href="./src/mixedbread/resources/stores/files.py">list</a>(store_identifier, \*\*<a href="src/mixedbread/types/stores/file_list_params.py">params</a>) -> <a href="./src/mixedbread/types/stores/file_list_response.py">FileListResponse</a></code>
- <code title="delete /v1/stores/{store_identifier}/files/{file_id}">client.stores.files.<a href="./src/mixedbread/resources/stores/files.py">delete</a>(file_id, \*, store_identifier) -> <a href="./src/mixedbread/types/stores/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="post /v1/stores/files/search">client.stores.files.<a href="./src/mixedbread/resources/stores/files.py">search</a>(\*\*<a href="src/mixedbread/types/stores/file_search_params.py">params</a>) -> <a href="./src/mixedbread/types/stores/file_search_response.py">FileSearchResponse</a></code>

# Parsing

## Jobs

Types:

```python
from mixedbread.types.parsing import (
    ChunkingStrategy,
    ElementType,
    ParsingJobStatus,
    ParsingJob,
    ReturnFormat,
    JobListResponse,
    JobDeleteResponse,
)
```

Methods:

- <code title="post /v1/parsing/jobs">client.parsing.jobs.<a href="./src/mixedbread/resources/parsing/jobs.py">create</a>(\*\*<a href="src/mixedbread/types/parsing/job_create_params.py">params</a>) -> <a href="./src/mixedbread/types/parsing/parsing_job.py">ParsingJob</a></code>
- <code title="get /v1/parsing/jobs/{job_id}">client.parsing.jobs.<a href="./src/mixedbread/resources/parsing/jobs.py">retrieve</a>(job_id) -> <a href="./src/mixedbread/types/parsing/parsing_job.py">ParsingJob</a></code>
- <code title="get /v1/parsing/jobs">client.parsing.jobs.<a href="./src/mixedbread/resources/parsing/jobs.py">list</a>(\*\*<a href="src/mixedbread/types/parsing/job_list_params.py">params</a>) -> <a href="./src/mixedbread/types/parsing/job_list_response.py">SyncCursor[JobListResponse]</a></code>
- <code title="delete /v1/parsing/jobs/{job_id}">client.parsing.jobs.<a href="./src/mixedbread/resources/parsing/jobs.py">delete</a>(job_id) -> <a href="./src/mixedbread/types/parsing/job_delete_response.py">JobDeleteResponse</a></code>
- <code title="patch /v1/parsing/jobs/{job_id}">client.parsing.jobs.<a href="./src/mixedbread/resources/parsing/jobs.py">cancel</a>(job_id) -> <a href="./src/mixedbread/types/parsing/parsing_job.py">ParsingJob</a></code>

# Files

Types:

```python
from mixedbread.types import FileObject, PaginationWithTotal, FileDeleteResponse
```

Methods:

- <code title="post /v1/files">client.files.<a href="./src/mixedbread/resources/files.py">create</a>(\*\*<a href="src/mixedbread/types/file_create_params.py">params</a>) -> <a href="./src/mixedbread/types/file_object.py">FileObject</a></code>
- <code title="get /v1/files/{file_id}">client.files.<a href="./src/mixedbread/resources/files.py">retrieve</a>(file_id) -> <a href="./src/mixedbread/types/file_object.py">FileObject</a></code>
- <code title="post /v1/files/{file_id}">client.files.<a href="./src/mixedbread/resources/files.py">update</a>(file_id, \*\*<a href="src/mixedbread/types/file_update_params.py">params</a>) -> <a href="./src/mixedbread/types/file_object.py">FileObject</a></code>
- <code title="get /v1/files">client.files.<a href="./src/mixedbread/resources/files.py">list</a>(\*\*<a href="src/mixedbread/types/file_list_params.py">params</a>) -> <a href="./src/mixedbread/types/file_object.py">SyncCursor[FileObject]</a></code>
- <code title="delete /v1/files/{file_id}">client.files.<a href="./src/mixedbread/resources/files.py">delete</a>(file_id) -> <a href="./src/mixedbread/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /v1/files/{file_id}/content">client.files.<a href="./src/mixedbread/resources/files.py">content</a>(file_id) -> BinaryAPIResponse</code>

# Extractions

## Jobs

Types:

```python
from mixedbread.types.extractions import ExtractionJob
```

Methods:

- <code title="post /v1/extractions/jobs">client.extractions.jobs.<a href="./src/mixedbread/resources/extractions/jobs.py">create</a>(\*\*<a href="src/mixedbread/types/extractions/job_create_params.py">params</a>) -> <a href="./src/mixedbread/types/extractions/extraction_job.py">ExtractionJob</a></code>
- <code title="get /v1/extractions/jobs/{job_id}">client.extractions.jobs.<a href="./src/mixedbread/resources/extractions/jobs.py">retrieve</a>(job_id) -> <a href="./src/mixedbread/types/extractions/extraction_job.py">ExtractionJob</a></code>

## Schema

Types:

```python
from mixedbread.types.extractions import CreatedJsonSchema, EnhancedJsonSchema, ValidatedJsonSchema
```

Methods:

- <code title="post /v1/extractions/schema">client.extractions.schema.<a href="./src/mixedbread/resources/extractions/schema.py">create</a>(\*\*<a href="src/mixedbread/types/extractions/schema_create_params.py">params</a>) -> <a href="./src/mixedbread/types/extractions/created_json_schema.py">CreatedJsonSchema</a></code>
- <code title="post /v1/extractions/schema/enhance">client.extractions.schema.<a href="./src/mixedbread/resources/extractions/schema.py">enhance</a>(\*\*<a href="src/mixedbread/types/extractions/schema_enhance_params.py">params</a>) -> <a href="./src/mixedbread/types/extractions/enhanced_json_schema.py">EnhancedJsonSchema</a></code>
- <code title="post /v1/extractions/schema/validate">client.extractions.schema.<a href="./src/mixedbread/resources/extractions/schema.py">validate</a>(\*\*<a href="src/mixedbread/types/extractions/schema_validate_params.py">params</a>) -> <a href="./src/mixedbread/types/extractions/validated_json_schema.py">ValidatedJsonSchema</a></code>

## Content

Types:

```python
from mixedbread.types.extractions import ExtractionResult, ImageURLInput, TextInput
```

Methods:

- <code title="post /v1/extractions/content">client.extractions.content.<a href="./src/mixedbread/resources/extractions/content.py">create</a>(\*\*<a href="src/mixedbread/types/extractions/content_create_params.py">params</a>) -> <a href="./src/mixedbread/types/extractions/extraction_result.py">ExtractionResult</a></code>

# Embeddings

Types:

```python
from mixedbread.types import EncodingFormat
```

Methods:

- <code title="post /v1/embeddings">client.embeddings.<a href="./src/mixedbread/resources/embeddings.py">create</a>(\*\*<a href="src/mixedbread/types/embedding_create_params.py">params</a>) -> <a href="./src/mixedbread/types/embedding_create_response.py">EmbeddingCreateResponse</a></code>

# DataSources

Types:

```python
from mixedbread.types import (
    DataSource,
    DataSourceOauth2Params,
    DataSourceType,
    LinearDataSource,
    NotionDataSource,
    Oauth2Params,
    DataSourceDeleteResponse,
)
```

Methods:

- <code title="post /v1/data_sources/">client.data_sources.<a href="./src/mixedbread/resources/data_sources/data_sources.py">create</a>(\*\*<a href="src/mixedbread/types/data_source_create_params.py">params</a>) -> <a href="./src/mixedbread/types/data_source.py">DataSource</a></code>
- <code title="get /v1/data_sources/{data_source_id}">client.data_sources.<a href="./src/mixedbread/resources/data_sources/data_sources.py">retrieve</a>(data_source_id) -> <a href="./src/mixedbread/types/data_source.py">DataSource</a></code>
- <code title="put /v1/data_sources/{data_source_id}">client.data_sources.<a href="./src/mixedbread/resources/data_sources/data_sources.py">update</a>(data_source_id, \*\*<a href="src/mixedbread/types/data_source_update_params.py">params</a>) -> <a href="./src/mixedbread/types/data_source.py">DataSource</a></code>
- <code title="get /v1/data_sources/">client.data_sources.<a href="./src/mixedbread/resources/data_sources/data_sources.py">list</a>(\*\*<a href="src/mixedbread/types/data_source_list_params.py">params</a>) -> <a href="./src/mixedbread/types/data_source.py">SyncCursor[DataSource]</a></code>
- <code title="delete /v1/data_sources/{data_source_id}">client.data_sources.<a href="./src/mixedbread/resources/data_sources/data_sources.py">delete</a>(data_source_id) -> <a href="./src/mixedbread/types/data_source_delete_response.py">DataSourceDeleteResponse</a></code>

## Connectors

Types:

```python
from mixedbread.types.data_sources import DataSourceConnector, ConnectorDeleteResponse
```

Methods:

- <code title="post /v1/data_sources/{data_source_id}/connectors">client.data_sources.connectors.<a href="./src/mixedbread/resources/data_sources/connectors.py">create</a>(data_source_id, \*\*<a href="src/mixedbread/types/data_sources/connector_create_params.py">params</a>) -> <a href="./src/mixedbread/types/data_sources/data_source_connector.py">DataSourceConnector</a></code>
- <code title="get /v1/data_sources/{data_source_id}/connectors/{connector_id}">client.data_sources.connectors.<a href="./src/mixedbread/resources/data_sources/connectors.py">retrieve</a>(connector_id, \*, data_source_id) -> <a href="./src/mixedbread/types/data_sources/data_source_connector.py">DataSourceConnector</a></code>
- <code title="put /v1/data_sources/{data_source_id}/connectors/{connector_id}">client.data_sources.connectors.<a href="./src/mixedbread/resources/data_sources/connectors.py">update</a>(connector_id, \*, data_source_id, \*\*<a href="src/mixedbread/types/data_sources/connector_update_params.py">params</a>) -> <a href="./src/mixedbread/types/data_sources/data_source_connector.py">DataSourceConnector</a></code>
- <code title="get /v1/data_sources/{data_source_id}/connectors">client.data_sources.connectors.<a href="./src/mixedbread/resources/data_sources/connectors.py">list</a>(data_source_id, \*\*<a href="src/mixedbread/types/data_sources/connector_list_params.py">params</a>) -> <a href="./src/mixedbread/types/data_sources/data_source_connector.py">SyncCursor[DataSourceConnector]</a></code>
- <code title="delete /v1/data_sources/{data_source_id}/connectors/{connector_id}">client.data_sources.connectors.<a href="./src/mixedbread/resources/data_sources/connectors.py">delete</a>(connector_id, \*, data_source_id) -> <a href="./src/mixedbread/types/data_sources/connector_delete_response.py">ConnectorDeleteResponse</a></code>

# APIKeys

Types:

```python
from mixedbread.types import APIKey, APIKeyCreated, APIKeyDeleteResponse
```

Methods:

- <code title="post /v1/api-keys">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">create</a>(\*\*<a href="src/mixedbread/types/api_key_create_params.py">params</a>) -> <a href="./src/mixedbread/types/api_key_created.py">APIKeyCreated</a></code>
- <code title="get /v1/api-keys/{api_key_id}">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">retrieve</a>(api_key_id) -> <a href="./src/mixedbread/types/api_key.py">APIKey</a></code>
- <code title="get /v1/api-keys">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">list</a>(\*\*<a href="src/mixedbread/types/api_key_list_params.py">params</a>) -> <a href="./src/mixedbread/types/api_key.py">SyncLimitOffset[APIKey]</a></code>
- <code title="delete /v1/api-keys/{api_key_id}">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">delete</a>(api_key_id) -> <a href="./src/mixedbread/types/api_key_delete_response.py">APIKeyDeleteResponse</a></code>
- <code title="post /v1/api-keys/{api_key_id}/reroll">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">reroll</a>(api_key_id) -> <a href="./src/mixedbread/types/api_key_created.py">APIKeyCreated</a></code>
- <code title="post /v1/api-keys/{api_key_id}/revoke">client.api_keys.<a href="./src/mixedbread/resources/api_keys.py">revoke</a>(api_key_id) -> <a href="./src/mixedbread/types/api_key.py">APIKey</a></code>

# Chat

Methods:

- <code title="post /v1/chat/completions">client.chat.<a href="./src/mixedbread/resources/chat.py">create_completion</a>() -> object</code>
