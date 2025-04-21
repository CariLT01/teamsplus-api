import { LifeEventProvider } from "./events";

const APIEndpointUrl: string = "http://127.0.0.1:5000/";

function onloadFunction() {

    const lifeEventProvider = new LifeEventProvider(APIEndpointUrl);
}

window.onload = onloadFunction;