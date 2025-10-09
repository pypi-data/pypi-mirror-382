"""Shared volume operations for the Mithril provider.

Contains shell snippets used by both startup-time mounting and runtime
mount operations. Handles device discovery, formatting when needed, mounting,
ownership, and persistence. APIs are explicit per mount type to avoid
boolean switches and reduce ambiguity.
"""

from __future__ import annotations

import os
import shlex
import textwrap


class VolumeOperations:
    """Encapsulates volume mount operations for Mithril instances."""

    @staticmethod
    def generate_mount_script(
        volume_index: int,
        mount_path: str,
        volume_id: str | None = None,
        format_if_needed: bool = True,
        add_to_fstab: bool = True,
        is_file_share: bool = False,
    ) -> str:
        """Backward-compatible wrapper. (Deprecated)

        Deprecated: Use `generate_block_mount_script` or
        `generate_file_share_mount_script` instead. This wrapper remains for
        compatibility and will be removed in a future minor release.
        """
        if is_file_share:
            return VolumeOperations.generate_file_share_mount_script(
                volume_index=volume_index,
                mount_path=mount_path,
                volume_id=volume_id,
                add_to_fstab=add_to_fstab,
            )
        else:
            return VolumeOperations.generate_block_mount_script(
                volume_index=volume_index,
                mount_path=mount_path,
                volume_id=volume_id,
                format_if_needed=format_if_needed,
                add_to_fstab=add_to_fstab,
            )

    @staticmethod
    def generate_block_mount_script(
        *,
        volume_index: int,
        mount_path: str,
        volume_id: str | None = None,
        format_if_needed: bool = True,
        add_to_fstab: bool = True,
    ) -> str:
        """Generate mount script for block storage devices.

        Args:
            volume_index: 0-based index used for device letter heuristics.
            mount_path: Absolute mount path inside the instance.
            volume_id: Optional provider volume ID (improves NVMe by-id resolution).
            format_if_needed: If True, format the device when no FS detected.
            add_to_fstab: If True, persist mount via /etc/fstab.
        """
        return VolumeOperations._generate_block_mount(
            volume_index,
            mount_path,
            format_if_needed,
            add_to_fstab,
            volume_id=volume_id,
        )

    @staticmethod
    def generate_file_share_mount_script(
        *,
        volume_index: int,
        mount_path: str,
        volume_id: str | None = None,
        volume_name: str | None = None,
        add_to_fstab: bool = True,
    ) -> str:
        """Generate mount script for file share volumes.

        Uses virtiofs bind-mount when safely detectable; falls back to NFS.

        Args:
            volume_index: Used to derive NFS fallback endpoint when ID absent.
            mount_path: Absolute mount path inside the instance.
            volume_id: Optional provider volume ID.
            add_to_fstab: If True, persist mount via /etc/fstab.
        """
        return VolumeOperations._generate_file_share_mount(
            volume_index,
            mount_path,
            volume_id,
            volume_name=volume_name,
            add_to_fstab=add_to_fstab,
        )

    @staticmethod
    def _generate_block_mount(
        volume_index: int,
        mount_path: str,
        format_if_needed: bool,
        add_to_fstab: bool,
        volume_id: str | None = None,
    ) -> str:
        """Generate mount script for block storage."""
        # Bounds check: device letters d..z (0..22) supported
        if volume_index > 25 - 3:
            raise ValueError(
                f"Volume index {volume_index} exceeds maximum supported device letter (z)"
            )
        device_letter = chr(100 + volume_index)  # d, e, f, ...
        timeout_seconds = int(os.environ.get("FLOW_VOLUME_DEVICE_TIMEOUT_SECONDS", "60"))

        # Core device detection and mount logic (supports vd/xvd and NVMe by-id)
        vol_id_line = f"VOL_ID={shlex.quote(volume_id)}" if volume_id else 'VOL_ID=""'
        device_detection = textwrap.dedent(
            f"""
            # Detect device name. Prefer traditional /dev/vd*/xvd*; also handle NVMe by-id on Nitro.
            DEVICE=""
            {vol_id_line}

            try_lsblk_unmounted() {{
                # Pick first unmounted block device (disk/part). Conservative fallback.
                cand=$(lsblk -rplno NAME,TYPE,MOUNTPOINT 2>/dev/null | awk '($2=="disk"||$2=="part") && $3=="" {{print $1}}' | head -n1)
                if [ -n "$cand" ] && [ -b "$cand" ]; then
                    DEVICE="$cand"
                fi
            }}

            try_dev_letters() {{
                for device in /dev/vd{device_letter} /dev/xvd{device_letter}; do
                    if [ -b "$device" ]; then
                        DEVICE="$device"
                        break
                    fi
                done
            }}

            try_nvme_by_id() {{
                # If volume ID is known, prefer exact by-id symlink
                if [ -n "$VOL_ID" ]; then
                    for link in \
                        "/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_${{VOL_ID}}" \
                        "/dev/disk/by-id/scsi-0Amazon_Elastic_Block_Store_${{VOL_ID}}"; do
                        if [ -e "$link" ]; then
                            realdev=$(readlink -f "$link" || true)
                            if [ -b "$realdev" ]; then
                                DEVICE="$realdev"
                                return
                            fi
                        fi
                    done
                fi
                # Otherwise, choose the first unused NVMe EBS device by-id
                for link in /dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_*; do
                    [ -e "$link" ] || continue
                    realdev=$(readlink -f "$link" || true)
                    # Skip if already mounted (device or its partitions)
                    if [ -b "$realdev" ] && ! lsblk -no MOUNTPOINT "$realdev" "$realdev"* 2>/dev/null | grep -q .; then
                        DEVICE="$realdev"
                        return
                    fi
                done
            }}

            try_dev_letters
            [ -n "$DEVICE" ] || try_nvme_by_id
            [ -n "$DEVICE" ] || try_lsblk_unmounted

            # Wait for device if not immediately available
            if [ -z "$DEVICE" ]; then
                echo "Waiting for volume device to appear..."
                TIMEOUT={timeout_seconds}
                ELAPSED=0
                while [ -z "$DEVICE" ] && [ $ELAPSED -lt $TIMEOUT ]; do
                    try_dev_letters
                    [ -n "$DEVICE" ] || try_nvme_by_id
                    [ -n "$DEVICE" ] || try_lsblk_unmounted
                    if [ -z "$DEVICE" ]; then
                        sleep 5
                        ELAPSED=$((ELAPSED + 5))
                        echo "  Waiting... ($ELAPSED/$TIMEOUT seconds)"
                    fi
                done
            fi

            if [ -z "$DEVICE" ]; then
                echo "ERROR: Volume device not found after $TIMEOUT seconds"
                echo "  Tried: /dev/vd{device_letter}, /dev/xvd{device_letter}, NVMe by-id (EBS), lsblk fallback"
                # Allow non-fatal mount behavior when explicitly requested via env.
                # When FLOW_MOUNT_REQUIRED=0, skip mounting this volume but continue startup.
                # Note: use double braces to avoid Python f-string interpolation.
                if [ "${{FLOW_MOUNT_REQUIRED:-1}}" = "0" ]; then
                    echo "Skipping mount (non-fatal) for: {mount_path}"
                else
                    exit 1
                fi
            else
                echo "Found volume device: $DEVICE"
            fi
        """
        ).strip()

        # Safe destination path used throughout
        _safe_mount = shlex.quote(str(mount_path))

        # Formatting logic (conditional)
        format_logic = ""
        if format_if_needed:
            format_logic = textwrap.dedent(
                """
                # Check if volume needs formatting (only when device is detected)
                if [ -n "$DEVICE" ]; then
                    if ! blkid "$DEVICE" >/dev/null 2>&1; then
                        echo "Formatting new volume $DEVICE..."
                        FS_TYPE="${FLOW_FS_TYPE:-ext4}"
                        if [ "$FS_TYPE" = "xfs" ]; then
                            mkfs.xfs -f "$DEVICE"
                        else
                            # Default to ext4
                            mkfs.ext4 -F "$DEVICE"
                        fi
                    else
                        echo "Volume $DEVICE already formatted"
                    fi
                fi
            """
            ).strip()

        # fstab logic (conditional)
        fstab_logic = ""
        if add_to_fstab:
            # Note: fstab does not support quoted fields; we assume sanitized mount paths without whitespace
            fstab_logic = textwrap.dedent(
                f"""
                # Add to fstab for persistence (only when device is detected)
                if [ -n \"$DEVICE\" ]; then
                    FS_TYPE=\"${{FLOW_FS_TYPE:-ext4}}\"
                    UUID=$(blkid -s UUID -o value \"$DEVICE\" 2>/dev/null || true)
                    if [ -n \"$UUID\" ]; then
                        if ! grep -q \"UUID=$UUID\" /etc/fstab; then
                            echo \"UUID=$UUID {mount_path} $FS_TYPE defaults,nofail,x-systemd.device-timeout=10 0 2\" >> /etc/fstab
                            echo \"Added UUID entry to /etc/fstab (UUID=$UUID)\"
                        fi
                    else
                        if ! grep -q \"$DEVICE\" /etc/fstab; then
                            echo \"$DEVICE {mount_path} $FS_TYPE defaults,nofail,x-systemd.device-timeout=10 0 2\" >> /etc/fstab
                            echo \"Added $DEVICE to /etc/fstab\"
                        fi
                    fi
                fi
            """
            ).strip()

        # Combine all parts
        script_parts = [
            f"# Mount volume to {_safe_mount}",
            f"echo 'Mounting: {_safe_mount}'",
            "",
            # Ensure the mount path exists even if the device is not yet available.
            # This makes downstream writes (e.g., container commands) non-fatal when
            # FLOW_MOUNT_REQUIRED=0 and the device never appears within the timeout.
            f"mkdir -p {_safe_mount} || true",
            "",
            device_detection,
            "",
        ]

        if format_logic:
            script_parts.extend([format_logic, ""])

        # Only attempt to mount when a device was found; otherwise, in non-fatal mode we skip.
        # Idempotency: skip mount when already mounted.
        script_parts.extend(
            [
                "# Create mount point and mount volume (when device is available)",
                'if [ -n "$DEVICE" ]; then ',
                f"  if mountpoint -q {_safe_mount}; then echo 'Already mounted at {_safe_mount}'; ",
                f'  else mkdir -p {_safe_mount} && mount "$DEVICE" {_safe_mount} && chmod 755 {_safe_mount}; fi; ',
                "fi",
                "",
            ]
        )

        # Ownership handling (best-effort, opinionated defaults)
        owner_logic = textwrap.dedent(
            f"""
            # Resolve mount owner preference
            OWNER="${{FLOW_MOUNT_OWNER:-${{FLOW_SSH_USER:-}}}}"
            if [ -z "$OWNER" ]; then
              for cand in ubuntu ec2-user rocky centos; do
                if id "$cand" >/dev/null 2>&1; then OWNER="$cand"; break; fi
              done
            fi
            if [ -z "$OWNER" ]; then OWNER="${{SUDO_USER:-$USER}}"; fi

            # Apply ownership to mount path
            if [ -n "$DEVICE" ] && mountpoint -q {_safe_mount}; then
              chown -R "$OWNER:$OWNER" {_safe_mount} || true
            fi
            """
        ).strip()
        script_parts.extend([owner_logic, ""])

        if fstab_logic:
            script_parts.extend([fstab_logic, ""])

        script_parts.extend(
            [
                "# Verify mount (only when device detected)",
                'if [ -n "$DEVICE" ]; then',
                f"  if mountpoint -q {_safe_mount}; then",
                f"    echo 'Mounted: {_safe_mount}'",
                f"    df -h {_safe_mount}",
                "  else",
                f"    echo 'ERROR: mount {_safe_mount}'",
                '    if [ "${FLOW_MOUNT_REQUIRED:-1}" = "1" ]; then exit 1; else echo \'Continuing without mount (non-fatal)\'; fi',
                "  fi",
                "fi",
            ]
        )

        return "\n".join(script_parts)

    @staticmethod
    def _generate_file_share_mount(
        volume_index: int,
        mount_path: str,
        volume_id: str | None,
        *,
        volume_name: str | None = None,
        add_to_fstab: bool = True,
    ) -> str:
        """Generate mount script for file shares.

        Strategy:
        - If target already mounted, no-op.
        - If exactly one virtiofs mount exists under /mnt, bind-mount it to target.
        - Else, fallback to NFS v4.1 endpoint.
        - Persist via fstab and apply ownership.
        """
        # Prefer mithril.internal, but tests also check for specific FQDNs
        nfs_endpoint = (
            f"fileshare-{volume_id}.mithril.internal"
            if volume_id
            else f"fileshare-{volume_index}.mithril.internal"
        )

        _safe_mount = shlex.quote(str(mount_path))
        script = """
            # Mount file share to %%MOUNT%%
            echo 'Mounting: %%MOUNT%%'

            # Install NFS client if needed
            if ! command -v mount.nfs >/dev/null; then
                echo "Installing NFS client..."
                export DEBIAN_FRONTEND=noninteractive
                install_pkgs nfs-common || install_pkgs nfs-utils || true
            fi

            # Create mount point
            mkdir -p %%MOUNT%%

            # Idempotency: skip if already mounted
            if mountpoint -q %%MOUNT%%; then
                echo 'Already mounted at %%MOUNT%%'
            else
                # Prefer virtiofs under /mnt; if name known, prefer /mnt/<name>, otherwise use single candidate only
                VIRT_SRC=""
                if [ -d "/mnt" ]; then
                    if [ -n "%%VNAME%%" ]; then
                        if mount -t virtiofs 2>/dev/null | awk '{{print $3}}' | grep -qx "/mnt/%%VNAME%%"; then
                            VIRT_SRC="/mnt/%%VNAME%%"
                        fi
                    fi
                    if [ -z "$VIRT_SRC" ]; then
                        VIRT_SRC=$(mount -t virtiofs 2>/dev/null | awk '{{print $3}}' | grep -E "^/mnt/" | sed -n '1{p;}' )
                        VIRT_COUNT=$(mount -t virtiofs 2>/dev/null | awk '{{print $3}}' | grep -E "^/mnt/" | wc -l | tr -d ' ')
                        if [ "$VIRT_COUNT" != "1" ]; then
                            VIRT_SRC=""
                        fi
                    fi
                fi
                if [ -n "$VIRT_SRC" ]; then
                    echo "Using virtiofs bind source: $VIRT_SRC"
                    if ! mountpoint -q %%MOUNT%%; then
                        mount --bind "$VIRT_SRC" %%MOUNT%%
                    fi
                else
                    # Fallback to NFS with optimized options
                    mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \\
                        "%%NFS%%:/" %%MOUNT%%
                fi
            fi

            # Add to fstab for persistence
            if mountpoint -q %%MOUNT%%; then
                # Determine source for persistence: bind vs nfs
                if mount | grep -E "^.* on %%MOUNT%% type virtiofs" >/dev/null 2>&1; then
                    SRC=$(mount | grep -E " type virtiofs " | awk '{{print $3}}' | grep -E "^/mnt/" | sed -n '1{p;}' )
                    if [ -n "$SRC" ]; then
                        if ! grep -q " $SRC %%MOUNT%% none bind " /etc/fstab; then
                            echo "$SRC %%MOUNT%% none bind 0 0" >> /etc/fstab
                        fi
                    fi
                else
                    if ! grep -q "%%NFS%%" /etc/fstab; then
                        echo "%%NFS%%:/ %%MOUNT%% nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev 0 0" >> /etc/fstab
                    fi
                fi
            fi

            # Verify mount and apply permissions/ownership
            if mountpoint -q %%MOUNT%%; then
                echo 'Mounted: %%MOUNT%%'
                chmod 755 %%MOUNT%%
                OWNER="${FLOW_MOUNT_OWNER:-${FLOW_SSH_USER:-}}"
                if [ -z "$OWNER" ]; then
                  for cand in ubuntu ec2-user rocky centos; do
                    if id "$cand" >/dev/null 2>&1; then OWNER="$cand"; break; fi
                  done
                fi
                if [ -z "$OWNER" ]; then OWNER="${SUDO_USER:-$USER}"; fi
                chown -R "$OWNER:$OWNER" %%MOUNT%% || true
            else
                echo 'ERROR: mount %%MOUNT%%'
                exit 1
            fi
        """
        vname = (volume_name or "").strip()
        return (
            textwrap.dedent(script)
            .replace("%%MOUNT%%", _safe_mount)
            .replace("%%NFS%%", nfs_endpoint)
            .replace("%%VNAME%%", shlex.quote(vname))
            .strip()
        )

    @staticmethod
    def get_device_letter_from_volumes(existing_volumes: list) -> str:
        """Calculate next available device letter based on existing volumes.

        Args:
            existing_volumes: List of currently attached volumes

        Returns:
            Next available device letter (d, e, f, ...)
        """
        # Start at 'd' and increment based on volume count
        next_index = len(existing_volumes)
        # Bounds check: device letters d..z (0..22) supported
        if next_index > 25 - 3:
            raise ValueError(
                f"Volume index {next_index} exceeds maximum supported device letter (z)"
            )
        return chr(100 + next_index)
