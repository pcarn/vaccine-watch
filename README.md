# Vaccine Watch
Bot to notify when vaccine appointments are available.

Support checking Hy-Vee, and notifying to slack.

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

## Deployment Instructions
