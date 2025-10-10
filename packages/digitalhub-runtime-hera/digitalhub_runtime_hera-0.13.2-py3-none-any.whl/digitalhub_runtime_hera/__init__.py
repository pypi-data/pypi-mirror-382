# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_hera.entities._commons.enums import EntityKinds
from digitalhub_runtime_hera.entities.run.hera_run.builder import RunHeraRunBuilder
from digitalhub_runtime_hera.entities.task.hera_build.builder import TaskHeraBuildBuilder
from digitalhub_runtime_hera.entities.task.hera_pipeline.builder import TaskHeraPipelineBuilder
from digitalhub_runtime_hera.entities.workflow.hera.builder import WorkflowHeraBuilder

entity_builders = (
    (EntityKinds.RUN_HERA.value, RunHeraRunBuilder),
    (EntityKinds.TASK_HERA_PIPELINE.value, TaskHeraPipelineBuilder),
    (EntityKinds.TASK_HERA_BUILD.value, TaskHeraBuildBuilder),
    (EntityKinds.WORKFLOW_HERA.value, WorkflowHeraBuilder),
)

try:
    from digitalhub_runtime_hera.runtimes.builder import RuntimeHeraBuilder

    runtime_builders = ((kind, RuntimeHeraBuilder) for kind in [e.value for e in EntityKinds])
except ImportError:
    runtime_builders = tuple()
