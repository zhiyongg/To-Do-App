# To-Do-App
This app allows users to log in via Google, GitHub, or Facebook. Users can add, update, and delete their tasks in the app.

## 1.1. Instruction for running the app

To run the application using Docker Compose, follow these steps:

1.  **Prerequisites:**
    * Docker installed on your system.
    * Docker Compose installed on your system.

2.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-github-username/your-repository-name.git](https://github.com/your-github-username/your-repository-name.git)
    cd your-repository-name
    ```

3.  **Important Configuration:**
    * You **MUST** set the following environment variables in your `docker-compose.yml` (or directly in your system if not using Docker) for the application to function correctly.  These are sensitive credentials, so handle them securely!
        * `SECRET_KEY`:  A secret key for Flask sessions (e.g., generate a random string).
        * `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID.
        * `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret.
        * `GITHUB_CLIENT_ID`: Your GitHub OAuth Client ID.
        * `GITHUB_CLIENT_SECRET`: Your GitHub OAuth Client Secret.
        * `FACEBOOK_CLIENT_ID`: Your Facebook App ID.
        * `FACEBOOK_CLIENT_SECRET`: Your Facebook App Secret.

    * **Example `docker-compose.yml` (adjust with your credentials):**
        ```yaml
        version: '3.8'
        services:
          web:
            build: .
            ports:
              - "80:5000"
            environment:
              - SECRET_KEY=your-super-secret-key
              - GOOGLE_CLIENT_ID=your-google-client-id
              - GOOGLE_CLIENT_SECRET=your-google-client-secret
              - GITHUB_CLIENT_ID=your-github-client-id
              - GITHUB_CLIENT_SECRET=your-github-client-secret
              - FACEBOOK_CLIENT_ID=your-facebook-app-id
              - FACEBOOK_CLIENT_SECRET=your-facebook-app-secret
            volumes:
              - ./app:/app
            depends_on:
              - db
          db:
            image: postgres:13
            environment:
              - POSTGRES_USER=postgres
              - POSTGRES_PASSWORD=postgres
              - POSTGRES_DB=app_db
            volumes:
              - db_data:/var/lib/postgresql/data/
        volumes:
          db_data:
        ```

4.  **Start the Application:**
    ```bash
    docker compose up -d --build
    ```
    This command will build the Docker image (if necessary) and start the Flask application and the database.

5.  **Access the Application:**
    * The web application will be accessible at `http://<host>:<port>/` (e.g., `http://localhost:80/`).
    * The to-do API will be accessible at `http://<host>:<port>/api/items/`\

## 1.2. Instruction for testing the app

* GET http://localhost:5000/api/items
Accept: application/json

* POST http://localhost:5000/api/items
Content-Type: application/json
{
    "title":"Reading"
}


* PATCH http://localhost:5000/api/items/3
Content-Type: application/json
{
    "title":"Homework",
    "completed": true
}

* DELETE http://localhost:5000/api/items/3
Content-Type: application/json
{"title": "irrelevant_value"}

## 1.3. Instruction for building the app
The application is built using Docker.  You no need to build it manually unless you want to create the image separately.

1.  **Navigate to the project root directory:**
    ```bash
    cd your-repository-name
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t your-dockerhub-username/your-image-name:<tag> .
    ```
    (Replace with your Docker Hub details if pushing to a registry is needed; otherwise, you can use a local name.)

## 1.4. Interface documentation
* **`GET /`:** The main page with login options.
* **`GET /login/google`:** Redirects to Google's OAuth login page.
* **`GET /login/google/authorize`:** Google's OAuth callback route; handles user login.
* **`GET /login/github`:** Redirects to GitHub's OAuth login page.
* **`GET /login/github/authorize`:** GitHub's OAuth callback route; handles user login.
* **`GET /login/facebook`:** Redirects to Facebook's OAuth login page.
* **`GET /login/facebook/authorize`:** Facebook's OAuth callback route; handles user login.
* **`GET /todo`:** The to-do application page (accessible after successful login).
