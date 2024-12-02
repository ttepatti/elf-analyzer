document.addEventListener("DOMContentLoaded", function () {
    const folderScanProgress = document.getElementById("folder-scan-progress");
    const folderScanStatus = document.getElementById("folder-scan-status");
    const binaryAnalysisProgress = document.getElementById("binary-analysis-progress");
    const binaryAnalysisStatus = document.getElementById("binary-analysis-status");
    const navigationButtons = document.getElementById("navigation-buttons");

    function updateProgress() {
        fetch("/progress/folder-scan")
            .then(response => response.json())
            .then(data => {
                folderScanProgress.value = data.progress || 0;
                folderScanProgress.max = data.total || 1;

                if (data.status === "complete") {
                    folderScanStatus.innerText = `Finished scanning ${data.total} folders.`;
                    checkCompletion();
                } else {
                    folderScanStatus.innerText = `${data.progress}/${data.total} folders scanned.`;
                }
            });

        fetch("/progress/binary-analysis")
            .then(response => response.json())
            .then(data => {
                binaryAnalysisProgress.value = data.progress || 0;
                binaryAnalysisProgress.max = data.total || 1;

                if (data.status === "complete") {
                    binaryAnalysisStatus.innerText = `Finished analyzing ${data.total} binaries.`;
                    checkCompletion();
                } else {
                    binaryAnalysisStatus.innerText = `${data.progress}/${data.total} binaries analyzed.`;
                }
            });
    }

    function checkCompletion() {
        if (
            folderScanStatus.innerText.startsWith("Finished") &&
            binaryAnalysisStatus.innerText.startsWith("Finished")
        ) {
            showNavigation();
        }
    }

    function showNavigation() {
        navigationButtons.style.display = "block";
    }

    // Poll progress every second
    setInterval(updateProgress, 1000);
});