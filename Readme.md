# Social Networking Project

This is a Django project that includes functionality for friend requests.

## Installation

Follow these steps to set up and run the Django project:

Clone the repository:
   `git clone https://github.com/harshitjain0701/social_network.git`

Navigate to the project directory:
   `cd social_network`


### Without Docker

1. Create a virtual environment:
   ```shell
   python -m venv venv

2. Activate the virtual environment:
    1. For Windows:
        ```shell
       .\env\Scripts\activate

    2. For macOS and Linux:
        ```shell
       source env/bin/activate


3. Install the project dependencies:
    ```shell
    pip install -r requirements.txt

4. Set up the database:

    1. Update the database settings in the settings.py file according to your database configuration.
    2. Run the database migrations:
        ```shell
        python manage.py migrate

5. Run the development server:
   ```shell
   python manage.py runserver

6. Open your web browser and access the APIs at http://localhost:8000/api/schema/swagger-ui/.

### With Docker
    docker-compose up
Open your web browser and access the APIs at http://localhost/api/schema/swagger-ui/.

## API Endpoints
The following API endpoints are available:

1. Login: POST /login/
    This endpoint is used for user authentication and returns an access token.
2. Sign Up: POST /signup/

    This endpoint is used to create a new user account.
3. Search Users: GET /search/?q=<search_query>

    This endpoint allows you to search for users by their name or email.
    Replace <search_query> with the keyword you want to search for.
4. Send Friend Request: POST /send-friend-request/

    This endpoint is used to send a friend request to another user.
5. Accept Friend Request: POST /accept-friend-request/

    This endpoint is used to accept a friend request received from another user.
6. Reject Friend Request: POST /reject-friend-request/

    This endpoint is used to reject a friend request received from another user.
7. List Friends: GET /friends/

    This endpoint returns a list of users who have accepted your friend requests.
8. List Pending Friend Requests: GET /pending-requests/

    This endpoint returns a list of pending friend requests received by you.


Make sure to replace http://localhost:8000 with the appropriate base URL for your development server.





