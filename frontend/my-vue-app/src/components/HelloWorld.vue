<template>
  <div class="hello-world-container">
    <h1>Hello World App</h1>
    
    <button @click="invokeLambda" class="invoke-button" :disabled="loading">
      {{ loading ? "Loading..." : "Invoke Lambda" }}
    </button>

    <!-- Success Response -->
    <div v-if="response && !error" class="response-box success">
      <h3>Response from Lambda:</h3>
      <pre>{{ JSON.stringify(response, null, 2) }}</pre>
    </div>

    <!-- Error Response -->
    <div v-if="error" class="response-box error">
      <h3>Error:</h3>
      <p>{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="response-box loading">
      <p>⏳ Fetching response...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const response = ref<any>(null);
const error = ref<string>("");
const loading = ref<boolean>(false);

const invokeLambda = async () => {
  loading.value = true;
  response.value = null;
  error.value = "";

  const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
  const authToken = import.meta.env.VITE_AUTH_TOKEN;
  
  try {
    const res = await fetch(apiEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({ message: "Hello from the frontend!" }),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    response.value = data;
    console.log("Response from Lambda:", data);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error occurred";
    console.error("Error invoking Lambda:", err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.hello-world-container {
  text-align: center;
  color: black;
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.invoke-button {
  background-color: #28a745;
  color: #fff;
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin: 20px 0;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.invoke-button:hover:not(:disabled) {
  background-color: #218838;
}

.invoke-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.response-box {
  margin-top: 20px;
  padding: 15px;
  border-radius: 5px;
  text-align: left;
  font-family: monospace;
}

.response-box h3 {
  margin-top: 0;
  margin-bottom: 10px;
}

.response-box.success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.response-box.error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.response-box.loading {
  background-color: #e7f3ff;
  border: 1px solid #b3d9ff;
  color: #004085;
}

pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 10px;
  border-radius: 3px;
  overflow-x: auto;
  margin: 0;
}
</style>
