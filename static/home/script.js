/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 431:
/***/ (function() {


var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const API_ENDPOINT4 = "";
let selectedVersion = "latest";
let selectedFilename = "";
function versionDownloadHandler() {
    const btn = document.querySelector("#version-download-btn");
    if (btn == null)
        return;
    btn.addEventListener("click", function () {
        fetch(`/api/v1/versions/download?file=${selectedFilename}`, {
            method: 'GET'
        })
            .then(response => {
            console.log(response);
            return response.json();
        })
            .then(data => {
            if (data.message == null) {
                throw new Error("No message field found");
            }
            if (data.success == null || data.success == false) {
                throw new Error(`Failed. Message: ${data.message}`);
            }
            // Get the actual versions
            console.log("Ok: got filename");
            const resp_data = data.data;
            if (resp_data == null) {
                throw new Error("Server did not respond with data");
            }
            // Open new window
            window.open(resp_data, "_blank");
        })
            .catch(error => {
            console.error('Error:', error);
            alert(`Failed to get version: ${error}`);
        });
    });
}
function getFileInfo(override) {
    return __awaiter(this, void 0, void 0, function* () {
        const downloadFileName = document.querySelector("#downloadFileName");
        if (downloadFileName == null)
            return;
        // PoGETst GET
        yield fetch(`${API_ENDPOINT4}/api/v1/versions/get_file?version=${override || selectedVersion}`, {
            method: 'GET'
        })
            .then(response => {
            console.log(response);
            return response.json();
        })
            .then(data => {
            if (data.message == null) {
                throw new Error("No message field found");
            }
            if (data.success == null || data.success == false) {
                throw new Error(`Failed. Message: ${data.message}`);
            }
            // Get the actual versions
            console.log("Ok: got filename");
            const resp_data = data.data;
            if (resp_data == null) {
                throw new Error("Server did not respond with data");
            }
            downloadFileName.innerHTML = `<strong>File name: </strong>${resp_data}`;
            selectedFilename = resp_data;
        })
            .catch(error => {
            console.error('Error:', error);
            alert(`Failed to get version: ${error}`);
        });
    });
}
function refreshVersions() {
    const selectField = document.querySelector("#downloadVersion");
    if (selectField == null) {
        throw new Error("Select field not found!");
    }
    // PoGETst GET
    fetch(`${API_ENDPOINT4}/api/v1/versions/get`, {
        method: 'GET'
    })
        .then(response => {
        console.log(response);
        return response.json();
    })
        .then(data => {
        if (data.message == null) {
            throw new Error("No message field found");
        }
        if (data.success == null || data.success == false) {
            throw new Error(`Failed. Message: ${data.message}`);
        }
        // Get the actual versions
        console.log("Ok: got versions");
        const versionData = data.data;
        const versionsList = versionData.versions;
        versionsList.push("latest");
        versionsList.reverse();
        for (const version of versionsList) {
            // New fucking <option> element
            const optionElement = document.createElement("option");
            optionElement.value = version;
            optionElement.textContent = version;
            selectField.appendChild(optionElement);
        }
        selectField.value = selectedVersion;
        selectField.addEventListener("change", function () {
            console.log("Changed!");
            selectedVersion = selectField.value;
            getFileInfo();
        });
    })
        .catch(error => {
        console.error('Error:', error);
        alert(`Failed to refresh versions: ${error}`);
    });
}
function downloadLatest() {
    return __awaiter(this, void 0, void 0, function* () {
        yield getFileInfo("latest");
        fetch(`${API_ENDPOINT4}/api/v1/versions/download?file=${selectedFilename}`, {
            method: 'GET'
        })
            .then(response => {
            console.log(response);
            return response.json();
        })
            .then(data => {
            if (data.message == null) {
                throw new Error("No message field found");
            }
            if (data.success == null || data.success == false) {
                throw new Error(`Failed. Message: ${data.message}`);
            }
            // Get the actual versions
            console.log("Ok: got filename");
            const resp_data = data.data;
            if (resp_data == null) {
                throw new Error("Server did not respond with data");
            }
            // Open new window
            window.open(resp_data, "_blank");
        })
            .catch(error => {
            console.error('Error:', error);
            alert(`Failed to get version: ${error}`);
        });
        getFileInfo();
    });
}
window.onload = function () {
    refreshVersions();
    getFileInfo();
    versionDownloadHandler();
};


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__[431]();
/******/ 	
/******/ })()
;