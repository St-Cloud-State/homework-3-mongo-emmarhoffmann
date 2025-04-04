// Array to store the application data
const applications = [];

// Function to submit the application and send it to the server
function submitApplication() {
    const name = document.getElementById('name').value;
    const zipcode = document.getElementById('zipcode').value;

    // Create a JSON object with the application data
    const applicationData = {
        name: name,
        zipcode: zipcode
    };

    // Send the application data to the server via POST request
    fetch('/api/submit-application', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(applicationData)
    })
        .then(response => response.json())
        .then(data => {
            alert(`Application submitted successfully!\nApplication Number: ${data.application_number}`);

            applicationData.number = data.application_number;

            applications.push(applicationData);
            
            displayApplications();
        })
        .catch(error => {
            alert('Error submitting application. Please try again.');
            console.error('Error submitting the application:', error);
        });


}

// Function to display applications in the list
function displayApplications() {
    const applicationList = document.getElementById('applicationList');
    applicationList.innerHTML = ''; // Clear existing list

    applications.forEach(application => { 
        const applicationElement = document.createElement('div');
        applicationElement.innerHTML = `
            <h2>Added Successfully</h2>
                <p>Name: ${application.name} </p>
                <p>Zipcode: ${application.zipcode} </p>
                <p>Application Number: ${application.number} </p>
        `;
        applicationList.appendChild(applicationElement);
    });
}


// Function for checking the status of application
function checkStatus() {
    const number = document.getElementById('applicationNumber').value;

    // Send status check to server
    fetch('/api/check-status?number=' + number) 
        .then(response => response.json())
        .then(data => {
            const status = document.getElementById('applicationStatus');
            status.innerHTML = `<h2>Status: ${data.status}</h2>`;

            // Display a success message or handle errors if needed
            console.log(data.status);    
        })

        .catch(error => {
            console.error('Error checking the application status:', error);
        });
}


// Function for updating the status of application
function updateStatus() {
    const number = document.getElementById('updateNumber').value;
    const status = document.getElementById('newStatus').value;
    const reason = document.getElementById('statusReason').value;

    // Send update request to server
    fetch('/api/update-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            number: number,
            status: status,
            reason: reason
        })
    })

        .then(response => response.json())
        .then(data => {
            alert(`Application #${number} updated to "${status}"` + (reason ? `\nReason: ${reason}` : ''));
    
            const result = document.getElementById('updateResult');
           
            result.innerHTML = `<h2>Status Successfully Updated</h2><p>New status: ${status}</p>`;
        })
        .catch(error => {
            alert('Error updating the application. Please try again.');
            console.error('Error updating the application status:', error);
        });        
}

// Function to add a note to an application
function addNote() {
    const number = document.getElementById('noteNumber').value;
    const phase = document.getElementById('notePhase').value;
    const task = document.getElementById('noteTask').value;
    const noteType = document.getElementById('noteType').value;
    const message = document.getElementById('noteMessage').value;

    // Create note data
    const noteData = {
        number: number,
        phase: phase,
        task: task,
        message: (noteType === 'bottleneck' ? 'BOTTLENECK: ' : '') + message
    };

    // Send note to server
    fetch('/api/add-note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(noteData)
    })
        .then(response => response.json())
        .then(data => {
            alert('Note added successfully');
            document.getElementById('noteMessage').value = '';
        })
        .catch(error => {
            console.error('Error adding note:', error);
        });
}

// Function to view application details and notess
function viewApplicationNotes() {
    const number = document.getElementById('viewNumber').value;
    
    fetch('/api/get-notes?number=' + number) 
        .then(response => response.json())
        .then(data => {
            const detailsDiv = document.getElementById('applicationDetails');

        if (data.error) {
            detailsDiv.innerHTML = `<h3>${data.error}</h3>`;
            return;
        }

        //Show application detials
        let html = `
        <h3>Application Details</h3>
        <p>Application Number: ${data.application_number}</p>
        <p>Name: ${data.name}</p>
        <p>Zipcode: ${data.zipcode}</p>
        <p>Status: ${data.status}</p>
        <p>Notes:</p>
        
        `;

        data.notes.forEach(note => {
            html += `<div>${note.phase} - ${note.message}</div>`;
        });

        detailsDiv.innerHTML = html;
    })
    .catch(error => {
        console.error('Error retrieving application details:', error);
    });    

}
