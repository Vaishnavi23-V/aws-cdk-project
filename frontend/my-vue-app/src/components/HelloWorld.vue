<template>
  <div class="hello-world-container">
    <h1>Hello World App</h1>
    <button @click="invokeLambda" class="invoke-button">Invoke Lambda</button>
  </div>
</template>

<script setup lang="ts">
const invokeLambda = async () => {
  const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
  const authToken = import.meta.env.VITE_AUTH_TOKEN;
  try {
    const response = await fetch(apiEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({ message: "Hello from the frontend!" }),
    });

    const data = await response.json();
    console.log("Response from Lambda:", data);
  } catch (error) {
    console.error("Error invoking Lambda:", error);
  }
};
</script>

<style scoped>
.hello-world-container {
  text-align: center;
  color: black;
}

.invoke-button {
  background-color: #28a745;
  color: #fff;
  padding: 10px;
  border: none;
  cursor: pointer;
  margin-top: 20px;
}

.invoke-button:hover {
  background-color: #218838;
}
</style>
