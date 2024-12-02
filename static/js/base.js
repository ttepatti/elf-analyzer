document.addEventListener("DOMContentLoaded", () => {
    const titleElement = document.getElementById("website-title");
    const originalTitle = "ELF Analyzer";

    function randomHexDigit() {
        return Math.floor(Math.random() * 16).toString(16).toUpperCase();
    }

    function flickerTitle() {
        let flickeredTitle = originalTitle
            .split("")
            .map((char) => (Math.random() < 0.1 ? randomHexDigit() : char))
            .join("");

        titleElement.textContent = flickeredTitle;

        // Restore the original title after 150ms
        setTimeout(() => {
            titleElement.textContent = originalTitle;
        }, 150);
    }

    // Flicker the title every 10–15 seconds (randomized)
    setInterval(flickerTitle, Math.random() * 5000 + 10000);
});
