/* =========================
   COMMON HELPERS
========================= */

function qs(id) {
    return document.getElementById(id);
}

function confirmDelete(msg = "Are you sure?") {
    return confirm(msg);
}

async function apiCall(url, method = "GET", data = null) {
    const options = {
        method: method,
        headers: { "Content-Type": "application/json" }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const res = await fetch(url, options);
        const json = await res.json();
        return json;
    } catch (err) {
        console.error("API Error:", err);
        return { success: false, message: "Network error" };
    }
}

/* =========================
   LOGIN
========================= */

function setupLoginForm() {
    const form = document.querySelector("form[action='/']");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const data = {
                username: qs("username").value,
                password: qs("password").value
            };
            
            const res = await apiCall("/", "POST", data);
            
            if (res.success) {
                window.location.href = res.redirect || "/admin";
            } else {
                alert(res.message || "Login failed");
            }
        });
    }
}

/* =========================
   SUBJECT MANAGEMENT
========================= */

function setupSubjectForm() {
    // Forms in admin dashboard use standard HTML form submission
    // No need for AJAX interception - let forms submit normally
}

function editSubject(id) {
    const name = prompt("Enter new subject name");
    if (!name) return;
    const hours = prompt("Enter weekly hours");
    if (!hours) return;
    
    apiCall(`/edit_subject/${id}`, "POST", { 
        name: name, 
        weekly_hours: hours 
    }).then(res => {
        if (res.success) {
            alert("Subject updated!");
            location.reload();
        } else {
            alert(res.message || "Failed to update");
        }
    });
}

function deleteSubject(id) {
    if (!confirmDelete("Delete this subject?")) return;
    
    apiCall(`/delete_subject/${id}`, "POST").then(res => {
        if (res.success) {
            alert("Subject deleted!");
            location.reload();
        } else {
            alert(res.message || "Failed to delete");
        }
    });
}

/* =========================
   FACULTY MANAGEMENT
========================= */

function setupFacultyForm() {
    // Forms in admin dashboard use standard HTML form submission
    // No need for AJAX interception - let forms submit normally
}

function editFaculty(id) {
    const name = prompt("Enter new faculty name");
    if (!name) return;
    const max_hours = prompt("Enter max hours");
    if (!max_hours) return;
    
    apiCall(`/edit_faculty/${id}`, "POST", { 
        name: name, 
        max_hours: max_hours 
    }).then(res => {
        if (res.success) {
            alert("Faculty updated!");
            location.reload();
        } else {
            alert(res.message || "Failed to update");
        }
    });
}

function deleteFaculty(id) {
    if (!confirmDelete("Delete this faculty?")) return;
    
    apiCall(`/delete_faculty/${id}`, "POST").then(res => {
        if (res.success) {
            alert("Faculty deleted!");
            location.reload();
        } else {
            alert(res.message || "Failed to delete");
        }
    });
}

/* =========================
   TIMETABLE GENERATION
========================= */

function setupGenerateForm() {
    // Forms in admin dashboard use standard HTML form submission
    // No need for AJAX interception - let forms submit normally
}

/* =========================
   AUTO INIT
========================= */

document.addEventListener("DOMContentLoaded", () => {
    setupLoginForm();
    setupSubjectForm();
    setupFacultyForm();
    setupGenerateForm();
});