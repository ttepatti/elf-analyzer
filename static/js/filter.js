document.addEventListener("DOMContentLoaded", function () {
    // binaryResults = location to output to
    const binaryResults = document.getElementById("binary-results");
    const filterName = document.getElementById("filter-name")
    const filterString = document.getElementById("filter-string");
    const filterLibrary = document.getElementById("filter-library");
    const toggleFiltersButton = document.getElementById("toggle-filters");
    const applyFiltersButton = document.getElementById("apply-filters");
    const clearFiltersButton = document.getElementById("clear-filters");

    // Add buttons for Expand All and Collapse All
    const expandAllButton = document.getElementById("expand-all");
    const collapseAllButton = document.getElementById("collapse-all");

    expandAllButton.addEventListener("click", () => toggleAllDetails(true));
    collapseAllButton.addEventListener("click", () => toggleAllDetails(false));

    // Render filtered binaries
    function renderBinaries(filteredBinaries) {
        const binaryResults = document.querySelector(".binary-table tbody");
        binaryResults.innerHTML = ""; // Clear the current table

        if (filteredBinaries.length === 0) {
            binaryResults.innerHTML = "<p>No binaries match the current filters.</p>";
            return;
        }
        
        filteredBinaries.forEach((binary, index) => {
            // Main row
            const mainRow = document.createElement("tr");
            mainRow.className = index % 2 === 0 ? "row-even" : "row-odd";
            mainRow.addEventListener("click", () => toggleDetails(`details-${binary.id}`));
            mainRow.innerHTML = `
                <td>${binary.name}</td>
                <td>${binary.file_type || "Unknown"}</td>
                <td>${binary.path}</td>
                <td class="expand-icon">&#9660;</td>
            `;
            
            // Hidden details row
            const detailsRow = document.createElement("tr");
            detailsRow.id = `details-${binary.id}`;
            detailsRow.className = "binary-details-row";
            detailsRow.style.display = "none"; // Hidden by default
            detailsRow.innerHTML = `
                <td colspan="4">
                    <div class="binary-details">
                        <p><strong>SHA256:</strong> ${binary.sha256}</p>
                        <p><strong>Strings Count:</strong> ${binary.strings_count || 0}</p>
                        ${
                            binary.matching_strings
                                ? `<div class="matching-strings">
                                        <p><strong>Matching Strings:</strong></p>
                                        <ul>${binary.matching_strings
                                            .map((s) => `<li>${s}</li>`)
                                            .join("")}</ul>
                                  </div>`
                                : ""
                        }
                        ${
                            binary.shared_libraries && binary.shared_libraries.length > 0
                                ? `<p><strong>Shared Libraries:</strong></p>
                                <ul>${binary.shared_libraries
                                    .map((lib) => `<li>${lib}</li>`)
                                    .join("")}</ul>`
                                : "<p>No shared libraries found.</p>"
                        }
                        <div class="binary-actions">
                            <a href="/binaries/${binary.id}" class="button">View Details</a>
                            <a href="/binaries/${binary.id}/strings" class="button">Save Strings</a>
                        </div>
                    </div>
                </td>
            `;

            binaryResults.appendChild(mainRow);
            binaryResults.appendChild(detailsRow);
        });
    }

    function toggleDetails(rowId) {
        const detailsRow = document.getElementById(rowId);
        detailsRow.style.display = detailsRow.style.display === "table-row" ? "none" : "table-row";
    }


    // Apply filters and render
    async function applyFilters() {
        const nameFilter = filterName.value.toLowerCase(); // New filter for binary name
        const stringFilter = filterString.value.toLowerCase();
        const libraryFilter = filterLibrary.value.toLowerCase();

        let filteredBinaries = [...binaries]; // Start with all binaries

        // If a string filter is provided, fetch matching binaries
        if (stringFilter) {
            try {
                const response = await fetch(`/projects/${projectId}/search_strings?query=${stringFilter}`);
                const stringFilterResults = await response.json();
    
                // Replace `filteredBinaries` with only those returned by the backend
                const matchedBinaryIds = stringFilterResults.map((result) => result.binary_id);
                filteredBinaries = filteredBinaries.filter((binary) =>
                    matchedBinaryIds.includes(binary.id)
                );
    
                // Attach matching strings to the relevant binaries
                filteredBinaries.forEach((binary) => {
                    const stringResult = stringFilterResults.find((result) => result.binary_id === binary.id);
                    binary.matching_strings = stringResult ? stringResult.matching_strings : null;
                });
            } catch (error) {
                console.error("Error fetching string search results:", error);
                return; // Exit if there's an error
            }
        } else {
            // Clear `matching_strings` if no string filter is applied
            filteredBinaries.forEach((binary) => {
                binary.matching_strings = null;
            });
        }

        // Apply frontend-side filters (name and libraries)
        filteredBinaries = filteredBinaries.filter((binary) => {
            // Match binary name
            const matchesName =
                !nameFilter || binary.name.toLowerCase().includes(nameFilter);

            // Match shared libraries
            const matchesLibrary =
                !libraryFilter ||
                (binary.shared_libraries || []).some((lib) =>
                    lib.toLowerCase().includes(libraryFilter)
                );

            // Return true if all filters match
            return matchesName && matchesLibrary;
        });

        // Render the final filtered list
        renderBinaries(filteredBinaries);
    }

    toggleFiltersButton.addEventListener("click", () => {
        const filterForm = document.getElementById("filter-form");
        const toggleButton = document.getElementById("toggle-filters");
    
        if (filterForm.classList.contains("hidden")) {
            filterForm.classList.remove("hidden"); // Show the filters
            toggleButton.textContent = "Collapse"; // Update button text
        } else {
            filterForm.classList.add("hidden"); // Hide the filters
            toggleButton.textContent = "Expand"; // Update button text
        }
    });

    // Initialize apply filters button
    applyFiltersButton.addEventListener("click", () => {
        applyFilters(); // Apply filters and update the grid
    });

    // Clear filters and render all binaries
    clearFiltersButton.addEventListener("click", () => {
        // Clear all filter inputs
        filterName.value = "";
        filterString.value = "";
        filterLibrary.value = "";

        // Reset `matching_strings` for all binaries
        binaries.forEach((binary) => {
            binary.matching_strings = null;
        });
        
        // Render the full list of binaries
        renderBinaries(binaries);
    });

    renderBinaries(binaries); // Render all binaries initially
});

