import subprocess
from mcp.server.fastmcp import FastMCP


def run_applescript(script: str) -> str:
    """Execute an AppleScript command via osascript and return its output."""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()


# Instantiate the MCP server.
mcp = FastMCP("iTunesControlServer")


@mcp.tool()
def itunes_play() -> str:
    """Start playback in Music (iTunes)."""
    script = 'tell application "Music" to play'
    return run_applescript(script)


@mcp.tool()
def itunes_pause() -> str:
    """Pause playback in Music (iTunes)."""
    script = 'tell application "Music" to pause'
    return run_applescript(script)


@mcp.tool()
def itunes_next() -> str:
    """Skip to the next track."""
    script = 'tell application "Music" to next track'
    return run_applescript(script)


@mcp.tool()
def itunes_previous() -> str:
    """Return to the previous track."""
    script = 'tell application "Music" to previous track'
    return run_applescript(script)


@mcp.tool()
def itunes_search(query: str) -> str:
    """
    Search the Music library for tracks whose names contain the given query.
    Returns a list of tracks formatted as "Track Name - Artist".
    """
    script = f"""
    tell application "Music"
        set trackList to every track of playlist "Library" whose name contains "{query}"
        set output to ""
        repeat with t in trackList
            set output to output & (name of t) & " - " & (artist of t) & linefeed
        end repeat
        return output
    end tell
    """
    return run_applescript(script)


@mcp.tool()
def itunes_play_song(song: str) -> str:
    """
    Play the first track whose name exactly matches the given song name.
    Returns a confirmation message.
    """
    script = f"""
    tell application "Music"
        set theTrack to first track of playlist "Library" whose name is "{song}"
        play theTrack
        return "Now playing: " & (name of theTrack) & " by " & (artist of theTrack)
    end tell
    """
    return run_applescript(script)


@mcp.tool()
def itunes_create_playlist(name: str, songs: str) -> str:
    """
    Create a new playlist with the given name and add tracks to it.
    'songs' should be a comma-separated list of exact track names.
    Returns a confirmation message including the number of tracks added.
    """
    # Split the songs string into a list.
    song_list = [s.strip() for s in songs.split(",") if s.strip()]
    if not song_list:
        return "No songs provided."
    # Build a condition string that matches any one of the song names.
    # Example: 'name is "Song1" or name is "Song2"'
    conditions = " or ".join([f'name is "{s}"' for s in song_list])
    script = f"""
    tell application "Music"
        set newPlaylist to make new user playlist with properties {{name:"{name}"}}
        set matchingTracks to every track of playlist "Library" whose ({conditions})
        repeat with t in matchingTracks
            duplicate t to newPlaylist
        end repeat
        return "Playlist \\"{name}\\" created with " & (count of tracks of newPlaylist) & " tracks."
    end tell
    """
    return run_applescript(script)


@mcp.tool()
def itunes_library() -> str:
    """
    Return a summary of the Music library, including total tracks and user playlists.
    """
    script = """
    tell application "Music"
        set totalTracks to count of every track of playlist "Library"
        set totalPlaylists to count of user playlists
        return "Total tracks: " & totalTracks & linefeed & "Total playlists: " & totalPlaylists
    end tell
    """
    return run_applescript(script)


@mcp.tool()
def itunes_current_song() -> str:
    """
    Get information about the currently playing track.
    Returns the track name, artist, and album.
    """
    script = """
    tell application "Music"
        if player state is playing then
            set currentTrack to current track
            return "Now playing: " & (name of currentTrack) & " by " & (artist of currentTrack) & " from " & (album of currentTrack)
        else
            return "No track is currently playing"
        end if
    end tell
    """
    return run_applescript(script)


@mcp.tool()
def itunes_all_songs() -> str:
    """
    Get a list of all songs in the Music library.
    Returns a formatted list of all tracks with their names and artists.
    """
    script = """
    tell application "Music"
        set trackList to every track of playlist "Library"
        set output to ""
        repeat with t in trackList
            set output to output & (name of t) & " - " & (artist of t) & linefeed
        end repeat
        return output
    end tell
    """
    return run_applescript(script)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
