# Music files

The music directory should contain one subdirectory for each playlist. Place audio files in these playlist directories.

An example:

```
music
├── CB
│   ├── Sub Focus & Wilkinson - Ray Of Sun.mp3
│   ├── The Elite - Falling Angels (Official Video) _ Coone & Da Tweekaz & Hard Driver.mp3
│   ├── Toneshifterz - I Am Australian (Hardstyle) _ HQ Videoclip.mp3
├── DK
│   ├── 025 Midnight Oil - Beds Are Burning.mp3
│   ├── 061 Pink Floyd - Another Brick In The Wall.mp3
│   └── 078 Nena - Irgendwie irgendwo irgendwann (long version).mp3
├── RS
│   ├── Tom Misch & Yussef Dayes - Storm Before The Calm (feat. Kaidi Akinnibi) (Official Audio).webm
│   ├── U & ME - Alt J (Official Audio) [RMkxrJuxRsk].webm
│   └── Zes - Juniper [UNYiVK3Cl98].webm
└── JK
    ├── Aerosmith - Dream On.mp3
    ├── A spaceman came travelling.mp3
    └── A Warrior's Call.mp3
```

If possible, add metadata to each file, like artist, album artist, album title, song title. This can be done using the metadata editor in the music player itself.

While the music player has built-in file management capabilities, manually modifying the file system is fully supported. You do however need to manually invoke the scanner: `raphson-mp scan`.

Nesting directories inside playlists is possible. With many (1000+) files in a directory, file browsing through the web file manager and WebDAV may become a bit slow. I would recommend creating a directory for each artist or album.
