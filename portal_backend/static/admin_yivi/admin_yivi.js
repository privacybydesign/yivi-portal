// Second login step of the Django admin: disclose the account's email with Yivi.
// The server does the checking; this only drives the widget and moves on.
"use strict";

(function () {
  const config = JSON.parse(document.getElementById("yivi-config").textContent);
  const request = {
    method: "POST",
    credentials: "same-origin",
    headers: { "X-CSRFToken": config.csrfToken },
  };

  function getSafeNextUrl(next) {
    try {
      const url = new URL(next, window.location.origin);
      const isHttp = url.protocol === "http:" || url.protocol === "https:";
      if (!isHttp || url.origin !== window.location.origin) {
        return null;
      }
      return url.toString();
    } catch (_) {
      return null;
    }
  }

  window.yivi
    .newWeb({
      element: "#yivi-web-form",
      language: "en",
      session: {
        start: { ...request, url: () => config.startUrl },
        result: { ...request, url: () => config.resultUrl },
      },
    })
    .start()
    .then(() => {
      const safeNext = getSafeNextUrl(config.next);
      if (!safeNext) {
        document.getElementById("yivi-error").hidden = false;
        return;
      }
      window.location.assign(safeNext);
    })
    .catch(() => {
      document.getElementById("yivi-error").hidden = false;
    });
})();
