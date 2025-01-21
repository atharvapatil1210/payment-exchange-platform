const express = require("express");
const path = require("path");
const axios = require("axios"); // For HTTP requests to FastAPI

const app = express();
const PORT = 3000;

// Middleware to parse JSON
app.use(express.json());

// Serve static files from /public
app.use(express.static(path.join(__dirname, "public")));

// Proxy request to FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000"; // FastAPI server URL

// Endpoint to register a user
app.post("/register", async (req, res) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/register`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data || { error: "Unknown error" });
    }
});

// Endpoint to find a match
app.post("/match", async (req, res) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/match`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data || { error: "Unknown error" });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Frontend running at http://localhost:${PORT}`);
});
