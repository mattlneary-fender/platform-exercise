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
docker-compose exec db psql --username=fender --dbname=fender_users
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

Responses

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


# Thought process

I decided to use Django/Django Rest Framework partially because I'm most familiar with it, but also because it provides an intuitive token authentication interface and automatically hases passwords. A common criticism of Django is that it's not lightweight which is true. For an API this small Django may have been overkill and I could have had fewer lines of code using Flask/SQLAlchemy or FastAPI, but Django was the quickest way for me to complete the task.

Since the API was going to be hitting a Postgres database, and this was just going to be hosted locally, I thought Docker would be particularly useful. Most of the Dockerfile and docker-compose file is boilerplate code for Django and Postgres so it was really easy to get up and running fast. Hopefully it is for you too!

I only created the User model but the auth tokens are stored in another table that DRF automatically generates. There is a serializer for that model which I used to validate the requests. If the data structures were more complex I would have used another serializer to generate the JSON response, but since they were so small I just wrote them in the return statements of the endpoints. 

The endpoints are organized into two sets of classes, the endpoints for authentication and user manipulation. This allowed me to focus on authentication first and then move onto the UsersView without having to worry about authentication. 

I didn't have a lot of time to think about security outside of the token authentication, but I did use a uuid primary key on User rather than a sequential ID. This is an easy way to gain a little bit of security since an attack/bot will have a much harder time guessing customer_id's

# Improvements

- Django is very strict about CSRF cookies, which I thought would get in the way of testing this project. I ended up removing the Django middleware responsible for enforcing CSRF checks, which would never be a good idea in a production system.

- Originally I had another app called instruments that was going to be a many to one relationship with the User table. I thought it'd be cool to show how the token gave ownership over more objects than just the User, but I ran out of time so I deleted it.

- Login, logout, and register are all separate classes but should be one. Having them separate made it easier to setup the routing, but they're all so logically similar that they should be under one AuthViewSet as separate detailed routes.

- If this was going to eventually be production code I would only accept requests over HTTPS, especially ones that contained a password.
