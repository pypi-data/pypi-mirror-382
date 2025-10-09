# Changelog

All notable changes to this project will be documented in this file (from version 13.0.1.1.0 onwards).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [16.0.1.1.1] - 2025-10-08

### 🐛 Bug Fixes

- Improve investment validation
- Bug related with language and searching by name

### 🧪 Testing

- Fix issues in investments

## [16.0.1.1.0] - 2025-09-25

### 🚀 Features

- New investments endpoint refactored from domatix
- Handle promotional_code in investment endpoint
- Update post contracts endpoint to update promotion data when discount applied
- Update get user endpoint to bring promotion data
- Endpoint to check promotional_code validity
- Add message post with discounted amount when creating contract

### 🐛 Bug Fixes

- Force translation in contracts products query
- Uncomment state field in UserOut model
- Don't update existing partners
- Translate error messages
- Improve check if partner is new
- Improve check if partner has valid code
- Update existing res.partner that are not participants

### 🧪 Testing

- Add simple test for individual investment

### ⚙️ Miscellaneous Tasks

- Add changelogs
- Update translations
- Bump photovoltaic_api version to 16.0.1.1.0 and update changelog

## [16.0.1.0.0] - 2025-03-14

### 🐛 Bug Fixes

- Make bank_account in Contract optional
- Corrected download of allocation report
- Delete user_signature field
- Raise UserError when signup password is empty
- Cannot search user by their signup_token
- Rename assertEquals to assertEqual to supress warnings
- Change use of deprecated flush()
- Use raw string for regex
- Change user_id_strategy selection to selection_add

### 🚜 Refactor

- Start migration to pydantic v2
- Migrate pydantic models
- Migrate pydantic methods
- Parse date to string
- Custom state_to_pydantic function

### ⚙️ Miscellaneous Tasks

- Add licenses
- Update translations
- Update version number to 16.0

## [13.0.1.4.3] - 2025-02-26

### 🐛 Bug Fixes

- Fix incorrect property name

### ⚙️ Miscellaneous Tasks

- Bump photovoltaic api to 13.0.1.4.3 and update changelog

## [13.0.1.4.2] - 2025-01-23

### 🐛 Bug Fixes

- Removed unnecesary debug loger

### ⚙️ Miscellaneous Tasks

- Bump version to 13.0.1.4.2 and update changelog

## [13.0.1.4.1] - 2024-12-12

### 🐛 Bug Fixes

- Correct comparison of contract_numbers length
- Import missing MissingError
- Delete copy of mail template after using it

### ⚙️ Miscellaneous Tasks

- Bump version to 13.0.1.4.1 and update changelog

## [13.0.1.4.0] - 2024-12-09

### 🚀 Features

- Added processing of minor and tutor fields

### 🐛 Bug Fixes

- Improved visibility of new contracts
- Used correct contact object in contact processing
- Check input contact has email before searching by it

### 🚜 Refactor

- Optimized new contract name composition
- Split create contact method in smaller methods

### 📚 Documentation

- Added cliff.toml for automatic changelog generation

### ⚙️ Miscellaneous Tasks

- Bump version to 13.0.1.4.0 and update changelog

## [13.0.1.3.1] - 2024-11-05

### 🐛 Bug Fixes

- Corrected product string search generation
- Contract date now set correctly on new contracts
- Corrected construction of product search string
- Corrected name generation for new contracts

### ⚙️ Miscellaneous Tasks

- Bump version to 13.0.1.3.1

## [13.0.1.3.0] - 2024-10-28

### 🚀 Features

- Added api method to create a new contract

### 🐛 Bug Fixes

- Changed email that recieves the new contract notification

### ⚡ Performance

- Limited search of contract products to speed search

### ⚙️ Miscellaneous Tasks

- Bumped photovoltaic api to 13.0.1.3.0

## [13.0.1.2.1] - 2024-10-11

### 🐛 Bug Fixes

- Append comment instead of overwriting in contacts endpoint

### ⚙️ Miscellaneous Tasks

- Bumped version to 13.0.1.2.1 and updated changelog

## [13.0.1.2.0] - 2024-09-24

### 🐛 Bug Fixes

- Correct name of allocation report in english
- Added missing field 'is_chalet' to contacts endpoint

### ⚙️ Miscellaneous Tasks

- Updated version number of photovoltaic_api and corresponding CHANGELOG

## [13.0.1.1.13] - 2024-04-23

### 🐛 Bug Fixes

- Added missing field to contacts endpoint

## [13.0.1.1.12] - 2024-04-02

### 🐛 Bug Fixes

- Removed contracts assigned to 'Guardabosques' from the list of contracts

## [13.0.1.1.11] - 2024-03-06

### 🚀 Features

- *(api)* Included tags field to contacts endpoint

### 🐛 Bug Fixes

- *(api)* Fixed use of non-existing variable
- Fixed country and state assignment in contacts endpoint
- Added search by vat first when upserting a contact
- Set correct operator when searching by vat in contacts endpoint
- Covered edge case so vat is not modified if is not needed
- Added to upper case transformation to vat

## [13.0.1.1.9] - 2023-12-13

### 🚀 Features

- Store string coming in [message_notes] into 'mail_message'

## [13.0.1.0.2] - 2022-10-26

## [13.0.1.1.8] - 28-09-2023

### Added

- Note on contact when rgpd is accepted

## [13.0.1.1.7] - 24-08-2023

### Fixed

- Missing property in allow promotions method

## [13.0.1.1.6] - 08-08-2023

### Added
- New endpoint to retrieve powerstations open for investment

## [13.0.1.1.5] - 05-06-2023

### Added
- New endpoint to allow synchronization with mailchimp via mailchimp webhooks


## [13.0.1.1.4] - 29-06-2023

### Fixed
- Promotions policy endpoint to allow both subscription and unsubscription

## [13.0.1.1.3] - 09-06-2023

### Added
- Endpoint to update promotions policy of a contact

### Fixed
- Comparator of vat in login and signup to be case insensitive

## [13.0.1.1.2] - 26-04-2023

### Fixed
- User update process
- Password regex to allow symbols

## [13.0.1.1.1] - 20-04-2023

### Fixed
- Selection of contacts on signup request

## [13.0.1.1.0] - 11-04-2023

### Fixed
- Incorrect retrieval of account allocations
- Count of allocations to use correct search domain
- Naming of company users
- Location of a user
- Allocations shown based on check
- Allocation period calculation
- Firsname and lastname of users with two first names

### Removed
- Email validation on users to allow multiple emails separated by ';'

<!-- generated by git-cliff -->
