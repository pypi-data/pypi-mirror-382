import { createToast, jsonPost, vars } from "./util.js";

const webauthnSetupButton = /** @type {HTMLButtonElement} */ (document.getElementById("webauthn-setup"));
/** @type {import("./types").WebauthnSetupVars} */
const webauthnVars = JSON.parse(/** @type {string} */ (document.getElementById("webauthn-vars")?.textContent));

webauthnSetupButton.addEventListener("click", async () => {
    // https://developer.mozilla.org/en-US/docs/Web/API/PublicKeyCredentialCreationOptions
    const options = {
        challenge: Uint8Array.from(webauthnVars.challenge, c => c.charCodeAt(0)),
        rp: {
            name: "music player",
        },
        user: {
            id: Uint8Array.from(webauthnVars.identifier, c => c.charCodeAt(0)),
            name: webauthnVars.username,
            displayName: webauthnVars.displayname,
        },
        authenticatorSelection: {
            residentKey: /** @type {ResidentKeyRequirement} */ ("required"),
        },
        pubKeyCredParams: [{alg: -7, type: /** @type {"public-key"} */ ("public-key")}],
        attestation: /** @type {AttestationConveyancePreference} */ ("none"),
    };
    console.debug("options", options);
    const credential = await navigator.credentials.create({publicKey: options});
    if (credential == null) {
        throw new Error("null credential");
    }
    console.debug('credential', credential);
    if (!(credential instanceof PublicKeyCredential)) {
        throw new Error("invalid credential type");
    }
    const response = /** @type {AuthenticatorAttestationResponse} */ (credential.response);

    // clientDataJSON contains type==webauthn.create, origin, random challenge
    // https://developer.mozilla.org/en-US/docs/Web/API/AuthenticatorResponse/clientDataJSON
    const clientDataJsonB64 = btoa(String.fromCharCode(...new Uint8Array(response.clientDataJSON)));

    // new method to easily get public key in DER format
    // saves much hassle of decoding CBOR data, manually extracting bits from binary data, and then convert the key to DER format.
    // https://www.w3.org/TR/webauthn-2/#sctn-public-key-easy
    // https://developer.mozilla.org/en-US/docs/Web/API/AuthenticatorAttestationResponse/getPublicKey
    const publicKey = btoa(String.fromCharCode(...new Uint8Array(/** @type{ArrayBuffer} */ (response.getPublicKey()))));

    await jsonPost("/account/webauthn_setup", {client: clientDataJsonB64, public_key: publicKey});
    createToast('icon-check', vars.tTokenSetUpSuccessfully);
});
