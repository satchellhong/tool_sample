import sys
import os
import json
from src.lib_tool import HandleTool
from src import merge_csv


def main(dict_param):
    try:
        handleTool = HandleTool(dict_param)

        args = handleTool.set_args()
        
        # lambda는 /tmp 경로에만 파일 및 디렉토리를 생성할 수 있음
        # lambda는 파일쓰기가 /tmp에서만 가능
        input_path = os.path.join("/tmp", "data")
        output_path = os.path.join("/tmp", "results")
        if not os.path.exists(input_path):
            os.makedirs(input_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # 1. 다운로드: lambda 서버로 s3경로의 파일을 다운로드
        handleTool.download_input()

        # 2. 함수 실행: 다운로드 받은 lambda 서버내 경로의 파일을 읽고 merge해줌
        merge_csv.merge_all(
            args.compound_name_column,
            args.smiles_column,
            input_path,
            os.path.join("/tmp", "results", "output.csv"),
        )

        # 3. 업로드: merge 완료한 csv 파일을 s3 경로에 업로드
        handleTool.upload_output_to_datatable()
        
        return {"statusCode": 200, "body": json.dumps("Tool ran successfully")}

    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps(f"Error running tool: {e}"),
        }


if __name__ == "__main__":
    handleTool = None

    dict_param = json.loads(sys.argv[1])

    main(dict_param)
