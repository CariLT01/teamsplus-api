/******/ (() => { // webpackBootstrap
/******/ 	"use strict";

const API_ENDPOINT = "";
const STORAGE_KEY = "teamsplus_api_token";
function showLoader() {
    const loader = document.querySelector("#loader");
    if (loader)
        loader.style.display = "block";
}
function hideLoader() {
    const loader = document.querySelector("#loader");
    if (loader)
        loader.style.display = "none";
}
function submitButtonHandler() {
    const loginSubmitButton = document.querySelector("#login-btn");
    const usernameField = document.querySelector("#loginUsername");
    const passwordField = document.querySelector("#loginPassword");
    if (loginSubmitButton == null || usernameField == null || passwordField == null) {
        throw new Error("One or many elements are null");
    }
    loginSubmitButton.addEventListener("click", (event) => {
        event.preventDefault();
        const usernameValue = usernameField.value;
        const passwordValue = passwordField.value;
        // Post request
        showLoader();
        fetch(`/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: usernameValue,
                password: passwordValue,
            })
        })
            .then(response => {
            console.log(response);
            return response.json();
        })
            .then(data => {
            hideLoader();
            if (data.message == null) {
                throw new Error("Server returned an invalid response: no message field found");
            }
            if (data.success == null || data.success == false) {
                throw new Error(`${data.message}`);
            }
            console.log("Login OK!");
            window.location.href = "/dashboard";
        })
            .catch(error => {
            hideLoader();
            console.error('Error:', error);
            alert(`Failed to login: ${error}`);
        });
    });
}
function m_onload() {
    console.log("Window loaded!");
    submitButtonHandler();
}
window.onload = m_onload;

/******/ })()
;