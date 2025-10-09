# Security

## Expectations

* The application is designed to be exposed to the internet.
    * Unauthenticated users should not be able to access any personal data, except through the share function.
    * Data that is part of the application itself (javascript source code, icon, etc.) is public.
* You should not give accounts to untrusted users
    * Authenticated users have full read-only access to the music files.
    * Authenticated users have control over all other user's players (seeking, play/pause, modifying the queue, etc.)
    * Authenticated users may be able to easily perform a denial of service attack. This is not considered a bug.
    * The attack surface for an authenticated user is much larger than for an unauthenticated user.

## Bugs

Please report security bugs using Signal `robin.03` or otherwise by email to `robin@rslot.nl`.

## Hardening

### Bubblewrap

Set the `--bwrap` command line option (or `MUSIC_BWRAP` environment variable) to enable sandboxing for subprocesses. Requires the `bubblewrap` package to be installed. For example, one of the subprocesses called by the music player is ffmpeg. It is written in an unsafe language and operates on user input. Using `bwrap`, ffmpeg is isolated with read-only access to /etc and /usr, and access to the specific media files it needs. Additionally, it operates in its own network namespace, so without any network access. This makes abusing ffmpeg for code execution a lot more difficult.

Bubblewrap sandboxing is still experimental and does not work in the container version without additional tweaking.


### Subsonic

Subsonic uses a custom authentication mechanism. If you do not use it, you may disable it with --disable-features=subsonic to reduce attack surface.
