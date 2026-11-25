# The catalogue of Tensela extensions

The extensions shown on [tensela.com/extensions](https://tensela.com/extensions/): one file per extension in
`extensions/<id>.json`. Tensela itself does not read this catalogue (it does not connect to anything): people find an
extension on the site, download its `.zip` and install it (**Extensions → Manage extensions… → Install from a
file…**). [En español](README.es.md).

## Add your extension

1. Its code in a public repository, and a release with its `.zip` (the template's workflow makes it:
   [extension-template](https://github.com/tensela/extension-template)).
2. Its file, made from the `.zip`:

   ```bash
   python tools/catalogue.py entry my-extension-0.1.0.zip https://github.com/your-name/my-extension/releases/download/v0.1.0/my-extension-0.1.0.zip > extensions/my-extension.json
   ```

   It copies what its card says (names, descriptions, permissions and why, links) and computes its fingerprint
   (SHA-256). Read it: what it says is what the site shows.
3. A pull request with that file. The check runs by itself (`tools/catalogue.py check --download`: the `.zip` is the
   one its fingerprint says, and its card agrees with its file). Then a person reviews it.

## What is reviewed

- **Its code is public**, and the `.zip` has what that code says.
- **Its permissions make sense** for what it does, and each one says why in words a person understands. Internet,
  files outside the project, other programs and talking with other programs of the computer are asked for in its
  card; one that does something it does not ask for does not enter.
- **Nothing hidden**: no code downloaded while it runs, nothing that sends the person's data anywhere without saying
  so, nothing obfuscated.
- **Its card is complete**: a name, what it does, who makes it, its licence, where its code is and where to report a
  problem.

The problems of an extension are reported where its file says (`issues`), not here.

## Update it

A new release, and a pull request that changes `version`, `download`, `sha256` and `updated` in its file (or makes it
again with `tools/catalogue.py entry`).

## For the site

`python tools/catalogue.py build catalogue.json` joins them all in one file; the site reads it when it is built.
