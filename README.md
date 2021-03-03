# Vaccine Watch
Bot to notify when vaccine appointments are available.

Supports checking Hy-Vee, and sending notifications to Slack and [Twitter](https://twitter.com/kcvaccinewatch).

Notifications are sent when a location has appointments. No more notifications are sent for that location until it becomes unavailable again.

PRs welcome to support other clinics or notification methods.

This project has no affiliation with Hy-Vee.

## Example
Slack

<img src="https://user-images.githubusercontent.com/5343931/109749025-81a4a680-7b9f-11eb-96e6-55c3742bad25.png" alt="Example of messages in Slack" width=500 />

Twitter

<img src="https://user-images.githubusercontent.com/5343931/109749189-c2042480-7b9f-11eb-89f2-2190e4d94585.png" alt="Example of messages in Twitter" width=500 />

## Setup
1. [Install docker](https://docs.docker.com/get-docker/)
2. Run `cp .env.template .env`
3. Fill in the variables in `.env`:
  - `SLACK_BOT_TOKEN`: token for slack integration
  - `SLACK_CHANNEL`: channel to post to (e.g. `#vaccine-watch`)
4. `docker-compose up --build`

## Lint
1. Install [pre-commit](https://pre-commit.com)
1. `pre-commit install`

Lint is run as a pre-commit, or on-demand with `pre-commit run --all-files`

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
