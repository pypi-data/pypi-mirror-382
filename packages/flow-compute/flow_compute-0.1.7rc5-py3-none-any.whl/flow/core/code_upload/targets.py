from __future__ import annotations

import posixpath as _pp
from dataclasses import dataclass
from pathlib import Path

"""Centralized logic for deciding upload destinations across CLI and provider.

This keeps 'where code lands' consistent between `flow submit` and `flow dev`.

Conventions:
- Run (containerized): upload flat into the working directory (default /workspace)
- Dev default env (host): nested by default at '~/<project>' unless flat is requested
- Dev named env (containerized): nested at '/envs/<env>/<project>' and appears at
  '/workspace/<project>' inside the container
"""


DEFAULT_WORKDIR = "/workspace"


@dataclass(frozen=True)
class UploadTargetPlan:
    """Planned upload destinations.

    remote_parent: where to create/upload on the VM
    remote_target: the concrete directory to pass to the transfer
    container_workdir: where the code will appear inside a container (if applicable)
    mode: 'flat' or 'nested'
    """

    remote_parent: str
    remote_target: str
    container_workdir: str | None
    mode: str


def plan_for_run(
    source_dir: Path | None = None,
    working_dir: str = DEFAULT_WORKDIR,
) -> UploadTargetPlan:
    """Plan upload target for flow submit.

    Always flat into the working directory so container '-w' and volume mount align.
    """
    wd = working_dir or DEFAULT_WORKDIR
    return UploadTargetPlan(remote_parent=wd, remote_target=wd, container_workdir=wd, mode="flat")


def plan_for_dev(
    source_dir: Path,
    env_name: str = "default",
    *,
    upload_mode: str = "nested",
    parent_override: str | None = None,
) -> UploadTargetPlan:
    """Plan upload target for flow dev.

    - default env (host): '~/<project>' when nested; '~' when flat
    - named env (containerized): '/envs/<env>/<project>' when nested; '/envs/<env>' when flat
      and appears at '/workspace' or '/workspace/<project>' inside the container
    """
    # Normalize inputs
    mode = "flat" if upload_mode == "flat" else "nested"
    project_name = (source_dir.name if isinstance(source_dir, Path) else "project") or "project"

    if env_name == "default":
        parent = parent_override or "~"
        target = _pp.join(parent, project_name) if mode == "nested" else parent
        return UploadTargetPlan(
            remote_parent=parent,
            remote_target=target,
            container_workdir=None,
            mode=mode,
        )

    # Named environment
    env_root = _pp.join("/envs", env_name)
    target = _pp.join(env_root, project_name) if mode == "nested" else env_root
    # In the container, env_root is bind-mounted at /workspace
    container_dir = _pp.join(DEFAULT_WORKDIR, project_name) if mode == "nested" else DEFAULT_WORKDIR
    return UploadTargetPlan(
        remote_parent=env_root,
        remote_target=target,
        container_workdir=container_dir,
        mode=mode,
    )


__all__ = ["DEFAULT_WORKDIR", "UploadTargetPlan", "plan_for_dev", "plan_for_run"]


def plan_for_upload_code(
    source_dir: Path | None = None,
    working_dir: str = DEFAULT_WORKDIR,
    *,
    nested: bool = True,
) -> UploadTargetPlan:
    """Plan upload target for manual `flow upload-code`.

    Prefer a nested target under the working directory (e.g., /workspace/<project>)
    for clarity and to mirror `flow dev` behavior. Callers may use this as the
    candidate and fall back to a user-writable home path (e.g., ~/<project>) when
    remote writability checks fail.
    """
    wd = working_dir or DEFAULT_WORKDIR
    project = (source_dir.name if isinstance(source_dir, Path) else None) or "project"
    if nested:
        target = _pp.join(wd, project)
    else:
        target = wd
    # Container view: when working_dir equals default, nested appears at /workspace/<project>
    if wd == DEFAULT_WORKDIR:
        container_dir = _pp.join(DEFAULT_WORKDIR, project) if nested else DEFAULT_WORKDIR
    else:
        container_dir = target
    return UploadTargetPlan(
        remote_parent=wd,
        remote_target=target,
        container_workdir=container_dir,
        mode=("nested" if nested else "flat"),
    )


__all__.append("plan_for_upload_code")
