import logging
from pathlib import Path as _Path

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)

logging = logging.getLogger(__name__)


class MultinodeSection(ScriptSection):
    """Multi-node cluster setup for distributed training.

    Extracts cluster configuration from /etc/hosts and exports environment variables:
    - NUM_NODES: Total number of nodes in the cluster
    - GPU_COUNT: Number of GPUs per node
    - HEAD_NODE_IP: IP address of the head node (last IP in /etc/hosts)

    These settings can then be passed to distributed launchers:

    torchrun \
    --nnodes ${NUM_NODES} \
    --nproc_per_node ${GPU_COUNT} \
    --rdzv_id ${FLOW_TASK_NAME} \
    --rdzv_backend c10d \
    --rdzv_endpoint "${HEAD_NODE_IP}:29500" \
    train.py

    """

    name = "multinode"
    # Run before docker (40)
    priority = 39

    def should_include(self, context: ScriptContext) -> bool:
        # Include for multi-node distributed jobs
        return context.num_instances > 1 and context.distributed_mode == "auto"

    def generate(self, context: ScriptContext) -> str:
        engine_name = type(self.template_engine).__name__
        tpl_dir = getattr(self.template_engine, "template_dir", None)
        logging.debug(
            "MultinodeSection: rendering with engine=%s template_dir=%s template='sections/multinode.sh.j2'",
            engine_name,
            tpl_dir,
        )
        return self.template_engine.render_file(_Path("sections/multinode.sh.j2"), {}).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        return []
