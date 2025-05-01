
import { SafeTunnel } from "../safeTunnel";


function showLoader2() {
  const loader: HTMLDivElement | null = document.querySelector("#loader");
  if (loader) loader.style.display = "block";
}
function hideLoader2() {
  const loader: HTMLDivElement | null = document.querySelector("#loader");
  if (loader) loader.style.display = "none";
}
function submitButtonHandler2() {
  const loginSubmitButton: HTMLButtonElement | null = document.querySelector("#register-btn");
  const usernameField: HTMLInputElement | null = document.querySelector("#registerUsername");
  const passwordField: HTMLInputElement | null = document.querySelector("#registerPassword");
  const confirmPasswordField: HTMLInputElement | null = document.querySelector("#confirmPassword");
  const privateKeyPasswordField: HTMLInputElement | null = document.querySelector("#privateKeyPassword");
  const privateKeyPasswordConfirmField: HTMLInputElement | null = document.querySelector("#privateKeyPasswordConfirm");

  if (loginSubmitButton == null || usernameField == null || passwordField == null || confirmPasswordField == null  || privateKeyPasswordField == null || privateKeyPasswordConfirmField == null) {
    throw new Error("One or many elements are null");
  }

  loginSubmitButton.addEventListener("click", async (event) => {
    event.preventDefault();

    /* 
                        <input type="password" name="password" id="privateKeyPassword" placeholder="Encryption Password" required autocomplete="off">
                    <input type="password" name="password" id="privateKeyPasswordConfirm" placeholder="Encryption Password Confirm" required autocomplete="off">
    */

    const usernameValue: string = usernameField.value;
    const passwordValue: string = passwordField.value;
    const confirmValue: string = confirmPasswordField.value;
    const privateKeyPasswordValue: string = privateKeyPasswordField.value;
    const privateKeyPasswordConfirmValue: string = privateKeyPasswordConfirmField.value;
    if (passwordValue != confirmValue) {
      alert("Passwords don't match!");
      return;
    }
    if (privateKeyPasswordValue != privateKeyPasswordConfirmValue) {
      alert("Encryption passwords don't match!");
      return;
    }

    const hiddenInput: HTMLInputElement | null = document.querySelector('textarea[name="h-captcha-response"]');
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
    const safeTunnel = new SafeTunnel();
    const b = JSON.stringify({
      username: usernameValue,
      password: passwordValue,
      privateKeyPassword: privateKeyPasswordField.value,
      captcha: token
    });
    const e = await safeTunnel.safeTunnelEncrypt(b);
    fetch(`/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(e)
    })
      .then(response => {
        console.log(response);
        return response.json()
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
  })
}

function m_onload3() {
  console.log("Window loaded!");
  submitButtonHandler2();
}

window.onload = m_onload3;