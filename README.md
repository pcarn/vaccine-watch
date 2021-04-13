# Vaccine Watch
Bot to notify when vaccine appointments are available.

Supports checking Hy-Vee, Cosentino's stores (KC), Ball's stores (KC), Rapid Test KC, and locations checked by [VaccineSpotter](https://vaccinespotter.org) (including Walmart, Walgreens, CVS, Costco).
Supports sending notifications to Slack, Discord, Microsoft Teams, Twilio, and [Twitter](https://twitter.com/kcvaccinewatch).

Notifications are sent when a location has appointments. No more notifications are sent for that location until it becomes unavailable again.

PRs welcome to support other clinics or notification methods.

This project has no affiliation with any of the clinics mentioned.

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

### Microsoft Teams
1.  In the channel where you want to add the incoming webhook, click ... and then Connectors.
1.  Search for Incoming Webhook and click Add.
1.  Give the webhook a name (e.g. Vaccine Watch).
1.  Click Create.
1.  A unique webhook URL will be provided for the channel.

### Twitter
1. Apply for a [Twitter Developer account](https://developer.twitter.com/en/portal/petition/use-case)
1. Once you have the account, go to the [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
1. Create a project and an app for your bot
1. Add `Read & Write` permissions to your app
1. In `Keys & Tokens`, generate Consumer Keys and Access Token/Secret to use as environment variables

### Twilio
1. Sign up for a [Twilio account](https://www.twilio.com/try-twilio)
1. Once you have the account, go to the [Console Dashboard](https://www.twilio.com/console) of your Twilio account console
1. Navigate to the `Phone Numbers` page in your Twilio account console, then click `Getting Started`
1. Select `Get your first Twilio phone number` and follow the prompts to procure a Twilio phone number
1. Verify any recipient phone numbers you will be notifying under `Phone Numbers` then [Verified Caller IDs](https://www.twilio.com/console/phone-numbers/verified) (only required for a trial account)
1. Copy your Twilio Account SID, Auth Token, Twilio phone number, and verified phone numbers to your `.env` file

## Lint
1. Install [pre-commit](https://pre-commit.com)
1. `pre-commit install`

Lint is run as a pre-commit, or on-demand with `pre-commit run --all-files`

## Deployment Instructions

Required Environment Variables:
- `REDIS_URL`: A redis service
- `VACCINE_CHECK_INTERVAL`: How often (in seconds) to check
- `RADIUS`: Within how many miles to check
- `LATITUDE`: Latitude of the location to check (e.g. `39.1040382`)
- `LONGITUDE`: Latitude of the location to check (e.g. `-94.5701803`)
- `STATES`: JSON: Abbreviations of which states are in radius of your location (e.g. `["MO", "KS"]`)

Optional Environment Variables:
- `REQUEST_TIMEOUT`: How long to wait, in seconds, for a response to begin before timing out (optional, defaults to 5 seconds)
- `ENABLE_BALLS`: If you want to check stores in the [Ball's family](https://ballsfoodspharmacy.com/) (Kansas City only)
- `ENABLE_COSENTINOS`: If you want to check stores in the [Cosentino's family](https://www.cosentinos.com/covid-vaccine) (Kansas City only)
- `ENABLE_HYVEE`: If you want to check Hy-Vee pharmacies
- `ENABLE_VACCINE_SPOTTER`: If you want to check locations checked by [VaccineSpotter](https://vaccinespotter.org) (Excluding Hy-Vee)
- `ENABLE_RAPID_TEST_KC`: Iff you want to check Rapid Test KC (Kansas City only)
- Slack:
  - `SLACK_BOT_TOKEN`: Token for your slack integration
  - `SLACK_TAG_CHANNEL`: If the channel should be tagged when appointments are available
  - `SLACK_CHANNEL`: Channel for the bot to post in (e.g. `#vaccine-watch`)
- Discord:
  - `DISCORD_WEBHOOK_URL`: Discord webhook url for channel.
    - example: `https://discordapp.com/api/webhooks/1234567890/abc123`
- Microsoft Teams:
  - `TEAMS_WEBHOOK_URL`: Teams webhook url for channel.
    - example: `https://company.webhook.office.com/webhookb2/abc123@def456/IncomingWebhook/aaa111/bbb222`
- Twilio:
  - `TWILIO_ACCOUNT_SID`: Account SID for your twilio account
  - `TWILIO_AUTH_TOKEN`: Auth token for your twilio account
  - `TWILIO_FROM_NUMBER`: Twilio phone number with SMS functionality in `[+][country code][phone number including area code]` format
  - `TWILIO_TO_NUMBERS`: Phone numbers to notify as an array of the following format `[+][country code][phone number including area code]`
    - example: `["+15551234567", "+15552345678"]`
- Twitter:
  - `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN_KEY`, `TWITTER_ACCESS_TOKEN_SECRET`
- `TIMEZONE`: Timezone of your location (defaults to `'US/Central'`)
- `CACHE_PREFIX`: If you want to run multiple copies of vaccine-watch, all sharing the same Redis database, you will want to give each instance a different CACHE_PREFIX.

### Docker
You can build a docker image with the Dockerfile, and run it with a redis server.

### Heroku
You can create an app in heroku, add a free redis plan, and push the source. Configure the dynos to enable `clock`.
