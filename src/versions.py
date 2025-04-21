from flask import Response, jsonify, request
import traceback
import json

from src.config import ABSOLUTE_PATH, DOWNLOAD_URL

from typing import cast
from typing import TypedDict


class VersionsDict(TypedDict):
    versions: dict[str, str]
    latest: str

def read_versions_file()->VersionsDict:
    with open(f"{ABSOLUTE_PATH}data/versions.json", "r") as f: return cast(VersionsDict, json.loads(f.read()))

############## ROUTES #######################

def get_versions_route()->tuple[Response, int]:
    try:
        versions_file = read_versions_file()

        versions = versions_file["versions"]

        versions_list = []
        for i in versions:
            versions_list.append(i)
        
        latest = versions_file["latest"]

        return jsonify(success=True, message="OK", data={
            "latest": latest,
            "versions": versions_list
        }), 200
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

def get_file_route()->tuple[Response, int]:
    try:
        query_version = request.args.get("version")
        if query_version == None:
            return jsonify(success=False, message="No version specified"), 400
        
        versions_file = read_versions_file()
        versions: dict[str, str] = versions_file["versions"]
        
        version_info = versions.get(query_version)
        if query_version == 'latest':
            version_info = versions.get(versions_file["latest"])
        if version_info == None:
            return jsonify(success=False, message="Version not found"), 404
        
        return jsonify(success=True, message="OK", data=f"{version_info}.zip"), 200
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500       

def get_link_from_version_route()->tuple[Response, int]:
    try:
        query_file = request.args.get("file")
        if query_file == None:
            return jsonify(success=False, message="No file specified"), 400

        return jsonify(success=True, message="OK", data=f"{DOWNLOAD_URL}{query_file}"), 200

    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500      