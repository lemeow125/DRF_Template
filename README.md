## DRF-Template

![Build Status](https://woodpecker.06222001.xyz/api/badges/3/status.svg)

This is a Django template that I personally use for my projects. This covers the following

- Emails (and templated email designs)
- Celery (For asynchronous tasks)
- Celery Beat (For scheduled tasks)
- Caching (via Redis)
- Performance profiling (via Django Silk)
- Selenium (Optional, for webscraping with support for Chrome and Firefox drivers)
- Stripe Subscriptions (Optional, with regular and pro-rated subscription support)
- Notifications (via traditional RESTful endpoints)

## Development

- Create a copy of the `.env.sample` file and name it as `.env` in the same directory
- Populate .env with values
- Run `docker-compose up`

Be sure to follow through the steps shown in the `stripe-listener` container for initial setup with Stripe!

## URLs

- [Django Admin](http://localhost:8000/admin)
- [OpenAPI Swagger](http://localhost:8000/swagger) (For testing endpoints)
- [Inbucket](http://localhost:8025) (For email testing)
- [Flower](http://localhost:5555/) (For task monitoring)
- [Django Silk](http://localhost:8000/silk) (For performance profiling)
