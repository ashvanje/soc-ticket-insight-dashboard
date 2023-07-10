// Add event listeners to each cell with the "overlay" class
var overlayCells = document.querySelectorAll('td');
overlayCells.forEach(function (cell) {
  cell.addEventListener('click', function (event) {
    var activeOverlay = document.querySelector('.overlay.active');
    if (activeOverlay) {
      activeOverlay.classList.remove('active');
    }
  
    var overlay = this.querySelector('.overlay');
    overlay.classList.add('active');
    event.stopPropagation(); // Prevent event bubbling to the table
  
    var loadingOverlay = overlay.querySelector('.loading-overlay');
    loadingOverlay.style.display = 'flex';
  
    var loadingIcon = document.createElement('span');
    loadingIcon.className = 'loading-icon';
    loadingIcon.textContent = 'Loading...';
  
    loadingOverlay.appendChild(loadingIcon);
  
    event.preventDefault();
    var tableData = [];
    var rows = overlay.querySelectorAll('.overlay-content table tbody tr');
    var counter = 0;  // Counter for the number of rows processed
    rows.forEach(function (row) {
      if (counter < 100) {  // Limit the number of rows to 20
        var rowData = [];
        var cells = row.querySelectorAll('td:nth-child(-n+3)');
        cells.forEach(function (cell) {
          rowData.push(cell.textContent);
        });
        tableData.push(rowData);
        counter++;
      }
    });
  
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/convert-to-csv', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        loadingOverlay.style.display = 'none';
        var response = JSON.parse(xhr.responseText);
        var activeOverlay2 = document.querySelector('.overlay.active');
        var responseContainer = activeOverlay2.querySelector('#response-container');
        responseContainer.innerHTML = response.data.replace(/\n/g, '<br>');  // Replace \n with <br> tags
      }
    };
  
    xhr.send(JSON.stringify({ 'tableData': tableData }));
  });
});
  
// Add event listener to close button
var closeButtons = document.querySelectorAll('.close-button');
closeButtons.forEach(function (button) {
  button.addEventListener('click', function (event) {
    event.stopPropagation();
    var overlay = this.closest('.overlay');
    overlay.classList.remove('active');
  });
});
  
// Add event listener to close overlay when clicking outside
document.addEventListener('click', function (event) {
  var overlayContent = document.querySelector('.overlay-content');
  if (overlayContent && !overlayContent.contains(event.target)) {
    var activeOverlay = document.querySelector('.overlay.active');
    if (activeOverlay) {
      activeOverlay.classList.remove('active');
    }
  }
});
  
// Function to sort a column in a table
function sortColumn(index, sortOrder, dateFormat) {
  var table = document.querySelector('table');
  var rows = Array.from(table.rows).slice(1); // Exclude the header row
  rows.sort(function (a, b) {
    var cellA = parseDate(a.cells[index].textContent.trim(), dateFormat);
    var cellB = parseDate(b.cells[index].textContent.trim(), dateFormat);
    if (sortOrder === 'asc') {
      return cellA - cellB;
    } else {
      return cellB - cellA;
    }
  });
  rows.forEach(function (row) {
    table.appendChild(row);
  });
}
  
// Function to convert a date string to a Date object based on the specified format
function parseDate(dateString, format) {
  var parts = dateString.split('/');
  var day = parseInt(parts[0]);
  var month = parseInt(parts[1]);
  var year = parseInt(parts[2]);
  if (format === 'dd/mm/yyyy') {
    return new Date(year, month - 1, day);
  } else {
    return new Date(year, month, day);
  }
}
  
// Sort the latest date's column (last column) in descending order on page load
window.onload = function () {
  var table = document.querySelector('table');
  var lastIndex = table.rows[0].cells.length - 1;
  sortColumn(lastIndex, 'asc', 'dd/mm/yyyy');
};
  
// Add event listeners to each "Investigate" button
var investigateButtons = document.querySelectorAll('.investigate-button');
investigateButtons.forEach(function (button) {
  button.addEventListener('click', function (event) {
    event.stopPropagation(); // Prevent event bubbling
  
    // Get the row data
    var row = this.parentNode.parentNode;
    var issueKey = row.cells[0].textContent;
    var summary = row.cells[1].textContent;
    var timeToFirstResponse = row.cells[2].textContent;
    var rawAlert = row.cells[3].textContent;
  
    // Create the request payload
    var requestData = {
      issueKey: issueKey,
      summary: summary,
      timeToFirstResponse: timeToFirstResponse,
      rawAlert: rawAlert
    };
  
    // Make the POST API call
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/investigate', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        event.stopPropagation();
        var response = JSON.parse(xhr.responseText);
        showInvestigationResult(response);
      }
    };
    xhr.send(JSON.stringify(requestData));
  });
});
  
// Function to show the investigation result in a new overlay
function showInvestigationLoading() {
  var overlay = document.createElement('div');
  overlay.className = 'overlay active';
  
  var overlayContent = document.createElement('div');
  overlayContent.className = 'overlay-content';
  
  var description = document.createElement('p');
  description.innerHTML = 'Loading...'
  overlayContent.appendChild(description);
  
  var closeButton = document.createElement('span');
  closeButton.className = 'close-button';
  closeButton.textContent = 'Close';
  
  closeButton.addEventListener('click', function (event) {
    event.stopPropagation();
    overlay.classList.remove('active');
  });
  
  overlayContent.appendChild(closeButton);
  overlay.appendChild(overlayContent);
  document.body.appendChild(overlay);
}
  
// Function to show the investigation result in a new overlay
function showInvestigationResult(response) {
  var overlay = document.createElement('div');
  overlay.className = 'overlay active';
  
  var overlayContent = document.createElement('div');
  overlayContent.className = 'overlay-content';
  
  var description = document.createElement('p');
  description.innerHTML = 'Description: ' + response.description.replace(/\n/g, '<br>');
  
  var proposedFix = document.createElement('p');
  proposedFix.innerHTML = 'Proposed Fix: ' + response.proposedFix.replace(/\n/g, '<br>');
  
  overlayContent.appendChild(description);
  overlayContent.appendChild(proposedFix);
  
  var closeButton = document.createElement('span');
  closeButton.className = 'close-button';
  closeButton.textContent = 'Close';
  
  closeButton.addEventListener('click', function (event) {
    event.stopPropagation();
    overlay.classList.remove('active');
  });
  
  overlayContent.appendChild(closeButton);
  overlay.appendChild(overlayContent);
  document.body.appendChild(overlay);
}
