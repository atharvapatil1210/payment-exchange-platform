const apiBaseUrl = "http://127.0.0.1:8000";

// Utility to update the response div
const updateResponse = (message, success = true) => {
    const responseDiv = document.getElementById("response");
    responseDiv.style.color = success ? "green" : "red";
    responseDiv.innerText = message;
};

// Register User
document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const amount = document.getElementById("amount").value;
    const type = document.getElementById("type").value;
    const contact = document.getElementById("contact").value;

    const data = { name, amount: parseFloat(amount), type, contact_info: { phone: contact } };

    try {
        const response = await fetch(`${apiBaseUrl}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const result = await response.json();
        updateResponse(result.message, response.ok);
    } catch (error) {
        updateResponse("Failed to register user", false);
    }
});

// Find Match
document.getElementById("matchForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const userId = document.getElementById("userIdMatch").value;

    try {
        const response = await fetch(`${apiBaseUrl}/match`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId }),
        });
        const result = await response.json();
        updateResponse(JSON.stringify(result, null, 2), response.ok);
    } catch (error) {
        updateResponse("Failed to find match", false);
    }
});

// Complete Transaction
document.getElementById("completeTransactionForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const transactionId = document.getElementById("transactionId").value;

    try {
        const response = await fetch(`${apiBaseUrl}/complete_transaction`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: transactionId }),
        });
        const result = await response.json();
        updateResponse(result.message, response.ok);
    } catch (error) {
        updateResponse("Failed to complete transaction", false);
    }
});

// View Messages
document.getElementById("viewMessagesForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const transactionId = document.getElementById("transactionIdMessages").value;

    try {
        const response = await fetch(`${apiBaseUrl}/get_messages/${transactionId}`);
        const result = await response.json();
        updateResponse(JSON.stringify(result.messages, null, 2), response.ok);
    } catch (error) {
        updateResponse("Failed to fetch messages", false);
    }
});
