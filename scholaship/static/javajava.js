document.getElementById("apply-button").addEventListener("click", function() {
    let userInput = {
        query: document.getElementById("scholarship-input").value  // Get user input
    };

    fetch("/get_scholarships", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userInput)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Scholarships:", data);
        displayScholarships(data);  // Call function to display scholarships
    })
    .catch(error => console.error("Error fetching scholarships:", error));
});

function displayScholarships(scholarships) {
    let resultsDiv = document.getElementById("scholarship-list");
    resultsDiv.innerHTML = ""; // Clear old results

    scholarships.forEach(scholarship => {
        let scholarshipDiv = document.createElement("div");
        scholarshipDiv.classList.add("scholarship-item");
        scholarshipDiv.innerHTML = `
            <h3>${scholarship["Scholarship Name"]}</h3>
            <p><strong>Provider:</strong> ${scholarship["Provider"]}</p>
            <p><strong>Amount:</strong> ${scholarship["Amount"]}</p>
            <p><strong>Eligibility:</strong> ${scholarship["Eligibility"]}</p>
        `;
        resultsDiv.appendChild(scholarshipDiv);
    });

    // Show the "Load More" button if there are more than 3 results
    let loadMoreButton = document.getElementById("load-more");
    if (scholarships.length > 3) {
        loadMoreButton.style.display = "block";
    } else {
        loadMoreButton.style.display = "none";
    }
}
