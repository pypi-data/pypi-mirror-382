// base.jinja2
export type Vars = {
    csrfToken: string,
    offlineMode: string,
    loadTimestamp: number,
    tBrowseArtist: string,
    tBrowseAlbum: string,
    tBrowseTag: string,
    tBrowsePlaylist: string,
    tBrowseYear: string,
    tBrowseTitle: string,
    tBrowseRecentlyAdded: string,
    tBrowseRecentlyReleased: string,
    tBrowseRandom: string,
    tBrowseMissingMetadata: string,
    tBrowseNothing: string,
    tActivityFileAdded: string,
    tActivityFileModified: string,
    tActivityFileDeleted: string,
    tActivityFileMoved: string,
    tTrackInfoUnavailable: string,
    tTheaterModeEnabled: string,
    tTheaterModeDisabled: string,
    tLyricsEnabled: string,
    tLyricsDisabled: string,
    tVisualiserEnabled: string,
    tVisualiserDisabled: string,
    tQueueCleared: string,
    tErrorOccurredReported: string,
    tErrorOccurredUnreported: string,
    tTokenSetUpSuccessfully: string,
    tInvalidSpotifyPlaylistUrl: string,
    tFingerprintFailed: string,
    tControlPause: string,
    tControlPlay: string,
    tControlPrevious: string,
    tControlNext: string,
    tControlSeek: string,
    tControlQueue: string,
    tControlPlaylist: string,
    tTrackProblemReported: string,
    tTooltipPlayNow: string,
    tTooltipAddToQueue: string,
    tTooltipEditMetadata: string,
    tActivityNothingPlaying: string,
    tLoading: string,
    tUnknownAlbum: string,
    tLyricsNotTimeSynced: string,
    tPlaylist: string,
    tAutoPlayBlocked: string,
};

// common.track.TrackDict
export type TrackJson = {
    path: string
    mtime: number
    ctime: number
    duration: number
    title?: string | null
    album?: string | null
    album_artist?: string | null
    year?: number | null
    track_number?: number | null
    video?: string | null
    lyrics?: string | null
    artists?: Array<string>
    tags?: Array<string>
};

// common.track.QueuedTrackDict
export type QueuedTrackJson = {
    track: TrackJson,
    manual: boolean,
}

// routes.tracks.route_filter
export type FilterJson = {
    limit?: number,
    offset?: number,
    playlist?: string,
    artist?: string,
    tag?: string,
    album_artist?: string,
    album?: string,
    year?: number,
    title?: string,
    has_metadata?: string,
    order?: string,
}

// common.music.Album
export type AlbumJson = {
    name: string,
    artist: string | null,
    track: string, // arbitrary track from the album, can be used to obtain a cover art image
};

// common.music.Artist
export type ArtistJson = {
    name: string,
};

// common.control.ClientPlaying
export type ControlClientPlaying = {
    track: TrackJson,
    paused: boolean,
    position?: number | null,
    duration?: number | null,
    control: boolean,
    volume?: number | null,
    client: string,
    queue: Array<QueuedTrackJson> | null,
    playlists: Array<string> | null,
}

export type ControlClientQueue = {
    tracks: Array<QueuedTrackJson>
}

export type ControlClientRequestUpdate = {
    player_id: string
}

export type ControlClientSubscribe = {
    topic: string,
}

export type ControlClientToken = {
    csrf: string,
}

export type ControlClientPlay = {
    player_id: string,
}

export type ControlClientPause = {
    player_id: string,
}

export type ControlClientPrevious = {
    player_id: string,
}

export type ControlClientNext = {
    player_id: string,
}

export type ControlClientVolume = {
    player_id: string,
    volume: number
}

export type ControlClientSeek = {
    player_id: string,
    position: number,
}

export type ControlClientSetQueue = {
    player_id: string,
    tracks: Array<QueuedTrackJson>
}

export type ControlClientPlaylists = {
    playlists: Array<string>,
}

export type ControlClientSetPlaylists = {
    player_id: string,
    playlists: Array<string>,
}

export type ControlClientCommand =
        ControlClientPlaying |
        ControlClientSubscribe |
        ControlClientToken |
        ControlClientPlay |
        ControlClientPause |
        ControlClientPrevious |
        ControlClientNext |
        ControlClientVolume |
        ControlClientSeek |
        ControlClientSetQueue |
        ControlClientPlaylists |
        ControlClientSetPlaylists;

// common.control.ServerPlaying
export type ControlServerPlaying = {
    player_id: string
    username: string
    paused: boolean,
    position: number | null,
    duration: number | null,
    control: boolean,
    volume: number | null,
    expiry: number,
    client: string,
    track: TrackJson,
    queue: Array<QueuedTrackJson> | null,
    playlists: Array<string> | null,
};

// common.control.ServerPlayed
export type ControlServerPlayed = {
    played_time: number,
    username: string,
    track: TrackJson,
};

export type ControlServerPlayingStopped = {
    player_id: string,
}

export type FileAction = "insert" | "delete" | "update" | "move";

// common.control.ServerFileChange
export type ControlServerFileChange = {
    change_time: number,
    action: FileAction,
    track: string,
    username: string | null,
};

export type ControlServerSetQueue = {
    tracks: Array<QueuedTrackJson>,
}

export type ControlServerSetPlaylists = {
    playlists: Array<string>,
}

export type WebauthnSetupVars = {
    challenge: string,
    identifier: string,
    username: string,
    displayname: string,
};

// musicbrainz.MBMeta
export type AcoustIDRelease = {
    id: string,
    title: string,
    album: string,
    artists: Array<string>,
    album_artist: string,
    year: number | null,
    release_type: string,
    packaging: string,
}

// routes.track.route_acoustid
export type AcoustIDResult = {
    acoustid: string,
    releases: Array<AcoustIDRelease>,
}

export type OfflineSyncLogEntry = {
    task?: string,
    state: "start" | "done" | "error" | "all_done",
};

// common.typing.PlaylistDict
export type PlaylistJson = {
    name: string
    track_count: number
    favorite: boolean
    write: boolean
}
