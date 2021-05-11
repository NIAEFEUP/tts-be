const got = require("got");

const AUTH_BASE_URL = "https://sigarra.up.pt/feup/pt/mob_val_geral.autentica?";

async function getCookie() {

    // build URL with credentials
    const urlRequest =
         `${AUTH_BASE_URL}pv_login=${encodeURIComponent(process.env.UP_USER)}&pv_password=${encodeURIComponent(process.env.UP_PWD)}`;

    try {
        const response = await got.post(urlRequest);
        const parts = response.headers["set-cookie"];
        const SI_SESSION = parts[0].split(";")[0];
        const SI_SECURITY = parts[1].split(";")[0];
        return [SI_SESSION, SI_SECURITY].join(";");

    } catch (error) {
        console.error(error.message);
        return undefined;
    }
}

module.exports = getCookie;
