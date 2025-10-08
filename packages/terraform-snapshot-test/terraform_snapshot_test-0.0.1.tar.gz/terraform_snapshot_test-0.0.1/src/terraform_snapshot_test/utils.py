import json
import os
import subprocess
from operator import itemgetter
from typing import Any, Dict, List


# Takes care of the path
def sanitise_file_path(file_path: str, working_directory: str = ".") -> str:
    if working_directory == ".":
        return file_path
    elif working_directory.endswith("/"):
        return f"{working_directory}{file_path}"
    else:
        return f"{working_directory}/{file_path}"


# Runs tflocal and return the json manifest
def synthetise_terraform_json(file_path: str, working_directory: str = ".") -> Any:
    os.makedirs("tests/__snapshots__", exist_ok=True)

    # Run tflocal script
    subprocess.run(
        f"{os.environ["TF_TEST_CMD"]} init", shell=True, check=True, cwd=working_directory, env=os.environ.copy()
    )
    subprocess.run(
        f"{os.environ["TF_TEST_CMD"]} validate", shell=True, check=True, cwd=working_directory, env=os.environ.copy()
    )
    subprocess.run(
        f"{os.environ["TF_TEST_CMD"]} plan -out={file_path}.plan",
        shell=True,
        check=True,
        cwd=working_directory,
        env=os.environ.copy(),
    )
    subprocess.run(
        f"{os.environ["TF_TEST_CMD"]} show -json {file_path}.plan > {file_path}.json",
        shell=True,
        check=True,
        cwd=working_directory,
        env=os.environ.copy(),
    )

    # Load the generated json and return
    with open(f"{sanitise_file_path(file_path, working_directory)}.json") as f:
        return json.load(f)


# Sort the lists within the dictionary and sub-dictionaries
def sort_lists_in_dictionary(
    dictionary: Dict[str, Any], sort_key: str = "address", sort_attributes: List[str] = ["modules", "child_modules"]
) -> Dict[str, Any]:
    for k in dictionary.keys():

        # If list, sort and call resursively for each element
        if isinstance(dictionary[k], list) and k in sort_attributes:
            sorted_list = sorted(dictionary[k], key=itemgetter(sort_key))
            dictionary[k] = []
            for element in sorted_list:
                if isinstance(element, dict):
                    element = sort_lists_in_dictionary(
                        dictionary=element, sort_key=sort_key, sort_attributes=sort_attributes
                    )
                dictionary[k].append(element)

        # If dictionary, call recursively
        if isinstance(dictionary[k], dict):
            dictionary[k] = dict(
                sort_lists_in_dictionary(dictionary=dictionary[k], sort_key=sort_key, sort_attributes=sort_attributes)
            )

    return dictionary


# DRY to load json from file
def get_json_from_file(file_path: str, working_directory: str = ".") -> Any:
    payload = {}
    with open(sanitise_file_path(file_path, working_directory)) as f:
        payload = json.load(f)
    return payload
