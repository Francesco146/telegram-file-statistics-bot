# Telegram Bot API Server

This subproject sets up a local Telegram Bot API server to support bots using the official [Telegram Bot API](https://core.telegram.org/bots/api). Running a local instance adds support of archives for the main bot.

- [Telegram Bot API Server](#telegram-bot-api-server)
  - [Overview](#overview)
    - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Create a `.env` File](#2-create-a-env-file)
    - [3. Start the Server](#3-start-the-server)
    - [4. Verify the Server](#4-verify-the-server)
  - [Additional Notes](#additional-notes)


## Overview

This setup uses Docker to run the [aiogram/telegram-bot-api](https://hub.docker.com/r/aiogram/telegram-bot-api) image. The server will run locally on port `8081` by default and store its data in a dedicated volume.

### Features

- Enables archives analysis for the main bot
- Dockerized
- Persistent data storage

---

## Prerequisites

- Docker and Docker Compose installed on your system
- A `.env` file in the root project directory containing your configuration (see below)

---

## Setup Instructions

### 1. Clone the repository
Ensure you have the necessary files:

```bash
.
├── docker-compose.yml
├── README.md
└── telegram-bot-api-data
```

### 2. Create a `.env` File
The `.env` file should be placed in the root directory (one level above the `docker-compose.yml`). Add the following variables:

```env
TELEGRAM_API_ID='your-telegram-api-id'
TELEGRAM_API_HASH='your-telegram-api-hash'
```

### 3. Start the Server
Run the following command to start the Telegram Bot API server:

```bash
docker compose up
```

### 4. Verify the Server
Access the local Telegram Bot API server at:

```
http://0.0.0.0:8081
```

---


## Additional Notes
- To update the `telegram-bot-api` image, pull the latest version and restart:
  ```bash
  docker compose pull
  docker compose up
  ```