# 🔮 cliotp

```
 ______     __         __     ______     ______   ______
/\  ___\   /\ \       /\ \   /\  __ \   /\__  _\ /\  == \
\ \ \____  \ \ \____  \ \ \  \ \ \/\ \  \/_/\ \/ \ \  _-/
 \ \_____\  \ \_____\  \ \_\  \ \_____\    \ \_\  \ \_\
  \/_____/   \/_____/   \/_/   \/_____/     \/_/   \/_/
```

> [!IMPORTANT]
> This project is very much a work in progres, but has the basic features for most use cases.

Easily organize, store, and generate your one time passwords from the comfort of your terminal.

This library follows [rfc4226](https://datatracker.ietf.org/doc/html/rfc4226) and [rfc6238](https://datatracker.ietf.org/doc/html/rfc6238). It can serve as a replacement for authenticator apps.

## Installation
Requires python >= 3.10

`pip install cliotp`

## Getting started

Initialize the library

`cliotp init`

This will prompt for a password. You password will be hashed to generate your master password. The master password is then stored locally and used to encrypt/decrypt each of your TOTP seeds.

After initialization you can add and retrieve codes using

`cliotp add IDENTIFIER SEED`

`cliotp code IDENTIFIER`

See `cliotp --help` for a full list of available commands
