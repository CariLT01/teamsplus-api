/******/ (() => { // webpackBootstrap
/******/ 	"use strict";

const API_ENDPOINT2 = "";
const PUBLISHED_THEME_CARD = `
<div class="published-theme">
    <h3 id="theme-name">THeme name</h3>
    <p id="theme-desc">desc</p>
    <button id="theme-del" class="normal-button">Delete</button>
</div>
`;
function onPublishHandler() {
    const submitBtn = document.querySelector("#publish-theme-btn");
    const themeNameField = document.querySelector("#theme-name");
    const themeDescField = document.querySelector("#theme-desc");
    const themeDataField = document.querySelector("#theme-data");
    if (submitBtn == null || themeNameField == null || themeDescField == null || themeDataField == null) {
        console.error("One or many elements are null");
        return;
    }
    ;
    submitBtn.addEventListener("click", (event) => {
        event.preventDefault();
        // Post request
        fetch(`/api/v1/themes/publish`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                themeName: themeNameField.value,
                themeDescription: themeDescField.value,
                themeData: themeDataField.value
            })
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
                throw new Error(`${data.message}`);
            }
            console.log("Publish OK!");
            alert("Publish OK");
            refreshThemeListings();
        })
            .catch(error => {
            console.error('Error:', error);
            alert(`Failed to login: ${error}`);
        });
    });
}
function deleteTheme(themeName) {
    fetch(`${API_ENDPOINT2}/api/v1/themes/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: themeName,
        })
    })
        .then(response => {
        console.log(response);
        return response.json();
    })
        .then(data => {
        if (data.success == null || data.success == false) {
            throw new Error("Success field not found or unsuccessfull");
        }
        if (data.message == null) {
            throw new Error("No message field found");
        }
        console.log("Delete OK!");
        alert("Delete OK");
        refreshThemeListings();
    })
        .catch(error => {
        console.error('Error:', error);
        alert(`Failed to delete: ${error}`);
    });
}
function addListing(themeName, listingsContainer) {
    fetch(`${API_ENDPOINT2}/api/v1/themes/get_info?theme=${themeName}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
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
            throw new Error(`${data.message}`);
        }
        if (data.data == null) {
            throw new Error("No data field found");
        }
        const name = data.data.name;
        const desc = data.data.desc;
        if (name == null || desc == null) {
            console.error("Invalid theme data. Name or desc not found");
            return;
        }
        const parser = new DOMParser();
        const parsed = parser.parseFromString(PUBLISHED_THEME_CARD, "text/html").body.firstElementChild;
        if (parsed == null)
            return;
        const themeNameEl = parsed.querySelector("#theme-name");
        const themeDescEl = parsed.querySelector("#theme-desc");
        const themeDelEl = parsed.querySelector("#theme-del");
        if (themeNameEl == null || themeDescEl == null || themeDelEl == null) {
            console.error("One or many elements null");
            return;
        }
        themeNameEl.textContent = name;
        themeDescEl.textContent = desc;
        themeDelEl.addEventListener("click", () => {
            deleteTheme(name);
        });
        listingsContainer.appendChild(parsed);
    })
        .catch(error => {
        console.error('Error:', error);
        alert(`Failed to process theme: ${error}`);
    });
}
function refreshThemeListings() {
    const themesContainer = document.querySelector("#my-themes");
    if (themesContainer == null)
        return;
    themesContainer.innerHTML = '';
    // Get request
    fetch(`${API_ENDPOINT2}/api/v1/themes/get_owned`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
        console.log(response);
        return response.json();
    })
        .then(data => {
        if (data.success == null || data.success == false) {
            throw new Error("Success field not found or unsuccessfull");
        }
        if (data.message == null) {
            throw new Error("No message field found");
        }
        if (data.data == null) {
            throw new Error("No data field found");
        }
        const listings = data.data;
        console.log(data.data);
        listings.forEach((value, index) => {
            addListing(value, themesContainer);
        });
    })
        .catch(error => {
        console.error('Error:', error);
        alert(`Failed to refresh listings: ${error}`);
    });
}
function m_onload2() {
    console.log("Window loaded!");
    onPublishHandler();
    refreshThemeListings();
}
window.onload = m_onload2;

/******/ })()
;