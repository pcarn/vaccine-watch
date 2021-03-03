# Vaccine Watch
Bot to notify when vaccine appointments are available.

Supports checking Hy-Vee, and sending notifications to slack.

Notifications are sent when a location has appointments. No more notifications are sent for that location until it becomes unavailable again.

PRs welcome to support other clinics or notification methods.

This project has no affiliation with Hy-Vee.

## Setup
1. [Install docker](https://docs.docker.com/get-docker/)
1. Run `cp .env.template .env`
1. Fill in the variables in `.env`:
  - `SLACK_BOT_TOKEN`: token for slack integration
  - `SLACK_CHANNEL`: channel to post to (e.g. `#vaccine-watch`)
1. `docker-compose up --build`

## Lint
1. Install [pre-commit](https://pre-commit.com)
1. `pre-commit install`

Lint is run as a pre-commit, or on-demand with `pre-commit run --all-files`

## Example
```
:large_green_circle: <!channel> Vaccines available at these clinics:
• MO: Hy-Vee Kansas City #2. Sign up here, zip code 64118
• KS: Hy-Vee Mission. Sign up here, zip code 66202
```

```
:red_circle: Vaccines no longer available at these clinics:
• MO: Hy-Vee Kansas City #2
• KS: Hy-Vee Mission
```

## Deployment Instructions
You can build a docker container, or push the source to heroku.

Required Environment Variables:
- `REDIS_URL`: A redis service
- `VACCINE_CHECK_INTERVAL`: How often (in seconds) to check

Optional Environment Variables:
- Hy-Vee:
  - `ENABLE_HYVEE`: If you want to check Hy-Vee pharmacies
  - `HYVEE_RADIUS`: Within how many miles to check Hy-Vee pharmacies
  - `HYVEE_LATITUDE`: Latitude of the location to check (e.g. 39.1040382)
  - `HYVEE_LONGITUDE`: Latitude of the location to check (e.g. -94.5701803)
- Slack:
  - `SLACK_BOT_TOKEN`: Token for your slack integration
  - `SLACK_TAG_CHANNEL`: If the channel should be tagged when appointments are available
  - `SLACK_CHANNEL`: Channel for the bot to post in (e.g. `#vaccine-watch`)
- Twitter:
  - `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN_KEY`, `TWITTER_ACCESS_TOKEN_SECRET`
