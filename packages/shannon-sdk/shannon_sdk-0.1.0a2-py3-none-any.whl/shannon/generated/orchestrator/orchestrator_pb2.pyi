from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATUS_UNSPECIFIED: _ClassVar[TaskStatus]
    TASK_STATUS_QUEUED: _ClassVar[TaskStatus]
    TASK_STATUS_RUNNING: _ClassVar[TaskStatus]
    TASK_STATUS_COMPLETED: _ClassVar[TaskStatus]
    TASK_STATUS_FAILED: _ClassVar[TaskStatus]
    TASK_STATUS_CANCELLED: _ClassVar[TaskStatus]
    TASK_STATUS_TIMEOUT: _ClassVar[TaskStatus]
TASK_STATUS_UNSPECIFIED: TaskStatus
TASK_STATUS_QUEUED: TaskStatus
TASK_STATUS_RUNNING: TaskStatus
TASK_STATUS_COMPLETED: TaskStatus
TASK_STATUS_FAILED: TaskStatus
TASK_STATUS_CANCELLED: TaskStatus
TASK_STATUS_TIMEOUT: TaskStatus

class TaskDecomposition(_message.Message):
    __slots__ = ("mode", "complexity_score", "agent_tasks", "dag")
    MODE_FIELD_NUMBER: _ClassVar[int]
    COMPLEXITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    AGENT_TASKS_FIELD_NUMBER: _ClassVar[int]
    DAG_FIELD_NUMBER: _ClassVar[int]
    mode: _common_pb2.ExecutionMode
    complexity_score: float
    agent_tasks: _containers.RepeatedCompositeFieldContainer[AgentTask]
    dag: DAGStructure
    def __init__(self, mode: _Optional[_Union[_common_pb2.ExecutionMode, str]] = ..., complexity_score: _Optional[float] = ..., agent_tasks: _Optional[_Iterable[_Union[AgentTask, _Mapping]]] = ..., dag: _Optional[_Union[DAGStructure, _Mapping]] = ...) -> None: ...

class AgentTask(_message.Message):
    __slots__ = ("agent_id", "task_id", "description", "dependencies", "input", "required_tools", "model_tier")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_TOOLS_FIELD_NUMBER: _ClassVar[int]
    MODEL_TIER_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    task_id: str
    description: str
    dependencies: _containers.RepeatedScalarFieldContainer[str]
    input: _struct_pb2.Struct
    required_tools: _containers.RepeatedScalarFieldContainer[str]
    model_tier: _common_pb2.ModelTier
    def __init__(self, agent_id: _Optional[str] = ..., task_id: _Optional[str] = ..., description: _Optional[str] = ..., dependencies: _Optional[_Iterable[str]] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., required_tools: _Optional[_Iterable[str]] = ..., model_tier: _Optional[_Union[_common_pb2.ModelTier, str]] = ...) -> None: ...

class DAGStructure(_message.Message):
    __slots__ = ("nodes", "edges")
    NODES_FIELD_NUMBER: _ClassVar[int]
    EDGES_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[DAGNode]
    edges: _containers.RepeatedCompositeFieldContainer[DAGEdge]
    def __init__(self, nodes: _Optional[_Iterable[_Union[DAGNode, _Mapping]]] = ..., edges: _Optional[_Iterable[_Union[DAGEdge, _Mapping]]] = ...) -> None: ...

class DAGNode(_message.Message):
    __slots__ = ("id", "agent_task_id", "level")
    ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    id: str
    agent_task_id: str
    level: int
    def __init__(self, id: _Optional[str] = ..., agent_task_id: _Optional[str] = ..., level: _Optional[int] = ...) -> None: ...

class DAGEdge(_message.Message):
    __slots__ = ("to",)
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    to: str
    def __init__(self, to: _Optional[str] = ..., **kwargs) -> None: ...

class SubmitTaskRequest(_message.Message):
    __slots__ = ("metadata", "query", "context", "auto_decompose", "manual_decomposition", "session_context", "require_approval")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    AUTO_DECOMPOSE_FIELD_NUMBER: _ClassVar[int]
    MANUAL_DECOMPOSITION_FIELD_NUMBER: _ClassVar[int]
    SESSION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    metadata: _common_pb2.TaskMetadata
    query: str
    context: _struct_pb2.Struct
    auto_decompose: bool
    manual_decomposition: TaskDecomposition
    session_context: SessionContext
    require_approval: bool
    def __init__(self, metadata: _Optional[_Union[_common_pb2.TaskMetadata, _Mapping]] = ..., query: _Optional[str] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., auto_decompose: bool = ..., manual_decomposition: _Optional[_Union[TaskDecomposition, _Mapping]] = ..., session_context: _Optional[_Union[SessionContext, _Mapping]] = ..., require_approval: bool = ...) -> None: ...

class SessionContext(_message.Message):
    __slots__ = ("history", "persistent_context", "files_created", "tools_used", "total_tokens_used", "total_cost_usd")
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    PERSISTENT_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    FILES_CREATED_FIELD_NUMBER: _ClassVar[int]
    TOOLS_USED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COST_USD_FIELD_NUMBER: _ClassVar[int]
    history: _containers.RepeatedCompositeFieldContainer[ConversationMessage]
    persistent_context: _struct_pb2.Struct
    files_created: _containers.RepeatedScalarFieldContainer[str]
    tools_used: _containers.RepeatedScalarFieldContainer[str]
    total_tokens_used: int
    total_cost_usd: float
    def __init__(self, history: _Optional[_Iterable[_Union[ConversationMessage, _Mapping]]] = ..., persistent_context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., files_created: _Optional[_Iterable[str]] = ..., tools_used: _Optional[_Iterable[str]] = ..., total_tokens_used: _Optional[int] = ..., total_cost_usd: _Optional[float] = ...) -> None: ...

class ConversationMessage(_message.Message):
    __slots__ = ("role", "content", "timestamp", "tokens_used")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    timestamp: _timestamp_pb2.Timestamp
    tokens_used: int
    def __init__(self, role: _Optional[str] = ..., content: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tokens_used: _Optional[int] = ...) -> None: ...

class SubmitTaskResponse(_message.Message):
    __slots__ = ("workflow_id", "task_id", "status", "decomposition", "message")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DECOMPOSITION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    task_id: str
    status: _common_pb2.StatusCode
    decomposition: TaskDecomposition
    message: str
    def __init__(self, workflow_id: _Optional[str] = ..., task_id: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.StatusCode, str]] = ..., decomposition: _Optional[_Union[TaskDecomposition, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class GetTaskStatusRequest(_message.Message):
    __slots__ = ("task_id", "include_details")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_DETAILS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    include_details: bool
    def __init__(self, task_id: _Optional[str] = ..., include_details: bool = ...) -> None: ...

class GetTaskStatusResponse(_message.Message):
    __slots__ = ("task_id", "status", "progress", "result", "metrics", "agent_statuses", "error_message")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    AGENT_STATUSES_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    status: TaskStatus
    progress: float
    result: str
    metrics: _common_pb2.ExecutionMetrics
    agent_statuses: _containers.RepeatedCompositeFieldContainer[AgentTaskStatus]
    error_message: str
    def __init__(self, task_id: _Optional[str] = ..., status: _Optional[_Union[TaskStatus, str]] = ..., progress: _Optional[float] = ..., result: _Optional[str] = ..., metrics: _Optional[_Union[_common_pb2.ExecutionMetrics, _Mapping]] = ..., agent_statuses: _Optional[_Iterable[_Union[AgentTaskStatus, _Mapping]]] = ..., error_message: _Optional[str] = ...) -> None: ...

class AgentTaskStatus(_message.Message):
    __slots__ = ("agent_id", "task_id", "status", "result", "token_usage")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_USAGE_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    task_id: str
    status: TaskStatus
    result: str
    token_usage: _common_pb2.TokenUsage
    def __init__(self, agent_id: _Optional[str] = ..., task_id: _Optional[str] = ..., status: _Optional[_Union[TaskStatus, str]] = ..., result: _Optional[str] = ..., token_usage: _Optional[_Union[_common_pb2.TokenUsage, _Mapping]] = ...) -> None: ...

class CancelTaskRequest(_message.Message):
    __slots__ = ("task_id", "reason")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    reason: str
    def __init__(self, task_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class CancelTaskResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ListTasksRequest(_message.Message):
    __slots__ = ("user_id", "session_id", "limit", "offset", "filter_status")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    session_id: str
    limit: int
    offset: int
    filter_status: TaskStatus
    def __init__(self, user_id: _Optional[str] = ..., session_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., filter_status: _Optional[_Union[TaskStatus, str]] = ...) -> None: ...

class ListTasksResponse(_message.Message):
    __slots__ = ("tasks", "total_count")
    TASKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    total_count: int
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class TaskSummary(_message.Message):
    __slots__ = ("task_id", "query", "status", "mode", "created_at", "completed_at", "total_token_usage")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKEN_USAGE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    query: str
    status: TaskStatus
    mode: _common_pb2.ExecutionMode
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    total_token_usage: _common_pb2.TokenUsage
    def __init__(self, task_id: _Optional[str] = ..., query: _Optional[str] = ..., status: _Optional[_Union[TaskStatus, str]] = ..., mode: _Optional[_Union[_common_pb2.ExecutionMode, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., total_token_usage: _Optional[_Union[_common_pb2.TokenUsage, _Mapping]] = ...) -> None: ...

class GetSessionContextRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class GetSessionContextResponse(_message.Message):
    __slots__ = ("session_id", "context", "recent_tasks", "session_token_usage")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    RECENT_TASKS_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_USAGE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    context: _struct_pb2.Struct
    recent_tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    session_token_usage: _common_pb2.TokenUsage
    def __init__(self, session_id: _Optional[str] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., recent_tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ..., session_token_usage: _Optional[_Union[_common_pb2.TokenUsage, _Mapping]] = ...) -> None: ...

class TemplateSummary(_message.Message):
    __slots__ = ("name", "version", "key", "content_hash")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    key: str
    content_hash: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., key: _Optional[str] = ..., content_hash: _Optional[str] = ...) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTemplatesResponse(_message.Message):
    __slots__ = ("templates",)
    TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    templates: _containers.RepeatedCompositeFieldContainer[TemplateSummary]
    def __init__(self, templates: _Optional[_Iterable[_Union[TemplateSummary, _Mapping]]] = ...) -> None: ...

class ApproveTaskRequest(_message.Message):
    __slots__ = ("approval_id", "workflow_id", "run_id", "approved", "feedback", "modified_action", "approved_by")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVED_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_ACTION_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    workflow_id: str
    run_id: str
    approved: bool
    feedback: str
    modified_action: str
    approved_by: str
    def __init__(self, approval_id: _Optional[str] = ..., workflow_id: _Optional[str] = ..., run_id: _Optional[str] = ..., approved: bool = ..., feedback: _Optional[str] = ..., modified_action: _Optional[str] = ..., approved_by: _Optional[str] = ...) -> None: ...

class ApproveTaskResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetPendingApprovalsRequest(_message.Message):
    __slots__ = ("user_id", "session_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    session_id: str
    def __init__(self, user_id: _Optional[str] = ..., session_id: _Optional[str] = ...) -> None: ...

class GetPendingApprovalsResponse(_message.Message):
    __slots__ = ("approvals",)
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    approvals: _containers.RepeatedCompositeFieldContainer[PendingApproval]
    def __init__(self, approvals: _Optional[_Iterable[_Union[PendingApproval, _Mapping]]] = ...) -> None: ...

class PendingApproval(_message.Message):
    __slots__ = ("approval_id", "workflow_id", "query", "proposed_action", "reason", "requested_at", "metadata")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    PROPOSED_ACTION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    workflow_id: str
    query: str
    proposed_action: str
    reason: str
    requested_at: _timestamp_pb2.Timestamp
    metadata: _struct_pb2.Struct
    def __init__(self, approval_id: _Optional[str] = ..., workflow_id: _Optional[str] = ..., query: _Optional[str] = ..., proposed_action: _Optional[str] = ..., reason: _Optional[str] = ..., requested_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
