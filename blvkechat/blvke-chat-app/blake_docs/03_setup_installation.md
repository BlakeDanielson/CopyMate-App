# 3. Setup and Installation Guide

This guide provides step-by-step instructions for setting up the `blvke-chat-app` project for local development.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Node.js:** (Specify recommended version, e.g., v18 or later) - Download from [nodejs.org](https://nodejs.org/)
*   **npm** or **yarn:** Comes bundled with Node.js.
*   **Docker** or **Podman:** Required for running the local development database.
    *   Docker Desktop: [https://docs.docker.com/desktop/](https://docs.docker.com/desktop/)
    *   Podman Desktop: [https://podman-desktop.io/](https://podman-desktop.io/)
*   **Git:** For cloning the repository.

## Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual Git repo URL
    cd blvke-chat-app
    ```

2.  **Install Dependencies:**
    Install the required Node.js packages using npm:
    ```bash
    npm install
    ```
    This command also triggers `prisma generate` automatically due to the `postinstall` script in `package.json`, generating the Prisma Client based on your schema.

3.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   **Edit the `.env` file:** Open the newly created `.env` file and fill in the required values. Pay close attention to:
        *   `DATABASE_URL`: This connection string is used by both Prisma and the `start-database.sh` script. The script can automatically generate a password if you leave the default `password`.
        *   `NEXTAUTH_SECRET`: Generate a strong secret key. You can use `openssl rand -base64 32` to generate one.
        *   `NEXTAUTH_URL`: Set this to `http://localhost:3000` for local development.
        *   (Add any other provider keys like `GITHUB_CLIENT_ID`, `GOOGLE_CLIENT_ID`, etc., if you plan to use those OAuth providers).
        *   `OPENAI_API_KEY`: Required if using the OpenAI integration via the AI SDK.
    *   **Important:** The `.env` file contains sensitive credentials and should **never** be committed to version control. It is already listed in the `.gitignore` file.

4.  **Set Up the Development Database:**
    *   Ensure Docker or Podman daemon is running.
    *   Run the database startup script. This script reads the `DATABASE_URL` from your `.env` file to configure and start a PostgreSQL container.
        ```bash
        chmod +x ./start-database.sh # Ensure the script is executable
        ./start-database.sh
        ```
    *   The script will prompt you if you're using the default password and can generate a secure one for you, updating the `.env` file accordingly.

5.  **Apply Database Migrations:**
    Apply the database schema defined in `prisma/schema.prisma` to your newly created database:
    ```bash
    npx prisma migrate dev
    ```
    This command will create the necessary tables and relations. You might be prompted to name the migration.

## Running the Application

1.  **Start the Development Server:**
    ```bash
    npm run dev
    ```
    This command starts the Next.js development server, typically available at `http://localhost:3000`. The application will automatically reload when you make changes to the code.

2.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:3000`.

## Other Useful Commands

*   **Build for Production:**
    ```bash
    npm run build
    ```
    This compiles the application for production deployment.

*   **Run Production Build:**
    ```bash
    npm run start
    ```
    This starts the application using the production build. Requires `npm run build` to be run first.

*   **Linting:**
    ```bash
    npm run lint
    ```
    This checks the code for linting errors based on the configuration in `eslint.config.js`.