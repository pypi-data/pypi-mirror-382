# Offline music player in Termux

## Installation

Install the F-Droid client from [f-droid.org](https://f-droid.org/F-Droid.apk).

Install "Termux" from F-Droid. Open Termux. You will be presented with a Linux terminal environment.

Install Python and pip:
```
pkg install python-pip
```

Install the `raphson-mp` package:
```
pip install raphson-mp[offline]
```

Create a script to start the music player with your arguments of choice. An example:

`./mp.sh`
```
python -m raphson_mp --offline --data-dir=./mp-data --short-log-format $@
```

don't forget: `chmod +x mp.sh`

## Start music player
```
./mp.sh start
```

Visit http://localhost:8080 in a web browser. Use Ctrl+C to stop the web server.

## Sync music

Go to the "Synchronise music" page. Configure the server, authentication token, and optionally a list of playlists. About 5GB of storage space is used for every 1000 tracks. Disliked tracks are not downloaded.

## Shortcut widget

Using the Termux:Widget addon (install from F-Droid) you can add commands as shortcuts to your home screen, allowing you to start the music player with a single click.

```
mkdir .shortcuts
chmod +x 700 .shortcuts
cd .shortcuts
echo "~/mp.sh start" > music
chmod +x music
```

## Updating

Updates may introduce bugs. It is advisable that you do not update at a time where you really need the music player to work, like just before going on a trip.

Run: `pip install --upgrade raphson-mp[offline]`

## Moving from legacy git clone installation to Python package

1. Follow the installation instructions again, but do not start the music player yet.
2. Move the `data` directory from your old installation (git clone of `raphson-music-player` or previously `WebApp`) to the correct location, for example `~/mp-data`
3. Start the music player, and make sure it all works
4. Delete the old git clone
