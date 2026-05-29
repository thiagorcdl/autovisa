# Visa Scheduler

[![Released under the MIT license.](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/thiagorcdl/autovisa/blob/master/LICENSE)

This script is intended as a learning exercise for automating tedious tasks in
browsers. The goal is to automatically log in with the user's credentials, and
reschedule their appointment to some sooner date.

Currently, the only cities listed are the ones in Canada.

> DISCLAIMER: This project is intended for educational purposes. 
> Make sure you read the Terms o Service for any website before using this tool.
> The author does not endorse or encourage any unethical activity and is not responsible for
> the usage of this script by third party actors.

# Usage

1. Clone repository
2. Install packages `pip install -r requirements.txt`
3. Install a matched Chrome browser + chromedriver: `./scripts/install_chrome.sh`
   - Downloads a self-contained, pinned Chrome build into a project-local
     `.chrome/` directory (works on Linux, WSL and macOS). This is the real
     browser used to drive the site; it is pinned so it always matches the
     chromedriver and never auto-updates out from under it. The version is set
     in `.chrome-version`.
4. Export env variables:
   ```
   VISA_EMAIL="your@email.com"
   VISA_PASSWORD="your_password"
   APPLICANT_ID="YOURAPPID"
   BASE_URL="https://consulate.base.url"
   PRODUCTION=1
   ```
5. Run `python -m autovisa`

# TODO
- [x] Add unit tests
- [ ] Add better support for appointments with multiple applicants
- [ ] Optionally pass credentials via arguments / input password via CLI
- [ ] Pass list of allowed cities via arguments
  - [ ] Slugify city names 
- [ ] Pass acceptable date range via arguments
- [ ] Add support for other countries
  - [ ] Replace locale in `LOGIN_URL`
  - [ ] Add country's cities to `CITY_NAME_ID_MAP`
