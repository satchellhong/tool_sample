import csv
import os


def get_all_headers(compound_name_column, smiles_column, directory="./data"):
    default_columns = list()
    if compound_name_column in [None, "id"]:
        default_columns = ["id", smiles_column]
    elif smiles_column in [None, "id"]:
        default_columns = ["id", compound_name_column]
    else:
        if compound_name_column == smiles_column:
            default_columns = ["id", smiles_column]
        else:
            default_columns = ["id", compound_name_column, smiles_column]

    file_order = ["input.csv"]  # Ensure input.csv is processed first
    csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    file_order.extend([f for f in csv_files if f != "input.csv"])

    # 재실행시 input에 있는 column명이 뒤에 tool의 output column명과 같은 것이 여러번 붙는 현상이 있으니
    # input.csv에 있는 column과 겹치면 새로 실행한 (tool에서 결과로 나온 output의 column) column으로 overwrite한다.
    # input.csv에 겹치는 column있는지 비교해서 headers_map["input.csv"]에서 뺀다.
    tool_headers = list()
    headers_map = dict()
    for filename in file_order:
        if filename != "input.csv":
            filename_no_ext = os.path.splitext(filename)[0]
            headers_map[filename] = list()
            with open(os.path.join(directory, filename), "r") as csvfile:
                row = csvfile.readline()
                file_headers = row.strip().split(",")
                prefix = f"{filename_no_ext}-" if filename != "input.csv" else ""
                for idx, header in enumerate(file_headers):
                    if header not in default_columns:
                        tool_headers.append(f"{prefix}{header}".lower())
                        headers_map[filename].append(idx)
    headers = list()
    filename = "input.csv"
    filename_no_ext = os.path.splitext(filename)[0]
    headers_map[filename] = list()
    with open(os.path.join(directory, filename), "r") as csvfile:
        row = csvfile.readline()
        file_headers = row.strip().split(",")
        for idx, header in enumerate(file_headers):
            if header not in tool_headers:
                headers.append(header)
                headers_map[filename].append(idx)

    headers.extend(tool_headers)

    return headers, headers_map, file_order


def process_and_write_csv(
    compound_name_column,
    smiles_column,
    directory="./data",
    output_file="./results/output.csv",
):
    headers, headers_map, file_order = get_all_headers(
        compound_name_column, smiles_column, directory
    )

    with open(output_file, "w", newline="") as outfile:
        outfile.write(",".join(headers) + "\n")

        # 값들을 header의 순서대로 정렬하여 입력 row by row로
        infiles = list()
        for filename in file_order:
            buffer = open(os.path.join(directory, filename), "r")
            infiles.append(buffer)

        # cut headers
        for filename, infile in zip(file_order, infiles):
            row = infile.readline()

        # read values
        is_eof = True
        while is_eof:
            for file_idx, (filename, infile) in enumerate(zip(file_order, infiles)):
                row = infile.readline()
                if not row or row == "":
                    is_eof = False
                    continue
                headers = row.strip().split(",")
                header_idx_list = headers_map[filename]
                for idx, header_idx in enumerate(header_idx_list):
                    if (
                        len(header_idx_list) - 1 == idx
                        and len(file_order) - 1 == file_idx
                    ):
                        outfile.write(headers[header_idx] + "\n")
                    else:
                        outfile.write(headers[header_idx] + ",")

        for infile in infiles:
            infile.close()


def merge_all(
    compound_name_column,
    smiles_column,
    directory="./data",
    output_file="./results/output.csv",
):
    process_and_write_csv(
        compound_name_column,
        smiles_column,
        directory=directory,
        output_file=output_file,
    )
