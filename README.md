## DRF-Template

![Build Status](https://woodpecker.06222001.xyz/api/badges/3/status.svg)
![Demo Page Status](https://kuma.keannu5.duckdns.org/api/badge/119/status)

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

A live API demo can be found [here](https://api.template.06222001.xyz/swagger)

### Development

- Create a copy of the `.env.sample` file and name it as `.env` in the same directory
- Populate .env with values
- Run `docker-compose -f docker-compose.dev.yml up`

Be sure to follow through the steps shown in the `stripe-listener` container for initial setup with Stripe!

### URLs

- [Django Admin Panel](http://localhost:8000/admin)
- [OpenAPI Swagger](http://localhost:8000/swagger) (For documenting endpoints)
- [Inbucket](http://localhost:8025) (For email testing)
- [Flower](http://localhost:5555/) (For monitoring Celery tasks)
- [Django Silk](http://localhost:8000/silk) (For performance profiling)
