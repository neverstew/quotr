Quotr
=====
Organise quotes from the books you love.
----------------------------------------

This little app is born from a frustration of ruining my own books with hundreds of dog-ears just to mark interesting snippets.

It's a work in progress right now.

## Development
### Getting Started 
This is a standard Django app and all the common practices that go with that are recognisable here.

[Read more about Django](https://docs.djangoproject.com/en/2.2/) to get started.

### Requirements
* Python 3
* Docker

To get up and running locally, install the project requirements
```bash
pip install -r requirements.txt
```

You'll need an instance of Postgres to be running in order for application to work. This can be
done easily with Docker.

```bash
docker run --name quotr-postgres -p 5432:5432 -e POSTGRES_USER=django -e POSTGRES_PASSWORD=django postgres
```

## Environment Variables
In order to run the application, some environment variables need to be defined.

```bash
echo "ENV=DEV\nSECRET_KEY=<some_long_string>" > .env
```

## Deployment
The application is deployed on Heroku.

```bash
git push heroku master
```

If there were migrations, these have to be run manually.

```bash
heroku run "./manage.py migrate"
```

Note: this assumes you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed. and configured.
