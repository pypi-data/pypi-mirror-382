# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_kfp.dsl import pipeline_context


def myhandler(ref):
    with pipeline_context() as pc:
        s1 = pc.step(
            name="step1",
            function="function-dbt",
            action="transform",
            inputs=[{"employees": ref}],
            outputs=[{"output_table": "e60"}],
        )

        s2 = pc.step(
            name="step2",
            function="function-dbt",
            action="transform",
            inputs=[{"employees": s1.outputs["e60"]}],
            outputs=[{"output_table": "employees_pipeline"}],
        )

        return s2.outputs["employees_pipeline"]
