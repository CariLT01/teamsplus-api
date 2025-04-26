const API_ENDPOINT = "";
async function exportKeyToPEM(
    key: CryptoKey,
    type: "public" | "private" = "public"
): Promise<string> {
    const format = type === "public" ? "spki" : "pkcs8";
    const label = type === "public" ? "PUBLIC KEY" : "PRIVATE KEY";

    const buf = await window.crypto.subtle.exportKey(format, key);
    const b64 = btoa(
        String.fromCharCode(...new Uint8Array(buf))
    );
    const pem = [
        `-----BEGIN ${label}-----`,
        ...b64.match(/.{1,64}/g)!,
        `-----END ${label}-----`
    ].join("\n");

    return pem;
}

function base64toBytes(b64: string) {
    const bin = atob(b64);
    const len = bin.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = bin.charCodeAt(i);
    }
    return bytes;  // Uint8Array of decoded bytes
}

async function waitForValue<T>(ref: T | null, check: () => boolean = () => ref !== null): Promise<T> {
    return new Promise<T>((resolve) => {
        const interval = setInterval(() => {
            if (check()) {
                clearInterval(interval);
                resolve(ref as T);  // type assertion since ref is no longer null
            }
        }, 100); // check every 100ms
    });
}

export class SafeTunnel {

    keypair!: CryptoKeyPair;
    aesKey!: CryptoKey;
    aesKeyString!: string;

    constructor() {
        this.asyncInit();
    }


    private async asyncInit() {
        await this.createRSAKeypair();
        await this.getSharedAESKey();
    }

    private async createRSAKeypair() {
        console.log("Creating RSA keypair");
        this.keypair = await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256"
            },
            true, // extractable
            ["encrypt", "decrypt"]
        );
        console.log("Keypair OK");
    }

    private async getSharedAESKey() {
        console.log("Attempt to establish safe-tunnel connection");
        const resp = await fetch(`${API_ENDPOINT}/api/v1/safe_tunnel/handshake`, {
            method: 'POST',
            body: JSON.stringify({
                publicKey: await exportKeyToPEM(this.keypair.publicKey, "public")
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const response_json = await resp.json();
        if (response_json.message == null) {
            throw new Error("Invalid server response");
        }
        if (response_json.success == false) {
            throw new Error(`Failed to establish secure connection: ${response_json.message}`);
        }
        if (response_json.data == null) {
            throw new Error(`Server returned an invalid response`);
        }

        this.aesKeyString = response_json.data.ks;
        console.log(this.aesKeyString);
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: "RSA-OAEP"
            },
            this.keypair.privateKey,       // previously imported/generated private CryptoKey
            base64toBytes(response_json.data.k)  // an ArrayBuffer (not base64 or string)
        );

        this.aesKey = await window.crypto.subtle.importKey(
            "raw",
            decrypted,
            { name: "AES-GCM" },  // or AES-GCM
            false,                // not extractable
            ["encrypt", "decrypt"]
        );

        console.log("Successfully established safe-tunnel connection");
    }

    async safeTunnelEncrypt(content: string) {
        console.log("Wait for AES finish creation");
        await waitForValue(this.aesKey, () => this.aesKey !== null);
        console.log("AES Creation is done");
        console.log("AES key:", this.aesKey);
        const iv = crypto.getRandomValues(new Uint8Array(12));  // 12-byte IV for GCM

        const data = new TextEncoder().encode(content);

        const ciphertext = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            this.aesKey,
            data
        );

        const b64 = btoa(String.fromCharCode(...new Uint8Array(ciphertext)));
        const b642 = btoa(String.fromCharCode(...new Uint8Array(iv)));
        return {
            iv: b642,
            ct: b64,
            k: this.aesKeyString,
        }
    }

    async safeTunnelDecrypt(ct: string, iv: string) {
        const algorithm = {
            name: "AES-GCM",
            iv: base64toBytes(iv),  // Initialization Vector
        };

        const decryptedData = await window.crypto.subtle.decrypt(
            algorithm,
            this.aesKey,
            base64toBytes(ct)
        );
        const decoder = new TextDecoder();
        const plain = decoder.decode(decryptedData);
        return JSON.parse(plain);

    }

}