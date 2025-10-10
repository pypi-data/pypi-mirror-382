## Contributing

There are many ways to help contribute to Bugsink. Here are a few:

* Star the project on [GitHub](https://github.com/bugsink/bugsink)
* Open an [issue](https://www.github.com/bugsink/bugsink/issues)
* Reach out via [email](mailto:info@bugsink.com) or [discord](https://discord.gg/6Af6Yzz77C).
* Spread the word about Bugsink on your own blog, README or website
* Mention the project at local meetups and tell your friends/colleagues

### Code contributions

Code contributions are welcome! We use the GitHub PR process to review and merge code changes.

#### Style guidance

* Bugsink uses flake8, with rules/exceptions documented in tox.ini

#### Tailwind

Bugsink uses tailwind for styling, and [django-tailwind](https://github.com/timonweb/django-tailwind/)
to "do tailwind stuff from the Django world".

If you're working on HTML, you should probably develop while running the following somewhere:

```
python manage.py tailwind start
```

The above is the "tailwind development server", a thing that watches your files
for changes and generates the relevant `styles.css` on the fly.

Bugsink "vendors" its generated `styles.css` in source control management (git) from the pragmatic
perspective that this saves "everybody else" from doing the tailwind build.

Before committing, run the following:

```
python manage.py tailwind build
git add theme/static/css/dist/styles.css
```

The pre-commit hook in the project's root does this automatically if needed, copy it to .git/hooks
to auto-run.

### Security

For security-related contributions, please refer to the [Security Policy](/SECURITY.md).

#### Legal

* Please confirm that you are the author of the code you are contributing, or that you have the right to contribute it.
* Sign the [Contributor License Agreement](/CLA.md); the "CLA bot" will join the PR to help you with this.
