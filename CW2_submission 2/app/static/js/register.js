document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const registerButton = document.getElementById("register-button");
    const usernameFeedback = document.getElementById("username-feedback");
    const passwordFeedback = document.getElementById("password-feedback");

    // Disable the register button by default
    registerButton.disabled = true;

    // Check username validity
    usernameInput.addEventListener("input", async () => {
        const username = usernameInput.value.trim();
        
        // Clear feedback if username is empty
        if (username.length === 0) {
            usernameFeedback.textContent = "Username cannot be empty.";
            registerButton.disabled = true;
            return;
        }

        // Check if username already exists by making an AJAX call to backend
        try {
            const response = await fetch(`/check_username/${username}`);
            const data = await response.json();

            // If the username exists, display an error message
            if (data.exists) {
                usernameFeedback.textContent = "Username already exists. Please choose another.";
                registerButton.disabled = true;
            } else {
                usernameFeedback.textContent = "";  // Clear feedback if username is available
                checkFormValidity();
            }
        } catch (error) {
            console.error("Error checking username:", error);
            usernameFeedback.textContent = "Error checking username availability. Please try again.";
            registerButton.disabled = true;
        }
    });

    // Validate confirm password
    confirmPasswordInput.addEventListener("input", () => {
        if (passwordInput.value !== confirmPasswordInput.value) {
            passwordFeedback.textContent = "Passwords do not match.";
            registerButton.disabled = true;
        } else {
            passwordFeedback.textContent = "";
            checkFormValidity();
        }
    });

    // Validate password input
    passwordInput.addEventListener("input", () => {
        if (passwordInput.value !== confirmPasswordInput.value) {
            passwordFeedback.textContent = "Passwords do not match.";
            registerButton.disabled = true;
        } else {
            passwordFeedback.textContent = "";
            checkFormValidity();
        }
    });

    // Enable register button if all fields are valid
    function checkFormValidity() {
        if (
            usernameFeedback.textContent === "" &&
            passwordFeedback.textContent === "" &&
            usernameInput.value.trim().length > 0 &&
            passwordInput.value.trim().length > 0
        ) {
            registerButton.disabled = false;
        } else {
            registerButton.disabled = true;
        }
    }
});
