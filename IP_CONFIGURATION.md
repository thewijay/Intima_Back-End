# IP Address Configuration

This document explains how to manage IP addresses and network configuration for the backend server.

## Quick Setup

1. **Copy the example file:**

   ```bash
   cp .env.dev.example .env.dev
   ```

2. **Update the configuration in `.env.dev`:**

   - Add your OpenAI API key
   - Update IP addresses for your network
   - Generate secure keys for Weaviate and Django

3. **See `.env.dev.example` for detailed comments and examples**

## Overview

All IP address configuration is now centralized in the `.env.dev` file. This makes it easy to change network settings without modifying code files.

## Configuration Variables

### `.env.dev` file contains:

```bash
# ALLOWED HOSTS (comma separated)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.8.165,192.168.8.100

# CORS ALLOWED ORIGINS (comma separated, include ports)
CORS_ALLOWED_ORIGINS=http://localhost:8081,http://192.168.8.100:8081,http://192.168.8.165:8081
```

## What Each Setting Controls

### DJANGO_ALLOWED_HOSTS

- Controls which host/domain names Django will serve
- Include your server's IP address for network access
- Always include `localhost` and `127.0.0.1` for local development

### CORS_ALLOWED_ORIGINS

- Controls which frontend origins can make API requests
- Include your development machine's IP with the frontend port (usually :8081)
- Format: `http://IP_ADDRESS:PORT`

## How to Update for Different Networks

### For Local Development Only:

```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8081
```

### For Network/Device Testing:

1. Find your machine's IP address:

   - **Windows**: `ipconfig`
   - **macOS/Linux**: `ifconfig | grep "inet "`

2. Update `.env.dev` with your IP:

```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_IP_ADDRESS
CORS_ALLOWED_ORIGINS=http://localhost:8081,http://YOUR_IP_ADDRESS:8081
```

### For Production:

```bash
DJANGO_ALLOWED_HOSTS=your-domain.com,your-server-ip
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## After Making Changes

1. Restart the Docker containers:

   ```bash
   docker compose --env-file .env.dev down
   docker compose --env-file .env.dev up -d --build
   ```

2. Update the frontend `.env` file to match:
   ```bash
   EXPO_PUBLIC_BASE_URL=http://YOUR_IP_ADDRESS:8000
   ```

## Troubleshooting

### "DisallowedHost" Error

- Add your IP address to `DJANGO_ALLOWED_HOSTS`

### CORS Errors in Frontend

- Add your IP with frontend port to `CORS_ALLOWED_ORIGINS`
- Ensure the protocol (http/https) matches

### Can't Connect from Mobile Device

- Ensure both frontend and backend are configured with your machine's network IP
- Check that ports 8000 (backend) and 8081 (frontend) are accessible on your network
