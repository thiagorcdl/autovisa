# Visa Scheduler

[![Released under the MIT license.](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/thiagorcdl/autovisa/blob/master/LICENSE)

This script is intended as a learning exercise for automating tedious tasks in
browsers. The goal is to automatically log in with the user's credentials, and
reschedule their appointment to some sooner date.

Currently, the only cities listed are the ones in Canada.

> DISCLAIMER: This project is intended for educational purposes. 
> Make sure you read the Terms of Service for any website before using this tool.
> The author does not endorse or encourage any unethical activity and is not responsible for
> the usage of this script by third party actors.

# Usage

1. Clone repository
2. Install packages `pip install -r requirements.txt`
3. Install a matched Chrome browser + chromedriver: `./scripts/install_chrome.sh`
4. Export env variables:
   ```
   VISA_EMAIL="your@email.com"
   VISA_PASSWORD="your_password"
   APPLICANT_ID="YOURAPPID"
   BASE_URL="https://your-consulate.base.url"
   PRODUCTION=1
   # Optional filters:
   ALLOWED_CITY_IDS="94,93" # (see CITY_NAME_ID_MAP in constants.py)
   # EXCLUDE_DATE_START / EXCLUDE_DATE_END define an appointment window to skip.
   # Either may be omitted: with only START, every date from START on is skipped;
   # with only END, every date up to END is skipped. Omit both to exclude nothing.
   EXCLUDE_DATE_START="2023-12-31"
   EXCLUDE_DATE_END="2025-12-31"
   ```
5. Run `python -m autovisa`

# TODO
- [ ] Add better support for appointments with multiple applicants
- [ ] Optionally pass credentials via arguments / input password via CLI
- [ ] Pass list of allowed cities via arguments
  - [ ] Slugify city names 
- [ ] Pass acceptable date range via arguments
- [ ] Add support for other countries
  - [ ] Replace locale in `LOGIN_URL`
  - [ ] Add country's cities to `CITY_NAME_ID_MAP`
