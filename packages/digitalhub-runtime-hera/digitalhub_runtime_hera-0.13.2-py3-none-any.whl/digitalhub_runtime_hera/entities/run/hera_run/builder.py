# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_hera.entities._base.runtime_entity.builder import RuntimeEntityBuilderHera
from digitalhub_runtime_hera.entities._commons.enums import EntityKinds
from digitalhub_runtime_hera.entities.run.hera_run.entity import RunHeraRun
from digitalhub_runtime_hera.entities.run.hera_run.spec import RunSpecHeraRun, RunValidatorHeraRun
from digitalhub_runtime_hera.entities.run.hera_run.status import RunStatusHeraRun


class RunHeraRunBuilder(RunBuilder, RuntimeEntityBuilderHera):
    """
    RunHeraRunBuilder runer.
    """

    ENTITY_CLASS = RunHeraRun
    ENTITY_SPEC_CLASS = RunSpecHeraRun
    ENTITY_SPEC_VALIDATOR = RunValidatorHeraRun
    ENTITY_STATUS_CLASS = RunStatusHeraRun
    ENTITY_KIND = EntityKinds.RUN_HERA.value
