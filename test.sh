# python run_tool.py --data_path ./data/bbb_martins.csv --pred_file_path ./results/ --model gcn --dataset BBBP --featurizer canonical --smiles_column Drug

# docker run -it -v `pwd`:/mnt/ --rm --entrypoint /bin/bash --name tool_adme --cpus 8 --memory 16384m 473130344367.dkr.ecr.ap-northeast-2.amazonaws.com/tool_merge
python run_tool.py '{
    "tool_name": "tool_merge",
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

