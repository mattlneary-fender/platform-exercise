# Setup

## Install Docker

First download Docker if you don't already have it installed from https://docs.docker.com/get-docker/

Start up docker and navigate to the `/app/` directory.

## Create a virtualenv

Create a virtualenv using python 3 by running
```python -m venv virtualenv```

Then start it with
```source /virtualenv/bin/activate```

## Create the Docker containers

Now that you're in the virtualenv and still in the `/app/` directory you have to create the containers and migrate the database.

```
docker-compose up -d --build
docker-compose exec api python manage.py migrate
```

You can verify that the api container is running correctly by running unit tests

```
docker-compose exec api python manage.py test
```

You can also verify that the database tables were created correctly

```
docker-compose exec postgres psql --username=fender --dbname=fender_users
$> \c fender_users
$> \dt
```

`\dt` will list all relations in the database, so hopefully you see a few different Django models and the `User` table.


# Interacting with the API

Now that the containers are up and running you can hit the API at http://localhost:8000`/127.0.0.1:8000` 

You'll first need to create yourself a User object using the /register endpoint. *Note:* All endpoints are expecting a JSON body.

## /register

Postman
```
POST - http://localhost:8000/register/
{
  "name": "Matt",
  "email": "myemail@gmail.com",
  "password": "example_password"
}

```
CURL
```curl --location --request POST 'http://localhost:8000/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Matt"
    "email": "myemail@gmail.com",
    "password": "example_password",
}' 
```
Responses
```
201 Created 
{
  "token": <auth_token_hash>,
  "user_id": <django_user_uuid>,
  "email": "myemail@gmail.com"
}
```

400 Bad Request - If you try to register an email that's already in use, or fields are missing

## /login

If you already created a User but no longer have an auth token use this endpoint to get another one

Postman
```
POST - http://localhost:8000/login/
{
  "name": "Matt",
  "email": "myemail@gmail.com",
  "password": "example_password"
}

```
CURL
```curl --location --request POST 'http://localhost:8000/login/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Matt"
    "email": "myemail@gmail.com",
    "password": "example_password",
}' 
```
Responses
```
200 OK 
{
  "token": <auth_token_hash>,
  "user_id": <django_user_uuid>,
  "email": "myemail@gmail.com"
}
```

400 Bad Request - If any fields are missing

403 Forbidden - If the email and password don't match, or doesn't exist

## /logout

Postman

```
GET 'http://localhost:8000/logout/'
Header - 'Authorization: Bearer <token_hash>'
```

CURL
```
curl --location --request GET 'http://localhost:8000/logout/' \
--header 'Authorization: Bearer <token_hash>'
```

Reponses

204 No Content

401 Unauthorized - Default response for a request that doesn't include a token

## /users/

### GET

Postman

```
GET 'http://localhost:8000/users/'
Header - 'Authorization: Bearer <token_hash>'
```

CURL
```
curl --location --request GET 'http://localhost:8000/users/' \
--header 'Authorization: Bearer <token_hash>'
```

Responses
```
200 OK 
{
  "user_id": <django_user_uuid>,
  "email": "myemail@gmail.com,
  "name": "Matt"
}
```

401 Unauthorized - Default response for a request that doesn't include a token

### PUT

Postman 
```
PUT - http://localhost:8000/users/
{
  "name": "Matt",
  "email": "myemail@gmail.com",
  "password": "example_password"
}
```

CURL
```curl --location --request POST 'http://localhost:8000/users/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Matt"
    "email": "myemail@gmail.com",
    "password": "example_password",
}' 
```

Reponses

```
200 OK 
{
  "user_id": <django_user_uuid>,
  "email": "myemail@gmail.com,
  "name": "Matt",
  "password_changed": <boolean>
}
```

400 Bad Request - If the user tries to change their email address to another one that's already in the database, or fields are missing
401 Unauthorized - Default response for a request that doesn't include a token

### DELETE

Postman
```
DELETE 'http://localhost:8000/users/'
Header - 'Authorization: Bearer <token_hash>'
```

CURL
```
curl --location --request DELETE 'http://localhost:8000/logout/' \
--header 'Authorization: Bearer <token_hash>'
```

Responses

204 No Content

401 Unauthorized - Default response for a request that doesn't include a token


# Fender Digital Platform Engineering Challenge

## Description

Design and implement a RESTful web service to facilitate a user authentication system. The authentication mechanism should be *token based*. Requests and responses should be in **JSON**.

## Requirements

**Models**

The **User** model should have the following properties (at minimum):

1. name
2. email
3. password

You should determine what, *if any*, additional models you will need.

**Endpoints**

All of these endpoints should be written from a user's perspective.

1. **User** Registration
2. Login (*token based*) - should return a token, given *valid* credentials
3. Logout - logs a user out
4. Update a **User**'s Information
5. Delete a **User**

**README**

Please include:
- a readme file that explains your thinking
- how to setup and run the project
- if you chose to use a database, include instructions on how to set that up
- if you have tests, include instructions on how to run them
- a description of what enhancements you might make if you had more time.

**Additional Info**

- We expect this project to take a few hours to complete
- You can use Rails/Sinatra, Python, Go, node.js or shiny-new-framework X, as long as you tell us why you chose it and how it was a good fit for the challenge. 
- Feel free to use whichever database you'd like; we suggest Postgres. 
- Bonus points for security, specs, etc. 
- Do as little or as much as you like.

Please fork this repo and commit your code into that fork.  Show your work and process through those commits.

