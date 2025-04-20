"use strict";
const API_ENDPOINT3 = "";
function showLoader2() {
    const loader = document.querySelector("#loader");
    if (loader)
        loader.style.display = "block";
}
function hideLoader2() {
    const loader = document.querySelector("#loader");
    if (loader)
        loader.style.display = "none";
}
function submitButtonHandler2() {
    const loginSubmitButton = document.querySelector("#register-btn");
    const usernameField = document.querySelector("#registerUsername");
    const passwordField = document.querySelector("#registerPassword");
    const confirmPasswordField = document.querySelector("#confirmPassword");
    if (loginSubmitButton == null || usernameField == null || passwordField == null || confirmPasswordField == null) {
        throw new Error("One or many elements are null");
    }
    loginSubmitButton.addEventListener("click", (event) => {
        event.preventDefault();
        const usernameValue = usernameField.value;
        const passwordValue = passwordField.value;
        const confirmValue = confirmPasswordField.value;
        if (passwordValue != confirmValue) {
            alert("Passwords don't match!");
            return;
        }
        const hiddenInput = document.querySelector('textarea[name="h-captcha-response"]');
        if (hiddenInput == null) {
            alert("Please complete the CAPTCHA.");
            return;
        }
        console.log(hiddenInput);
        const token = hiddenInput.value;
        if (token == null || token == '') {
            alert("Please complete the CAPTCHA.");
            return;
        }
        console.log(token);
        //hiddenInput.remove();
        // Post request
        showLoader2();
        fetch(`/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: usernameValue,
                password: passwordValue,
                captcha: token
            })
        })
            .then(response => {
            console.log(response);
            return response.json();
        })
            .then(data => {
            hideLoader2();
            if (data.message == null) {
                throw new Error("Server returned an invalid response: no message field found");
            }
            if (data.success == null || data.success == false) {
                throw new Error(`${data.message}`);
            }
            console.log("Register OK! Now go login");
            alert("Register OK. Now go login");
            window.location.href = "/login";
        })
            .catch(error => {
            hideLoader2();
            console.error('Error:', error);
            alert(`Failed to register: ${error}`);
            window.hcaptcha.reset();
        });
    });
}
function m_onload3() {
    console.log("Window loaded!");
    submitButtonHandler2();
}
window.onload = m_onload3;
