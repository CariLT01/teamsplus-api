const API_ENDPOINT4 = ""

let selectedVersion = "latest";
let selectedFilename = "";

function versionDownloadHandler() {
    const btn = document.querySelector("#version-download-btn");
    if (btn == null) return;

    btn.addEventListener("click", function() {
        fetch(`/api/v1/versions/download?file=${selectedFilename}`, {
            method: 'GET'
        })
            .then(response => {
                console.log(response);
                return response.json()
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
    })
}

async function getFileInfo(override?: string) {

    const downloadFileName = document.querySelector("#downloadFileName");
    if (downloadFileName == null) return;

    // PoGETst GET
    await fetch(`${API_ENDPOINT4}/api/v1/versions/get_file?version=${override || selectedVersion}`, {
        method: 'GET'
    })
        .then(response => {
            console.log(response);
            return response.json()
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


}

function refreshVersions() {
    const selectField: HTMLSelectElement | null = document.querySelector("#downloadVersion");
    if (selectField == null) {
        throw new Error("Select field not found!");
    }
    // PoGETst GET
    fetch(`${API_ENDPOINT4}/api/v1/versions/get`, {
        method: 'GET'
    })
        .then(response => {
            console.log(response);
            return response.json()
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
            
            const versionData: {latest: string, versions: string[]} = data.data;
            
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
            selectField.addEventListener("change", function() {
                console.log("Changed!");
                selectedVersion = selectField.value;
                getFileInfo();
            })

        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Failed to refresh versions: ${error}`);

        });


}

async function downloadLatest() {
    await getFileInfo("latest");
    fetch(`${API_ENDPOINT4}/api/v1/versions/download?file=${selectedFilename}`, {
        method: 'GET'
    })
        .then(response => {
            console.log(response);
            return response.json()
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
}

window.onload = function() {
    refreshVersions();
    getFileInfo();
    versionDownloadHandler();

    const a = document.querySelector("#download-latest");
    if (a) {
        a.addEventListener("click", () => {
            downloadLatest();
        })
    } else {
        throw new Error("Button is null");
    }
}