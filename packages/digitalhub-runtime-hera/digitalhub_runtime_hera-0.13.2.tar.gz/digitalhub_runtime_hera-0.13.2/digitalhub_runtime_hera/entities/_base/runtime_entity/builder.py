# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
from digitalhub.entities.task._base.utils import build_task_actions

from digitalhub_runtime_hera.entities._commons.enums import EntityKinds, TaskActions


class RuntimeEntityBuilderHera(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.WORKFLOW_HERA.value
    TASKS_KINDS = build_task_actions(
        [
            (
                EntityKinds.TASK_HERA_PIPELINE.value,
                TaskActions.PIPELINE.value,
            ),
            (
                EntityKinds.TASK_HERA_BUILD.value,
                TaskActions.BUILD.value,
            ),
        ]
    )
    RUN_KIND = EntityKinds.RUN_HERA.value
