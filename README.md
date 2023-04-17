# Visa Scheduler

[![Released under the MIT license.](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/thiagorcdl/autovisa/blob/master/LICENSE)

This script is intended as a learning exercise for automating tedious tasks in
browsers. The goal is to automatically log in with the user's credentials, and
reschedule their appointment to some sooner date.

Currently, the only cities listed are the ones in Canada.


# Usage

1. Clone repository
2. Export credentials in env variables `VISA_EMAIL` and `VISA_PASSWORD`
1. Run `python -m autovisa`

# TODO
- [ ] Add unit tests
- [ ] Add better support for multiple appointments
- [ ] Optionallly pass credentials via arguments / input password via CLI
- [ ] Pass list of allowed cities via arguments
- [ ] Pass acceptable date range via arguments
- [ ] Pass allowed cities via arguments
  - [ ] Slugify city names 
- [ ] Add support for other countries
  - [ ] Replace locale in `LOGIN_URL`
  - [ ] Add country's cities to `CITY_NAME_ID_MAP`
