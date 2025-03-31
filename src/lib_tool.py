import io
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import json
import time
from datetime import datetime, timezone
from dateutil import parser
from botocore.exceptions import NoCredentialsError, ClientError
from boto3.dynamodb.conditions import Key, Attr


class Args:
    def __getattr__(self, name):
        if name not in self.__dict__:
            self.__dict__[name] = None
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

class HandleBucket:
    def __init__(self):
        self.data_table = None

    def read_json(self, file_path, client_s3, bucket_name):
        json_file = client_s3.get_object(Bucket=bucket_name, Key=file_path)
        dict_result = json.loads(json_file["Body"].read().decode("utf-8"))

        return dict_result

    def write_json(self, dict_data, file_path, client_s3, bucket_name):
        json_data = json.dumps(dict_data)

        client_s3.put_object(
            Body=json_data,
            Bucket=bucket_name,
            Key=file_path,
        )

    def pq2csv(self, bucket_name, file_key, args):
        client_s3 = boto3.client("s3")

        buffer = io.BytesIO()
        client_s3.download_fileobj(bucket_name, file_key, buffer)
        buffer.seek(0)
        df = pq.read_table(buffer).to_pandas()
        self.data_table = df

        df.to_csv(args.data_path, index=False)

    def csv2pq(self, bucket_name, file_key, df):
        client_s3 = boto3.client("s3")

        buffer = io.BytesIO()
        table = pa.Table.from_pandas(df)
        pq.write_table(table, buffer)
        buffer.seek(0)
        client_s3.upload_fileobj(buffer, bucket_name, file_key)

    def make_dir_p(self, bucket_name, directory_path):
        client_s3 = boto3.client("s3")
        client_s3.put_object(Bucket=bucket_name, Key=directory_path, Body="")

    def upload_directory_to_s3(self, local_directory, bucket_name, s3_prefix):
        s3_client = boto3.client("s3")

        for root, dirs, files in os.walk(local_directory):
            for filename in files:
                local_path = os.path.join(root, filename)

                # Calculate relative path
                relative_path = os.path.relpath(local_path, local_directory)
                s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")

                try:
                    print(f"Uploading {local_path} to {bucket_name}/{s3_path}")
                    s3_client.upload_file(local_path, bucket_name, s3_path)
                except FileNotFoundError:
                    print(f"The file {local_path} was not found")
                except NoCredentialsError:
                    print("Credentials not available")
                    return False

        print("Upload completed successfully")
        return True

    def get_list_output_csvs(self, bucket, path):
        s3_client = boto3.client("s3")
        paginator = s3_client.get_paginator("list_objects_v2")

        list_output_csvs = list()
        try:
            for page in paginator.paginate(Bucket=bucket, Prefix=path):
                for obj in page.get("Contents", []):
                    if obj["Key"].endswith(".csv"):
                        list_output_csvs.append(obj["Key"])
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return list_output_csvs

    def download_file_src_to_dest(self, src_path, dest_path, bucket_name):
        s3_client = boto3.client("s3")
        try:
            dir_names = src_path.split("/")
            file_name = f"{dir_names[-3]}-{dir_names[-2]}.csv"
            s3_client.download_file(
                bucket_name,
                src_path,
                os.path.join(dest_path, file_name),
            )
        except Exception as e:
            print("FAILED", str(e) + " in _copy_file_src_to_dest()")
            return False
        return True


class HandleTool(HandleBucket):
    def __init__(self, params):
        HandleBucket.__init__(self)

        self.params = params

    def set_args(self):
        self.input_path = os.path.join("/tmp", "data")
        self.output_path = os.path.join("/tmp", "results")
        self.info = self.params["function"]["info"]
        self.function_name = self.params["function"]["name"]

        self.args = Args()

        self.args.tool_name = self.params["tool_name"]
        self.args.function_name = self.params["function"]["name"]

        if self.info["input"]["library"]["path"].endswith("/"):
            self.args.user_name = (
                f"{self.info['input']['library']['path'].split('/')[-4]}"
            )
            self.args.group_name = (
                f"{self.info['input']['library']['path'].split('/')[-3]}"
            )
            self.args.lib_name = (
                f"{self.info['input']['library']['path'].split('/')[-2]}"
            )
        else:
            self.args.user_name = (
                f"{self.info['input']['library']['path'].split('/')[-3]}"
            )
            self.args.group_name = (
                f"{self.info['input']['library']['path'].split('/')[-2]}"
            )
            self.args.lib_name = (
                f"{self.info['input']['library']['path'].split('/')[-1]}"
            )

        self.args.data_path = os.path.join(self.input_path, "input.csv")
        self.args.results_path = os.path.join(self.output_path, "output.csv")
        self.args.compound_name_column = self.info["option"].get(
            "compoundNameColumn", "name"
        )
        self.args.smiles_column = self.info["option"].get("smilesColumn", "smiles")

        return self.args

    def download_input(self):
        list_output_csvs = self.get_list_output_csvs(
            self.info["input"]["ensemble"]["bucket"],
            os.path.join(self.info["input"]["ensemble"]["path"], self.function_name),
        )
        for output_csv in list_output_csvs:
            print(output_csv)
            self.download_file_src_to_dest(
                output_csv, self.input_path, self.info["input"]["ensemble"]["bucket"]
            )
        self.pq2csv(
            self.info["input"]["library"]["bucket"],
            os.path.join(self.info["input"]["library"]["path"], "main.parquet"),
            args=self.args,
        )

    def upload_csv_to_s3(self, local_file_path, bucket_name, s3_file_name):
        # Create an S3 client
        s3_client = boto3.client("s3")

        try:
            # Upload the file
            s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
            print(
                f"Successfully uploaded {local_file_path} to {bucket_name}/{s3_file_name}"
            )
        except ClientError as e:
            print(f"Error uploading file to S3: {str(e)}")
            return False
        return True

    def upload_output_to_s3(self):
        s3_file_path = (
            "/".join(
                ["ensemble"]
                + self.info["input"]["library"]["path"].split("/")[1:]
                + ["ensemble_adme", self.args.tool_name]
            )
            + "/output.csv"
        )
        self.upload_csv_to_s3(
            self.args.results_path,
            self.info["input"]["library"]["bucket"],
            s3_file_path,
        )

    def upload_output_to_datatable(self) -> None:
        result_csv_name = "output.csv"
        result_df = pd.read_csv(os.path.join(self.output_path, result_csv_name))
        result_df.columns = result_df.columns.str.lower()
        print(result_df)

        # 생성된 csv 파일을 pyarrow 형태로 저장
        self.csv2pq(
            self.info["input"]["library"]["bucket"],
            os.path.join(self.info["input"]["library"]["path"], "main.parquet"),
            result_df,
        )

        # 테이블 이름 지정
        table_name = "_".join(
            [
                item
                for item in self.info["input"]["library"]["path"].split("/")
                if item != ""
            ][-2:]
        )

        # 테이블 업데이트
        self.update_table(
            self.info["input"]["library"]["bucket"],
            table_name,
            self.info["input"]["library"]["path"],
            self.info["option"]["dbname"],
        )
