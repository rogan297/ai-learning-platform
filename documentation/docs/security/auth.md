---
sidebar_position: 1
sidebar_label: Auth
---
# Authentication and Configuration Guide

## Overview
The authentication service is managed by **Keycloak**, which ensures the validity of **JWT token** authentication. 

By default, the **AgentGateway** has a specific audience policy defined. This policy is also managed by the Keycloak service during the token creation process.

## Setup Instructions
To ensure proper integration and allow agents to perform queries through the AgentGateway, please follow the steps outlined in the [**Installation Guide**](http://localhost:3000/docs/introduction/Installing#prerequisites) and the **Video Tutorial**. These resources provide detailed instructions on how to configure:

* **Realm:** Your dedicated management space.
* **User:** The identity credentials.
* **Client-ID:** The unique identifier for your application.
* **Audience:** The specific claim required by the AgentGateway for secure access.

:::info  
 Proper configuration of the audience is mandatory for agents to successfully communicate with the gateway.
:::
