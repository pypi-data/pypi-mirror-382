# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from enum import Enum


class EntityKinds(Enum):
    """
    Entity kinds.
    """

    WORKFLOW_HERA = "hera"
    TASK_HERA_PIPELINE = "hera+pipeline"
    TASK_HERA_BUILD = "hera+build"
    RUN_HERA = "hera+run"


class TaskActions(Enum):
    """
    Task actions.
    """

    PIPELINE = "pipeline"
    BUILD = "build"
