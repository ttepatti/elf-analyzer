document.addEventListener("DOMContentLoaded", () => {
    const asciiTreeElement = document.getElementById("ascii-tree");
    const binaryResults = document.getElementById("binary-results");
    let originalTreeData = []; // To store the unfiltered tree structure

    // Fetch tree data and render it
    fetch(`/projects/${projectId}/tree`)
        .then((response) => response.json())
        .then((treeData) => {
            if (!treeData || !treeData.children) {
                console.error("Tree data is empty or malformed:", treeData);
                document.getElementById("ascii-tree").innerHTML = "<p>Error loading folder structure.</p>";
                return;
            }
            originalTreeData = treeData; // Save the complete unfiltered tree structure
            const ascii = generateAsciiTree(treeData);
            asciiTreeElement.innerHTML = ascii; // Use HTML for interactivity
            
            setupFolderTracking(); // Track folder visibility
            addTreeNodeClickHandlers(); // Attach click handlers after rendering
        }).catch((error) => {
            console.error("Failed to fetch tree data:", error);
            document.getElementById("ascii-tree").innerHTML = "<p>Error loading folder structure.</p>";
        });

        function generateAsciiTree(node, prefix = "", isLast = true) {
            const isFile = !node.children || node.children.length === 0;
            const isElfFile = binaries.some((binary) => binary.path === node.path);
            const isFolder = !isFile;
        
            const dataPath = isElfFile ? `data-path="${node.path}"` : "";
            const folderData = isFolder ? `data-folder="${node.path}"` : "";
            const clickableClass = isElfFile ? "clickable-node" : isFolder ? "folder-node" : "non-clickable-node";
            const colorClass = isElfFile
                ? "elf-file"
                : isFolder
                ? "folder"
                : "non-elf-file";
        
            let result = `<span class="${clickableClass} ${colorClass}" ${dataPath} ${folderData}>`;
            result += prefix + (isLast ? "└── " : "├── ");
            result += node.name + (isFolder ? "/" : "");
            result += "</span>\n";
        
            if (node.children && node.children.length > 0) {
                const newPrefix = prefix + (isLast ? "    " : "│   ");
                node.children.forEach((child, index) => {
                    const lastChild = index === node.children.length - 1;
                    result += generateAsciiTree(child, newPrefix, lastChild);
                });
            }
            return result;
        }

    function setupFolderTracking() {
        const treePane = document.querySelector(".tree-pane"); // Main scrollable container
        const folderNodes = document.querySelectorAll('[data-folder]');
        const stickyFolder = document.getElementById("current-folder");
    
        function updateStickyFolder() {
            let closestFolder = null;
            let closestDistance = Infinity;
    
            folderNodes.forEach((node) => {
                const rect = node.getBoundingClientRect();
                const treePaneRect = treePane.getBoundingClientRect();
    
                // Calculate the distance from the node's top to the tree-pane's top
                const distance = rect.top - treePaneRect.top;
    
                if (distance >= 0 && distance < closestDistance) {
                    closestDistance = distance;
                    closestFolder = node;
                }
            });
    
            if (closestFolder) {
                const folderName = closestFolder.getAttribute("data-folder");
                stickyFolder.textContent = folderName || "/";
            }
        }
    
        // Attach scroll listener to the correct container
        treePane.addEventListener("scroll", updateStickyFolder);
    
        // Initial call to set the folder correctly
        updateStickyFolder();
    }

    function rebuildTree(node, matchingBinaries) {
        console.log("Rebuilding node:", node);
        console.log("Matching binaries:", matchingBinaries);
    
        if (!node) {
            return null;
        }
    
        // If matchingBinaries contains all binaries, return the node as-is
        const includeAll = matchingBinaries.length === binaries.length;
    
        if (!node.children) {
            // Leaf node: check if it's a matching binary or include all
            const isMatchingBinary = includeAll || matchingBinaries.some((binary) => binary.path === node.path);
            return isMatchingBinary ? { ...node, children: [] } : null;
        }
    
        // Internal node: filter its children recursively
        const filteredChildren = node.children
            .map((child) => rebuildTree(child, matchingBinaries))
            .filter(Boolean);
    
        if (includeAll || filteredChildren.length > 0 || matchingBinaries.some((binary) => binary.path === node.path)) {
            // If this node has matching children, is itself a matching binary, or includeAll is true
            return { ...node, children: filteredChildren };
        }
    
        // Otherwise, discard this node
        return null;
    }

    // Update the tree view when filters are applied
    function updateTreeView(filteredBinaries) {
        console.log("Updating tree view with binaries:", filteredBinaries);
        const filteredTree = rebuildTree(originalTreeData, filteredBinaries);
    
        if (!filteredTree) {
            console.error("Filtered tree is empty or invalid.");
            document.getElementById("ascii-tree").innerHTML = "<p>No matching binaries in the tree.</p>";
            return;
        }
    
        const prunedAsciiTree = generateAsciiTree(filteredTree);
        const asciiTreeElement = document.getElementById("ascii-tree");
        asciiTreeElement.innerHTML = prunedAsciiTree;
    
        addTreeNodeClickHandlers();
    }

    function addTreeNodeClickHandlers() {
        const nodes = document.querySelectorAll(".clickable-node");
        nodes.forEach((node) => {
            node.addEventListener("click", (event) => {
                event.stopPropagation();
                const path = node.getAttribute("data-path");
                scrollToBinary(path);
                highlightNode(node);
            });
        });
    }

    function scrollToBinary(path) {
        const rows = binaryResults.querySelectorAll("tr");
        rows.forEach((row) => {
            if (row.textContent.includes(path)) {
                row.scrollIntoView({ behavior: "smooth", block: "center" }); // Align the binary in the center of the viewport
                row.classList.add("highlighted");

                setTimeout(() => row.classList.remove("highlighted"), 3000); // Remove highlight after 3 seconds
            }
        });
    }

    function highlightNode(node) {
        const allNodes = document.querySelectorAll(".clickable-node");
        allNodes.forEach((n) => n.classList.remove("highlighted-node"));
        node.classList.add("highlighted-node");
    }

    // Expose updateTreeView to be callable from other files (like filter.js)
    window.updateTreeView = updateTreeView;
});
