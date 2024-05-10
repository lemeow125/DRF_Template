## DRF-Template

This is a Django batteries-included template I personally use for my projects. This covers the following

- Emails (and templated email designs)
- Celery (For asynchronous tasks)
- Celery Beat (For scheduled tasks)
- Caching (via Redis or optionally, Memcached)
- Performance profiling (via Django Silk)
- Selenium (Optional, for webscraping with support for Chrome and Firefox drivers)
- Stripe Subscriptions (Optional, with regular and pro-rated subscription support)
- Notifications (via traditional RESTful endpoints)

## Development

- Create a copy of the `.env.sample` file and name it as `.env` in the same directory
- Populate .env with values
- Run `docker-compose up`
