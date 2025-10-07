import json


def main_script_test_json_in_json_out_labels(_input_files, _output_files):
    # read inputs
    with _input_files["json"].open("rt") as fh:
        inp_dat = json.load(fh)
        p1_1 = int(inp_dat["p1[one]"])
        p1_2 = int(inp_dat["p1[two]"])

    # process
    p2 = p1_1 + p1_2

    # save outputs
    with _output_files["json"].open("wt") as fh:
        json.dump({"p2": p2}, fh)
