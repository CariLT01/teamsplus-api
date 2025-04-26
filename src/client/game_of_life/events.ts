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
    eventContent: string;
    eventOptions: string[];
    eventId: number;

    constructor(eventContent: string, eventOptions: string[], eventId: number) {
        this.eventContent = eventContent;
        this.eventOptions = eventOptions;
        this.eventId = eventId;
    }
}

export class LifeEventProvider {

    lifeEvents: InstanceType<typeof LifeEvent>[] = [];
    private apiEndPointURL: string;
    private domParser: InstanceType<typeof DOMParser> = new DOMParser();

    private lifeEventCounter: number = 0;

    constructor(apiEndpointURL: string) {
        this.apiEndPointURL = apiEndpointURL;

        // Get first event;

        this.getEventFromAPI();

    }

    private parseHtml(html: string): HTMLElement {
        return this.domParser.parseFromString(html, 'text/html').body.firstChild as HTMLElement;
    }

    private optionButtonPressProcess(counter: number, option: string, buttonElement: HTMLButtonElement) {
        if (counter != this.lifeEventCounter) {
            console.log("Ignore button press: outdated");
            return;
        } else {
            console.log("Old counter: " + counter + " New counter: " + this.lifeEventCounter);
        }

        buttonElement.classList.add("option-selected");
        // OK, ready to post

        this.postOptionToAPI(option, counter);

    }

    private createEventHTML(eventContent: string, eventOptions: string[]): HTMLDivElement {

        const eventListElement: HTMLDivElement | null = document.querySelector("#event-list");
        if (eventListElement == null) {
            throw new Error("Could not create new LifeEvent element: #event-list not found");
        }

        const lifeEventBaseElement: HTMLDivElement = this.parseHtml(LifeEventBaseHTML) as HTMLDivElement;
        const elementContentDiv: HTMLDivElement | null = lifeEventBaseElement.querySelector(".content");
        if (elementContentDiv === null) {
            throw new Error(".content DIV not found");
        }

        elementContentDiv.innerHTML = eventContent;

        const optionsElementDiv: HTMLDivElement | null = lifeEventBaseElement.querySelector(".options");
        if (optionsElementDiv == null) {
            throw new Error(".options not found");
        }

        // Create options

        for (const option of eventOptions) {

            const optionButtonElement: HTMLButtonElement = this.parseHtml(LifeEventOptionBaseHTML) as HTMLButtonElement;
            optionButtonElement.textContent = option;

            const lifeEventCounterOld: number = this.lifeEventCounter;

            optionButtonElement.addEventListener("click", () => {
                this.optionButtonPressProcess(lifeEventCounterOld, option, optionButtonElement);
            })

            optionsElementDiv.appendChild(optionButtonElement);
        }

        // Animation
        lifeEventBaseElement.style.transform = "translateY(100%)";
        lifeEventBaseElement.style.filter = "blur(10px)";
        lifeEventBaseElement.style.opacity = "0";
        eventListElement.appendChild(lifeEventBaseElement);
        lifeEventBaseElement.animate([
            { transform: "translateY(100%)", opacity: 0 , filter: "blur(10px)"},
            { transform: "translateY(0)", opacity: 1, filter: "blur(0px)" }
        ], {
            duration: 1000,
            easing: "ease-out",
            fill: "forwards"
        });


        return lifeEventBaseElement
    }

    private getEventFromAPI() {
        fetch(`${this.apiEndPointURL}/api/v1/game_of_life/get_event`, {
            method: 'GET'
        }).then((response) => response.json()).then((APIresponse) => {
            if (APIresponse.message == null) {
                throw new Error("No 'message' key found in API response");
            }
            console.log(APIresponse.success)
            if (APIresponse.success != true) {
                console.log(APIresponse);
                console.log(APIresponse.success);
                console.log(APIresponse["success"])
                throw new Error(`API response failed: ${APIresponse.message}`);
            }
            if (APIresponse.data == null) {
                throw new Error("API response success, but no 'data' key found in response");
            }

            const responseData = APIresponse.data;

            const eventContent: string = responseData.content;
            const eventOptions: string[] = responseData.options;
            const eventId: number = responseData.eventId;

            if (eventContent == null || eventOptions == null || eventId == null) {
                throw new Error("Event options / Event content / Event ID is null. Invalid response from server");
            }

            const eventObject: InstanceType<typeof LifeEvent> = new LifeEvent(eventContent, eventOptions, eventId);
            this.lifeEventCounter = eventId;
            this.lifeEvents.push(eventObject);

            this.createEventHTML(eventContent, eventOptions); // Automatically appends it
            console.log("API response processing OK");

        })
    }

    private postOptionToAPI(selectedOption: string, eventId: number) {
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
        })
    }



}