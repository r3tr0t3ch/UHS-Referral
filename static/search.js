let debounceTimeout;
let selectedRegNo = null;

// Event listener for registration number input
document.getElementById('reg-search').addEventListener('input', (e) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        fetchRegistrationSuggestions(e.target.value);
    }, 300);
});

// Handle registration number search form submission
function handleRegSearch(event) {
    event.preventDefault();
    const regNo = selectedRegNo || document.getElementById('reg-search').value;
    if (regNo) {
        searchByRegistration(regNo);
    }
}

// Handle date search form submission
function handleDateSearch(event) {
    event.preventDefault();
    const date = document.getElementById('date-search').value;
    if (date) {
        searchByDate(date);
    }
}

// Fetch registration number suggestions
async function fetchRegistrationSuggestions(query) {
    if (query.length < 3) {
        document.getElementById('reg-suggestions').style.display = 'none';
        selectedRegNo = null;
        return;
    }

    try {
        const response = await fetch(`/api/search-clients?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const patients = await response.json();

        const suggestionsBox = document.getElementById('reg-suggestions');
        suggestionsBox.innerHTML = '';

        patients.forEach(patient => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = `${patient.registrationNumber}`;
            item.onclick = () => {
                document.getElementById('reg-search').value = patient.registrationNumber;
                selectedRegNo = patient.registrationNumber;
                suggestionsBox.style.display = 'none';
            };
            suggestionsBox.appendChild(item);
        });

        suggestionsBox.style.display = patients.length ? 'block' : 'none';
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        document.getElementById('reg-suggestions').style.display = 'none';
    }
}

// Search by registration number
async function searchByRegistration(regNo) {
    try {
        console.log(`Searching for referrals with EXACT registration number: "${regNo}"`);
        const response = await fetch(`/api/search-referrals/registration/${encodeURIComponent(regNo)}`);

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response text:', errorText);
            throw new Error('Network response was not ok');
        }

        const referrals = await response.json();
        console.log('Referrals received:', referrals);

        displayResults(referrals);
    } catch (error) {
        console.error('Error searching by registration:', error);
        alert('Error searching for referrals. Please try again.');
    }
}

// Search by date
async function searchByDate(date) {
    try {
        const response = await fetch(`/api/search-referrals/date/${encodeURIComponent(date)}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const referrals = await response.json();
        displayResults(referrals);
    } catch (error) {
        console.error('Error searching by date:', error);
        alert('Error searching for referrals. Please try again.');
    }
}

// Display results in table
function displayResults(referrals) {
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';

    if (referrals.length === 0) {
        document.getElementById('results-table').style.display = 'none';
        alert('No referrals found for your search criteria.');
        return;
    }

    referrals.forEach(referral => {
        const row = tbody.insertRow();
        row.onclick = () => showReferralDetails(referral.id);

        row.insertCell(0).textContent = new Date(referral.referral_date).toLocaleDateString();
        row.insertCell(1).textContent = referral.patient_referred.patient_no;
        row.insertCell(2).textContent = `${referral.patient_referred.last_name} ${referral.patient_referred.other_names}`;
        row.insertCell(3).textContent = referral.diagnosis;
        row.insertCell(4).textContent = referral.referral_comment;
    });

    document.getElementById('results-table').style.display = 'table';
}

// Show referral details in modal
async function showReferralDetails(referralId) {
    try {
        const response = await fetch(`/api/referral/${referralId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const referral = await response.json();

        const detailContent = document.getElementById('detail-content');
        detailContent.innerHTML = `
            <div class="referral-details-grid">
                <h4>Patient Information</h4>
                <p>Registration Number: ${referral.patient_referred.patient_no}</p>
                <p>Name: ${referral.patient_referred.last_name} ${referral.patient_referred.other_names}</p>
                <p>Sex: ${referral.patient_referred.sex}</p>
                <p>Age: ${referral.patient_referred.age}</p>

                <h4>Referral Information</h4>
                <p>Referral Number: ${referral.referral_no}</p>
                <p>Date: ${new Date(referral.referral_date).toLocaleDateString()}</p>
                <p>Time: ${referral.referral_time}</p>
                <p>Departure Time: ${referral.departure_time || 'N/A'}</p>

                <h4>Vital Signs</h4>
                <p>Temperature: ${referral.temperature}°C</p>
                <p>Pulse: ${referral.pulse}</p>
                <p>BP: ${referral.bp_sys}/${referral.bp_dias}</p>
                <p>RR: ${referral.resp_rate || 'N/A'}</p>
                <p>Weight: ${referral.weight ? referral.weight + 'kg' : 'N/A'}</p>
                <p>TEWS: ${referral.tews}</p>

                <h4>Clinical Information</h4>
                <p>Diagnosis: ${referral.diagnosis}</p>
                <p>Referral Comment: ${referral.referral_comment}</p>

                <h4>Referring Officer</h4>
                <p>Name: ${referral.mo.name}</p>
            </div>
        `;

        document.getElementById('referral-details').style.display = 'block';
    } catch (error) {
        console.error('Error fetching referral details:', error);
        alert('Error loading referral details. Please try again.');
    }
}

// Close modal when clicking the close button or outside the modal
document.querySelector('.close').onclick = () => {
    document.getElementById('referral-details').style.display = 'none';
};

window.onclick = (event) => {
    const modal = document.getElementById('referral-details');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// Close suggestions when clicking outside
document.addEventListener('click', (event) => {
    const suggestionsBox = document.getElementById('reg-suggestions');
    const searchInput = document.getElementById('reg-search');

    if (!searchInput.contains(event.target) && !suggestionsBox.contains(event.target)) {
        suggestionsBox.style.display = 'none';
    }
});