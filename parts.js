const tableBody = document.getElementById("parts-table-body");
const searchInput = document.getElementById("search-input");

let jsons = observeArray([], (newArray) => {
    reAdd();
});


var button = document.querySelector("#search-btn");
button.addEventListener("click",async function(){
    try {
        const response = await fetch(`http://127.0.0.1:8000/thing`);
        console.log("response");
        if (!response.ok) throw new Error(`Response status: ${response.status}`);

        const data = await response.text();
        var thing = data.split("XXX")
        thing.forEach(function(element){
            if (element.length > 4){
                console.log(element.length);
                addJSONS(element);
            }
            
        })
    } catch (error) {
        console.error("Error:", error.message);
    }
})

function observeArray(arr, callback) {
    return new Proxy(arr, {
        set(target, property, value) {
            target[property] = value;
            callback(target);
            return true;
        },
        deleteProperty(target, property) {
            delete target[property];
            callback(target);
            return true;
        }
    });
}

function addReplacementPart(json) {
    console.log(json);
    const row = document.createElement("tr");
    row.innerHTML = `
        <td><img src="${json.thumbnail}" alt="Part Image" width="50"></td>
        <td>${json.keyword}</td>
        <td>${json.title}</td>
        <td><a href='${json.product_link}'>${json.product_link}</a></td>
        <td>${json.source}</td>
        <td>${(json.rating) ? json.rating : "--"}⭐</td>
        <td>${json.price}</td>
    `;
    tableBody.appendChild(row);
}

function reAdd() {
    tableBody.innerHTML = "";
    jsons.forEach(addReplacementPart);
    filterResults();
}

async function addJSONS(keyword) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/amazon/?keyword=${keyword}`);
        console.log("response");
        if (!response.ok) throw new Error(`Response status: ${response.status}`);

        const data = await response.json();
        data.forEach(json => {
            json.keyword = keyword;
            jsons.push(json);
        });
    } catch (error) {
        console.error("Error:", error.message);
    }
}

function filterResults() {
    const searchText = searchInput.value.toLowerCase();
    const rows = tableBody.getElementsByTagName("tr");
    let hasResults = false;
    
    for (let row of rows) {
        const textContent = row.textContent.toLowerCase();
        row.style.display = textContent.includes(searchText) ? "" : "none";
        if (textContent.includes(searchText)) hasResults = true;
    }
    document.getElementById("no-results").style.display = hasResults ? "none" : "block";
}

searchInput.addEventListener("input", filterResults);

document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("parts-table");
    const headers = table.querySelectorAll(".sortable");
    const tbody = document.getElementById("parts-table-body");

    headers.forEach(header => {
        header.addEventListener("click", function () {
            const sortKey = this.dataset.sort;
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const isAscending = this.classList.contains("asc");

            // Determine column index
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);

            rows.sort((rowA, rowB) => {
                const cellA = rowA.children[columnIndex].textContent.trim();
                const cellB = rowB.children[columnIndex].textContent.trim();

                // Handle numeric sorting for price
                // if (sortKey === "price" || sortKey == "stars") {
                //     return isAscending
                //         ? parseFloat(cellA.replace(/[^0-9.]/g, "")) - parseFloat(cellB.replace(/[^0-9.]/g, ""))
                //         : parseFloat(cellB.replace(/[^0-9.]/g, "")) - parseFloat(cellA.replace(/[^0-9.]/g, ""));
                // }

                return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });

            // Remove existing rows and re-add sorted ones
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));

            // Toggle sorting order
            headers.forEach(h => h.classList.remove("asc", "desc"));
            this.classList.toggle("asc", !isAscending);
            this.classList.toggle("desc", isAscending);
        });
    });
});