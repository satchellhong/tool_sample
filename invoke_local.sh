curl -XPOST "http://localhost:18000/2015-03-31/functions/function/invocations" -d '{
    "tool_name": "tool_merge",
    "log_id": "seokcholhong@aigendrug.com:group-20240923065405:chemprops-20240923065419:tool_merge:2024-10-21T03:56:50.301829+00:00",
    "function": {
        "name": "ensemble_adme",
        "info": {
            "option": {
                "compoundNameColumn": "name",
                "smilesColumn": "smiles",
                "dbname": "seokcholhong@aigendrug_com_drugvlab_db"
            },
            "input": {
                "library": {
                    "bucket": "drugvlab-bucket",
                    "path": "library/seokcholhong@aigendrug.com/group-20240923065405/chemprops-20240923065419"
                },
                "ensemble": {
                    "bucket": "drugvlab-bucket",
                    "path": "ensemble/seokcholhong@aigendrug.com/group-20240923065405/chemprops-20240923065419"
                }
            }
        }
    }
}'