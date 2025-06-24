# Sentiment Analysis Web App

This is a web application for sentiment analysis of tweets, supporting user feedback collection and version-aware monitoring.

## Features

- **Sentiment Analysis API**  
  `/sentiment` accepts a tweet and returns a sentiment prediction (`positive` or `negative`).

- **Feedback Collection**  
  Users can submit corrections via `/correction`. All corrections are stored in a `.jsonl` file for future model improvement.

- **Version Display in Frontend**  
  The UI footer shows:
  - `lib-version` (retrieved via `lib-version`),
  - `model-service version` (fetched via `/model-service/version`),
  - `app version` (injected from the `APP_VERSION` environment variable).

## Tech Stack

- Backend: Python (Flask)
- Frontend: HTML + JavaScript
- Containerization: Docker

## Automatic Versioning
We have two types of tags: vX.X.X or vX.X.X-pre-DATE-XXX. The first version is used for production. These will always be versions that work. The latter tag is an experimental model for developing purposes, this doesn't always have to be a working version. The version bump is now done automatically, so if v0.0.1 already exists, it will automatically bump the VERSION.txt up one count. Same story for the experimental tags, they will be based on the VERSION.txt as a base and increment based on date and based on last three digits if there are multiple models on the same day.

To trigger the automated version release:

1) Go to repo model-training on GitHub.
2) Click on the "Actions" tab.
3) Select "Versioning Workflow (SemVer + Dated Pre-Releases) " from the list on the left.
4) Click the “Run workflow” button and choose the type of version tag you want.
5) When this workflow has finished, go to Release model-training from the list on the left
6) You will now see that this workflow has been triggered automatically by the previous workflow.
