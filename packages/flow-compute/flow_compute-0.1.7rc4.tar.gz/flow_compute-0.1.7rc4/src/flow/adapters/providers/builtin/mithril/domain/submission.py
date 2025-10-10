"""Submission orchestration service for Mithril.

Encapsulates the end-to-end submit flow (mount processing, env injection,
script preparation, SSH key resolution, bid submission with retry/circuit
breaker, and initial Task assembly) to keep the provider façade thin.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from httpx import HTTPStatusError as HTTPError

from flow.adapters.providers.builtin.mithril.core.constants import DEFAULT_REGION
from flow.cli.utils.origin import detect_origin
from flow.errors import (
    NetworkError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationAPIError,
)
from flow.sdk.models import Task, TaskConfig

logger = logging.getLogger(__name__)


class SubmissionService:
    """Coordinates submit flow using Mithril context collaborators.

    Post-refactor, this service depends on `MithrilContext` and accesses
    collaborators (bids, pricing, script prep, ssh keys, code upload, etc.)
    through the context, avoiding private provider attributes.
    """

    def __init__(self, ctx) -> None:  # ctx type: MithrilContext
        self._ctx = ctx

    # Keep signature aligned with IProvider.submit_task
    def submit(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Task:
        ctx = self._ctx

        # Reserved allocation flow
        try:
            allocation_mode = getattr(config, "allocation_mode", "spot")
        except Exception:  # noqa: BLE001
            allocation_mode = "spot"

        if allocation_mode == "reserved" or getattr(config, "reservation_id", None):
            # If a specific reservation_id is provided, use it directly
            if getattr(config, "reservation_id", None):
                r = ctx.reservations.get(config.reservation_id)  # type: ignore[arg-type]
                return ctx.task_service.build_task_from_reservation(r, config)

            # Otherwise, create a reservation from config hints (best-effort)
            try:
                num_nodes = getattr(config, "num_instances", 1) or 1
            except Exception:  # noqa: BLE001
                num_nodes = 1
            try:
                duration_hours = getattr(config, "max_run_time_hours", 1) or 1
            except Exception:  # noqa: BLE001
                duration_hours = 1
            try:
                region_hint = getattr(config, "region", None)
            except Exception:  # noqa: BLE001
                region_hint = None

            reservation = ctx.reservations.create(
                instance_type=instance_type,
                num_nodes=int(num_nodes),
                duration_hours=float(duration_hours),
                region=region_hint,
            )
            return ctx.task_service.build_task_from_reservation(reservation, config)

        # Override instance type for staging environment
        original_instance_type = instance_type
        try:
            # Extract base URL from the HTTP client to detect staging
            api_url = getattr(getattr(ctx.api, "_http", None), "base_url", None)
            if api_url and "staging.mithril.ai" in api_url:
                # In staging, always use the standard 8xH100 instance for all requests
                instance_type = "it_ccxjkIF3125aiv4h"
                logger.info(
                    f"Staging override: {original_instance_type} -> {instance_type} (8xH100)"
                )
        except Exception:  # noqa: BLE001
            # If we can't detect staging, continue with original instance type
            pass

        # Validate/resolve instance type
        try:
            # If this is already a staging internal ID (starts with "it_"), use it directly
            if instance_type and instance_type.startswith("it_"):
                logger.info(f"Using staging internal instance ID directly: {instance_type}")
                instance_fid = instance_type
            else:
                instance_fid = ctx.instance_types.resolve(instance_type)
        except Exception:
            # Re-raise with provider's helpful message
            raise

        # Provider constraints
        adjusted_config = self._apply_instance_constraints(config, instance_type)

        # Region and instance selection (prefer bids service)
        outcome = ctx.bids.select_region_and_instance_with_fallback(
            adjusted_config=adjusted_config,
            instance_type=instance_type,
            instance_fid=instance_fid,
            region_selector=ctx.region,
        )

        # TODO(oliviert): revisit when instance type resolver is refactored.
        # This error is sometimes inaccurate because the current instance type resolver
        # only considers H100s in us-central1-b
        # but availability exists in other regions like us-central2-a.
        # But this error is still useful because it raises an error when
        # a requested region is definitely not available
        # i.e. false negatives are better than false positives.
        if adjusted_config.region and outcome.region != adjusted_config.region:
            raise ResourceNotFoundError(
                f"No {instance_type} instances available in the requested region",
                suggestions=[
                    f"Available region(s) for {instance_type}: {', '.join(outcome.candidate_regions)}",
                ],
            )

        selected_region = outcome.region
        auction = outcome.auction
        instance_type_id = outcome.instance_type_id or ctx.instance_types.resolve(instance_type)

        if not selected_region:
            regions_checked = outcome.candidate_regions or ["all regions"]
            raise ResourceNotFoundError(
                f"No {instance_type} instances available",
                suggestions=[
                    f"Checked regions: {', '.join(regions_checked)}",
                    "Try a different instance type",
                    "Increase your max price limit",
                    "Check back later for availability",
                ],
            )

        auction_id = auction.fid if auction else None

        # Ensure config uses the selected region
        # Always override here because a pre-filled default/preferred region may be unavailable.
        # The selection flow already honors an explicit preferred region when available.
        adjusted_config = adjusted_config.model_copy(update={"region": selected_region})

        project_id = ctx.get_project_id()

        # Resolve/create volumes declared in config and accumulate IDs
        try:
            from flow.adapters.providers.builtin.mithril.domain.volume_prep import (
                VolumePreparationService as _VPS,
            )

            vps = _VPS(ctx)
            updated_specs, resolved_from_config = vps.resolve_and_ensure_volumes(
                adjusted_config, region=selected_region, project_id=project_id
            )
            if updated_specs != list(adjusted_config.volumes):
                adjusted_config = adjusted_config.model_copy(update={"volumes": updated_specs})
            if resolved_from_config:
                volume_ids = list(volume_ids) if volume_ids else []
                volume_ids.extend(resolved_from_config)
        except Exception:  # noqa: BLE001
            # Non-fatal: allow submit to proceed even if volume prep fails
            pass

        # Data mounts processing and env injection
        if adjusted_config.data_mounts:
            from flow.core.data.mount_processor import MountProcessor

            processor = MountProcessor()
            resolved_mounts = processor.process_mounts(adjusted_config, ctx)
            mount_volumes, mount_env = ctx.mount_adapter.adapt_mounts(resolved_mounts)

            volume_ids = list(volume_ids) if volume_ids else []
            volume_ids.extend([v.volume_id for v in mount_volumes if v.volume_id])

            if mount_env:
                adjusted_config = adjusted_config.model_copy(
                    update={"env": {**adjusted_config.env, **mount_env}}
                )

            # Best-effort: inject AWS credentials if needed for S3 mounts
            try:
                from flow.adapters.providers.builtin.mithril.domain.mounts import (
                    MountsService as _MountsService,
                )

                adjusted_config = _MountsService().inject_env_for_s3(adjusted_config)
            except Exception:  # noqa: BLE001
                pass

        # Default working_dir layout for code upload (nested-by-default for pre-release):
        # If upload_code is enabled and the user didn't explicitly override working_dir,
        # place code under /workspace/<project>. This keeps run semantics consistent with
        # dev-style nested layout while preserving explicit user overrides.
        try:
            if adjusted_config.upload_code:
                wd = (getattr(adjusted_config, "working_dir", None) or "").strip() or "/workspace"
                if wd == "/workspace":
                    try:
                        from pathlib import Path as _Path

                        code_root_val = getattr(adjusted_config, "code_root", None)
                        project = (
                            _Path(code_root_val).name if code_root_val else _Path.cwd().name
                        ) or "project"
                    except Exception:  # noqa: BLE001
                        project = "project"
                    adjusted_config = adjusted_config.model_copy(
                        update={"working_dir": f"/workspace/{project}"}
                    )
        except Exception:  # noqa: BLE001
            pass

        # Embedded code packaging (only when not using SCP and not explicitly 'none')
        # Only determine upload strategy if upload_code is enabled to avoid
        # accidentally scanning the entire filesystem and triggering macOS
        # privacy prompts.
        using_scp_upload = (
            ctx.code_upload.should_use_scp_upload(adjusted_config)
            if adjusted_config.upload_code
            else False
        )
        try:
            strategy = getattr(adjusted_config, "upload_strategy", None)
        except Exception:  # noqa: BLE001
            strategy = None
        if adjusted_config.upload_code and (not using_scp_upload):
            if strategy == "none":
                logger.info(
                    "Upload strategy 'none': skipping embedded packaging and background upload"
                )
            else:
                logger.info("Packaging local directory for upload...")
            adjusted_config = ctx.code_upload.package_local_code(adjusted_config)

        # Minimal runtime env for monitoring/telemetry
        # Inject credentials when either runtime monitoring or terminate_on_exit is enabled
        if adjusted_config.max_run_time_hours or bool(
            getattr(adjusted_config, "terminate_on_exit", False)
        ):
            runtime_env = {
                "MITHRIL_API_KEY": ctx.mithril_config.api_key,
                "MITHRIL_API_URL": ctx.http.base_url,
                "MITHRIL_PROJECT": project_id,
            }
            adjusted_config = adjusted_config.model_copy(
                update={"env": {**adjusted_config.env, **runtime_env}}
            )

        origin = detect_origin()
        flow_env = {
            "MITHRIL_API_KEY": ctx.mithril_config.api_key,
            "MITHRIL_API_URL": ctx.http.base_url,
            "MITHRIL_PROJECT": project_id,
            "FLOW_TASK_NAME": adjusted_config.name,
            # Origin hint for telemetry/scripts
            "FLOW_ORIGIN": origin,
        }
        adjusted_config = adjusted_config.model_copy(
            update={"env": {**adjusted_config.env, **flow_env}}
        )

        # Build and prepare startup script
        try:
            prep = ctx.script_prep.build_and_prepare(adjusted_config)
            startup_script = prep.content
            if prep.requires_network:
                logger.info(
                    "Startup script requires network access for download (using storage strategy)"
                )
        except Exception as e:
            from flow.adapters.providers.builtin.mithril.runtime.script_size import (
                ScriptTooLargeError,
            )
            from flow.errors import ValidationError

            if not isinstance(e, ScriptTooLargeError):
                raise

            size_kb = e.script_size / 1024
            limit_kb = e.max_size / 1024
            exceeds_limit = e.script_size > e.max_size

            # Use the handler behind the script prep service for suggestions
            try:
                suggestions = ctx.script_prep._size.get_failure_suggestions(  # type: ignore[attr-defined]
                    e.script_size, e.strategies_tried
                )
            except Exception:  # noqa: BLE001
                suggestions = []

            # Auto-fallback to SCP if embedding code caused the failure
            if adjusted_config.upload_code and not using_scp_upload:
                try:
                    logger.debug(
                        "Startup script size handling failed; retrying with upload_strategy='scp'"
                    )
                    fallback_env = dict(adjusted_config.env or {})
                    fallback_env.pop("_FLOW_CODE_ARCHIVE", None)
                    fallback_config = adjusted_config.model_copy(
                        update={"upload_strategy": "scp", "env": fallback_env}
                    )
                    fb_prep = ctx.script_prep.build_and_prepare(fallback_config)
                    startup_script = fb_prep.content
                    adjusted_config = fallback_config
                    using_scp_upload = True
                    if fb_prep.requires_network:
                        logger.info(
                            "Startup script requires network access for download (using storage strategy)"
                        )
                    suggestions = [s for s in suggestions if "upload_strategy='scp'" not in s]
                except ScriptTooLargeError:
                    pass

            if using_scp_upload:
                suggestions = [s for s in suggestions if "upload_strategy='scp'" not in s]
                suggestions.insert(
                    0,
                    (
                        "You're already using upload_strategy='scp'; reduce the startup script size "
                        "by trimming mounts, environment entries, or user startup commands."
                    ),
                )
            else:
                suggestions.insert(
                    0,
                    "Use upload_strategy='scp' to transfer code after the instance starts (no size limit)",
                )
                suggestions.insert(
                    1,
                    "Or disable code upload: upload_code=False when your image already has what you need",
                )

            if adjusted_config.upload_code and not using_scp_upload:
                if exceeds_limit:
                    error_msg = (
                        f"Startup script too large ({size_kb:.1f}KB > {limit_kb:.1f}KB limit). "
                        f"This often happens when upload_code=True includes too many files. "
                        f"Try upload_strategy='scp' or upload_code=False."
                    )
                else:
                    error_msg = (
                        "Startup script could not be prepared within size limits. "
                        "This often happens when upload_code=True includes too many files that don't compress well. "
                        "Try upload_strategy='scp' or upload_code=False."
                    )
            elif adjusted_config.upload_code and using_scp_upload:
                if exceeds_limit:
                    error_msg = (
                        f"Startup script too large ({size_kb:.1f}KB > {limit_kb:.1f}KB limit). "
                        f"Your code is uploaded via SCP, so this size comes from the startup script itself "
                        f"(mounts/env/commands), not embedded project files."
                    )
                else:
                    error_msg = (
                        "Startup script could not be prepared within size limits. "
                        "Your code is uploaded via SCP, so this size comes from the startup script itself "
                        "(mounts/env/commands), not embedded project files."
                    )
            else:
                if exceeds_limit:
                    error_msg = (
                        f"Startup script too large ({size_kb:.1f}KB > {limit_kb:.1f}KB limit). "
                        f"The script content exceeds Mithril's size restrictions."
                    )
                else:
                    error_msg = (
                        "Startup script could not be prepared within size limits. "
                        "The script content could not be handled by available strategies."
                    )

            raise ValidationError(error_msg, suggestions=suggestions[:5]) from e

        # Volume attachments (includes mount volumes)
        # Plan volume attachments
        try:
            from flow.adapters.providers.builtin.mithril.domain.attachments import (
                VolumeAttachmentPlanner as _VAP,
            )

            planner = _VAP(ctx)
            volume_attachments = planner.prepare_volume_attachments(
                volume_ids, adjusted_config, strict=False
            )
        except Exception:  # noqa: BLE001
            volume_attachments = self._prepare_volume_attachments(volume_ids, adjusted_config)

        # SSH keys (project-scoped)
        ssh_keys = ctx.ssh_keys_svc.resolve_keys_for_task(adjusted_config)

        # Ensure the submitted Task carries effective SSH key IDs in its attached config
        # so downstream UI can accurately report SSH/log availability.
        try:
            if ssh_keys:
                try:
                    # Prefer immutable update where supported by Pydantic v2
                    adjusted_config = adjusted_config.model_copy(
                        update={"ssh_keys": list(ssh_keys)}
                    )
                except Exception:  # noqa: BLE001
                    # Fallback to attribute assignment
                    adjusted_config.ssh_keys = list(ssh_keys)
        except Exception:  # noqa: BLE001
            # Non-fatal; submission proceeds even if config decoration fails
            pass

        # Region from config (set above), fallback to defaults defensively
        region = adjusted_config.region or ctx.mithril_config.region or DEFAULT_REGION

        # Bid submission via bids service with circuit breaker + retry
        def _submit_bid():
            return ctx.bids.submit_bid(
                config=adjusted_config,
                region=region,
                instance_type_id=instance_type_id,
                project_id=project_id,
                ssh_keys=ssh_keys,
                startup_script=startup_script,
                volume_attachments=volume_attachments,
                auction_id=auction_id,
            )

        try:
            retry_config = (
                adjusted_config.retries
                if hasattr(adjusted_config, "retries") and adjusted_config.retries
                else None
            )
            from flow.adapters.resilience.retry import (
                ExponentialBackoffPolicy,
                with_retry,
            )

            if retry_config:
                policy = ExponentialBackoffPolicy(
                    max_attempts=retry_config.max_retries,
                    initial_delay=retry_config.initial_delay,
                    max_delay=retry_config.max_delay,
                    exponential_base=retry_config.backoff_coefficient,
                )

                @with_retry(
                    policy=policy,
                    retryable_exceptions=(NetworkError, TimeoutError, HTTPError),
                )
                def _submit_with_retry():
                    return _submit_bid()

                response = _submit_with_retry()
            else:
                default_policy = ExponentialBackoffPolicy(max_attempts=3, initial_delay=1.0)

                @with_retry(
                    policy=default_policy,
                    retryable_exceptions=(NetworkError, TimeoutError, HTTPError),
                )
                def _submit_with_retry():
                    return _submit_bid()

                response = _submit_with_retry()
        except ValidationAPIError as e:
            if ctx.pricing.is_price_validation_error(e):
                instance_name = ctx.task_service.get_instance_type_name(instance_type_id)
                enhanced_error = ctx.pricing.enhance_price_error(
                    e,
                    instance_type_id=instance_type_id,
                    region=region,
                    attempted_price=getattr(config, "max_price_per_hour", None),
                    instance_display_name=instance_name,
                )
                raise enhanced_error from e
            else:
                raise

        # Extract bid id
        try:
            from flow.adapters.providers.builtin.mithril.domain.bids import BidsService

            bid_id = BidsService.extract_bid_id(response)
        except Exception as e:
            from flow.adapters.providers.builtin.mithril.core.errors import MithrilBidError

            raise MithrilBidError(
                f"Failed to create bid for task '{adjusted_config.name}': {e}"
            ) from e

        logger.info(
            f"Created bid {bid_id} for task '{adjusted_config.name}' "
            f"({'spot' if auction_id else 'on-demand'})"
        )

        # Build initial Task object
        initial_bid_data: dict[str, Any] = {
            "fid": bid_id,
            "task_name": adjusted_config.name,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "created_by": None,
            "instance_type": instance_type_id,
            "num_instances": adjusted_config.num_instances,
            "region": region,
            "price_per_hour": (
                f"${adjusted_config.max_price_per_hour:.2f}"
                if adjusted_config.max_price_per_hour
                else "$0"
            ),
            "instances": [],
        }

        # Populate created_by from identity API if available
        try:
            me_resp = ctx.api.get_me()
            me_data = me_resp.get("data", me_resp) if isinstance(me_resp, dict) else None
            if isinstance(me_data, dict):
                initial_bid_data["created_by"] = (
                    me_data.get("fid") or me_data.get("id") or me_data.get("user_id")
                )
        except Exception:  # noqa: BLE001
            pass

        task = ctx.task_service.build_task(initial_bid_data, config=adjusted_config)

        # CRITICAL: Invalidate HTTP cache so subsequent status queries see the new task
        # Without this, the cached /v2/spot/bids response (90s TTL) causes TaskNotFoundError
        try:
            ctx.http.invalidate_task_cache()
        except Exception:  # noqa: BLE001
            # Best-effort invalidation; proceed even if it fails
            pass

        # Attach provider reference so Task methods can call back
        try:
            task._provider = self.provider
        except Exception:  # noqa: BLE001
            pass
        try:
            task._upload_pending = False
            task._upload_failed = False
            task._upload_error = None
        except Exception:  # noqa: BLE001
            pass

        # SCP code upload (async) if selected
        if adjusted_config.upload_code and ctx.code_upload.should_use_scp_upload(adjusted_config):
            logger.info("Task submitted. Code will be uploaded after instance starts.")
            try:
                task._upload_pending = True  # type: ignore[attr-defined]
                task._upload_config = adjusted_config  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                pass
            try:
                ctx.code_upload.initiate_async_upload(task, adjusted_config)
                try:
                    task._upload_pending = True  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001
                    pass
            except Exception as e:  # noqa: BLE001
                logger.debug(
                    f"Failed to initiate SCP upload: {e}. Code upload may need to be done manually."
                )

        return task

    # ---- Helpers moved from provider/facets to decouple from private access ----
    def _apply_instance_constraints(self, config: TaskConfig, instance_type: str) -> TaskConfig:
        """Apply provider-specific constraints based on instance type.

        Mirrors SelectionFacet.apply_instance_constraints without requiring the facet.
        """
        adjusted = config.model_copy()

        try:
            it_lower = (instance_type or "").lower()
        except Exception:  # noqa: BLE001
            it_lower = ""

        # High-end GPU constraints
        try:
            if any(gpu in it_lower for gpu in ["a100", "h100", "a6000"]):
                if not adjusted.memory:
                    adjusted.memory = "32Gi"
                if not adjusted.disk:
                    adjusted.disk = "100Gi"
        except Exception:  # noqa: BLE001
            pass

        # Multi-GPU constraints
        try:
            if "8x" in instance_type:
                if not adjusted.cpu:
                    adjusted.cpu = "32"
                if not adjusted.memory:
                    adjusted.memory = "64Gi"
            elif "4x" in instance_type:
                if not adjusted.cpu:
                    adjusted.cpu = "16"
                if not adjusted.memory:
                    adjusted.memory = "32Gi"
        except Exception:  # noqa: BLE001
            pass

        # Ensure resource formats
        try:
            if adjusted.memory and not any(
                str(adjusted.memory).endswith(s) for s in ["Mi", "Gi", "Ti"]
            ):
                adjusted.memory = f"{adjusted.memory}Gi"
        except Exception:  # noqa: BLE001
            pass
        try:
            if adjusted.disk and not any(
                str(adjusted.disk).endswith(s) for s in ["Mi", "Gi", "Ti"]
            ):
                adjusted.disk = f"{adjusted.disk}Gi"
        except Exception:  # noqa: BLE001
            pass

        return adjusted

    def _prepare_volume_attachments(
        self, volume_ids: list[str] | None, config: TaskConfig
    ) -> list[dict[str, Any]]:
        """Resolve volume identifiers and build attachment specs.

        Reimplements provider StorageFacet.prepare_volume_attachments using context services.
        """
        if not volume_ids:
            return []

        # Resolve volume names to IDs
        resolved: list[str] = []
        try:
            all_vols = self._ctx.volumes.list_volumes(
                project_id=self._ctx.get_project_id(), region=None, limit=1000
            )
        except Exception:  # noqa: BLE001
            all_vols = []

        def _is_volume_id(identifier: str) -> bool:
            return str(identifier).startswith("vol_")

        for ident in volume_ids:
            if _is_volume_id(ident):
                resolved.append(ident)
                continue
            # Exact name match
            matches = [v for v in all_vols if getattr(v, "name", None) == ident]
            if len(matches) == 1:
                resolved.append(matches[0].id)
                continue
            # Partial match
            partial = [
                v for v in all_vols if getattr(v, "name", "").lower().find(ident.lower()) != -1
            ]
            if len(partial) == 1:
                resolved.append(partial[0].id)
                continue
            # If unresolved, skip silently to avoid hard failure during submit

        # Build attachment specifications
        from flow.adapters.providers.builtin.mithril.bidding.builder import BidBuilder

        attachments: list[dict[str, Any]] = []

        for i, vid in enumerate(resolved):
            # Determine mount path
            if i < len(getattr(config, "volumes", []) or []) and hasattr(
                config.volumes[i], "mount_path"
            ):
                mount_path = config.volumes[i].mount_path
            else:
                from flow.utils.paths import default_volume_mount_path

                name = None
                try:
                    name = (
                        getattr(config.volumes[i], "name", None)
                        if i < len(config.volumes)
                        else None
                    )
                except Exception:  # noqa: BLE001
                    name = None
                mount_path = default_volume_mount_path(name=name, volume_id=vid)

            attachments.append(
                BidBuilder.format_volume_attachment(
                    volume_id=vid,
                    mount_path=mount_path,
                    mode="rw",
                )
            )

        return attachments
