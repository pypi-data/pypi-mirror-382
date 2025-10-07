# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, Union, Iterable, cast
from typing_extensions import Literal

import httpx

from .legacy import (
    LegacyResource,
    AsyncLegacyResource,
    LegacyResourceWithRawResponse,
    AsyncLegacyResourceWithRawResponse,
    LegacyResourceWithStreamingResponse,
    AsyncLegacyResourceWithStreamingResponse,
)
from .formats import (
    FormatsResource,
    AsyncFormatsResource,
    FormatsResourceWithRawResponse,
    AsyncFormatsResourceWithRawResponse,
    FormatsResourceWithStreamingResponse,
    AsyncFormatsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from .templates import (
    TemplatesResource,
    AsyncTemplatesResource,
    TemplatesResourceWithRawResponse,
    AsyncTemplatesResourceWithRawResponse,
    TemplatesResourceWithStreamingResponse,
    AsyncTemplatesResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ....types.v2 import (
    document_split_params,
    document_search_params,
    document_combine_params,
    document_extract_params,
    document_classify_params,
    document_generate_csv_params,
    document_create_from_splits_params,
    document_presigned_upload_url_params,
    document_transform_json_to_html_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .pdf_template import (
    PdfTemplateResource,
    AsyncPdfTemplateResource,
    PdfTemplateResourceWithRawResponse,
    AsyncPdfTemplateResourceWithRawResponse,
    PdfTemplateResourceWithStreamingResponse,
    AsyncPdfTemplateResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from ....types.v2.document_split_response import DocumentSplitResponse
from ....types.v2.document_unzip_response import DocumentUnzipResponse
from ....types.v2.document_search_response import DocumentSearchResponse
from ....types.v2.document_combine_response import DocumentCombineResponse
from ....types.v2.document_extract_response import DocumentExtractResponse
from ....types.v2.document_classify_response import DocumentClassifyResponse
from ....types.v2.document_retrieve_response import DocumentRetrieveResponse
from ....types.v2.document_unzip_async_response import DocumentUnzipAsyncResponse
from ....types.v2.document_generate_csv_response import DocumentGenerateCsvResponse
from ....types.v2.document_retrieve_metadata_response import DocumentRetrieveMetadataResponse
from ....types.v2.document_create_from_splits_response import DocumentCreateFromSplitsResponse
from ....types.v2.document_presigned_upload_url_response import DocumentPresignedUploadURLResponse
from ....types.v2.document_retrieve_csv_content_response import DocumentRetrieveCsvContentResponse
from ....types.v2.document_transform_json_to_html_response import DocumentTransformJsonToHTMLResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def legacy(self) -> LegacyResource:
        return LegacyResource(self._client)

    @cached_property
    def templates(self) -> TemplatesResource:
        return TemplatesResource(self._client)

    @cached_property
    def pdf_template(self) -> PdfTemplateResource:
        return PdfTemplateResource(self._client)

    @cached_property
    def formats(self) -> FormatsResource:
        return FormatsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveResponse:
        """
        Retrieves comprehensive details for a specific document, including its content
        or OCR data if available, and a presigned URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return cast(
            DocumentRetrieveResponse,
            self._get(
                f"/api/v2/documents/{document_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, DocumentRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def classify(
        self,
        *,
        document: document_classify_params.Document,
        label_schemas: Iterable[document_classify_params.LabelSchema],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentClassifyResponse:
        """
        Initiates an asynchronous document classification process based on provided
        schemas. Returns an ID to track the async result.

        Args:
          document: The document to be classified.

          label_schemas: An array of label schemas to classify against.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/classify",
            body=maybe_transform(
                {
                    "document": document,
                    "label_schemas": label_schemas,
                },
                document_classify_params.DocumentClassifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentClassifyResponse,
        )

    def combine(
        self,
        *,
        combined_file_name: str,
        documents: Iterable[document_combine_params.Document],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCombineResponse:
        """
        Combines multiple PDF documents into a single PDF and returns the combined
        document's metadata.

        Args:
          combined_file_name: The desired file name for the combined PDF (e.g., 'combined.pdf').

          documents: An array of document resources to be combined. All documents must be PDFs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/combine",
            body=maybe_transform(
                {
                    "combined_file_name": combined_file_name,
                    "documents": documents,
                },
                document_combine_params.DocumentCombineParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCombineResponse,
        )

    def create_from_splits(
        self,
        *,
        document: document_create_from_splits_params.Document,
        splits: Iterable[float],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCreateFromSplitsResponse:
        """
        Creates new documents from specified page splits of an existing document.

        Args:
          document: The source document from which to create new documents based on splits.

          splits: Array of page numbers indicating where to split the document. Each number is the
              start of a new document segment.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/create-from-splits",
            body=maybe_transform(
                {
                    "document": document,
                    "splits": splits,
                },
                document_create_from_splits_params.DocumentCreateFromSplitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCreateFromSplitsResponse,
        )

    def extract(
        self,
        *,
        documents: Iterable[document_extract_params.Document],
        prompt: str,
        response_json_schema: Dict[str, object],
        model: Literal["reasoning-3-mini", "reasoning-3", "base-5", "base-5-mini", "base-5-nano"] | Omit = omit,
        priority: Literal["interactive", "non-interactive"] | Omit = omit,
        reasoning_effort: Literal["low", "medium", "high"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentExtractResponse:
        """
        Initiates a modern, flexible asynchronous data extraction process using a JSON
        schema for the desired output and a prompt. Returns an ID for tracking.

        Args:
          documents: An array of documents to extract data from.

          prompt: A prompt guiding the extraction process.

          response_json_schema: A JSON schema defining the structure of the desired extraction output.

          model: The model to use for extraction.

          priority: The priority of the extraction task. Non-interactive is lower priority.

          reasoning_effort: Optional control over the reasoning effort for extraction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/extract",
            body=maybe_transform(
                {
                    "documents": documents,
                    "prompt": prompt,
                    "response_json_schema": response_json_schema,
                    "model": model,
                    "priority": priority,
                    "reasoning_effort": reasoning_effort,
                },
                document_extract_params.DocumentExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentExtractResponse,
        )

    def generate_csv(
        self,
        *,
        file_name: str,
        rows: Iterable[Dict[str, Union[str, float]]],
        options: document_generate_csv_params.Options | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGenerateCsvResponse:
        """
        Creates a new CSV document from the provided rows of data and returns the new
        document's metadata.

        Args:
          file_name: The desired file name for the generated CSV (e.g., 'report.csv').

          rows: Array of objects, where each object represents a row with column headers as
              keys.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/generate-csv",
            body=maybe_transform(
                {
                    "file_name": file_name,
                    "rows": rows,
                    "options": options,
                },
                document_generate_csv_params.DocumentGenerateCsvParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGenerateCsvResponse,
        )

    def presigned_upload_url(
        self,
        *,
        file_name: str,
        mime_type: Literal[
            "application/zip",
            "application/x-zip-compressed",
            "multipart/x-zip",
            "application/x-compress",
            "application/pdf",
            "text/csv",
            "application/javascript",
            "text/css",
            "image/png",
            "video/mp4",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/html",
            "application/json",
            "application/fhir+json",
            "application/fhir+jsonl",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentPresignedUploadURLResponse:
        """
        Generates a presigned URL that can be used to directly upload a file to storage.
        Returns the URL and document metadata.

        Args:
          file_name: The name of the file to be uploaded.

          mime_type: The MIME type of the file to be uploaded.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/presigned-upload-url",
            body=maybe_transform(
                {
                    "file_name": file_name,
                    "mime_type": mime_type,
                },
                document_presigned_upload_url_params.DocumentPresignedUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentPresignedUploadURLResponse,
        )

    def retrieve_csv_content(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveCsvContentResponse:
        """
        Retrieves the content of a CSV document as a structured JSON array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._get(
            f"/api/v2/documents/{document_id}/csv-content",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveCsvContentResponse,
        )

    def retrieve_metadata(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveMetadataResponse:
        """
        Retrieves metadata for a specific document, including a presigned URL for direct
        access if applicable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._get(
            f"/api/v2/documents/{document_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveMetadataResponse,
        )

    def search(
        self,
        *,
        documents: Iterable[document_search_params.Document],
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentSearchResponse:
        """
        Performs a search query across a specified set of documents and returns matching
        results.

        Args:
          documents: An array of document resources to search within.

          query: The search query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/search",
            body=maybe_transform(
                {
                    "documents": documents,
                    "query": query,
                },
                document_search_params.DocumentSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentSearchResponse,
        )

    def split(
        self,
        *,
        document: document_split_params.Document,
        split_description: Iterable[document_split_params.SplitDescription],
        split_rules: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentSplitResponse:
        """Initiates an asynchronous document splitting process.

        Returns an ID to track the
        async result.

        Args:
          document: The document to be split.

          split_description: Split description configuration.

          split_rules: Optional split rules prompt for the splitter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/split",
            body=maybe_transform(
                {
                    "document": document,
                    "split_description": split_description,
                    "split_rules": split_rules,
                },
                document_split_params.DocumentSplitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentSplitResponse,
        )

    def transform_json_to_html(
        self,
        *,
        json: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentTransformJsonToHTMLResponse:
        """
        Transforms a Sample JSON document to HTML

        Args:
          json: The JSON object to transform.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/json-to-html",
            body=maybe_transform(
                {"json": json}, document_transform_json_to_html_params.DocumentTransformJsonToHTMLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentTransformJsonToHTMLResponse,
        )

    def unzip(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUnzipResponse:
        """
        Given a document ID representing a ZIP file, unzip it, traverse the directory
        structure and return all PDFs found as a list of documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._post(
            f"/api/v2/documents/{document_id}/unzip",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUnzipResponse,
        )

    def unzip_async(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUnzipAsyncResponse:
        """
        Given a document ID representing a ZIP file, unzip it, traverse the directory
        structure and return all PDFs found as a list of documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._post(
            f"/api/v2/documents/{document_id}/unzip-async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUnzipAsyncResponse,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def legacy(self) -> AsyncLegacyResource:
        return AsyncLegacyResource(self._client)

    @cached_property
    def templates(self) -> AsyncTemplatesResource:
        return AsyncTemplatesResource(self._client)

    @cached_property
    def pdf_template(self) -> AsyncPdfTemplateResource:
        return AsyncPdfTemplateResource(self._client)

    @cached_property
    def formats(self) -> AsyncFormatsResource:
        return AsyncFormatsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveResponse:
        """
        Retrieves comprehensive details for a specific document, including its content
        or OCR data if available, and a presigned URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return cast(
            DocumentRetrieveResponse,
            await self._get(
                f"/api/v2/documents/{document_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, DocumentRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def classify(
        self,
        *,
        document: document_classify_params.Document,
        label_schemas: Iterable[document_classify_params.LabelSchema],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentClassifyResponse:
        """
        Initiates an asynchronous document classification process based on provided
        schemas. Returns an ID to track the async result.

        Args:
          document: The document to be classified.

          label_schemas: An array of label schemas to classify against.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/classify",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "label_schemas": label_schemas,
                },
                document_classify_params.DocumentClassifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentClassifyResponse,
        )

    async def combine(
        self,
        *,
        combined_file_name: str,
        documents: Iterable[document_combine_params.Document],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCombineResponse:
        """
        Combines multiple PDF documents into a single PDF and returns the combined
        document's metadata.

        Args:
          combined_file_name: The desired file name for the combined PDF (e.g., 'combined.pdf').

          documents: An array of document resources to be combined. All documents must be PDFs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/combine",
            body=await async_maybe_transform(
                {
                    "combined_file_name": combined_file_name,
                    "documents": documents,
                },
                document_combine_params.DocumentCombineParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCombineResponse,
        )

    async def create_from_splits(
        self,
        *,
        document: document_create_from_splits_params.Document,
        splits: Iterable[float],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCreateFromSplitsResponse:
        """
        Creates new documents from specified page splits of an existing document.

        Args:
          document: The source document from which to create new documents based on splits.

          splits: Array of page numbers indicating where to split the document. Each number is the
              start of a new document segment.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/create-from-splits",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "splits": splits,
                },
                document_create_from_splits_params.DocumentCreateFromSplitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCreateFromSplitsResponse,
        )

    async def extract(
        self,
        *,
        documents: Iterable[document_extract_params.Document],
        prompt: str,
        response_json_schema: Dict[str, object],
        model: Literal["reasoning-3-mini", "reasoning-3", "base-5", "base-5-mini", "base-5-nano"] | Omit = omit,
        priority: Literal["interactive", "non-interactive"] | Omit = omit,
        reasoning_effort: Literal["low", "medium", "high"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentExtractResponse:
        """
        Initiates a modern, flexible asynchronous data extraction process using a JSON
        schema for the desired output and a prompt. Returns an ID for tracking.

        Args:
          documents: An array of documents to extract data from.

          prompt: A prompt guiding the extraction process.

          response_json_schema: A JSON schema defining the structure of the desired extraction output.

          model: The model to use for extraction.

          priority: The priority of the extraction task. Non-interactive is lower priority.

          reasoning_effort: Optional control over the reasoning effort for extraction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/extract",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "prompt": prompt,
                    "response_json_schema": response_json_schema,
                    "model": model,
                    "priority": priority,
                    "reasoning_effort": reasoning_effort,
                },
                document_extract_params.DocumentExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentExtractResponse,
        )

    async def generate_csv(
        self,
        *,
        file_name: str,
        rows: Iterable[Dict[str, Union[str, float]]],
        options: document_generate_csv_params.Options | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGenerateCsvResponse:
        """
        Creates a new CSV document from the provided rows of data and returns the new
        document's metadata.

        Args:
          file_name: The desired file name for the generated CSV (e.g., 'report.csv').

          rows: Array of objects, where each object represents a row with column headers as
              keys.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/generate-csv",
            body=await async_maybe_transform(
                {
                    "file_name": file_name,
                    "rows": rows,
                    "options": options,
                },
                document_generate_csv_params.DocumentGenerateCsvParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGenerateCsvResponse,
        )

    async def presigned_upload_url(
        self,
        *,
        file_name: str,
        mime_type: Literal[
            "application/zip",
            "application/x-zip-compressed",
            "multipart/x-zip",
            "application/x-compress",
            "application/pdf",
            "text/csv",
            "application/javascript",
            "text/css",
            "image/png",
            "video/mp4",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/html",
            "application/json",
            "application/fhir+json",
            "application/fhir+jsonl",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentPresignedUploadURLResponse:
        """
        Generates a presigned URL that can be used to directly upload a file to storage.
        Returns the URL and document metadata.

        Args:
          file_name: The name of the file to be uploaded.

          mime_type: The MIME type of the file to be uploaded.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/presigned-upload-url",
            body=await async_maybe_transform(
                {
                    "file_name": file_name,
                    "mime_type": mime_type,
                },
                document_presigned_upload_url_params.DocumentPresignedUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentPresignedUploadURLResponse,
        )

    async def retrieve_csv_content(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveCsvContentResponse:
        """
        Retrieves the content of a CSV document as a structured JSON array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._get(
            f"/api/v2/documents/{document_id}/csv-content",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveCsvContentResponse,
        )

    async def retrieve_metadata(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentRetrieveMetadataResponse:
        """
        Retrieves metadata for a specific document, including a presigned URL for direct
        access if applicable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._get(
            f"/api/v2/documents/{document_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveMetadataResponse,
        )

    async def search(
        self,
        *,
        documents: Iterable[document_search_params.Document],
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentSearchResponse:
        """
        Performs a search query across a specified set of documents and returns matching
        results.

        Args:
          documents: An array of document resources to search within.

          query: The search query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/search",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "query": query,
                },
                document_search_params.DocumentSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentSearchResponse,
        )

    async def split(
        self,
        *,
        document: document_split_params.Document,
        split_description: Iterable[document_split_params.SplitDescription],
        split_rules: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentSplitResponse:
        """Initiates an asynchronous document splitting process.

        Returns an ID to track the
        async result.

        Args:
          document: The document to be split.

          split_description: Split description configuration.

          split_rules: Optional split rules prompt for the splitter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/split",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "split_description": split_description,
                    "split_rules": split_rules,
                },
                document_split_params.DocumentSplitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentSplitResponse,
        )

    async def transform_json_to_html(
        self,
        *,
        json: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentTransformJsonToHTMLResponse:
        """
        Transforms a Sample JSON document to HTML

        Args:
          json: The JSON object to transform.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/json-to-html",
            body=await async_maybe_transform(
                {"json": json}, document_transform_json_to_html_params.DocumentTransformJsonToHTMLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentTransformJsonToHTMLResponse,
        )

    async def unzip(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUnzipResponse:
        """
        Given a document ID representing a ZIP file, unzip it, traverse the directory
        structure and return all PDFs found as a list of documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._post(
            f"/api/v2/documents/{document_id}/unzip",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUnzipResponse,
        )

    async def unzip_async(
        self,
        document_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUnzipAsyncResponse:
        """
        Given a document ID representing a ZIP file, unzip it, traverse the directory
        structure and return all PDFs found as a list of documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._post(
            f"/api/v2/documents/{document_id}/unzip-async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUnzipAsyncResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.retrieve = to_raw_response_wrapper(
            documents.retrieve,
        )
        self.classify = to_raw_response_wrapper(
            documents.classify,
        )
        self.combine = to_raw_response_wrapper(
            documents.combine,
        )
        self.create_from_splits = to_raw_response_wrapper(
            documents.create_from_splits,
        )
        self.extract = to_raw_response_wrapper(
            documents.extract,
        )
        self.generate_csv = to_raw_response_wrapper(
            documents.generate_csv,
        )
        self.presigned_upload_url = to_raw_response_wrapper(
            documents.presigned_upload_url,
        )
        self.retrieve_csv_content = to_raw_response_wrapper(
            documents.retrieve_csv_content,
        )
        self.retrieve_metadata = to_raw_response_wrapper(
            documents.retrieve_metadata,
        )
        self.search = to_raw_response_wrapper(
            documents.search,
        )
        self.split = to_raw_response_wrapper(
            documents.split,
        )
        self.transform_json_to_html = to_raw_response_wrapper(
            documents.transform_json_to_html,
        )
        self.unzip = to_raw_response_wrapper(
            documents.unzip,
        )
        self.unzip_async = to_raw_response_wrapper(
            documents.unzip_async,
        )

    @cached_property
    def legacy(self) -> LegacyResourceWithRawResponse:
        return LegacyResourceWithRawResponse(self._documents.legacy)

    @cached_property
    def templates(self) -> TemplatesResourceWithRawResponse:
        return TemplatesResourceWithRawResponse(self._documents.templates)

    @cached_property
    def pdf_template(self) -> PdfTemplateResourceWithRawResponse:
        return PdfTemplateResourceWithRawResponse(self._documents.pdf_template)

    @cached_property
    def formats(self) -> FormatsResourceWithRawResponse:
        return FormatsResourceWithRawResponse(self._documents.formats)


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.retrieve = async_to_raw_response_wrapper(
            documents.retrieve,
        )
        self.classify = async_to_raw_response_wrapper(
            documents.classify,
        )
        self.combine = async_to_raw_response_wrapper(
            documents.combine,
        )
        self.create_from_splits = async_to_raw_response_wrapper(
            documents.create_from_splits,
        )
        self.extract = async_to_raw_response_wrapper(
            documents.extract,
        )
        self.generate_csv = async_to_raw_response_wrapper(
            documents.generate_csv,
        )
        self.presigned_upload_url = async_to_raw_response_wrapper(
            documents.presigned_upload_url,
        )
        self.retrieve_csv_content = async_to_raw_response_wrapper(
            documents.retrieve_csv_content,
        )
        self.retrieve_metadata = async_to_raw_response_wrapper(
            documents.retrieve_metadata,
        )
        self.search = async_to_raw_response_wrapper(
            documents.search,
        )
        self.split = async_to_raw_response_wrapper(
            documents.split,
        )
        self.transform_json_to_html = async_to_raw_response_wrapper(
            documents.transform_json_to_html,
        )
        self.unzip = async_to_raw_response_wrapper(
            documents.unzip,
        )
        self.unzip_async = async_to_raw_response_wrapper(
            documents.unzip_async,
        )

    @cached_property
    def legacy(self) -> AsyncLegacyResourceWithRawResponse:
        return AsyncLegacyResourceWithRawResponse(self._documents.legacy)

    @cached_property
    def templates(self) -> AsyncTemplatesResourceWithRawResponse:
        return AsyncTemplatesResourceWithRawResponse(self._documents.templates)

    @cached_property
    def pdf_template(self) -> AsyncPdfTemplateResourceWithRawResponse:
        return AsyncPdfTemplateResourceWithRawResponse(self._documents.pdf_template)

    @cached_property
    def formats(self) -> AsyncFormatsResourceWithRawResponse:
        return AsyncFormatsResourceWithRawResponse(self._documents.formats)


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.retrieve = to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.classify = to_streamed_response_wrapper(
            documents.classify,
        )
        self.combine = to_streamed_response_wrapper(
            documents.combine,
        )
        self.create_from_splits = to_streamed_response_wrapper(
            documents.create_from_splits,
        )
        self.extract = to_streamed_response_wrapper(
            documents.extract,
        )
        self.generate_csv = to_streamed_response_wrapper(
            documents.generate_csv,
        )
        self.presigned_upload_url = to_streamed_response_wrapper(
            documents.presigned_upload_url,
        )
        self.retrieve_csv_content = to_streamed_response_wrapper(
            documents.retrieve_csv_content,
        )
        self.retrieve_metadata = to_streamed_response_wrapper(
            documents.retrieve_metadata,
        )
        self.search = to_streamed_response_wrapper(
            documents.search,
        )
        self.split = to_streamed_response_wrapper(
            documents.split,
        )
        self.transform_json_to_html = to_streamed_response_wrapper(
            documents.transform_json_to_html,
        )
        self.unzip = to_streamed_response_wrapper(
            documents.unzip,
        )
        self.unzip_async = to_streamed_response_wrapper(
            documents.unzip_async,
        )

    @cached_property
    def legacy(self) -> LegacyResourceWithStreamingResponse:
        return LegacyResourceWithStreamingResponse(self._documents.legacy)

    @cached_property
    def templates(self) -> TemplatesResourceWithStreamingResponse:
        return TemplatesResourceWithStreamingResponse(self._documents.templates)

    @cached_property
    def pdf_template(self) -> PdfTemplateResourceWithStreamingResponse:
        return PdfTemplateResourceWithStreamingResponse(self._documents.pdf_template)

    @cached_property
    def formats(self) -> FormatsResourceWithStreamingResponse:
        return FormatsResourceWithStreamingResponse(self._documents.formats)


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.retrieve = async_to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.classify = async_to_streamed_response_wrapper(
            documents.classify,
        )
        self.combine = async_to_streamed_response_wrapper(
            documents.combine,
        )
        self.create_from_splits = async_to_streamed_response_wrapper(
            documents.create_from_splits,
        )
        self.extract = async_to_streamed_response_wrapper(
            documents.extract,
        )
        self.generate_csv = async_to_streamed_response_wrapper(
            documents.generate_csv,
        )
        self.presigned_upload_url = async_to_streamed_response_wrapper(
            documents.presigned_upload_url,
        )
        self.retrieve_csv_content = async_to_streamed_response_wrapper(
            documents.retrieve_csv_content,
        )
        self.retrieve_metadata = async_to_streamed_response_wrapper(
            documents.retrieve_metadata,
        )
        self.search = async_to_streamed_response_wrapper(
            documents.search,
        )
        self.split = async_to_streamed_response_wrapper(
            documents.split,
        )
        self.transform_json_to_html = async_to_streamed_response_wrapper(
            documents.transform_json_to_html,
        )
        self.unzip = async_to_streamed_response_wrapper(
            documents.unzip,
        )
        self.unzip_async = async_to_streamed_response_wrapper(
            documents.unzip_async,
        )

    @cached_property
    def legacy(self) -> AsyncLegacyResourceWithStreamingResponse:
        return AsyncLegacyResourceWithStreamingResponse(self._documents.legacy)

    @cached_property
    def templates(self) -> AsyncTemplatesResourceWithStreamingResponse:
        return AsyncTemplatesResourceWithStreamingResponse(self._documents.templates)

    @cached_property
    def pdf_template(self) -> AsyncPdfTemplateResourceWithStreamingResponse:
        return AsyncPdfTemplateResourceWithStreamingResponse(self._documents.pdf_template)

    @cached_property
    def formats(self) -> AsyncFormatsResourceWithStreamingResponse:
        return AsyncFormatsResourceWithStreamingResponse(self._documents.formats)
