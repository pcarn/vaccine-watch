# Vaccine Watch
Bot to notify when vaccine appointments are available.

Supports checking Hy-Vee, Walgreens, CVS, Walmart, Cosentino's stores (KC), and Ball's stores (KC).
Supports sending notifications to Slack, Discord, and [Twitter](https://twitter.com/kcvaccinewatch).

Notifications are sent when a location has appointments. No more notifications are sent for that location until it becomes unavailable again.

PRs welcome to support other clinics or notification methods.

This project has no affiliation with any of the clinics mentioned.

Walmart and Walgreens data courtesy of [covid-vaccine-spotter](https://github.com/GUI/covid-vaccine-spotter).

## Example
Slack

<img src="https://user-images.githubusercontent.com/5343931/109823900-f4446f00-7bfd-11eb-8661-68167f013cf2.png" alt="Example of messages in Slack" width=500 />

Twitter

<img src="https://user-images.githubusercontent.com/5343931/109823499-9b74d680-7bfd-11eb-88f4-45743d824e57.png" alt="Example of messages in Twitter" width=500 />

## Setup
1. [Install docker](https://docs.docker.com/get-docker/)
1. Run `cp .env.template .env`
1. Fill in the variables in `.env`
1. `docker-compose up --build`

### Slack
1. While logged into your slack account, go to https://api.slack.com/apps/
1. Click `Create New App`
1. Choose a name and workspace
1. Click `Permissions`, and `Add an OAuth Scope`
1. Add `chat:write:public` and `chat:write`
1. At the top, click `Install to Workspace`
1. Copy your OAuth Token to use as `SLACK_BOT_TOKEN`

### Discord
1. Click the cog on the channel you want to add the notifications to and select `Edit Channel`
1. Select the `Integrations` tab and click `Create Webhook`
1. Enter a `Name` and `Channel` you want the webhook to notify and copy the Webhook URL.

### Twitter
1. Apply for a [Twitter Developer account](https://developer.twitter.com/en/portal/petition/use-case)
1. Once you have the account, go to the [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
1. Create a project and an app for your bot
1. Add `Read & Write` permissions to your app
1. In `Keys & Tokens`, generate Consumer Keys and Access Token/Secret to use as environment variables

## Lint
1. Install [pre-commit](https://pre-commit.com)
1. `pre-commit install`

Lint is run as a pre-commit, or on-demand with `pre-commit run --all-files`

## Deployment Instructions

Required Environment Variables:
- `REDIS_URL`: A redis service
- `VACCINE_CHECK_INTERVAL`: How often (in seconds) to check
- `RADIUS`: Within how many miles to check
  - CVS has a maximum of 25, vaccine-watch will use 25 for CVS if you set this higher.
- `LATITUDE`: Latitude of the location to check (e.g. `39.1040382`)
- `LONGITUDE`: Latitude of the location to check (e.g. `-94.5701803`)
- `STATES`: JSON: Abbreviations of which states are in radius of your location (e.g. `["MO", "KS"]`)

Optional Environment Variables:
- `ENABLE_HYVEE`: If you want to check Hy-Vee pharmacies
- `ENABLE_WALGREENS`: If you want to check Walgreens pharmacies
- `ENABLE_WALMART`: If you want to check Walmart pharmacies
- `ENABLE_COSENTINOS`: If you want to check stores in the [Cosentino's family](https://www.cosentinos.com/covid-vaccine) (Kansas City only)
- `ENABLE_BALLS`: If you want to check stores in the [Ball's family](https://ballsfoodspharmacy.com/) (Kansas City only)
- CVS:
  - `ENABLE_CVS`: If you want to check CVS pharmacies
  - `CVS_ALLOW_LIST`: JSON of states and cities to be notified for.
    - example: `{"MO": ["SAINT LOUIS"], "KS": []}`
  - `CVS_BLOCK_LIST`: (optional): JSON of states and cities to not be warned about new city for.
    - example: `{"MO": ["SAINT LOUIS"], "KS": []}`
  - Any city that CVS returns for the state(s) in `STATES` that are not listed in either the allow or block list will cause a warning message to be logged. Then it may be added to the allow or block list depending on if you wish to have the locations in that city checked or not checked.
- Slack:
  - `SLACK_BOT_TOKEN`: Token for your slack integration
  - `SLACK_TAG_CHANNEL`: If the channel should be tagged when appointments are available
  - `SLACK_CHANNEL`: Channel for the bot to post in (e.g. `#vaccine-watch`)
- Discord:
  - `DISCORD_WEBHOOK_URL`: Discord webhook url for channel.
    - example: `https://discordapp.com/api/webhooks/1234567890/abc123`
- Twitter:
  - `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN_KEY`, `TWITTER_ACCESS_TOKEN_SECRET`
- `TIMEZONE`: Timezone of your location (defaults to `'US/Central'`)
- `CACHE_PREFIX`: If you want to run multiple copies of vaccine-watch, all sharing the same Redis database, you will want to give each instance a different CACHE_PREFIX.

### Docker
You can build a docker image with the Dockerfile, and run it with a redis server.

### Heroku
You can create an app in heroku, add a free redis plan, and push the source. Configure the dynos to enable `clock`.
