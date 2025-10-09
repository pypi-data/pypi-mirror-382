# Subsonic

The Raphson music player partially implements the [OpenSubsonic API](https://opensubsonic.netlify.app/), allowing you to use many Subsonic clients to play music from the music server.

Use the following settings:
 * Server Address: https://music.raphson.nl
 * Username: your username
 * Password: authentication token from https://music.raphson.nl/token

## Recommended clients

* Android: Tempo, Ultrasonic

## Tested clients

| name       | platform | login | browse  | playback | lyrics | offline | mix    | scrobble | download
| ---------- | -------- | ----- | ------- | -------- | ------ | ------- | ------ | -------- | --------
| Tempo      | Android  | yes   | yes     | yes      | yes    | yes     | yes    | yes      | [F-Droid](https://f-droid.org/en/packages/com.cappielloantonio.notquitemy.tempo/)
| Ultrasonic | Android  | yes   | yes     | yes      | yes    | no      | ?      | yes      | [F-Droid](https://f-droid.org/packages/org.moire.ultrasonic/)
| Subtracks  | Android  | yes   | yes     | yes      | no     | no      | no     | no       | [F-Droid](https://f-droid.org/en/packages/com.subtracks/)
| Twelve     | Android  | yes   | yes     | yes      | yes    | no      | no     | no       | [Compile from source](https://github.com/LineageOS/android_packages_apps_Twelve)
| Supersonic | Desktop  | yes   | yes     | yes      | yes    | no      | ?      | no       | [Flatpak](https://flathub.org/apps/io.github.dweymouth.supersonic)
| Feishin    | Desktop  | yes   | yes     | yes      | no     | no      | ?      | broken   | [Feishin](https://github.com/jeffvli/feishin/releases)

Issues:
* Twelve: cannot log in without legacy authentication. Patch accepted: https://review.lineageos.org/c/LineageOS/android_packages_apps_Twelve/+/432489
* Tempo: crash when sorting albums. Patch submitted: https://github.com/CappielloAntonio/tempo/pull/389
* Tempo: if album art is slow to load, a placeholder image is displayed. The next time it is loaded, it will work.
* Ultrasonic: uses suboptimal `getLyrics` endpoint, does not support time synced lyrics and will fail to show lyrics in some cases

## Supported API methods

| method                    | status | notes
| ------------------------- | ------ | -----------
addChatMessage              | no     |
changePassword              | no     |
createBookmark              | no     |
createInternetRadioStation  | no     |
createPlaylist              | no     | maybe
createPodcastChannel        | no     |
createShare                 | no     | maybe
createUser                  | no     |
deleteBookmark              | no     |
deleteInternetRadioStation  | no     |
deletePlaylist              | no     |
deletePodcastChannel        | no     |
deletePodcastEpisode        | no     |
deleteShare                 | no     |
deleteUser                  | no     |
download                    | yes    | downloads transcoded audio instead of original file
downloadPodcastEpisode      | no     |
getAlbum                    | no     | TODO
getAlbumInfo                | no     |
getAlbumInfo2               | yes    | returns no info
getAlbumList                | no     |
getAlbumList2               | yes    |
getArtist                   | yes    |
getArtistInfo               | no     |
getArtistInfo2              | yes    | returns no info
getArtists                  | yes    |
getAvatar                   | no     |
getBookmarks                | no     |
getCaptions                 | no     |
getChatMessages             | no     |
getCoverArt                 | yes    |
getGenres                   | yes    |
getIndexes                  | no     |
getInternetRadioStations    | no     |
getLicense                  | yes    |
getLyrics                   | yes    | getLyricsBySongId is preferred
getLyricsBySongId           | yes    |
getMusicDirectory           | no     | maybe
getMusicFolders             | no     | maybe
getNewestPodcasts           | no     |
getNowPlaying               | no     | maybe
getOpenSubsonicExtensions   | yes    |
getPlaylist                 | yes    |
getPlaylists                | yes    |
getPlayQueue                | no     |
getPodcasts                 | no     |
getRandomSongs              | partial | supports fromYear and toYear, not genre and musicFolderId
getScanStatus               | yes    |
getShares                   | no     | maybe
getSimilarSongs             | no     | maybe
getSimilarSongs2            | yes    |
getSong                     | yes    |
getSongsByGenre             | yes    |
getStarred                  | partial | always returns nothing
getStarred2                 | partial | always returns nothing
getTopSongs                 | no     |
getUser                     | no     | maybe
getUsers                    | no     | maybe
getVideoInfo                | no     |
getVideos                   | no     |
jukeboxControl              | no     |
ping                        | yes    |
refreshPodcasts             | no     |
savePlayQueue               | no     |
scrobble                    | partial | does not support multiple scrobbles
search                      | no     | deprecated
search2                     | no     | maybe
search3                     | yes    |
setRating                   | no     |
star                        | no     |
startScan                   | yes    |
stream                      | yes    | TODO: maxBitRate
tokenInfo                   | yes    |
unstar                      | no     |
updateInternetRadioStation  | no     |
updatePlaylist              | partial| only adding, not removing songs
updateShare                 | no     |
updateUser                  | no     |
