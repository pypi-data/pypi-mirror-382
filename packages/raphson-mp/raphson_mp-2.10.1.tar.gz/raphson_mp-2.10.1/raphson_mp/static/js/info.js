if (document.getElementById("dav-nautilus")) {
    const nautilusUrl = /** @type {HTMLSpanElement} */ (document.getElementById("dav-nautilus"));
    const dolphinUrl = /** @type {HTMLSpanElement} */ (document.getElementById("dav-dolphin"));
    const materialHost = /** @type {HTMLSpanElement} */ (document.getElementById("material-host"));
    const materialPort = /** @type {HTMLSpanElement} */ (document.getElementById("material-port"));
    const materialProto = /** @type {HTMLSpanElement} */ (document.getElementById("material-proto"));
    const davx5Url = /** @type {HTMLSpanElement} */ (document.getElementById("davx5-url"));
    const windowsUrl = /** @type {HTMLSpanElement} */ (document.getElementById("dav-windows"));

    const proto = window.location.protocol;
    const port = window.location.port != "" ? window.location.port : (proto == "https:" ? 443 : 80);

    nautilusUrl.textContent = proto.replace("http", "dav") + "//" + window.location.host + "/dav";
    dolphinUrl.textContent = proto.replace("http", "webdav") + "//" + window.location.host + "/dav";
    materialHost.textContent = window.location.hostname;
    materialPort.textContent = port + '';
    materialProto.textContent = proto.substring(0, proto.length - 1).toUpperCase();
    davx5Url.textContent = proto + "//" + window.location.hostname + "/dav";
    windowsUrl.textContent = "net use R: \\\\" + window.location.hostname + (proto == "https:" ? "@SSL" : "") + "@" + port + "\\dav\\ /savecred";
}
