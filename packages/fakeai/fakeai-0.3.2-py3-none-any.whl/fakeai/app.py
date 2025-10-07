#!/usr/bin/env python3
"""
FakeAI: OpenAI Compatible API Server

This module provides a FastAPI implementation that mimics the OpenAI API.
It supports all endpoints and features of the official OpenAI API but returns
simulated responses instead of performing actual inference.
"""
#  SPDX-License-Identifier: Apache-2.0

import logging
import random
import time
from datetime import datetime
from typing import Annotated

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse

from fakeai.config import AppConfig
from fakeai.fakeai_service import FakeAIService, RealtimeSessionHandler
from fakeai.metrics import MetricsTracker
from fakeai.metrics_streaming import MetricsStreamer
from fakeai.model_metrics import ModelMetricsTracker
from fakeai.models import (
    Assistant,
    AssistantList,
    ArchiveOrganizationProjectResponse,
    AudioSpeechesUsageResponse,
    AudioTranscriptionsUsageResponse,
    Batch,
    BatchListResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    CompletionsUsageResponse,
    CostsResponse,
    CreateBatchRequest,
    CreateAssistantRequest,
    CreateMessageRequest,
    CreateRunRequest,
    CreateThreadRequest,
    CreateOrganizationInviteRequest,
    CreateOrganizationProjectRequest,
    CreateOrganizationUserRequest,
    CreateProjectUserRequest,
    CreateServiceAccountRequest,
    CreateVectorStoreFileBatchRequest,
    CreateVectorStoreFileRequest,
    CreateVectorStoreRequest,
    DeleteOrganizationInviteResponse,
    DeleteProjectUserResponse,
    DeleteServiceAccountResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingsUsageResponse,
    ErrorDetail,
    ErrorResponse,
    FileListResponse,
    FileObject,
    FineTuningCheckpointList,
    FineTuningJob,
    FineTuningJobList,
    FineTuningJobRequest,
    MessageList,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImagesUsageResponse,
    ModelCapabilitiesResponse,
    ModifyAssistantRequest,
    ModifyRunRequest,
    ModifyThreadRequest,
    ModelListResponse,
    ModerationRequest,
    ModerationResponse,
    ModifyOrganizationProjectRequest,
    ModifyOrganizationUserRequest,
    ModifyProjectUserRequest,
    ModifyVectorStoreRequest,
    OrganizationInvite,
    Run,
    RunList,
    RunStatus,
    RunStep,
    RunStepList,
    OrganizationInviteListResponse,
    OrganizationProject,
    OrganizationProjectListResponse,
    OrganizationUser,
    OrganizationUserListResponse,
    ProjectUser,
    Thread,
    ThreadMessage,
    Usage,
    ProjectUserListResponse,
    RankingRequest,
    RankingResponse,
    ResponsesRequest,
    ResponsesResponse,
    ServiceAccount,
    ServiceAccountListResponse,
    SolidoRagRequest,
    SolidoRagResponse,
    SpeechRequest,
    TextGenerationRequest,
    TextGenerationResponse,
    VectorStore,
    VectorStoreFile,
    VectorStoreFileBatch,
    VectorStoreFileListResponse,
    VectorStoreListResponse,
)
from fakeai.rate_limiter import RateLimiter
from fakeai.security import (
    AbuseDetector,
    ApiKeyManager,
    InjectionAttackDetected,
    InputValidator,
    PayloadTooLarge,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the application
app = FastAPI(
    title="FakeAI Server",
    description="An OpenAI-compatible API implementation for testing and development.",
    version="1.0.0",
)

# Load configuration
config = AppConfig()

# Add CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allowed_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for context length exceeded errors
from fakeai.context_validator import ContextLengthExceededError


@app.exception_handler(ContextLengthExceededError)
async def context_length_exceeded_handler(request: Request, exc: ContextLengthExceededError):
    """Handle context length exceeded errors with proper OpenAI-compatible format."""
    return JSONResponse(
        status_code=400,
        content=exc.error_dict,
    )


# Initialize security components
api_key_manager = ApiKeyManager()
abuse_detector = AbuseDetector()
input_validator = InputValidator()

# Add API keys to manager (with hashing if enabled)
if config.hash_api_keys:
    for key in config.api_keys:
        api_key_manager.add_key(key)
else:
    # For backward compatibility, plain keys still work
    pass

# Initialize the FakeAI service
fakeai_service = FakeAIService(config)

# Get the metrics tracker singleton instance
metrics_tracker = fakeai_service.metrics_tracker

# Initialize per-model metrics tracker
model_metrics_tracker = ModelMetricsTracker()

# Initialize metrics streamer
metrics_streamer = MetricsStreamer(metrics_tracker)

# Server readiness state
server_ready = False

# Initialize rate limiter
rate_limiter = RateLimiter()
rate_limiter.configure(
    tier=config.rate_limit_tier,
    rpm_override=config.rate_limit_rpm,
    tpm_override=config.rate_limit_tpm,
)


# Authentication dependency
async def verify_api_key(
    request: Request,
    api_key: Annotated[str | None, Header(alias="Authorization")] = None,
):
    """Verifies the API key from the Authorization header with security checks."""
    client_ip = request.client.host if request.client else "unknown"

    # Check if IP is banned
    if config.enable_abuse_detection:
        is_banned, ban_time = abuse_detector.is_banned(client_ip)
        if is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"IP address temporarily banned. Retry after {int(ban_time)} seconds.",
                headers={"Retry-After": str(int(ban_time))},
            )

    # Skip authentication if not required
    if not config.require_api_key:
        return None

    if not api_key:
        if config.enable_abuse_detection:
            abuse_detector.record_failed_auth(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    # Strip "Bearer " prefix if present
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]

    # Verify API key
    is_valid = False
    if config.hash_api_keys:
        # Use secure API key manager
        is_valid = api_key_manager.verify_key(api_key)
    else:
        # Backward compatibility: plain key check
        is_valid = api_key in config.api_keys

    if not is_valid:
        if config.enable_abuse_detection:
            abuse_detector.record_failed_auth(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


# Request logging and rate limiting middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and enforce rate limits with security checks"""
    request_id = f"{int(time.time())}-{random.randint(1000, 9999)}"
    endpoint = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    logger.debug(
        "Request %s: %s %s from %s", request_id, request.method, endpoint, client_ip
    )
    start_time = time.time()

    # Track the request in the metrics
    metrics_tracker.track_request(endpoint)

    # Check if IP is banned (for non-health endpoints)
    if config.enable_abuse_detection and endpoint not in ["/health", "/metrics"]:
        is_banned, ban_time = abuse_detector.is_banned(client_ip)
        if is_banned:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="ip_banned",
                        message=f"IP address temporarily banned due to abuse. Retry after {int(ban_time)} seconds.",
                        param=None,
                        type="security_error",
                    )
                ).model_dump(),
                headers={"Retry-After": str(int(ban_time))},
            )

    # Validate payload size
    if config.enable_input_validation:
        try:
            body = await request.body()
            # Store body for later use since it can only be read once
            request._body = body

            # Check payload size
            input_validator.validate_payload_size(body, config.max_request_size)

            # Validate for injection attacks if enabled
            if config.enable_injection_detection and body:
                try:
                    body_str = body.decode("utf-8", errors="ignore")
                    # Quick check for injection patterns in the raw request
                    input_validator.sanitize_string(
                        body_str[:10000]
                    )  # Check first 10KB
                except InjectionAttackDetected as e:
                    if config.enable_abuse_detection:
                        abuse_detector.record_injection_attempt(client_ip)
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content=ErrorResponse(
                            error=ErrorDetail(
                                code="injection_detected",
                                message="Potential injection attack detected in request.",
                                param=None,
                                type="security_error",
                            )
                        ).model_dump(),
                    )

        except PayloadTooLarge as e:
            if config.enable_abuse_detection:
                abuse_detector.record_oversized_payload(client_ip)
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="payload_too_large",
                        message=str(e),
                        param=None,
                        type="invalid_request_error",
                    )
                ).model_dump(),
            )
        except Exception as e:
            # Restore body for normal processing
            pass

    # Check rate limits if enabled
    rate_limit_headers = {}
    if config.rate_limit_enabled:
        # Extract API key from Authorization header
        auth_header = request.headers.get("Authorization", "")
        api_key = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header

        # Use API key if available, otherwise use default key for rate limiting
        effective_api_key = api_key if api_key else "anonymous"

        # Estimate token count from request body for chat/completions endpoints
        estimated_tokens = 0
        if endpoint in [
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/embeddings",
        ]:
            try:
                body = await request.body()
                # Store body for later use since it can only be read once
                request._body = body

                # Rough estimate: 1 token per 4 characters
                estimated_tokens = max(100, len(body) // 4)
            except Exception:
                estimated_tokens = 100  # Default estimate

        # Check rate limits
        allowed, retry_after, rate_limit_headers = rate_limiter.check_rate_limit(
            effective_api_key, estimated_tokens
        )

        if not allowed:
            # Record rate limit violation for abuse detection
            if config.enable_abuse_detection:
                abuse_detector.record_rate_limit_violation(client_ip)

            # Return 429 with rate limit headers
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="rate_limit_exceeded",
                        message="Rate limit exceeded. Please retry after the specified time.",
                        param=None,
                        type="rate_limit_error",
                    )
                ).model_dump(),
                headers={
                    **rate_limit_headers,
                    "Retry-After": retry_after,
                },
            )

    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = process_time * 1000

        # Track the response in the metrics
        metrics_tracker.track_response(endpoint, process_time)

        # Add rate limit headers to successful responses
        if rate_limit_headers:
            for header_name, header_value in rate_limit_headers.items():
                response.headers[header_name] = header_value

        logger.debug(
            "Request %s completed in %.2fms with status %s",
            request_id,
            process_time_ms,
            response.status_code,
        )
        return response
    except Exception as e:
        # Track the error in the metrics
        metrics_tracker.track_error(endpoint)

        logger.exception("Request %s failed: %s", request_id, str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="internal_server_error",
                    message="An unexpected error occurred.",
                    param=None,
                    type="server_error",
                )
            ).model_dump(),
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with readiness status"""
    global server_ready
    status = "healthy" if server_ready else "starting"
    return {
        "status": status,
        "ready": server_ready,
        "timestamp": datetime.now().isoformat(),
    }


# Startup event to mark server as ready
@app.on_event("startup")
async def startup_event():
    """Mark server as ready after startup."""
    global server_ready
    # Give a brief moment for all initialization to complete
    import asyncio

    await asyncio.sleep(0.1)
    server_ready = True

    # Start metrics streamer
    await metrics_streamer.start()

    logger.info("Server is ready to accept requests")


# Shutdown event to cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await metrics_streamer.stop()
    logger.info("Server shutdown complete")


# Dashboard endpoint
@app.get("/dashboard")
async def get_dashboard():
    """Serve the interactive metrics dashboard"""
    import os

    dashboard_path = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/dashboard/dynamo")
async def get_dynamo_dashboard():
    """Serve the advanced Dynamo dashboard with DCGM, KVBM, and SLA metrics"""
    import os

    dashboard_path = os.path.join(
        os.path.dirname(__file__), "static", "dashboard_advanced.html"
    )
    return FileResponse(dashboard_path, media_type="text/html")


# Models endpoints
@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
async def list_models() -> ModelListResponse:
    """List available models"""
    return await fakeai_service.list_models()


@app.get("/v1/models/{model_id:path}", dependencies=[Depends(verify_api_key)])
async def get_model(model_id: str):
    """Get model details"""
    try:
        return await fakeai_service.get_model(model_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/models/{model_id:path}/capabilities", dependencies=[Depends(verify_api_key)]
)
async def get_model_capabilities(model_id: str) -> ModelCapabilitiesResponse:
    """Get model capabilities including context window, pricing, and feature support"""
    return await fakeai_service.get_model_capabilities(model_id)


# Chat completions endpoints
@app.post(
    "/v1/chat/completions", dependencies=[Depends(verify_api_key)], response_model=None
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
):
    """Create a chat completion"""
    start_time = time.time()

    # Extract user from API key
    user = None
    if authorization and authorization.startswith("Bearer "):
        user = authorization[7:][:20]  # Use first 20 chars as identifier

    if request.stream:

        async def generate():
            async for chunk in fakeai_service.create_chat_completion_stream(request):
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
    else:
        response = await fakeai_service.create_chat_completion(request)

        # Track per-model metrics
        latency_ms = (time.time() - start_time) * 1000
        model_metrics_tracker.track_request(
            model=request.model,
            endpoint="/v1/chat/completions",
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            latency_ms=latency_ms,
            user=user,
            error=False,
        )

        return response


# Completions endpoints
@app.post(
    "/v1/completions", dependencies=[Depends(verify_api_key)], response_model=None
)
async def create_completion(
    request: CompletionRequest,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
):
    """Create a completion"""
    start_time = time.time()

    # Extract user from API key
    user = None
    if authorization and authorization.startswith("Bearer "):
        user = authorization[7:][:20]

    if request.stream:

        async def generate():
            async for chunk in fakeai_service.create_completion_stream(request):
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
    else:
        response = await fakeai_service.create_completion(request)

        # Track per-model metrics
        latency_ms = (time.time() - start_time) * 1000
        model_metrics_tracker.track_request(
            model=request.model,
            endpoint="/v1/completions",
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            latency_ms=latency_ms,
            user=user,
            error=False,
        )

        return response


# Embeddings endpoint
@app.post("/v1/embeddings", dependencies=[Depends(verify_api_key)])
async def create_embedding(
    request: EmbeddingRequest,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> EmbeddingResponse:
    """Create embeddings"""
    start_time = time.time()

    # Extract user from API key
    user = None
    if authorization and authorization.startswith("Bearer "):
        user = authorization[7:][:20]

    response = await fakeai_service.create_embedding(request)

    # Track per-model metrics
    latency_ms = (time.time() - start_time) * 1000
    model_metrics_tracker.track_request(
        model=request.model,
        endpoint="/v1/embeddings",
        prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
        completion_tokens=0,
        latency_ms=latency_ms,
        user=user,
        error=False,
    )

    return response


# Images endpoints
@app.post("/v1/images/generations", dependencies=[Depends(verify_api_key)])
async def generate_images(request: ImageGenerationRequest) -> ImageGenerationResponse:
    """Generate images"""
    return await fakeai_service.generate_images(request)


@app.get("/images/{image_id}.png")
async def get_image(image_id: str) -> Response:
    """
    Retrieve a generated image by ID.

    This endpoint serves actual generated images when image generation is enabled.
    Images are stored in memory and automatically cleaned up after retention period.
    """
    if not fakeai_service.image_generator:
        raise HTTPException(
            status_code=404,
            detail="Image generation is disabled. Enable with FAKEAI_GENERATE_ACTUAL_IMAGES=true",
        )

    image_bytes = fakeai_service.image_generator.get_image(image_id)

    if image_bytes is None:
        raise HTTPException(status_code=404, detail="Image not found or expired")

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{image_id}.png"',
        },
    )


# Audio (Text-to-Speech) endpoint
@app.post("/v1/audio/speech", dependencies=[Depends(verify_api_key)])
async def create_speech(request: SpeechRequest) -> Response:
    """
    Create text-to-speech audio.

    Generates audio from the input text using the specified voice and returns
    the audio file in the requested format.
    """
    # Generate audio bytes
    audio_bytes = await fakeai_service.create_speech(request)

    # Determine content type based on format
    content_type_map = {
        "mp3": "audio/mpeg",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "wav": "audio/wav",
        "pcm": "audio/pcm",
    }
    content_type = content_type_map.get(request.response_format, "audio/mpeg")

    # Return binary audio response
    return Response(
        content=audio_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="speech.{request.response_format}"',
        },
    )


# Files endpoints
@app.get("/v1/files", dependencies=[Depends(verify_api_key)])
async def list_files() -> FileListResponse:
    """List files"""
    return await fakeai_service.list_files()


@app.post("/v1/files", dependencies=[Depends(verify_api_key)])
async def upload_file():
    """Upload a file"""
    # This would typically handle file uploads
    return await fakeai_service.upload_file()


@app.get("/v1/files/{file_id}", dependencies=[Depends(verify_api_key)])
async def get_file(file_id: str) -> FileObject:
    """Get file details"""
    return await fakeai_service.get_file(file_id)


@app.delete("/v1/files/{file_id}", dependencies=[Depends(verify_api_key)])
async def delete_file(file_id: str):
    """Delete a file"""
    return await fakeai_service.delete_file(file_id)


# Text generation endpoints (for Azure compatibility) - Moved to /v1/text/generation
@app.post("/v1/text/generation", dependencies=[Depends(verify_api_key)])
async def create_text_generation(
    request: TextGenerationRequest,
) -> TextGenerationResponse:
    """Create a text generation (Azure API compatibility)"""
    return await fakeai_service.create_text_generation(request)


# OpenAI Responses API endpoint (March 2025 format)
@app.post("/v1/responses", dependencies=[Depends(verify_api_key)], response_model=None)
async def create_response(request: ResponsesRequest):
    """Create an OpenAI Responses API response"""
    return await fakeai_service.create_response(request)


# NVIDIA NIM Rankings API endpoint
@app.post("/v1/ranking", dependencies=[Depends(verify_api_key)])
async def create_ranking(request: RankingRequest) -> RankingResponse:
    """Create a NVIDIA NIM ranking response"""
    return await fakeai_service.create_ranking(request)


# Solido RAG API endpoint
@app.post("/rag/api/prompt", dependencies=[Depends(verify_api_key)])
async def create_solido_rag(request: SolidoRagRequest) -> SolidoRagResponse:
    """
    Create a Solido RAG response with retrieval-augmented generation.

    Retrieves relevant documents based on filters and generates
    context-aware responses using the specified inference model.
    """
    return await fakeai_service.create_solido_rag(request)


# Metrics endpoints
@app.get("/metrics")
async def get_metrics():
    """Get server metrics in JSON format"""
    return metrics_tracker.get_metrics()


@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get server metrics in Prometheus format"""
    return Response(
        content=metrics_tracker.get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/metrics/csv")
async def get_csv_metrics():
    """Get server metrics in CSV format"""
    return Response(
        content=metrics_tracker.get_csv_metrics(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=metrics.csv"},
    )


@app.websocket("/metrics/stream")
async def metrics_stream(websocket: WebSocket):
    """
    Real-time metrics streaming via WebSocket.

    Supports subscription-based filtering by endpoint, model, and metric type.
    Clients can control update intervals and receive delta calculations.

    Example client usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/metrics/stream');
    ws.onopen = () => {
        ws.send(JSON.stringify({
            type: 'subscribe',
            filters: {
                endpoint: '/v1/chat/completions',
                interval: 1.0
            }
        }));
    };
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Metrics update:', data);
    };
    ```
    """
    await metrics_streamer.handle_websocket(websocket)


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with metrics summary"""
    return metrics_tracker.get_detailed_health()


@app.get("/kv-cache/metrics")
async def get_kv_cache_metrics():
    """Get KV cache and AI-Dynamo smart routing metrics."""
    return {
        "cache_performance": fakeai_service.kv_cache_metrics.get_stats(),
        "smart_router": fakeai_service.kv_cache_router.get_stats(),
    }


# Per-Model Metrics endpoints
@app.get("/metrics/by-model")
async def get_metrics_by_model():
    """Get metrics grouped by model in JSON format."""
    return model_metrics_tracker.get_all_models_stats()


@app.get("/metrics/by-model/prometheus")
async def get_model_metrics_prometheus():
    """Get per-model metrics in Prometheus format."""
    return Response(
        content=model_metrics_tracker.get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/metrics/by-model/{model_id:path}")
async def get_model_metrics(model_id: str):
    """Get metrics for a specific model."""
    return model_metrics_tracker.get_model_stats(model_id)


@app.get("/metrics/compare")
async def compare_models(
    model1: str = Query(..., description="First model ID"),
    model2: str = Query(..., description="Second model ID"),
):
    """
    Compare two models side-by-side.

    Returns comparison metrics including:
    - Request counts
    - Latency differences
    - Error rates
    - Cost comparisons
    - Winner determination
    """
    return model_metrics_tracker.compare_models(model1, model2)


@app.get("/metrics/ranking")
async def get_model_ranking(
    metric: str = Query(
        default="request_count",
        description="Metric to rank by (request_count, latency, error_rate, cost, tokens)",
    ),
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of models to return"
    ),
):
    """
    Get top models ranked by a specific metric.

    Supports ranking by:
    - request_count: Most used models
    - latency: Fastest models
    - error_rate: Most reliable models
    - cost: Most expensive models
    - tokens: Highest token usage
    """
    return model_metrics_tracker.get_model_ranking(metric=metric, limit=limit)


@app.get("/metrics/costs")
async def get_costs_by_model():
    """Get estimated cost breakdown by model."""
    return {
        "costs_by_model": model_metrics_tracker.get_cost_by_model(),
        "total_cost_usd": sum(model_metrics_tracker.get_cost_by_model().values()),
    }


@app.get("/metrics/multi-dimensional")
async def get_multi_dimensional_metrics():
    """
    Get multi-dimensional metrics breakdown.

    Returns 2D breakdowns:
    - Model by endpoint
    - Model by user
    - Model by time (24h buckets)
    """
    return model_metrics_tracker.get_multi_dimensional_stats()


# DCGM GPU Metrics endpoints
@app.get("/dcgm/metrics")
async def get_dcgm_metrics_prometheus():
    """Get simulated DCGM GPU metrics in Prometheus format."""
    # Return real simulated DCGM metrics in Prometheus format
    return Response(
        content=fakeai_service.dcgm_simulator.get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/dcgm/metrics/json")
async def get_dcgm_metrics_json():
    """Get simulated DCGM GPU metrics in JSON format."""
    # Return real simulated GPU metrics
    return fakeai_service.dcgm_simulator.get_metrics_dict()


# Dynamo LLM Metrics endpoints
@app.get("/dynamo/metrics")
async def get_dynamo_metrics_prometheus():
    """Get AI-Dynamo LLM inference metrics in Prometheus format."""
    # Return real Prometheus metrics from DynamoMetricsCollector
    return Response(
        content=fakeai_service.dynamo_metrics.get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/dynamo/metrics/json")
async def get_dynamo_metrics_json():
    """Get AI-Dynamo LLM inference metrics in JSON format."""
    # Return real metrics from DynamoMetricsCollector
    return fakeai_service.dynamo_metrics.get_stats_dict()


# Rate Limiter Metrics endpoints
@app.get("/metrics/rate-limits")
async def get_rate_limit_metrics():
    """
    Get comprehensive rate limiting metrics.

    Returns detailed statistics including:
    - Per-key metrics (requests, tokens, throttling)
    - Tier-level aggregations
    - Throttle analytics (histograms, distributions)
    - Abuse pattern detection
    """
    return rate_limiter.metrics.get_all_metrics()


@app.get("/metrics/rate-limits/key/{api_key}")
async def get_rate_limit_key_stats(api_key: str):
    """
    Get rate limiting statistics for a specific API key.

    Args:
        api_key: The API key to retrieve stats for

    Returns detailed metrics including:
    - Request counts (attempted, allowed, throttled)
    - Token consumption and efficiency
    - Throttling statistics
    - Usage patterns and peaks
    - Quota utilization
    """
    stats = rate_limiter.metrics.get_key_stats(api_key)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for API key: {api_key}",
        )
    return stats


@app.get("/metrics/rate-limits/tier")
async def get_rate_limit_tier_stats():
    """
    Get rate limiting statistics aggregated by tier.

    Returns per-tier aggregations including:
    - Total requests and tokens
    - Average throttle rates
    - Keys with high throttle rates
    - Quota exhaustion events
    - Upgrade opportunities
    """
    return rate_limiter.metrics.get_tier_stats()


@app.get("/metrics/rate-limits/throttle-analytics")
async def get_throttle_analytics():
    """
    Get detailed throttling analytics.

    Returns:
    - Throttle duration histogram
    - Retry-after distribution (percentiles)
    - RPM vs TPM exceeded breakdown
    """
    return rate_limiter.metrics.get_throttle_analytics()


@app.get("/metrics/rate-limits/abuse-patterns")
async def get_abuse_patterns():
    """
    Detect potential abuse patterns across API keys.

    Analyzes:
    - High throttle rates (>50%)
    - Excessive retries
    - Burst behavior
    - Quota exhaustion patterns

    Returns list of API keys with detected abuse patterns,
    including severity classification.
    """
    return rate_limiter.metrics.detect_abuse_patterns()


# Moderation endpoint
@app.post("/v1/moderations", dependencies=[Depends(verify_api_key)])
async def create_moderation(request: ModerationRequest) -> ModerationResponse:
    """Classify if text and/or image inputs are potentially harmful."""
    return await fakeai_service.create_moderation(request)


# Batch API endpoints
@app.post("/v1/batches", dependencies=[Depends(verify_api_key)])
async def create_batch(request: CreateBatchRequest) -> Batch:
    """Create a batch processing job."""
    return await fakeai_service.create_batch(request)


@app.get("/v1/batches/{batch_id}", dependencies=[Depends(verify_api_key)])
async def retrieve_batch(batch_id: str) -> Batch:
    """Retrieve a batch by ID."""
    try:
        return await fakeai_service.retrieve_batch(batch_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/v1/batches/{batch_id}/cancel", dependencies=[Depends(verify_api_key)])
async def cancel_batch(batch_id: str) -> Batch:
    """Cancel a batch."""
    try:
        return await fakeai_service.cancel_batch(batch_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/v1/batches", dependencies=[Depends(verify_api_key)])
async def list_batches(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> BatchListResponse:
    """List all batches with pagination."""
    return await fakeai_service.list_batches(limit=limit, after=after)


# Organization and Project Management API endpoints


# Organization Users
@app.get("/v1/organization/users", dependencies=[Depends(verify_api_key)])
async def list_organization_users(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> OrganizationUserListResponse:
    """List all users in the organization."""
    return await fakeai_service.list_organization_users(limit=limit, after=after)


@app.get("/v1/organization/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def get_organization_user(user_id: str) -> OrganizationUser:
    """Get a specific organization user."""
    try:
        return await fakeai_service.get_organization_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/v1/organization/users", dependencies=[Depends(verify_api_key)])
async def create_organization_user(
    request: CreateOrganizationUserRequest,
) -> OrganizationUser:
    """Add a user to the organization."""
    return await fakeai_service.create_organization_user(request)


@app.post("/v1/organization/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def modify_organization_user(
    user_id: str, request: ModifyOrganizationUserRequest
) -> OrganizationUser:
    """Modify an organization user's role."""
    try:
        return await fakeai_service.modify_organization_user(user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete("/v1/organization/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def delete_organization_user(user_id: str) -> dict:
    """Remove a user from the organization."""
    try:
        return await fakeai_service.delete_organization_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Organization Invites
@app.get("/v1/organization/invites", dependencies=[Depends(verify_api_key)])
async def list_organization_invites(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> OrganizationInviteListResponse:
    """List all organization invites."""
    return await fakeai_service.list_organization_invites(limit=limit, after=after)


@app.post("/v1/organization/invites", dependencies=[Depends(verify_api_key)])
async def create_organization_invite(
    request: CreateOrganizationInviteRequest,
) -> OrganizationInvite:
    """Create an organization invite."""
    return await fakeai_service.create_organization_invite(request)


@app.get("/v1/organization/invites/{invite_id}", dependencies=[Depends(verify_api_key)])
async def get_organization_invite(invite_id: str) -> OrganizationInvite:
    """Get a specific organization invite."""
    try:
        return await fakeai_service.get_organization_invite(invite_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/v1/organization/invites/{invite_id}", dependencies=[Depends(verify_api_key)]
)
async def delete_organization_invite(
    invite_id: str,
) -> DeleteOrganizationInviteResponse:
    """Delete an organization invite."""
    try:
        return await fakeai_service.delete_organization_invite(invite_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Organization Projects
@app.get("/v1/organization/projects", dependencies=[Depends(verify_api_key)])
async def list_organization_projects(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
) -> OrganizationProjectListResponse:
    """List all projects in the organization."""
    return await fakeai_service.list_organization_projects(
        limit=limit, after=after, include_archived=include_archived
    )


@app.post("/v1/organization/projects", dependencies=[Depends(verify_api_key)])
async def create_organization_project(
    request: CreateOrganizationProjectRequest,
) -> OrganizationProject:
    """Create a new project in the organization."""
    return await fakeai_service.create_organization_project(request)


@app.get(
    "/v1/organization/projects/{project_id}", dependencies=[Depends(verify_api_key)]
)
async def get_organization_project(project_id: str) -> OrganizationProject:
    """Get a specific project."""
    try:
        return await fakeai_service.get_organization_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/organization/projects/{project_id}", dependencies=[Depends(verify_api_key)]
)
async def modify_organization_project(
    project_id: str, request: ModifyOrganizationProjectRequest
) -> OrganizationProject:
    """Modify a project."""
    try:
        return await fakeai_service.modify_organization_project(project_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/organization/projects/{project_id}/archive",
    dependencies=[Depends(verify_api_key)],
)
async def archive_organization_project(
    project_id: str,
) -> ArchiveOrganizationProjectResponse:
    """Archive a project."""
    try:
        return await fakeai_service.archive_organization_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Project Users
@app.get(
    "/v1/organization/projects/{project_id}/users",
    dependencies=[Depends(verify_api_key)],
)
async def list_project_users(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> ProjectUserListResponse:
    """List all users in a project."""
    try:
        return await fakeai_service.list_project_users(
            project_id, limit=limit, after=after
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/organization/projects/{project_id}/users",
    dependencies=[Depends(verify_api_key)],
)
async def create_project_user(
    project_id: str, request: CreateProjectUserRequest
) -> ProjectUser:
    """Add a user to a project."""
    try:
        return await fakeai_service.create_project_user(project_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/organization/projects/{project_id}/users/{user_id}",
    dependencies=[Depends(verify_api_key)],
)
async def get_project_user(project_id: str, user_id: str) -> ProjectUser:
    """Get a specific user in a project."""
    try:
        return await fakeai_service.get_project_user(project_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/organization/projects/{project_id}/users/{user_id}",
    dependencies=[Depends(verify_api_key)],
)
async def modify_project_user(
    project_id: str, user_id: str, request: ModifyProjectUserRequest
) -> ProjectUser:
    """Modify a user's role in a project."""
    try:
        return await fakeai_service.modify_project_user(project_id, user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/v1/organization/projects/{project_id}/users/{user_id}",
    dependencies=[Depends(verify_api_key)],
)
async def delete_project_user(
    project_id: str, user_id: str
) -> DeleteProjectUserResponse:
    """Remove a user from a project."""
    try:
        return await fakeai_service.delete_project_user(project_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Project Service Accounts
@app.get(
    "/v1/organization/projects/{project_id}/service_accounts",
    dependencies=[Depends(verify_api_key)],
)
async def list_service_accounts(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> ServiceAccountListResponse:
    """List all service accounts in a project."""
    try:
        return await fakeai_service.list_service_accounts(
            project_id, limit=limit, after=after
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/organization/projects/{project_id}/service_accounts",
    dependencies=[Depends(verify_api_key)],
)
async def create_service_account(
    project_id: str, request: CreateServiceAccountRequest
) -> ServiceAccount:
    """Create a service account in a project."""
    try:
        return await fakeai_service.create_service_account(project_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/organization/projects/{project_id}/service_accounts/{service_account_id}",
    dependencies=[Depends(verify_api_key)],
)
async def get_service_account(
    project_id: str, service_account_id: str
) -> ServiceAccount:
    """Get a specific service account."""
    try:
        return await fakeai_service.get_service_account(project_id, service_account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/v1/organization/projects/{project_id}/service_accounts/{service_account_id}",
    dependencies=[Depends(verify_api_key)],
)
async def delete_service_account(
    project_id: str, service_account_id: str
) -> DeleteServiceAccountResponse:
    """Delete a service account."""
    try:
        return await fakeai_service.delete_service_account(
            project_id, service_account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Usage and Billing API endpoints


@app.get("/v1/organization/usage/completions", dependencies=[Depends(verify_api_key)])
async def get_completions_usage(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
    model: str | None = Query(default=None, description="Optional model filter"),
) -> CompletionsUsageResponse:
    """
    Get usage data for completions endpoints.

    Returns aggregated usage data grouped by time buckets.
    """
    return await fakeai_service.get_completions_usage(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
        model=model,
    )


@app.get("/v1/organization/usage/embeddings", dependencies=[Depends(verify_api_key)])
async def get_embeddings_usage(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
    model: str | None = Query(default=None, description="Optional model filter"),
) -> EmbeddingsUsageResponse:
    """
    Get usage data for embeddings endpoints.

    Returns aggregated usage data grouped by time buckets.
    """
    return await fakeai_service.get_embeddings_usage(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
        model=model,
    )


@app.get("/v1/organization/usage/images", dependencies=[Depends(verify_api_key)])
async def get_images_usage(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
) -> ImagesUsageResponse:
    """
    Get usage data for images endpoints.

    Returns aggregated usage data grouped by time buckets.
    """
    return await fakeai_service.get_images_usage(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
    )


@app.get(
    "/v1/organization/usage/audio_speeches", dependencies=[Depends(verify_api_key)]
)
async def get_audio_speeches_usage(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
) -> AudioSpeechesUsageResponse:
    """
    Get usage data for audio speeches endpoints.

    Returns aggregated usage data grouped by time buckets.
    """
    return await fakeai_service.get_audio_speeches_usage(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
    )


@app.get(
    "/v1/organization/usage/audio_transcriptions",
    dependencies=[Depends(verify_api_key)],
)
async def get_audio_transcriptions_usage(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
) -> AudioTranscriptionsUsageResponse:
    """
    Get usage data for audio transcriptions endpoints.

    Returns aggregated usage data grouped by time buckets.
    """
    return await fakeai_service.get_audio_transcriptions_usage(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
    )


@app.get("/v1/organization/costs", dependencies=[Depends(verify_api_key)])
async def get_costs(
    start_time: int = Query(description="Start time (Unix timestamp)"),
    end_time: int = Query(description="End time (Unix timestamp)"),
    bucket_width: str = Query(
        default="1d", description="Time bucket width ('1m', '1h', '1d')"
    ),
    project_id: str | None = Query(
        default=None, description="Optional project ID filter"
    ),
    group_by: list[str] | None = Query(
        default=None, description="Optional grouping dimensions"
    ),
) -> CostsResponse:
    """
    Get cost data aggregated by time buckets.

    Returns cost breakdowns grouped by line item and project.
    """
    return await fakeai_service.get_costs(
        start_time=start_time,
        end_time=end_time,
        bucket_width=bucket_width,
        project_id=project_id,
        group_by=group_by,
    )


# Realtime WebSocket API endpoint
@app.websocket("/v1/realtime")
async def realtime_websocket(
    websocket: WebSocket,
    model: str = Query(default="openai/gpt-oss-120b-realtime-preview-2024-10-01"),
):
    """
    Realtime WebSocket API endpoint.

    Provides bidirectional streaming conversation with audio and text support,
    voice activity detection, and function calling.
    """
    await websocket.accept()
    logger.info(f"Realtime WebSocket connection established for model: {model}")

    # Create session handler
    session_handler = RealtimeSessionHandler(
        model=model,
        config=config,
        fakeai_service=fakeai_service,
    )

    # Send session.created event
    from fakeai.models import RealtimeEventType

    session_created = session_handler._create_event(
        RealtimeEventType.SESSION_CREATED,
        session=session_handler.session,
    )
    await websocket.send_text(session_created.model_dump_json())

    try:
        while True:
            # Receive client event
            data = await websocket.receive_text()

            try:
                import json

                event_data = json.loads(data)
                event_type = event_data.get("type")

                logger.debug(f"Received Realtime event: {event_type}")

                # Handle different event types
                if event_type == "session.update":
                    # Update session configuration
                    session_config = event_data.get("session", {})
                    response_event = session_handler.update_session(session_config)
                    await websocket.send_text(response_event.model_dump_json())

                elif event_type == "input_audio_buffer.append":
                    # Append audio to buffer
                    audio = event_data.get("audio", "")
                    events = session_handler.append_audio_buffer(audio)
                    for event in events:
                        await websocket.send_text(event.model_dump_json())

                elif event_type == "input_audio_buffer.commit":
                    # Commit audio buffer
                    events = session_handler.commit_audio_buffer()
                    for event in events:
                        await websocket.send_text(event.model_dump_json())

                elif event_type == "input_audio_buffer.clear":
                    # Clear audio buffer
                    event = session_handler.clear_audio_buffer()
                    await websocket.send_text(event.model_dump_json())

                elif event_type == "conversation.item.create":
                    # Create conversation item
                    item_data = event_data.get("item", {})
                    event = session_handler.create_conversation_item(item_data)
                    await websocket.send_text(event.model_dump_json())

                elif event_type == "conversation.item.delete":
                    # Delete conversation item
                    item_id = event_data.get("item_id", "")
                    event = session_handler.delete_conversation_item(item_id)
                    await websocket.send_text(event.model_dump_json())

                elif event_type == "response.create":
                    # Create response (streaming)
                    response_config = event_data.get("response", {})
                    async for event in session_handler.create_response(response_config):
                        await websocket.send_text(event.model_dump_json())

                elif event_type == "response.cancel":
                    # Cancel current response
                    event = session_handler.cancel_response()
                    await websocket.send_text(event.model_dump_json())

                else:
                    # Unknown event type
                    from fakeai.models import RealtimeError, RealtimeEventType

                    error_event = session_handler._create_event(
                        RealtimeEventType.ERROR,
                        error=RealtimeError(
                            type="invalid_request_error",
                            code="unknown_event",
                            message=f"Unknown event type: {event_type}",
                        ),
                    )
                    await websocket.send_text(error_event.model_dump_json())

            except json.JSONDecodeError as e:
                # Invalid JSON
                from fakeai.models import RealtimeError, RealtimeEventType

                error_event = session_handler._create_event(
                    RealtimeEventType.ERROR,
                    error=RealtimeError(
                        type="invalid_request_error",
                        code="invalid_json",
                        message=f"Invalid JSON: {str(e)}",
                    ),
                )
                await websocket.send_text(error_event.model_dump_json())

            except Exception as e:
                # Other errors
                logger.exception(f"Error processing Realtime event: {str(e)}")
                from fakeai.models import RealtimeError, RealtimeEventType

                error_event = session_handler._create_event(
                    RealtimeEventType.ERROR,
                    error=RealtimeError(
                        type="server_error",
                        code="internal_error",
                        message=f"Internal server error: {str(e)}",
                    ),
                )
                await websocket.send_text(error_event.model_dump_json())

    except WebSocketDisconnect:
        logger.info("Realtime WebSocket connection closed")
    except Exception as e:
        logger.exception(f"Unexpected error in Realtime WebSocket: {str(e)}")


# Fine-Tuning API endpoints
@app.post("/v1/fine_tuning/jobs", dependencies=[Depends(verify_api_key)])
async def create_fine_tuning_job(request: FineTuningJobRequest) -> FineTuningJob:
    """Create a new fine-tuning job."""
    try:
        return await fakeai_service.create_fine_tuning_job(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/fine_tuning/jobs", dependencies=[Depends(verify_api_key)])
async def list_fine_tuning_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = Query(default=None),
) -> FineTuningJobList:
    """List fine-tuning jobs with pagination."""
    return await fakeai_service.list_fine_tuning_jobs(limit=limit, after=after)


@app.get("/v1/fine_tuning/jobs/{job_id}", dependencies=[Depends(verify_api_key)])
async def retrieve_fine_tuning_job(job_id: str) -> FineTuningJob:
    """Retrieve a specific fine-tuning job."""
    try:
        return await fakeai_service.retrieve_fine_tuning_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post(
    "/v1/fine_tuning/jobs/{job_id}/cancel", dependencies=[Depends(verify_api_key)]
)
async def cancel_fine_tuning_job(job_id: str) -> FineTuningJob:
    """Cancel a running or queued fine-tuning job."""
    try:
        return await fakeai_service.cancel_fine_tuning_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/fine_tuning/jobs/{job_id}/events", dependencies=[Depends(verify_api_key)])
async def list_fine_tuning_events(
    job_id: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    """Stream fine-tuning events via Server-Sent Events (SSE)."""
    try:

        async def event_stream():
            async for event in fakeai_service.list_fine_tuning_events(job_id, limit):
                yield event

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/v1/fine_tuning/jobs/{job_id}/checkpoints", dependencies=[Depends(verify_api_key)]
)
async def list_fine_tuning_checkpoints(
    job_id: str,
    limit: int = Query(default=10, ge=1, le=100),
) -> FineTuningCheckpointList:
    """List checkpoints for a fine-tuning job."""
    try:
        return await fakeai_service.list_fine_tuning_checkpoints(job_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Vector Stores API endpoints
@app.post("/v1/vector_stores", dependencies=[Depends(verify_api_key)])
async def create_vector_store(request: CreateVectorStoreRequest) -> VectorStore:
    """Create a new vector store."""
    return await fakeai_service.create_vector_store(request)


@app.get("/v1/vector_stores", dependencies=[Depends(verify_api_key)])
async def list_vector_stores(
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> VectorStoreListResponse:
    """List all vector stores with pagination."""
    return await fakeai_service.list_vector_stores(
        limit=limit, order=order, after=after, before=before
    )


@app.get("/v1/vector_stores/{vector_store_id}", dependencies=[Depends(verify_api_key)])
async def retrieve_vector_store(vector_store_id: str) -> VectorStore:
    """Retrieve a vector store by ID."""
    try:
        return await fakeai_service.retrieve_vector_store(vector_store_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/v1/vector_stores/{vector_store_id}", dependencies=[Depends(verify_api_key)])
async def modify_vector_store(
    vector_store_id: str, request: ModifyVectorStoreRequest
) -> VectorStore:
    """Modify a vector store."""
    try:
        return await fakeai_service.modify_vector_store(vector_store_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/v1/vector_stores/{vector_store_id}", dependencies=[Depends(verify_api_key)]
)
async def delete_vector_store(vector_store_id: str) -> dict:
    """Delete a vector store."""
    try:
        return await fakeai_service.delete_vector_store(vector_store_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Vector Store Files endpoints
@app.post(
    "/v1/vector_stores/{vector_store_id}/files", dependencies=[Depends(verify_api_key)]
)
async def create_vector_store_file(
    vector_store_id: str, request: CreateVectorStoreFileRequest
) -> VectorStoreFile:
    """Add a file to a vector store."""
    try:
        return await fakeai_service.create_vector_store_file(vector_store_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/vector_stores/{vector_store_id}/files", dependencies=[Depends(verify_api_key)]
)
async def list_vector_store_files(
    vector_store_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> VectorStoreFileListResponse:
    """List all files in a vector store with pagination."""
    try:
        return await fakeai_service.list_vector_store_files(
            vector_store_id, limit=limit, order=order, after=after, before=before
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/vector_stores/{vector_store_id}/files/{file_id}",
    dependencies=[Depends(verify_api_key)],
)
async def retrieve_vector_store_file(
    vector_store_id: str, file_id: str
) -> VectorStoreFile:
    """Retrieve a specific file from a vector store."""
    try:
        return await fakeai_service.retrieve_vector_store_file(vector_store_id, file_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/v1/vector_stores/{vector_store_id}/files/{file_id}",
    dependencies=[Depends(verify_api_key)],
)
async def delete_vector_store_file(vector_store_id: str, file_id: str) -> dict:
    """Remove a file from a vector store."""
    try:
        return await fakeai_service.delete_vector_store_file(vector_store_id, file_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Vector Store File Batches endpoints
@app.post(
    "/v1/vector_stores/{vector_store_id}/file_batches",
    dependencies=[Depends(verify_api_key)],
)
async def create_vector_store_file_batch(
    vector_store_id: str, request: CreateVectorStoreFileBatchRequest
) -> VectorStoreFileBatch:
    """Create a batch of files in a vector store."""
    try:
        return await fakeai_service.create_vector_store_file_batch(
            vector_store_id, request
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/vector_stores/{vector_store_id}/file_batches/{batch_id}",
    dependencies=[Depends(verify_api_key)],
)
async def retrieve_vector_store_file_batch(
    vector_store_id: str, batch_id: str
) -> VectorStoreFileBatch:
    """Retrieve a file batch from a vector store."""
    try:
        return await fakeai_service.retrieve_vector_store_file_batch(
            vector_store_id, batch_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post(
    "/v1/vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel",
    dependencies=[Depends(verify_api_key)],
)
async def cancel_vector_store_file_batch(
    vector_store_id: str, batch_id: str
) -> VectorStoreFileBatch:
    """Cancel a file batch in a vector store."""
    try:
        return await fakeai_service.cancel_vector_store_file_batch(
            vector_store_id, batch_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/v1/vector_stores/{vector_store_id}/file_batches/{batch_id}/files",
    dependencies=[Depends(verify_api_key)],
)
async def list_vector_store_files_in_batch(
    vector_store_id: str,
    batch_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> VectorStoreFileListResponse:
    """List files in a specific batch."""
    try:
        # For simplicity, just list all files in the vector store
        return await fakeai_service.list_vector_store_files(
            vector_store_id, limit=limit, order=order, after=after, before=before
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
# ==============================================================================
# ASSISTANTS API
# ==============================================================================

# In-memory storage for assistants, threads, messages, and runs
assistants_storage: dict[str, Assistant] = {}
threads_storage: dict[str, dict] = {}
messages_storage: dict[str, list[ThreadMessage]] = {}
runs_storage: dict[str, dict[str, Run]] = {}
run_steps_storage: dict[str, dict[str, list[RunStep]]] = {}


def _generate_assistant_id() -> str:
    """Generate a unique assistant ID."""
    import uuid
    return f"asst_{uuid.uuid4().hex}"


def _generate_thread_id() -> str:
    """Generate a unique thread ID."""
    import uuid
    return f"thread_{uuid.uuid4().hex}"


def _generate_message_id() -> str:
    """Generate a unique message ID."""
    import uuid
    return f"msg_{uuid.uuid4().hex}"


def _generate_run_id() -> str:
    """Generate a unique run ID."""
    import uuid
    return f"run_{uuid.uuid4().hex}"


def _generate_step_id() -> str:
    """Generate a unique step ID."""
    import uuid
    return f"step_{uuid.uuid4().hex}"


# Assistants CRUD endpoints
@app.post("/v1/assistants", dependencies=[Depends(verify_api_key)])
async def create_assistant(request: CreateAssistantRequest) -> Assistant:
    """Create a new assistant."""
    assistant_id = _generate_assistant_id()
    created_at = int(time.time())

    assistant = Assistant(
        id=assistant_id,
        created_at=created_at,
        name=request.name,
        description=request.description,
        model=request.model,
        instructions=request.instructions,
        tools=request.tools,
        tool_resources=request.tool_resources,
        metadata=request.metadata,
        temperature=request.temperature,
        top_p=request.top_p,
        response_format=request.response_format,
    )

    assistants_storage[assistant_id] = assistant
    return assistant


@app.get("/v1/assistants", dependencies=[Depends(verify_api_key)])
async def list_assistants(
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> AssistantList:
    """List assistants with pagination."""
    assistants = list(assistants_storage.values())

    # Sort by created_at
    assistants.sort(key=lambda a: a.created_at, reverse=(order == "desc"))

    # Apply pagination
    if after:
        try:
            after_idx = next(i for i, a in enumerate(assistants) if a.id == after)
            assistants = assistants[after_idx + 1:]
        except StopIteration:
            pass

    if before:
        try:
            before_idx = next(i for i, a in enumerate(assistants) if a.id == before)
            assistants = assistants[:before_idx]
        except StopIteration:
            pass

    # Limit results
    has_more = len(assistants) > limit
    assistants = assistants[:limit]

    return AssistantList(
        data=assistants,
        first_id=assistants[0].id if assistants else None,
        last_id=assistants[-1].id if assistants else None,
        has_more=has_more,
    )


@app.get("/v1/assistants/{assistant_id}", dependencies=[Depends(verify_api_key)])
async def retrieve_assistant(assistant_id: str) -> Assistant:
    """Retrieve a specific assistant."""
    if assistant_id not in assistants_storage:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")
    return assistants_storage[assistant_id]


@app.post("/v1/assistants/{assistant_id}", dependencies=[Depends(verify_api_key)])
async def modify_assistant(
    assistant_id: str, request: ModifyAssistantRequest
) -> Assistant:
    """Modify an existing assistant."""
    if assistant_id not in assistants_storage:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")

    assistant = assistants_storage[assistant_id]

    # Update fields if provided
    if request.model is not None:
        assistant.model = request.model
    if request.name is not None:
        assistant.name = request.name
    if request.description is not None:
        assistant.description = request.description
    if request.instructions is not None:
        assistant.instructions = request.instructions
    if request.tools is not None:
        assistant.tools = request.tools
    if request.tool_resources is not None:
        assistant.tool_resources = request.tool_resources
    if request.metadata is not None:
        assistant.metadata = request.metadata
    if request.temperature is not None:
        assistant.temperature = request.temperature
    if request.top_p is not None:
        assistant.top_p = request.top_p
    if request.response_format is not None:
        assistant.response_format = request.response_format

    return assistant


@app.delete("/v1/assistants/{assistant_id}", dependencies=[Depends(verify_api_key)])
async def delete_assistant(assistant_id: str) -> dict:
    """Delete an assistant."""
    if assistant_id not in assistants_storage:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")

    del assistants_storage[assistant_id]

    return {
        "id": assistant_id,
        "object": "assistant.deleted",
        "deleted": True,
    }


# Threads endpoints
@app.post("/v1/threads", dependencies=[Depends(verify_api_key)])
async def create_thread(request: CreateThreadRequest) -> Thread:
    """Create a new thread."""
    thread_id = _generate_thread_id()
    created_at = int(time.time())

    thread = Thread(
        id=thread_id,
        created_at=created_at,
        metadata=request.metadata,
        tool_resources=request.tool_resources,
    )

    threads_storage[thread_id] = thread.model_dump()
    messages_storage[thread_id] = []

    # Create initial messages if provided
    if request.messages:
        for msg_data in request.messages:
            message_id = _generate_message_id()
            content = msg_data.get("content", "")

            # Convert string content to content array format
            if isinstance(content, str):
                content_array = [{"type": "text", "text": {"value": content}}]
            else:
                content_array = content

            message = ThreadMessage(
                id=message_id,
                created_at=int(time.time()),
                thread_id=thread_id,
                role=msg_data.get("role", "user"),
                content=content_array,
                metadata=msg_data.get("metadata", {}),
            )
            messages_storage[thread_id].append(message)

    return thread


@app.get("/v1/threads/{thread_id}", dependencies=[Depends(verify_api_key)])
async def retrieve_thread(thread_id: str) -> Thread:
    """Retrieve a specific thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
    return Thread(**threads_storage[thread_id])


@app.post("/v1/threads/{thread_id}", dependencies=[Depends(verify_api_key)])
async def modify_thread(thread_id: str, request: ModifyThreadRequest) -> Thread:
    """Modify a thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    thread_data = threads_storage[thread_id]

    if request.metadata is not None:
        thread_data["metadata"] = request.metadata
    if request.tool_resources is not None:
        thread_data["tool_resources"] = request.tool_resources

    return Thread(**thread_data)


@app.delete("/v1/threads/{thread_id}", dependencies=[Depends(verify_api_key)])
async def delete_thread(thread_id: str) -> dict:
    """Delete a thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    del threads_storage[thread_id]
    if thread_id in messages_storage:
        del messages_storage[thread_id]
    if thread_id in runs_storage:
        del runs_storage[thread_id]
    if thread_id in run_steps_storage:
        del run_steps_storage[thread_id]

    return {
        "id": thread_id,
        "object": "thread.deleted",
        "deleted": True,
    }


# Messages endpoints
@app.post("/v1/threads/{thread_id}/messages", dependencies=[Depends(verify_api_key)])
async def create_message(thread_id: str, request: CreateMessageRequest) -> ThreadMessage:
    """Create a message in a thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    message_id = _generate_message_id()
    created_at = int(time.time())

    # Convert string content to content array format
    if isinstance(request.content, str):
        content_array = [{"type": "text", "text": {"value": request.content}}]
    else:
        content_array = request.content

    message = ThreadMessage(
        id=message_id,
        created_at=created_at,
        thread_id=thread_id,
        role=request.role,
        content=content_array,
        attachments=request.attachments,
        metadata=request.metadata,
    )

    if thread_id not in messages_storage:
        messages_storage[thread_id] = []

    messages_storage[thread_id].append(message)

    return message


@app.get("/v1/threads/{thread_id}/messages", dependencies=[Depends(verify_api_key)])
async def list_messages(
    thread_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> MessageList:
    """List messages in a thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    messages = messages_storage.get(thread_id, [])

    # Sort by created_at
    messages = sorted(messages, key=lambda m: m.created_at, reverse=(order == "desc"))

    # Apply pagination
    if after:
        try:
            after_idx = next(i for i, m in enumerate(messages) if m.id == after)
            messages = messages[after_idx + 1:]
        except StopIteration:
            pass

    if before:
        try:
            before_idx = next(i for i, m in enumerate(messages) if m.id == before)
            messages = messages[:before_idx]
        except StopIteration:
            pass

    # Limit results
    has_more = len(messages) > limit
    messages = messages[:limit]

    return MessageList(
        data=messages,
        first_id=messages[0].id if messages else None,
        last_id=messages[-1].id if messages else None,
        has_more=has_more,
    )


@app.get(
    "/v1/threads/{thread_id}/messages/{message_id}",
    dependencies=[Depends(verify_api_key)],
)
async def retrieve_message(thread_id: str, message_id: str) -> ThreadMessage:
    """Retrieve a specific message."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    messages = messages_storage.get(thread_id, [])
    message = next((m for m in messages if m.id == message_id), None)

    if not message:
        raise HTTPException(status_code=404, detail=f"Message {message_id} not found")

    return message


@app.post(
    "/v1/threads/{thread_id}/messages/{message_id}",
    dependencies=[Depends(verify_api_key)],
)
async def modify_message(
    thread_id: str, message_id: str, request: dict
) -> ThreadMessage:
    """Modify a message (only metadata)."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    messages = messages_storage.get(thread_id, [])
    message = next((m for m in messages if m.id == message_id), None)

    if not message:
        raise HTTPException(status_code=404, detail=f"Message {message_id} not found")

    # Only metadata can be modified
    if "metadata" in request:
        message.metadata = request["metadata"]

    return message


# Runs endpoints
@app.post("/v1/threads/{thread_id}/runs", dependencies=[Depends(verify_api_key)], response_model=None)
async def create_run(thread_id: str, request: CreateRunRequest):
    """Create a run."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    if request.assistant_id not in assistants_storage:
        raise HTTPException(
            status_code=404, detail=f"Assistant {request.assistant_id} not found"
        )

    assistant = assistants_storage[request.assistant_id]
    run_id = _generate_run_id()
    created_at = int(time.time())

    # Determine model and instructions
    model = request.model or assistant.model
    instructions = request.instructions or assistant.instructions
    tools = request.tools if request.tools is not None else assistant.tools

    run = Run(
        id=run_id,
        created_at=created_at,
        thread_id=thread_id,
        assistant_id=request.assistant_id,
        status=RunStatus.QUEUED,
        model=model,
        instructions=instructions,
        tools=tools,
        metadata=request.metadata,
        temperature=request.temperature or assistant.temperature,
        top_p=request.top_p or assistant.top_p,
        max_prompt_tokens=request.max_prompt_tokens,
        max_completion_tokens=request.max_completion_tokens,
        truncation_strategy=request.truncation_strategy,
        tool_choice=request.tool_choice,
        parallel_tool_calls=request.parallel_tool_calls,
        response_format=request.response_format or assistant.response_format,
    )

    if thread_id not in runs_storage:
        runs_storage[thread_id] = {}

    runs_storage[thread_id][run_id] = run

    # Initialize run steps storage
    if thread_id not in run_steps_storage:
        run_steps_storage[thread_id] = {}
    if run_id not in run_steps_storage[thread_id]:
        run_steps_storage[thread_id][run_id] = []

    # Handle streaming
    if request.stream:
        async def generate_run_stream():
            # Send initial event
            yield f"event: thread.run.created\ndata: {run.model_dump_json()}\n\n"

            # Simulate status progression
            import asyncio

            # Update to in_progress
            await asyncio.sleep(0.1)
            run.status = RunStatus.IN_PROGRESS
            run.started_at = int(time.time())
            yield f"event: thread.run.in_progress\ndata: {run.model_dump_json()}\n\n"

            # Create a message step
            step_id = _generate_step_id()
            step = RunStep(
                id=step_id,
                created_at=int(time.time()),
                run_id=run_id,
                assistant_id=request.assistant_id,
                thread_id=thread_id,
                type="message_creation",
                status="in_progress",
                step_details={
                    "type": "message_creation",
                    "message_creation": {"message_id": _generate_message_id()},
                },
            )

            run_steps_storage[thread_id][run_id].append(step)

            yield f"event: thread.run.step.created\ndata: {step.model_dump_json()}\n\n"

            # Generate assistant message
            await asyncio.sleep(0.2)
            assistant_message = ThreadMessage(
                id=_generate_message_id(),
                created_at=int(time.time()),
                thread_id=thread_id,
                role="assistant",
                content=[
                    {
                        "type": "text",
                        "text": {
                            "value": "I'm an AI assistant. I can help you with various tasks."
                        },
                    }
                ],
                assistant_id=request.assistant_id,
                run_id=run_id,
            )
            messages_storage[thread_id].append(assistant_message)

            # Complete the step
            step.status = "completed"
            step.completed_at = int(time.time())
            yield f"event: thread.run.step.completed\ndata: {step.model_dump_json()}\n\n"

            # Complete the run
            await asyncio.sleep(0.1)
            run.status = RunStatus.COMPLETED
            run.completed_at = int(time.time())
            run.usage = Usage(
                prompt_tokens=50,
                completion_tokens=20,
                total_tokens=70,
            )
            yield f"event: thread.run.completed\ndata: {run.model_dump_json()}\n\n"
            yield f"data: [DONE]\n\n"

        return StreamingResponse(
            generate_run_stream(),
            media_type="text/event-stream",
        )

    # Non-streaming: simulate async processing
    import asyncio
    import uuid

    async def process_run():
        await asyncio.sleep(0.5)

        # Update status to in_progress
        run.status = RunStatus.IN_PROGRESS
        run.started_at = int(time.time())

        # Create a message step
        step_id = _generate_step_id()
        step = RunStep(
            id=step_id,
            created_at=int(time.time()),
            run_id=run_id,
            assistant_id=request.assistant_id,
            thread_id=thread_id,
            type="message_creation",
            status="in_progress",
            step_details={
                "type": "message_creation",
                "message_creation": {"message_id": _generate_message_id()},
            },
        )

        run_steps_storage[thread_id][run_id].append(step)

        # Check if any function tools are present
        has_function_tools = any(
            tool.get("type") == "function" for tool in tools
        )

        if has_function_tools and random.random() < 0.3:  # 30% chance to require action
            # Simulate requiring tool call
            tool_call_id = f"call_{uuid.uuid4().hex}"
            function_tool = next(
                (t for t in tools if t.get("type") == "function"), None
            )

            run.status = RunStatus.REQUIRES_ACTION
            run.required_action = {
                "type": "submit_tool_outputs",
                "submit_tool_outputs": {
                    "tool_calls": [
                        {
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": function_tool["function"]["name"],
                                "arguments": '{"location": "San Francisco"}',
                            },
                        }
                    ]
                },
            }
        else:
            # Generate assistant message
            await asyncio.sleep(0.3)
            assistant_message = ThreadMessage(
                id=_generate_message_id(),
                created_at=int(time.time()),
                thread_id=thread_id,
                role="assistant",
                content=[
                    {
                        "type": "text",
                        "text": {
                            "value": "I'm an AI assistant. I can help you with various tasks."
                        },
                    }
                ],
                assistant_id=request.assistant_id,
                run_id=run_id,
            )
            messages_storage[thread_id].append(assistant_message)

            # Complete the step
            step.status = "completed"
            step.completed_at = int(time.time())

            # Complete the run
            run.status = RunStatus.COMPLETED
            run.completed_at = int(time.time())
            run.usage = Usage(
                prompt_tokens=50,
                completion_tokens=20,
                total_tokens=70,
            )

    # Start background processing
    asyncio.create_task(process_run())

    return run


@app.get("/v1/threads/{thread_id}/runs", dependencies=[Depends(verify_api_key)])
async def list_runs(
    thread_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> RunList:
    """List runs in a thread."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    runs = list(runs_storage.get(thread_id, {}).values())

    # Sort by created_at
    runs = sorted(runs, key=lambda r: r.created_at, reverse=(order == "desc"))

    # Apply pagination
    if after:
        try:
            after_idx = next(i for i, r in enumerate(runs) if r.id == after)
            runs = runs[after_idx + 1:]
        except StopIteration:
            pass

    if before:
        try:
            before_idx = next(i for i, r in enumerate(runs) if r.id == before)
            runs = runs[:before_idx]
        except StopIteration:
            pass

    # Limit results
    has_more = len(runs) > limit
    runs = runs[:limit]

    return RunList(
        data=runs,
        first_id=runs[0].id if runs else None,
        last_id=runs[-1].id if runs else None,
        has_more=has_more,
    )


@app.get(
    "/v1/threads/{thread_id}/runs/{run_id}",
    dependencies=[Depends(verify_api_key)],
)
async def retrieve_run(thread_id: str, run_id: str) -> Run:
    """Retrieve a specific run."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    run = runs_storage.get(thread_id, {}).get(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return run


@app.post(
    "/v1/threads/{thread_id}/runs/{run_id}",
    dependencies=[Depends(verify_api_key)],
)
async def modify_run(thread_id: str, run_id: str, request: ModifyRunRequest) -> Run:
    """Modify a run (only metadata)."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    run = runs_storage.get(thread_id, {}).get(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if request.metadata is not None:
        run.metadata = request.metadata

    return run


@app.post(
    "/v1/threads/{thread_id}/runs/{run_id}/cancel",
    dependencies=[Depends(verify_api_key)],
)
async def cancel_run(thread_id: str, run_id: str) -> Run:
    """Cancel a run."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    run = runs_storage.get(thread_id, {}).get(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Update status to cancelling or cancelled
    if run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS]:
        run.status = RunStatus.CANCELLING
        run.cancelled_at = int(time.time())

        # Simulate quick cancellation
        import asyncio

        async def complete_cancellation():
            await asyncio.sleep(0.1)
            run.status = RunStatus.CANCELLED

        asyncio.create_task(complete_cancellation())

    return run


@app.post(
    "/v1/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
    dependencies=[Depends(verify_api_key)],
)
async def submit_tool_outputs(
    thread_id: str, run_id: str, request: dict
) -> Run:
    """Submit tool outputs for a run."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    run = runs_storage.get(thread_id, {}).get(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if run.status != RunStatus.REQUIRES_ACTION:
        raise HTTPException(
            status_code=400,
            detail=f"Run is in {run.status} status, not requires_action",
        )

    # Clear required action and continue processing
    run.required_action = None
    run.status = RunStatus.IN_PROGRESS

    # Simulate completing the run
    import asyncio

    async def complete_run():
        await asyncio.sleep(0.3)

        # Generate assistant message with tool results
        assistant_message = ThreadMessage(
            id=_generate_message_id(),
            created_at=int(time.time()),
            thread_id=thread_id,
            role="assistant",
            content=[
                {
                    "type": "text",
                    "text": {
                        "value": f"Based on the tool output, the result is: {request.get('tool_outputs', [{}])[0].get('output', 'unknown')}"
                    },
                }
            ],
            assistant_id=run.assistant_id,
            run_id=run_id,
        )
        messages_storage[thread_id].append(assistant_message)

        # Complete the run
        run.status = RunStatus.COMPLETED
        run.completed_at = int(time.time())
        run.usage = Usage(
            prompt_tokens=60,
            completion_tokens=25,
            total_tokens=85,
        )

    asyncio.create_task(complete_run())

    return run


# Run Steps endpoints
@app.get(
    "/v1/threads/{thread_id}/runs/{run_id}/steps",
    dependencies=[Depends(verify_api_key)],
)
async def list_run_steps(
    thread_id: str,
    run_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    order: str = Query(default="desc"),
    after: str | None = Query(default=None),
    before: str | None = Query(default=None),
) -> RunStepList:
    """List steps for a run."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    if run_id not in runs_storage.get(thread_id, {}):
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    steps = run_steps_storage.get(thread_id, {}).get(run_id, [])

    # Sort by created_at
    steps = sorted(steps, key=lambda s: s.created_at, reverse=(order == "desc"))

    # Apply pagination
    if after:
        try:
            after_idx = next(i for i, s in enumerate(steps) if s.id == after)
            steps = steps[after_idx + 1:]
        except StopIteration:
            pass

    if before:
        try:
            before_idx = next(i for i, s in enumerate(steps) if s.id == before)
            steps = steps[:before_idx]
        except StopIteration:
            pass

    # Limit results
    has_more = len(steps) > limit
    steps = steps[:limit]

    return RunStepList(
        data=steps,
        first_id=steps[0].id if steps else None,
        last_id=steps[-1].id if steps else None,
        has_more=has_more,
    )


@app.get(
    "/v1/threads/{thread_id}/runs/{run_id}/steps/{step_id}",
    dependencies=[Depends(verify_api_key)],
)
async def retrieve_run_step(thread_id: str, run_id: str, step_id: str) -> RunStep:
    """Retrieve a specific run step."""
    if thread_id not in threads_storage:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    if run_id not in runs_storage.get(thread_id, {}):
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    steps = run_steps_storage.get(thread_id, {}).get(run_id, [])
    step = next((s for s in steps if s.id == step_id), None)

    if not step:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")

    return step
