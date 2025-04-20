/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 332:
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.LifeEventProvider = void 0;
const LifeEventBaseHTML = `
<div class="event">
    <div class="content">

    </div>
    <div class="options">

    </div>
</div>
`;
const LifeEventOptionBaseHTML = `<button type="button">Go to school</button>`;
class LifeEvent {
    constructor(eventContent, eventOptions, eventId) {
        this.eventContent = eventContent;
        this.eventOptions = eventOptions;
        this.eventId = eventId;
    }
}
class LifeEventProvider {
    constructor(apiEndpointURL) {
        this.lifeEvents = [];
        this.domParser = new DOMParser();
        this.lifeEventCounter = 0;
        this.apiEndPointURL = apiEndpointURL;
        // Get first event;
        this.getEventFromAPI();
    }
    parseHtml(html) {
        return this.domParser.parseFromString(html, 'text/html').body.firstChild;
    }
    optionButtonPressProcess(counter, option, buttonElement) {
        if (counter != this.lifeEventCounter) {
            console.log("Ignore button press: outdated");
            return;
        }
        else {
            console.log("Old counter: " + counter + " New counter: " + this.lifeEventCounter);
        }
        buttonElement.classList.add("option-selected");
        // OK, ready to post
        this.postOptionToAPI(option, counter);
    }
    createEventHTML(eventContent, eventOptions) {
        const eventListElement = document.querySelector("#event-list");
        if (eventListElement == null) {
            throw new Error("Could not create new LifeEvent element: #event-list not found");
        }
        const lifeEventBaseElement = this.parseHtml(LifeEventBaseHTML);
        const elementContentDiv = lifeEventBaseElement.querySelector(".content");
        if (elementContentDiv === null) {
            throw new Error(".content DIV not found");
        }
        elementContentDiv.innerHTML = eventContent;
        const optionsElementDiv = lifeEventBaseElement.querySelector(".options");
        if (optionsElementDiv == null) {
            throw new Error(".options not found");
        }
        // Create options
        for (const option of eventOptions) {
            const optionButtonElement = this.parseHtml(LifeEventOptionBaseHTML);
            optionButtonElement.textContent = option;
            const lifeEventCounterOld = this.lifeEventCounter;
            optionButtonElement.addEventListener("click", () => {
                this.optionButtonPressProcess(lifeEventCounterOld, option, optionButtonElement);
            });
            optionsElementDiv.appendChild(optionButtonElement);
        }
        // Animation
        lifeEventBaseElement.style.transform = "translateY(100%)";
        lifeEventBaseElement.style.filter = "blur(10px)";
        lifeEventBaseElement.style.opacity = "0";
        eventListElement.appendChild(lifeEventBaseElement);
        lifeEventBaseElement.animate([
            { transform: "translateY(100%)", opacity: 0, filter: "blur(10px)" },
            { transform: "translateY(0)", opacity: 1, filter: "blur(0px)" }
        ], {
            duration: 1000,
            easing: "ease-out",
            fill: "forwards"
        });
        return lifeEventBaseElement;
    }
    getEventFromAPI() {
        fetch(`${this.apiEndPointURL}/api/v1/game_of_life/get_event`, {
            method: 'GET'
        }).then((response) => response.json()).then((APIresponse) => {
            if (APIresponse.message == null) {
                throw new Error("No 'message' key found in API response");
            }
            console.log(APIresponse.success);
            if (APIresponse.success != true) {
                console.log(APIresponse);
                console.log(APIresponse.success);
                console.log(APIresponse["success"]);
                throw new Error(`API response failed: ${APIresponse.message}`);
            }
            if (APIresponse.data == null) {
                throw new Error("API response success, but no 'data' key found in response");
            }
            const responseData = APIresponse.data;
            const eventContent = responseData.content;
            const eventOptions = responseData.options;
            const eventId = responseData.eventId;
            if (eventContent == null || eventOptions == null || eventId == null) {
                throw new Error("Event options / Event content / Event ID is null. Invalid response from server");
            }
            const eventObject = new LifeEvent(eventContent, eventOptions, eventId);
            this.lifeEventCounter = eventId;
            this.lifeEvents.push(eventObject);
            this.createEventHTML(eventContent, eventOptions); // Automatically appends it
            console.log("API response processing OK");
        });
    }
    postOptionToAPI(selectedOption, eventId) {
        fetch(`${this.apiEndPointURL}/api/v1/game_of_life/option_select_post`, {
            method: 'POST',
            body: JSON.stringify({
                eventId: eventId,
                option: selectedOption
            })
        }).then((response) => {
            return response.json();
        }).then(APIResponse => {
            if (APIResponse.message == null) {
                throw new Error("No 'message' key found in API response");
            }
            if (APIResponse.success != true) {
                throw new Error(`API response failed: ${APIResponse.message}`);
            }
            console.log("Server returned OK");
            this.getEventFromAPI();
        });
    }
}
exports.LifeEventProvider = LifeEventProvider;


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry needs to be wrapped in an IIFE because it uses a non-standard name for the exports (exports).
(() => {
var exports = __webpack_exports__;
var __webpack_unused_export__;

__webpack_unused_export__ = ({ value: true });
const events_1 = __webpack_require__(332);
const APIEndpointUrl = "http://127.0.0.1:5000/";
function onloadFunction() {
    const lifeEventProvider = new events_1.LifeEventProvider(APIEndpointUrl);
}
window.onload = onloadFunction;

})();

/******/ })()
;