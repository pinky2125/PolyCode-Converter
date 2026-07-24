function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const main = document.querySelector(".main");
    if (!sidebar) return;

    sidebar.classList.toggle("active");
    if (main) {
        main.classList.toggle("expanded");
    }
}

window.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const loadFileBtn = document.getElementById("loadFileBtn");
    const assistantBtn = document.getElementById("assistantBtn");
    const assistantInput = document.getElementById("assistantInput");
    const assistantOutput = document.getElementById("assistantOutput");
    const sourceCodeField = document.querySelector("textarea[name='source_code']");
    const editorGutter = document.getElementById("editorGutter");
    const uploadDropZone = document.getElementById("uploadDropZone");

    function updateLineNumbers() {
        if (!sourceCodeField || !editorGutter) return;
        const lines = sourceCodeField.value.split("\n").length;
        editorGutter.innerHTML = Array.from({ length: lines }, (_, index) => `<div>${index + 1}</div>`).join("");
    }

    function handleFileSelection(file) {
        if (!file || !sourceCodeField) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            sourceCodeField.value = event.target.result;
            updateLineNumbers();
        };
        reader.readAsText(file);
    }

    if (loadFileBtn && fileInput && sourceCodeField) {
        loadFileBtn.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", () => {
            const file = fileInput.files && fileInput.files[0];
            handleFileSelection(file);
        });
    }

    if (uploadDropZone) {
        ["dragenter", "dragover"].forEach((eventName) => {
            uploadDropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                uploadDropZone.classList.add("drop-active");
            });
        });
        ["dragleave", "drop"].forEach((eventName) => {
            uploadDropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                uploadDropZone.classList.remove("drop-active");
            });
        });
        uploadDropZone.addEventListener("drop", (event) => {
            const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
            handleFileSelection(file);
        });
    }

    if (sourceCodeField) {
        sourceCodeField.addEventListener("input", updateLineNumbers);
        sourceCodeField.addEventListener("scroll", () => {
            if (editorGutter) editorGutter.scrollTop = sourceCodeField.scrollTop;
        });
        updateLineNumbers();
    }

    if (assistantBtn && assistantInput && assistantOutput) {
        assistantBtn.addEventListener("click", async () => {
            const code = sourceCodeField ? sourceCodeField.value : "";
            const question = assistantInput.value.trim();
            assistantOutput.textContent = "Thinking...";
            try {
                const response = await fetch("/api/assistant", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ code, question })
                });
                const data = await response.json();
                assistantOutput.textContent = data.answer || "No response.";
            } catch (error) {
                assistantOutput.textContent = "Assistant is unavailable right now.";
            }
        });
    }
});