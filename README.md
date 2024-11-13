## DRF-Template

![Build Status](https://woodpecker.06222001.xyz/api/badges/2/status.svg)
![Demo Page Status](https://stats.06222001.xyz/api/badge/119/status)

This is a Django template that I personally use for my projects. This covers the following

- Emails (and templated email designs)
- Celery (For asynchronous tasks)
- Celery Beat (For scheduled tasks)
- Caching (via Redis)
- Performance profiling (via Django Silk)
- Selenium (Optional, for webscraping with support for Chrome and Firefox drivers)
- Stripe Subscriptions (Optional, with regular and pro-rated subscription support)
- Notifications (via traditional RESTful endpoints)
- A working Woodpecker CI/CD template for automated deployments

A live API demo can be found [here](https://api.template.06222001.xyz/api/v1/swagger)

### Development

- Create a copy of the `.env.sample` file and name it as `.env` in the same directory
- Populate .env with values
- Run `docker-compose -f docker-compose.dev.yml up`

When using `docker-compose.dev.yml`, the entire project directory is mounted onto the container allowing for hot-reloading. This requires `DEBUG` to be set to `True`.

Also make sure to follow through the steps shown in the `stripe-listener` container for initial setup with Stripe.

### Deployment

A sample `docker-compose.yml` is provided which I use in hosting the demo. `DEBUG` should be set to `False` when deploying as to not expose the URLs fro Celery Flower and the Django Silk Profiler. The local Inbucket container is not present with `DEBUG` turned off so make sure to specify an external SMTP server to process emails properly.

### URLs

- [Django Admin Panel](http://localhost:8000/api/v1/admin)
- [OpenAPI Swagger](http://localhost:8000/api/v1/swagger) (For documenting endpoints)
- [Inbucket](http://localhost:8025) (For email testing)
- [Flower](http://localhost:5555/) (For monitoring Celery tasks)
- [Django Silk](http://localhost:8000/api/v1/silk) (For performance profiling)
