/**
 * Handles reordering of dynamic page rows
 */

(function () {
  "use strict";

  // Initialize when DOM is loaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRowReordering);
  } else {
    initRowReordering();
  }

  function initRowReordering() {
    // Only run on dynamic-view with edit permissions
    if (
      !document.body.classList.contains("template-dynamic-view") ||
      !document.body.classList.contains("userrole-manager")
    ) {
      console.log(
        "Not in dynamic-view edit mode, skipping row reordering initialization"
      );
      return;
    }

    console.log("Initializing row reordering...");
    // Find all move up/down buttons
    const moveUpButtons = document.querySelectorAll('a[data-action="move-up"]');
    const moveDownButtons = document.querySelectorAll(
      'a[data-action="move-down"]'
    );
    console.log(
      `Found ${moveUpButtons.length} move-up buttons and ${moveDownButtons.length} move-down buttons`
    );

    // Add event listeners to move up buttons
    moveUpButtons.forEach((button) => {
      button.addEventListener(
        "click",
        function (e) {
          e.preventDefault();
          e.stopPropagation(); // Detener la propagación del evento

          // Deshabilitar el botón temporalmente
          if (this.disabled) return;
          this.disabled = true;

          console.log("Move up button clicked");
          const element = this.closest('[data-move-target="true"]');
          console.log(
            `Moving element with ID: ${element.dataset.elementid} up`
          );

          // Re-habilitar el botón después de un tiempo
          setTimeout(() => {
            this.disabled = false;
          }, 2000);

          moveElement(element, -1);
        },
        { once: true }
      ); // Usar { once: true } para que el listener se ejecute solo una vez
    });

    // Add event listeners to move down buttons
    moveDownButtons.forEach((button) => {
      button.addEventListener(
        "click",
        function (e) {
          e.preventDefault();
          e.stopPropagation(); // Detener la propagación del evento

          // Deshabilitar el botón temporalmente
          if (this.disabled) return;
          this.disabled = true;

          console.log("Move down button clicked");
          const element = this.closest('[data-move-target="true"]');
          console.log(
            `Moving element with ID: ${element.dataset.elementid} down`
          );

          // Re-habilitar el botón después de un tiempo
          setTimeout(() => {
            this.disabled = false;
          }, 2000);

          moveElement(element, 1);
        },
        { once: true }
      ); // Usar { once: true } para que el listener se ejecute solo una vez
    });
  }

  function moveElement(element, delta) {
    const elementId = element.dataset.elementid;
    if (!elementId) {
      const errorMsg = "No data-element-id attribute found on element";
      console.error(errorMsg);
      alert(errorMsg);
      return;
    }

    console.log(`Preparing to move element ${elementId} with delta ${delta}`);

    const baseUrl = element.dataset.parenturl || "";
    console.log(`Sending request to: ${baseUrl}`);

    const requestBody = {
      ordering: {
        obj_id: elementId,
        delta: delta,
      },
    };

    console.log("Request payload:", JSON.stringify(requestBody, null, 2));

    fetch(baseUrl, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(requestBody),
      credentials: "same-origin",
    })
      .then((response) => {
        console.log(`Received response with status: ${response.status}`);
        console.log("Response headers:", response.headers);
        console.log("Response ok:", response.ok);
        if (!response.ok) {
          const error = new Error(`HTTP error! status: ${response.status}`);
          console.error("Response not OK:", error);
          throw error;
        }
      })
      .finally(() => {
        // Refresh the page after successful update
        window.location.reload();
      });
  }
})();
