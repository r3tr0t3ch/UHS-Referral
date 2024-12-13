// Fetch patient suggestions
async function fetchPatientSuggestions(query) {
    if (query.length < 3) {
        document.getElementById("suggestions").style.display = "none";
        return;
    }

    try {
        const response = await fetch(`/api/search-patients?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const patients = await response.json();

        // Display suggestions in the dropdown
        const suggestionsBox = document.getElementById("suggestions");
        suggestionsBox.innerHTML = "";

        patients.forEach((patient) => {
            const suggestionItem = document.createElement("div");
            suggestionItem.className = "suggestion-item";
            suggestionItem.textContent = `${patient.registrationNumber}`;
            suggestionItem.onclick = () => populatePatientInfo(patient);
            suggestionsBox.appendChild(suggestionItem);
        });

        suggestionsBox.style.display = patients.length ? "block" : "none";
    } catch (error) {
        console.error('Error fetching patient suggestions:', error);
        document.getElementById("suggestions").style.display = "none";
    }
}


let debounceTimeout;
document.getElementById("patient-reg-no").addEventListener("input", (e) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        fetchPatientSuggestions(e.target.value);
    }, 300);
});


// Populate form fields
function populatePatientInfo(patient) {
    document.getElementById("patient-reg-no").value = patient.registrationNumber;
    document.getElementById("surname").value = patient.surname;
    document.getElementById("other-names").value = patient.otherNames;
    document.getElementById("dob").value = patient.dateOfBirth;
    document.getElementById("age").value = patient.age;
    document.getElementById("contact-person").value = patient.contactPerson;
    document.getElementById("contact-number").value = patient.contactNumber;

    const sexElement = document.getElementById(patient.sex.toLowerCase());
    if (sexElement) {
        sexElement.checked = true;
    }

    document.getElementById("suggestions").style.display = "none";
}


function calculateAge()
      {
        const dobInput = document.getElementById("dob").value;
        const dob = new Date(dobInput);
        const today = new Date();

        let age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();
        const dayDiff = today.getDate() - dob.getDate();


        if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
            age--;
        }

        if (age < 0 || age > 130) {
            document.getElementById("age").value = "";
        }
        else {
            document.getElementById("age").value = age;
        }
       }
