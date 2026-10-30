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
    .then(() => window.location.assign(config.next))
    .catch(() => {
      document.getElementById("yivi-error").hidden = false;
    });
})();
