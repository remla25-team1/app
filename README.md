# app
- Sentiment analysis endpoint `/sentiment` with tweet input.
- User feedback and correction via `/correction`.
- Corrections are stored in a JSONL file for future training.
- Version info is fetched via lib-version and displayed in the frontend footer.

## Automatic Versioning
We have two types of tags: vX.X.X or vX.X.X-pre-DATE-XXX. The first version is used for production. These will always be versions that work. The latter tag is an experimental model for developing purposes, this doesn't always have to be a working version. The version bump is now done automatically, so if v0.0.1 already exists, it will automatically bump the VERSION.txt up one count. Same story for the experimental tags, they will be based on the VERSION.txt as a base and increment based on date and based on last three digits if there are multiple models on the same day.

To trigger the automated version release:

1) Go to repo model-training on GitHub.
2) Click on the "Actions" tab.
3) Select "Versioning Workflow (SemVer + Dated Pre-Releases) " from the list on the left.
4) Click the “Run workflow” button and choose the type of version tag you want.
5) When this workflow has finished, go to Release model-training from the list on the left
6) You will now see that this workflow has been triggered automatically by the previous workflow.
