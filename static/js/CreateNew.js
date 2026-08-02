document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("fileInput");
    const fileText = document.getElementById("fileText");
    const dropArea = document.querySelector(".drop-area");

    if (fileInput && fileText && dropArea) {

        fileInput.addEventListener("change", function () {

            if (fileInput.files.length > 0) {

                const file = fileInput.files[0];

                fileText.innerHTML = "✅ " + file.name + " uploaded";
                fileText.style.color = "#22c55e";

                dropArea.classList.add("success");
            }

        });

    }

});