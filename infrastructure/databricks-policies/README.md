# Databricks cluster policies (generated)

Generated daily from Databricks by `scripts/gen_databricks_policies.py` (D114). Do not edit.
Environment variables are left out; see the policy in Databricks.
What each policy is for: [databricks.md](../databricks.md#compute-policies).

| policy_id | name | description |
|---|---|---|
| [`000C79D951EAF0D6`](000C79D951EAF0D6.json) | Job Compute | General-purpose for running non-interactive workloads. |
| [`0017962FF5D1E3B9`](0017962FF5D1E3B9.json) | Job Compute (single node) | Ephemeral single-node job clusters for the team's pandas/xarray pipelines: one VM, Jobs DBU rate, spot with fallback, all dsci secrets injected. Clone of Job Compute (000C79D951EAF0D6) with num_workers fixed at 0 and the single-node profile. See KB infrastructure/databricks-bundle-template.md. |
| [`00172B0065CD27E1`](00172B0065CD27E1.json) | Legacy Shared Compute | Shared with teams for interactive data exploration, data analysis, and machine learning. Cannot access Unity Catalog. |
| [`000945F7985D4950`](000945F7985D4950.json) | Personal Compute | Use with small-to-medium data or libraries like pandas and scikit-learn. Spark runs in local mode. |
| [`0007F5A0B62E8B7A`](0007F5A0B62E8B7A.json) | Power User Compute | Run advanced, complex data science projects with dedicated resources. |
| [`00039FDBACC1B739`](00039FDBACC1B739.json) | SSH tunnel compute |  |
| [`001B7A44BDAA510F`](001B7A44BDAA510F.json) | Shared Compute | Shared with teams for interactive data exploration, data analysis, and machine learning. |
