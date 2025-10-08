from __future__ import annotations

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Dict, List, Optional
import uvicorn
import time


# ---------- OpenAPI Models ----------
class Command(str, Enum):
    """
    Accepted commands as implemented by ManagerSnort.rule_translator
    (see manager_snort.py -> tranlator_book)
    """

    block_ip = "block_ip"
    block_domain = "block_domain"
    alert_ip = "alert_ip"
    alert_domain = "alert_domain"
    block_icmp = "block_icmp"
    custom = "custom"


class UploadPayload(BaseModel):
    """
    Payload schema for /upload. The accepted commands mirror ManagerSnort.rule_translator.
    - For IP-based commands (*_ip / *_icmp) use an IPv4/IPv6 address in `target`.
    - For domain-based commands (*_domain) use a domain name in `target`.
    - For 'custom', `target` must be a full Snort rule string that will be appended as-is.
    """

    command: Command = Field(
        ..., description="The high-level action to translate into a Snort rule."
    )
    target: str = Field(
        ..., description="IP, domain, or full Snort rule (when command='custom')."
    )
    msg: Optional[str] = Field(
        None, description="Optional message to embed into the generated rule."
    )
    file: Optional[str] = Field(
        None,
        description="Optional reference label stored with history (not used for translation).",
    )


class UploadResponse(BaseModel):
    message: str = Field(..., description="Confirmation message.")
    rule: str = Field(..., description="The Snort rule derived from the payload.")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error details.")


class LatestHistory(BaseModel):
    # Kept loose because history structure is controlled by external manager_files code.
    # This preserves useful docs without over-constraining schema.
    any: Optional[Dict[str, Any]] | Optional[List[Any]] = Field(
        None, description="Latest history entry or None."
    )


class NotificationsResponse(BaseModel):
    message: str = Field(..., description="Status message.")
    latest: Optional[Any] = Field(
        None, description="Most recent history record, if any."
    )
    timestamp: float = Field(..., description="Unix epoch seconds at response time.")
    notifications: List[Any] = Field(
        default_factory=list, description="Older history records (may be empty)."
    )


class ShowRulesResponse(BaseModel):
    """Response model for the `/show_rules` endpoint.

    Always returns a list of rule strings under the `rules` key for 200 responses.
    """

    rules: List[str] = Field(..., description="List of rules from the rules file.")


class ClearRulesResponse(BaseModel):
    """Response model for the `/clear_rules` endpoint."""

    message: str = Field(..., description="Status message.")
    result: Optional[Any] = Field(None, description="Optional backend result/value.")


# ---------- API Class ----------
class ManagerAPI:
    """
    API surface for the Snort rule manager.

    Notes
    -----
    - The /upload route triggers the pipeline:
      rule_translator -> rule_exists (duplicate check) -> append_rule -> save_history
    - The concrete implementations live on this same instance (mixed-in via ManagerSnort/ManagerFiles).
    """

    # Default host/port may be provided by a parent mixin in the user's project.
    host: str = "0.0.0.0"
    port: int = 8000

    def __init__(self, *args, **kwargs):
        # Initialize app with richer OpenAPI/Swagger metadata
        self.port = kwargs.get("port", getattr(self, "port", 8000))
        self.host = kwargs.get("host", getattr(self, "host", "0.0.0.0"))

        tags = [
            {"name": "Rules", "description": "Create and manage Snort rules."},
            {
                "name": "Notifications",
                "description": "Retrieve processing history and notifications.",
            },
        ]

        self.app = FastAPI(
            title="Snort Manager API",
            description=(
                "HTTP interface for translating high‑level security actions into Snort 3 rules "
                "and appending the result to a rules file.\n\n"
                "This API is designed to be composed with `ManagerSnort` (for rule building) "
                "and a file/history mixin that provides `get_file_content`, `append_rule`, "
                "`save_history`, `file_backup`, and `rules_file`.\n"
            ),
            version="1.0.0",
            openapi_tags=tags,
            contact={
                "name": "Snort Manager",
                "url": "https://github.com/ISSG-UPAT/FileAgent-SAND5G/",
            },
        )
        self.setup_routes()
        super().__init__(*args, **kwargs)

    def setup_routes(self) -> None:
        """Register routes on the FastAPI app."""

        @self.app.post(
            "/upload",
            response_model=UploadResponse,
            responses={
                400: {
                    "model": ErrorResponse,
                    "description": "Invalid or empty JSON payload / translation failed.",
                },
                409: {
                    "model": ErrorResponse,
                    "description": "Duplicate rule — already present in rules file.",
                },
                500: {
                    "model": ErrorResponse,
                    "description": "Internal error while persisting the rule.",
                },
            },
            tags=["Rules"],
            summary="Translate payload to a Snort rule and persist",
            description=(
                "Accepts a JSON payload and translates it into a Snort rule via `rule_translator`.\n\n"
                "Accepted commands (from ManagerSnort): `block_ip`, `block_domain`, `alert_ip`, "
                "`alert_domain`, `block_icmp`, `custom`.\n"
                "- For `custom`, provide the full Snort rule in `target`.\n"
            ),
        )
        async def upload_json(
            payload: UploadPayload = Body(
                ...,
                openapi_extra={
                    "examples": {
                        "alert_ip": {
                            "summary": "Alert on IP",
                            "value": {
                                "file": "example",
                                "command": "alert_ip",
                                "target": "10.1.39.20",
                                "msg": "Incoming IP alert",
                            },
                        },
                        "block_ip": {
                            "summary": "Block an IP",
                            "value": {
                                "file": "example",
                                "command": "block_ip",
                                "target": "10.1.39.20",
                            },
                        },
                        "block_domain": {
                            "summary": "Block a domain (SNI)",
                            "value": {
                                "file": "Block Domain",
                                "command": "block_domain",
                                "target": "forbidden.site",
                            },
                        },
                        "block_icmp": {
                            "summary": "Block ICMP from IP",
                            "value": {
                                "file": "ICMP",
                                "command": "block_icmp",
                                "target": "10.45.0.3",
                            },
                        },
                        "custom_rule": {
                            "summary": "Provide a full custom rule",
                            "value": {
                                "file": "custom",
                                "command": "custom",
                                "target": 'alert ip 192.0.2.1 any -> any any (msg:"Custom"; sid:19999; rev:1;)',
                            },
                        },
                    }
                },
            ),
        ) -> UploadResponse:
            if not payload:
                raise HTTPException(status_code=400, detail="Empty JSON payload")

            # Attempt translation if available
            rule: Optional[str] = None
            try:
                if hasattr(self, "rule_translator"):
                    # ManagerSnort.rule_translator expects a dict
                    rule = self.rule_translator(payload.model_dump())
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Translation error: {exc}")

            if not rule:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Translation failed or returned no rule. Ensure payload matches "
                        "the expected schema (command + target, or 'custom' with full rule)."
                    ),
                )

            # Duplicate check
            try:
                if hasattr(self, "rule_exists") and self.rule_exists(rule):
                    raise HTTPException(status_code=409, detail="Duplicate rule")
            except HTTPException:
                raise
            except Exception:
                # If duplicate check fails for any reason, continue cautiously
                pass

            # Append and save
            try:
                if hasattr(self, "append_rule"):
                    # Existing implementation expects the original payload dict
                    self.append_rule(payload.model_dump())
                if hasattr(self, "save_history"):
                    self.save_history(payload.model_dump())
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail=f"Failed to persist rule: {exc}"
                )

            return UploadResponse(
                message="JSON payload received and processed", rule=rule
            )

        @self.app.get(
            "/notifications",
            response_model=NotificationsResponse,
            tags=["Notifications"],
            summary="Retrieve processing notifications/history",
            description=(
                "Returns the stored history/notifications. This endpoint relies on a mixin that provides:\n"
                "- `get_file_content(history_file, 'json')` to read history\n"
                "- `history_file` attribute pointing to the history store\n"
            ),
        )
        async def notifications() -> NotificationsResponse:
            # function from manager_files.py (not part of this file)
            if not hasattr(self, "get_file_content") or not hasattr(
                self, "history_file"
            ):
                raise HTTPException(
                    status_code=500,
                    detail="History backend not configured on this instance.",
                )

            notifications = self.get_file_content(self.history_file, "json")
            if notifications is None:
                raise HTTPException(status_code=404, detail="No notifications found")

            history = notifications.get("history")

            return NotificationsResponse(
                message="notifications is ready",
                latest=(history[-1] if history else None),
                timestamp=time.time(),
                notifications=(history[1:] if history and len(history) > 1 else []),
            )

        @self.app.get(
            "/show_rules",
            response_model=ShowRulesResponse,
            responses={
                404: {"model": ErrorResponse, "description": "No rules found."},
                500: {"model": ErrorResponse, "description": "Failed to read rules."},
            },
            tags=["Rules"],
            summary="Return the current Snort rules file contents",
            description=(
                "Returns the contents of the configured rules file. This endpoint relies on a mixin that provides:\n"
                "- `get_file_content(path, [fmt])` to read the file\n"
                "- `rules_file` attribute pointing to the rules file path."
            ),
        )
        async def show_rules():
            # Ensure the hosting instance exposes the required API
            if not hasattr(self, "rules_file"):
                raise HTTPException(
                    status_code=500,
                    detail="Rules backend not configured on this instance.",
                )

            # Prefer a generic file reader if provided, otherwise fall back to
            # instance-specific helpers (e.g. show_snort_rules()).
            reader = getattr(self, "show_snort_rules", None) or getattr(
                self, "show_snort_rules", None
            )
            if reader is None:
                raise HTTPException(
                    status_code=500,
                    detail="No method available to read rules on this instance.",
                )

            try:
                # If reader is get_file_content it typically expects (path, [fmt])
                if getattr(self, "get_file_content", None) is reader:
                    raw = reader(self.rules_file)
                else:
                    raw = reader()
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail=f"Failed to read rules: {exc}"
                )

            if raw is None:
                raise HTTPException(status_code=404, detail="No rules found")

            # Normalize to List[str]
            def _normalize(r):
                if isinstance(r, list):
                    return [str(x).strip() for x in r if str(x).strip()]
                if isinstance(r, str):
                    return [
                        line for line in (ln.strip() for ln in r.splitlines()) if line
                    ]
                if isinstance(r, dict):
                    # Some backends might return {'rules': [...]}
                    if "rules" in r:
                        return _normalize(r["rules"])
                    # Otherwise flatten stringified values
                    vals = []
                    for v in r.values():
                        vals.extend(_normalize(v) if v is not None else [])
                    return vals
                # Fallback: stringify
                return [str(r).strip()]

            rules_list = _normalize(raw)

            if not rules_list:
                raise HTTPException(status_code=404, detail="No rules found")

            return JSONResponse(content={"rules": rules_list})

        @self.app.post(
            "/clear_rules",
            response_model=ClearRulesResponse,
            responses={
                500: {"model": ErrorResponse, "description": "Failed to clear rules."}
            },
            tags=["Rules"],
            summary="Clear the current Snort rules",
            description=(
                "Clears the configured rules file by invoking `clear_rules()` on the hosting instance. "
            ),
        )
        async def clear_rules():
            if not hasattr(self, "clear_snort_rules") or not hasattr(
                self, "rules_file"
            ):
                raise HTTPException(
                    status_code=500,
                    detail="Rules backend not configured on this instance.",
                )

            try:
                result = self.clear_snort_rules()
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail=f"Failed to clear rules: {exc}"
                )

            return JSONResponse(content={"message": "rules cleared", "result": result})

    def run_uvicorn(self) -> None:
        """Start uvicorn with current host/port."""
        uvicorn.run(self.app, host=self.host, port=self.port)


# If someone needs a quick local run for testing:
if __name__ == "__main__":
    api = ManagerAPI()
    api.run_uvicorn()
