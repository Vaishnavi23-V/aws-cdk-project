<template>
  <div class="login-container">
    <h1>User Login</h1>
    <form @submit.prevent="handleLogin" class="login-form">
      <label for="username">Username</label>
      <input v-model="username" type="text" id="username" required />

      <label for="password">Password</label>
      <input v-model="password" type="password" id="password" required />

      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  CognitoUser,
  AuthenticationDetails,
  CognitoUserPool,
} from "amazon-cognito-identity-js";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");

const handleLogin = async () => {
  const authenticationData = {
    Username: username.value,
    Password: password.value,
  };

  const authenticationDetails = new AuthenticationDetails(authenticationData);

  const userData = {
    Username: username.value,
    Pool: new CognitoUserPool({
      UserPoolId: "us-east-1_qnxMFVVGv",
      ClientId: "22c0mmogt0qosl1a63vms1ch0n",
    }),
  };

  const cognitoUser = new CognitoUser(userData);

  cognitoUser.authenticateUser(authenticationDetails, {
    onSuccess: (session) => {
      // If login is successful, redirect to Hello World component
      console.log("Authentication successful:", session);
      router.push({ path: "/HelloWorld" });
    },
    onFailure: (error) => {
      console.error("Authentication failed:", error);
    },
  });
};
</script>

<style scoped>
.login-container {
  text-align: center;
  color: black;
}

.login-form {
  max-width: 300px;
  width: 100%;
  text-align: center;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
}

button {
  background-color: #007bff;
  color: #fff;
  padding: 10px;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
