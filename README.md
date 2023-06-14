# Chirper Backend

Welcome to the backend of Chirper, built with Flask and Jinja. This README will guide you through the setup and usage of the application.

## Installation

To get started with the backend, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies by running: `pip install -r requirements.txt`.
3. Create a virtual environment (venv) for the project (optional but recommended).
4. Activate the virtual environment.

## Starting the Server

To start the backend server, run the following command:

- On a newer Mac: `flask run -p 5001`
- On other computers: `flask run`

This will start the server on the specified port (usually port 5000) and you can access it at `http://localhost:5000`.

## API Endpoints

The backend exposes various API endpoints to interact with the Chirper app. Here are some of the important endpoints:

### Root Route

- '/' (GET): Show homepage:
  - anon users: no messages
  - logged in: 100 most recent messages of followed_users

### Auth and Signup Routes

- '/signup' (GET/POST): Handle user signup. Creates new user and adds to DB. Redirects to home page. If form is not valid, rerender form.
- '/login' (GET/POST): Handle user login and redirect to homepage on success.
- 'logout' (POST): Handle logout of user and redirect to homepage.

### User Routes

- '/users': Page with listing of users.
- '/users/user_id' (GET): Show user profile.
- '/users/user_id/following' (GET): Show list of people this user is following.
- '/users/user_id/followers' (GET): Show list of people that are following this user.
- '/users/follow/follow_id' (GET): Follow a user. Redirect to the following page for the current user.
- '/users/stop-following/follow_id' (POST): Stop following a user. Redirect to the following page for the current user.
- '/users/profile' (GET): Render template for user to edit their profile.
- '/users/profile' (POST): Handle form, check that password is correct, and commit changes to the database.
- '/users/delete' (POST): Delete user. Redirect to signup page.

### Messages Routes

- '/messages/new' (GET/POST): Show form if GET. If valid, update message and redirect to user page.
- '/messages/message_id' (GET): Show a message.
- '/messages/message_id/delete' (POST): Delete a message.

### Liked Chirps Routes

- '/messages/message_id/like' (POST): Adds liked 'chirp' to the LikedChirp table. Redirects user back to the page that they were currently visiting.
- '/messages/message_id/unlike' (POST): Removes likedWarble instance and removes from the likedWarbles table. Redirects user to the page they were previously on
- '/users/user_id/liked_messages' (GET): Displays user profile and a list of the users liked messages.

Please refer to the backend source code or API documentation for more details on available endpoints and their usage.

## Database

The backend uses a PostgreSQL (psql) database to store user accounts, tweets, and other relevant data. Make sure to configure the appropriate database connection settings in the `.env` file.

## Testing

The backend includes test cases to ensure its functionality. To run the tests, use the following command:

```shell
pytest
```

Make sure to set up a separate test database and configure the connection settings in the `.env` file for testing purposes.

## Additional Information

For additional information or assistance, please refer to the backend source code and documentation. Feel free to reach out if you have any questions or need further support.
