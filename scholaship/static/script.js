document.addEventListener("DOMContentLoaded", async function () {
    const response = await fetch("/static/combined4.csv");
    const data = await response.text();
    const rows = data.split("\n").slice(1); // Skip the header row

    const container = document.getElementById("scholarship-list");
    const loadMoreBtn = document.getElementById("load-more");
    let currentIndex = 0;
    const itemsPerPage = 9;

    function displayScholarships() {
        let endIndex = currentIndex + itemsPerPage;
        for (let i = currentIndex; i < endIndex && i < rows.length; i++) {
            const columns = rows[i].match(/("[^"]*")|([^,]+)/g); // CSV parsing
            if (columns && columns.length >= 4) {
                const name = columns[0].replace(/"/g, "").trim();
                const provider = columns[1].replace(/"/g, "").trim();
                const eligibility = columns[2].replace(/"/g, "").trim();
                const amount = columns[3].replace(/"/g, "").trim();

                const card = document.createElement("div");
                card.classList.add("scholarship-card");
                card.innerHTML = `
                    <h2>${name}</h2>
                    <p><strong>Provider:</strong> ${provider}</p>
                    <p><strong>Eligibility:</strong> ${eligibility}</p>
                    <p><strong>Amount:</strong> ${amount}</p>
                `;
                container.appendChild(card);
            }
        }

        currentIndex = endIndex;

        if (currentIndex < rows.length) {
            loadMoreBtn.style.display = "block"; // Show Load More button
        } else {
            loadMoreBtn.style.display = "none"; // Hide if no more scholarships
        }
    }

    loadMoreBtn.addEventListener("click", function () {
        displayScholarships();

        // Smooth scroll down when new scholarships are loaded
        setTimeout(() => {
            window.scrollBy({
                top: 500, // Adjust for smooth scrolling effect
                behavior: "smooth"
            });
        }, 100);
    });

    // Initial load
    displayScholarships();
});
