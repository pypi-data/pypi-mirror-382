# V1

Types:

```python
from samplehc.types import V1QueryAuditLogsResponse, V1SqlExecuteResponse
```

Methods:

- <code title="post /api/v1/audit-logs">client.v1.<a href="./src/samplehc/resources/v1/v1.py">query_audit_logs</a>(\*\*<a href="src/samplehc/types/v1_query_audit_logs_params.py">params</a>) -> <a href="./src/samplehc/types/v1_query_audit_logs_response.py">V1QueryAuditLogsResponse</a></code>
- <code title="post /api/v1/sql">client.v1.<a href="./src/samplehc/resources/v1/v1.py">sql_execute</a>(\*\*<a href="src/samplehc/types/v1_sql_execute_params.py">params</a>) -> <a href="./src/samplehc/types/v1_sql_execute_response.py">V1SqlExecuteResponse</a></code>

# V2

## AsyncResults

Types:

```python
from samplehc.types.v2 import AsyncResultRetrieveResponse, AsyncResultSleepResponse
```

Methods:

- <code title="get /api/v2/async-results/{asyncResultId}">client.v2.async_results.<a href="./src/samplehc/resources/v2/async_results.py">retrieve</a>(async_result_id) -> <a href="./src/samplehc/types/v2/async_result_retrieve_response.py">AsyncResultRetrieveResponse</a></code>
- <code title="post /api/v2/async-results/sleep">client.v2.async_results.<a href="./src/samplehc/resources/v2/async_results.py">sleep</a>(\*\*<a href="src/samplehc/types/v2/async_result_sleep_params.py">params</a>) -> <a href="./src/samplehc/types/v2/async_result_sleep_response.py">AsyncResultSleepResponse</a></code>

## WorkflowRuns

Types:

```python
from samplehc.types.v2 import (
    WorkflowRunRetrieveResponse,
    WorkflowRunGetStartDataResponse,
    WorkflowRunResumeWhenCompleteResponse,
)
```

Methods:

- <code title="get /api/v2/workflow-runs/{workflowRunId}">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">retrieve</a>(workflow_run_id) -> <a href="./src/samplehc/types/v2/workflow_run_retrieve_response.py">WorkflowRunRetrieveResponse</a></code>
- <code title="put /api/v2/workflow-runs/{workflowRunId}/cancel">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">cancel</a>(workflow_run_id) -> object</code>
- <code title="get /api/v2/workflow-runs/start-data">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">get_start_data</a>() -> <a href="./src/samplehc/types/v2/workflow_run_get_start_data_response.py">WorkflowRunGetStartDataResponse</a></code>
- <code title="post /api/v2/workflow-runs/resume-when-complete">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">resume_when_complete</a>(\*\*<a href="src/samplehc/types/v2/workflow_run_resume_when_complete_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_run_resume_when_complete_response.py">WorkflowRunResumeWhenCompleteResponse</a></code>
- <code title="get /api/v2/workflow-runs/current-task">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">retrieve_current_task</a>() -> None</code>

### Step

Types:

```python
from samplehc.types.v2.workflow_runs import StepGetOutputResponse
```

Methods:

- <code title="get /api/v2/workflow-runs/step/{stepId}/output">client.v2.workflow_runs.step.<a href="./src/samplehc/resources/v2/workflow_runs/step.py">get_output</a>(step_id) -> <a href="./src/samplehc/types/v2/workflow_runs/step_get_output_response.py">StepGetOutputResponse</a></code>

## Tasks

Types:

```python
from samplehc.types.v2 import (
    TaskRetrieveResponse,
    TaskCancelResponse,
    TaskCompleteResponse,
    TaskGetSuspendedPayloadResponse,
    TaskRetryResponse,
    TaskUpdateScreenTimeResponse,
)
```

Methods:

- <code title="get /api/v2/tasks/{taskId}">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">retrieve</a>(task_id) -> <a href="./src/samplehc/types/v2/task_retrieve_response.py">TaskRetrieveResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/cancel">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">cancel</a>(task_id) -> <a href="./src/samplehc/types/v2/task_cancel_response.py">TaskCancelResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/complete">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">complete</a>(task_id, \*\*<a href="src/samplehc/types/v2/task_complete_params.py">params</a>) -> <a href="./src/samplehc/types/v2/task_complete_response.py">TaskCompleteResponse</a></code>
- <code title="get /api/v2/tasks/{taskId}/suspended-payload">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">get_suspended_payload</a>(task_id) -> <a href="./src/samplehc/types/v2/task_get_suspended_payload_response.py">TaskGetSuspendedPayloadResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/retry">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">retry</a>(task_id) -> <a href="./src/samplehc/types/v2/task_retry_response.py">TaskRetryResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/update-screen-time">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">update_screen_time</a>(task_id, \*\*<a href="src/samplehc/types/v2/task_update_screen_time_params.py">params</a>) -> Optional[TaskUpdateScreenTimeResponse]</code>

### State

Types:

```python
from samplehc.types.v2.tasks import StateUpdateResponse, StateGetResponse
```

Methods:

- <code title="post /api/v2/tasks/{taskId}/state">client.v2.tasks.state.<a href="./src/samplehc/resources/v2/tasks/state.py">update</a>(task_id, \*\*<a href="src/samplehc/types/v2/tasks/state_update_params.py">params</a>) -> <a href="./src/samplehc/types/v2/tasks/state_update_response.py">StateUpdateResponse</a></code>
- <code title="get /api/v2/tasks/{taskId}/state">client.v2.tasks.state.<a href="./src/samplehc/resources/v2/tasks/state.py">get</a>(task_id) -> <a href="./src/samplehc/types/v2/tasks/state_get_response.py">StateGetResponse</a></code>

## Workflows

Types:

```python
from samplehc.types.v2 import WorkflowDeployResponse, WorkflowQueryResponse, WorkflowStartResponse
```

Methods:

- <code title="post /api/v2/workflows/{workflowId}/deploy">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">deploy</a>(workflow_id) -> <a href="./src/samplehc/types/v2/workflow_deploy_response.py">WorkflowDeployResponse</a></code>
- <code title="post /api/v2/workflows/{workflowSlug}/query">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">query</a>(workflow_slug, \*\*<a href="src/samplehc/types/v2/workflow_query_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_query_response.py">WorkflowQueryResponse</a></code>
- <code title="post /api/v2/workflows/{workflowSlug}/start">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">start</a>(workflow_slug, \*\*<a href="src/samplehc/types/v2/workflow_start_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_start_response.py">WorkflowStartResponse</a></code>

## Documents

Types:

```python
from samplehc.types.v2 import (
    DocumentRetrieveResponse,
    DocumentClassifyResponse,
    DocumentCombineResponse,
    DocumentCreateFromSplitsResponse,
    DocumentExtractResponse,
    DocumentGenerateCsvResponse,
    DocumentPresignedUploadURLResponse,
    DocumentRetrieveCsvContentResponse,
    DocumentRetrieveMetadataResponse,
    DocumentSearchResponse,
    DocumentSplitResponse,
    DocumentTransformJsonToHTMLResponse,
    DocumentUnzipResponse,
    DocumentUnzipAsyncResponse,
)
```

Methods:

- <code title="get /api/v2/documents/{documentId}">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_response.py">DocumentRetrieveResponse</a></code>
- <code title="post /api/v2/documents/classify">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">classify</a>(\*\*<a href="src/samplehc/types/v2/document_classify_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_classify_response.py">DocumentClassifyResponse</a></code>
- <code title="post /api/v2/documents/combine">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">combine</a>(\*\*<a href="src/samplehc/types/v2/document_combine_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_combine_response.py">DocumentCombineResponse</a></code>
- <code title="post /api/v2/documents/create-from-splits">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">create_from_splits</a>(\*\*<a href="src/samplehc/types/v2/document_create_from_splits_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_create_from_splits_response.py">DocumentCreateFromSplitsResponse</a></code>
- <code title="post /api/v2/documents/extract">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">extract</a>(\*\*<a href="src/samplehc/types/v2/document_extract_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_extract_response.py">DocumentExtractResponse</a></code>
- <code title="post /api/v2/documents/generate-csv">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">generate_csv</a>(\*\*<a href="src/samplehc/types/v2/document_generate_csv_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_generate_csv_response.py">DocumentGenerateCsvResponse</a></code>
- <code title="post /api/v2/documents/presigned-upload-url">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">presigned_upload_url</a>(\*\*<a href="src/samplehc/types/v2/document_presigned_upload_url_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_presigned_upload_url_response.py">DocumentPresignedUploadURLResponse</a></code>
- <code title="get /api/v2/documents/{documentId}/csv-content">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve_csv_content</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_csv_content_response.py">DocumentRetrieveCsvContentResponse</a></code>
- <code title="get /api/v2/documents/{documentId}/metadata">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve_metadata</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_metadata_response.py">DocumentRetrieveMetadataResponse</a></code>
- <code title="post /api/v2/documents/search">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">search</a>(\*\*<a href="src/samplehc/types/v2/document_search_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_search_response.py">DocumentSearchResponse</a></code>
- <code title="post /api/v2/documents/split">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">split</a>(\*\*<a href="src/samplehc/types/v2/document_split_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_split_response.py">DocumentSplitResponse</a></code>
- <code title="post /api/v2/documents/json-to-html">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">transform_json_to_html</a>(\*\*<a href="src/samplehc/types/v2/document_transform_json_to_html_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_transform_json_to_html_response.py">DocumentTransformJsonToHTMLResponse</a></code>
- <code title="post /api/v2/documents/{documentId}/unzip">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">unzip</a>(document_id) -> <a href="./src/samplehc/types/v2/document_unzip_response.py">DocumentUnzipResponse</a></code>
- <code title="post /api/v2/documents/{documentId}/unzip-async">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">unzip_async</a>(document_id) -> <a href="./src/samplehc/types/v2/document_unzip_async_response.py">DocumentUnzipAsyncResponse</a></code>

### Legacy

Types:

```python
from samplehc.types.v2.documents import (
    LegacyExtractResponse,
    LegacyReasonResponse,
    LegacySplitResponse,
)
```

Methods:

- <code title="post /api/v2/documents/legacy/extract">client.v2.documents.legacy.<a href="./src/samplehc/resources/v2/documents/legacy.py">extract</a>(\*\*<a href="src/samplehc/types/v2/documents/legacy_extract_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/legacy_extract_response.py">LegacyExtractResponse</a></code>
- <code title="post /api/v2/documents/legacy/reason">client.v2.documents.legacy.<a href="./src/samplehc/resources/v2/documents/legacy.py">reason</a>(\*\*<a href="src/samplehc/types/v2/documents/legacy_reason_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/legacy_reason_response.py">LegacyReasonResponse</a></code>
- <code title="post /api/v2/documents/legacy/split">client.v2.documents.legacy.<a href="./src/samplehc/resources/v2/documents/legacy.py">split</a>(\*\*<a href="src/samplehc/types/v2/documents/legacy_split_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/legacy_split_response.py">LegacySplitResponse</a></code>

### Templates

Types:

```python
from samplehc.types.v2.documents import (
    TemplateGenerateDocumentAsyncResponse,
    TemplateRenderDocumentResponse,
)
```

Methods:

- <code title="post /api/v2/documents/templates/generate-document">client.v2.documents.templates.<a href="./src/samplehc/resources/v2/documents/templates.py">generate_document_async</a>(\*\*<a href="src/samplehc/types/v2/documents/template_generate_document_async_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/template_generate_document_async_response.py">TemplateGenerateDocumentAsyncResponse</a></code>
- <code title="post /api/v2/documents/templates/render">client.v2.documents.templates.<a href="./src/samplehc/resources/v2/documents/templates.py">render_document</a>(\*\*<a href="src/samplehc/types/v2/documents/template_render_document_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/template_render_document_response.py">TemplateRenderDocumentResponse</a></code>

### PdfTemplate

Types:

```python
from samplehc.types.v2.documents import PdfTemplateRetrieveMetadataResponse
```

Methods:

- <code title="get /api/v2/documents/pdf-template/{slug}/metadata">client.v2.documents.pdf_template.<a href="./src/samplehc/resources/v2/documents/pdf_template.py">retrieve_metadata</a>(slug) -> <a href="./src/samplehc/types/v2/documents/pdf_template_retrieve_metadata_response.py">PdfTemplateRetrieveMetadataResponse</a></code>

### Formats

Types:

```python
from samplehc.types.v2.documents import FormatCreatePdfResponse
```

Methods:

- <code title="post /api/v2/documents/{documentId}/formats/pdf">client.v2.documents.formats.<a href="./src/samplehc/resources/v2/documents/formats.py">create_pdf</a>(document_id, \*\*<a href="src/samplehc/types/v2/documents/format_create_pdf_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/format_create_pdf_response.py">FormatCreatePdfResponse</a></code>

## Communication

Types:

```python
from samplehc.types.v2 import CommunicationSendFaxResponse, CommunicationSendLetterResponse
```

Methods:

- <code title="post /api/v2/communication/send-email">client.v2.communication.<a href="./src/samplehc/resources/v2/communication.py">send_email</a>(\*\*<a href="src/samplehc/types/v2/communication_send_email_params.py">params</a>) -> object</code>
- <code title="post /api/v2/communication/send-fax">client.v2.communication.<a href="./src/samplehc/resources/v2/communication.py">send_fax</a>(\*\*<a href="src/samplehc/types/v2/communication_send_fax_params.py">params</a>) -> <a href="./src/samplehc/types/v2/communication_send_fax_response.py">CommunicationSendFaxResponse</a></code>
- <code title="post /api/v2/communication/letters">client.v2.communication.<a href="./src/samplehc/resources/v2/communication.py">send_letter</a>(\*\*<a href="src/samplehc/types/v2/communication_send_letter_params.py">params</a>) -> <a href="./src/samplehc/types/v2/communication_send_letter_response.py">CommunicationSendLetterResponse</a></code>

## Clearinghouse

Types:

```python
from samplehc.types.v2 import (
    ClearinghouseCheckEligibilityResponse,
    ClearinghouseRunDiscoveryResponse,
)
```

Methods:

- <code title="post /api/v2/clearinghouse/patient-cost">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">calculate_patient_cost</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_calculate_patient_cost_params.py">params</a>) -> None</code>
- <code title="post /api/v2/clearinghouse/claim-status">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">check_claim_status</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_check_claim_status_params.py">params</a>) -> object</code>
- <code title="post /api/v2/clearinghouse/check-eligibility">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">check_eligibility</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_check_eligibility_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse_check_eligibility_response.py">ClearinghouseCheckEligibilityResponse</a></code>
- <code title="post /api/v2/clearinghouse/coordination-of-benefits">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">coordination_of_benefits</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_coordination_of_benefits_params.py">params</a>) -> object</code>
- <code title="post /api/v2/clearinghouse/discovery">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">run_discovery</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_run_discovery_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse_run_discovery_response.py">ClearinghouseRunDiscoveryResponse</a></code>

### Payers

Types:

```python
from samplehc.types.v2.clearinghouse import PayerListResponse, PayerSearchResponse
```

Methods:

- <code title="get /api/v2/clearinghouse/payers">client.v2.clearinghouse.payers.<a href="./src/samplehc/resources/v2/clearinghouse/payers.py">list</a>() -> <a href="./src/samplehc/types/v2/clearinghouse/payer_list_response.py">PayerListResponse</a></code>
- <code title="get /api/v2/clearinghouse/payers/search">client.v2.clearinghouse.payers.<a href="./src/samplehc/resources/v2/clearinghouse/payers.py">search</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse/payer_search_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse/payer_search_response.py">PayerSearchResponse</a></code>

### Claim

Types:

```python
from samplehc.types.v2.clearinghouse import ClaimSubmitResponse
```

Methods:

- <code title="post /api/v2/clearinghouse/claim/{claimId}/cancel">client.v2.clearinghouse.claim.<a href="./src/samplehc/resources/v2/clearinghouse/claim.py">cancel</a>(claim_id) -> object</code>
- <code title="get /api/v2/clearinghouse/claim/{claimId}">client.v2.clearinghouse.claim.<a href="./src/samplehc/resources/v2/clearinghouse/claim.py">retrieve_status</a>(claim_id) -> object</code>
- <code title="post /api/v2/clearinghouse/claim">client.v2.clearinghouse.claim.<a href="./src/samplehc/resources/v2/clearinghouse/claim.py">submit</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse/claim_submit_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse/claim_submit_response.py">ClaimSubmitResponse</a></code>

## Ledger

### Entry

Types:

```python
from samplehc.types.v2.ledger import EntryPostResponse, EntryReverseResponse
```

Methods:

- <code title="post /api/v2/ledger/entry">client.v2.ledger.entry.<a href="./src/samplehc/resources/v2/ledger/entry.py">post</a>(\*\*<a href="src/samplehc/types/v2/ledger/entry_post_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger/entry_post_response.py">EntryPostResponse</a></code>
- <code title="post /api/v2/ledger/entry/{id}/reverse">client.v2.ledger.entry.<a href="./src/samplehc/resources/v2/ledger/entry.py">reverse</a>(id, \*\*<a href="src/samplehc/types/v2/ledger/entry_reverse_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger/entry_reverse_response.py">EntryReverseResponse</a></code>

### Account

Types:

```python
from samplehc.types.v2.ledger import AccountWriteoffResponse
```

Methods:

- <code title="get /api/v2/ledger/account/{orderId}/line-item/{lineItemId}/balance">client.v2.ledger.account.<a href="./src/samplehc/resources/v2/ledger/account.py">get_balance</a>(line_item_id, \*, order_id) -> None</code>
- <code title="post /api/v2/ledger/account/{orderId}/line-item/{lineItemId}/writeoff">client.v2.ledger.account.<a href="./src/samplehc/resources/v2/ledger/account.py">writeoff</a>(line_item_id, \*, order_id, \*\*<a href="src/samplehc/types/v2/ledger/account_writeoff_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger/account_writeoff_response.py">AccountWriteoffResponse</a></code>

## Integrations

### Snowflake

Types:

```python
from samplehc.types.v2.integrations import SnowflakeQueryResponse
```

Methods:

- <code title="post /api/v2/integrations/snowflake/{slug}/query">client.v2.integrations.snowflake.<a href="./src/samplehc/resources/v2/integrations/snowflake.py">query</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/snowflake_query_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/snowflake_query_response.py">SnowflakeQueryResponse</a></code>

### Bank

#### Transactions

Types:

```python
from samplehc.types.v2.integrations.bank import TransactionSyncResponse
```

Methods:

- <code title="post /api/v2/integrations/bank/transactions/sync">client.v2.integrations.bank.transactions.<a href="./src/samplehc/resources/v2/integrations/bank/transactions.py">sync</a>(\*\*<a href="src/samplehc/types/v2/integrations/bank/transaction_sync_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/bank/transaction_sync_response.py">TransactionSyncResponse</a></code>

### Careviso

Types:

```python
from samplehc.types.v2.integrations import CarevisoGetPayersResponse
```

Methods:

- <code title="get /api/v2/integrations/careviso/payers">client.v2.integrations.careviso.<a href="./src/samplehc/resources/v2/integrations/careviso.py">get_payers</a>() -> <a href="./src/samplehc/types/v2/integrations/careviso_get_payers_response.py">CarevisoGetPayersResponse</a></code>
- <code title="post /api/v2/integrations/careviso/{slug}/prior-authorizations">client.v2.integrations.careviso.<a href="./src/samplehc/resources/v2/integrations/careviso.py">submit_prior_authorization</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/careviso_submit_prior_authorization_params.py">params</a>) -> object</code>

### Kno2

#### Messages

Types:

```python
from samplehc.types.v2.integrations.kno2 import (
    MessageRetrieveResponse,
    MessageGetAttachmentResponse,
)
```

Methods:

- <code title="get /api/v2/integrations/kno2/{slug}/messages/{messageId}">client.v2.integrations.kno2.messages.<a href="./src/samplehc/resources/v2/integrations/kno2/messages.py">retrieve</a>(message_id, \*, slug) -> <a href="./src/samplehc/types/v2/integrations/kno2/message_retrieve_response.py">MessageRetrieveResponse</a></code>
- <code title="get /api/v2/integrations/kno2/{slug}/messages/{messageId}/attachments/{attachmentId}">client.v2.integrations.kno2.messages.<a href="./src/samplehc/resources/v2/integrations/kno2/messages.py">get_attachment</a>(attachment_id, \*, slug, message_id) -> <a href="./src/samplehc/types/v2/integrations/kno2/message_get_attachment_response.py">MessageGetAttachmentResponse</a></code>

### Glidian

Types:

```python
from samplehc.types.v2.integrations import (
    GlidianGetSubmissionRequirementsResponse,
    GlidianListPayersResponse,
    GlidianListServicesResponse,
)
```

Methods:

- <code title="get /api/v2/integrations/glidian/{slug}/submission-requirements">client.v2.integrations.glidian.<a href="./src/samplehc/resources/v2/integrations/glidian/glidian.py">get_submission_requirements</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian_get_submission_requirements_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian_get_submission_requirements_response.py">GlidianGetSubmissionRequirementsResponse</a></code>
- <code title="get /api/v2/integrations/glidian/{slug}/payers">client.v2.integrations.glidian.<a href="./src/samplehc/resources/v2/integrations/glidian/glidian.py">list_payers</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian_list_payers_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian_list_payers_response.py">GlidianListPayersResponse</a></code>
- <code title="get /api/v2/integrations/glidian/{slug}/services">client.v2.integrations.glidian.<a href="./src/samplehc/resources/v2/integrations/glidian/glidian.py">list_services</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian_list_services_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian_list_services_response.py">GlidianListServicesResponse</a></code>

#### PriorAuthorizations

Types:

```python
from samplehc.types.v2.integrations.glidian import (
    PriorAuthorizationCreateDraftResponse,
    PriorAuthorizationRetrieveRecordResponse,
    PriorAuthorizationSubmitResponse,
    PriorAuthorizationUpdateRecordResponse,
)
```

Methods:

- <code title="post /api/v2/integrations/glidian/{slug}/prior-authorizations">client.v2.integrations.glidian.prior_authorizations.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/prior_authorizations.py">create_draft</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian/prior_authorization_create_draft_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorization_create_draft_response.py">PriorAuthorizationCreateDraftResponse</a></code>
- <code title="get /api/v2/integrations/glidian/{slug}/prior-authorizations/{recordId}">client.v2.integrations.glidian.prior_authorizations.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/prior_authorizations.py">retrieve_record</a>(record_id, \*, slug) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorization_retrieve_record_response.py">PriorAuthorizationRetrieveRecordResponse</a></code>
- <code title="post /api/v2/integrations/glidian/{slug}/prior-authorizations/{recordId}/submit">client.v2.integrations.glidian.prior_authorizations.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/prior_authorizations.py">submit</a>(record_id, \*, slug) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorization_submit_response.py">PriorAuthorizationSubmitResponse</a></code>
- <code title="put /api/v2/integrations/glidian/{slug}/prior-authorizations/{recordId}">client.v2.integrations.glidian.prior_authorizations.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/prior_authorizations.py">update_record</a>(record_id, \*, slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian/prior_authorization_update_record_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorization_update_record_response.py">PriorAuthorizationUpdateRecordResponse</a></code>

##### ClinicalQuestions

Types:

```python
from samplehc.types.v2.integrations.glidian.prior_authorizations import (
    ClinicalQuestionUpdateResponse,
    ClinicalQuestionListResponse,
)
```

Methods:

- <code title="put /api/v2/integrations/glidian/{slug}/prior-authorizations/{recordId}/clinical-questions">client.v2.integrations.glidian.prior_authorizations.clinical_questions.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/clinical_questions.py">update</a>(record_id, \*, slug, \*\*<a href="src/samplehc/types/v2/integrations/glidian/prior_authorizations/clinical_question_update_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorizations/clinical_question_update_response.py">ClinicalQuestionUpdateResponse</a></code>
- <code title="get /api/v2/integrations/glidian/{slug}/prior-authorizations/{recordId}/clinical-questions">client.v2.integrations.glidian.prior_authorizations.clinical_questions.<a href="./src/samplehc/resources/v2/integrations/glidian/prior_authorizations/clinical_questions.py">list</a>(record_id, \*, slug) -> <a href="./src/samplehc/types/v2/integrations/glidian/prior_authorizations/clinical_question_list_response.py">ClinicalQuestionListResponse</a></code>

### Xcures

Methods:

- <code title="post /api/v2/integrations/xcures/{slug}/request">client.v2.integrations.xcures.<a href="./src/samplehc/resources/v2/integrations/xcures.py">make_request</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/xcure_make_request_params.py">params</a>) -> object</code>

### Salesforce

Methods:

- <code title="post /api/v2/integrations/salesforce/{slug}/crud-action">client.v2.integrations.salesforce.<a href="./src/samplehc/resources/v2/integrations/salesforce.py">run_crud_action</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/salesforce_run_crud_action_params.py">params</a>) -> object</code>

## Events

Types:

```python
from samplehc.types.v2 import EventEmitResponse
```

Methods:

- <code title="post /api/v2/events/">client.v2.events.<a href="./src/samplehc/resources/v2/events.py">emit</a>(\*\*<a href="src/samplehc/types/v2/event_emit_params.py">params</a>) -> <a href="./src/samplehc/types/v2/event_emit_response.py">EventEmitResponse</a></code>

## BrowserAgents

Types:

```python
from samplehc.types.v2 import BrowserAgentInvokeResponse
```

Methods:

- <code title="post /api/v2/browser-agents/{slug}/invoke">client.v2.browser_agents.<a href="./src/samplehc/resources/v2/browser_agents/browser_agents.py">invoke</a>(slug, \*\*<a href="src/samplehc/types/v2/browser_agent_invoke_params.py">params</a>) -> <a href="./src/samplehc/types/v2/browser_agent_invoke_response.py">BrowserAgentInvokeResponse</a></code>

### Runs

#### HelpRequests

Types:

```python
from samplehc.types.v2.browser_agents.runs import HelpRequestResolveResponse
```

Methods:

- <code title="patch /api/v2/browser-agents/{slug}/runs/{browserAgentRunId}/help-requests/{helpRequestId}/resolution">client.v2.browser_agents.runs.help_requests.<a href="./src/samplehc/resources/v2/browser_agents/runs/help_requests.py">resolve</a>(help_request_id, \*, slug, browser_agent_run_id, \*\*<a href="src/samplehc/types/v2/browser_agents/runs/help_request_resolve_params.py">params</a>) -> <a href="./src/samplehc/types/v2/browser_agents/runs/help_request_resolve_response.py">HelpRequestResolveResponse</a></code>

## Policies

Types:

```python
from samplehc.types.v2 import (
    PolicyListResponse,
    PolicyListCompaniesResponse,
    PolicyListPlansResponse,
    PolicyRetrievePresignedURLResponse,
    PolicyRetrieveTextResponse,
)
```

Methods:

- <code title="get /api/v2/policies/">client.v2.policies.<a href="./src/samplehc/resources/v2/policies.py">list</a>(\*\*<a href="src/samplehc/types/v2/policy_list_params.py">params</a>) -> <a href="./src/samplehc/types/v2/policy_list_response.py">PolicyListResponse</a></code>
- <code title="get /api/v2/policies/companies">client.v2.policies.<a href="./src/samplehc/resources/v2/policies.py">list_companies</a>(\*\*<a href="src/samplehc/types/v2/policy_list_companies_params.py">params</a>) -> <a href="./src/samplehc/types/v2/policy_list_companies_response.py">PolicyListCompaniesResponse</a></code>
- <code title="get /api/v2/policies/plans">client.v2.policies.<a href="./src/samplehc/resources/v2/policies.py">list_plans</a>(\*\*<a href="src/samplehc/types/v2/policy_list_plans_params.py">params</a>) -> <a href="./src/samplehc/types/v2/policy_list_plans_response.py">PolicyListPlansResponse</a></code>
- <code title="get /api/v2/policies/{policyId}/url">client.v2.policies.<a href="./src/samplehc/resources/v2/policies.py">retrieve_presigned_url</a>(policy_id) -> <a href="./src/samplehc/types/v2/policy_retrieve_presigned_url_response.py">PolicyRetrievePresignedURLResponse</a></code>
- <code title="get /api/v2/policies/{policyId}/text">client.v2.policies.<a href="./src/samplehc/resources/v2/policies.py">retrieve_text</a>(policy_id) -> <a href="./src/samplehc/types/v2/policy_retrieve_text_response.py">PolicyRetrieveTextResponse</a></code>

## Hie

### Documents

Types:

```python
from samplehc.types.v2.hie import DocumentQueryResponse
```

Methods:

- <code title="post /api/v2/hie/documents/query">client.v2.hie.documents.<a href="./src/samplehc/resources/v2/hie/documents.py">query</a>(\*\*<a href="src/samplehc/types/v2/hie/document_query_params.py">params</a>) -> <a href="./src/samplehc/types/v2/hie/document_query_response.py">DocumentQueryResponse</a></code>
- <code title="post /api/v2/hie/documents/upload">client.v2.hie.documents.<a href="./src/samplehc/resources/v2/hie/documents.py">upload</a>(\*\*<a href="src/samplehc/types/v2/hie/document_upload_params.py">params</a>) -> object</code>

### Adt

Methods:

- <code title="post /api/v2/hie/adt/subscribe">client.v2.hie.adt.<a href="./src/samplehc/resources/v2/hie/adt.py">subscribe</a>(\*\*<a href="src/samplehc/types/v2/hie/adt_subscribe_params.py">params</a>) -> object</code>

## Database

Types:

```python
from samplehc.types.v2 import DatabaseExecuteSqlResponse
```

Methods:

- <code title="post /api/v2/database/sql">client.v2.database.<a href="./src/samplehc/resources/v2/database.py">execute_sql</a>(\*\*<a href="src/samplehc/types/v2/database_execute_sql_params.py">params</a>) -> <a href="./src/samplehc/types/v2/database_execute_sql_response.py">DatabaseExecuteSqlResponse</a></code>

## BrowserAutomation

### Availity

Types:

```python
from samplehc.types.v2.browser_automation import AvailitySubmitAppealResponse
```

Methods:

- <code title="post /api/v2/browser-automation/availity/submit-appeal">client.v2.browser_automation.availity.<a href="./src/samplehc/resources/v2/browser_automation/availity.py">submit_appeal</a>(\*\*<a href="src/samplehc/types/v2/browser_automation/availity_submit_appeal_params.py">params</a>) -> <a href="./src/samplehc/types/v2/browser_automation/availity_submit_appeal_response.py">AvailitySubmitAppealResponse</a></code>
