# Jellyfin: review of the places flagged by DeepSeek flash

Read on 11 November 2026 (shallow clone of the default branch at 8466670): DeepSeek flash gave a verdict on every candidate found by the C# search signs, and Sonnet read what it flagged, with whole files and callers. Not reproduced on a running instance.

The list has 64 places. Whole files of the places and their callers were read. C15 and C8 were not read completely: C15 — 18 of 18 places (for 3 of them only the neighbouring lines of the same kind were read), C8 — a sample of 21 of 33 (the other 12 follow the same `is not <Type>` template and were not opened).

General conclusion: Jellyfin keeps the "kind" in the class hierarchy and the states in several entities. The serious findings are only in the Live TV recordings and in the common exception handler. The rest is either formal by the card but harmless, or false.

## Confirmed, by descending consequence

| Card | File:line | Verdict | Where the value comes from and what the user sees |
|---|---|---|---|
| C4 | src/Jellyfin.LiveTv/Recordings/RecordingsManager.cs:408 (and 372-383, 417) | dirty, medium | `RecordStream` changes `timer.Status` by hand in three places (New for a retry, Completed at the end, InProgress at the start); there is no transition table. `OperationCanceledException` gives `Completed` both when the user stops the recording and when the server stops (`RecordingsManager.Dispose` cancels all recordings). A retry (`Status = New`) happens only on `Error`. The user sees a cut-off recording as `Completed`, with no retry, while the stream is still running. `Status.Error` is never written to the timer in the code. |
| C15 | Jellyfin.Api/Middleware/ExceptionMiddleware.cs:57-102 | dirty, medium (DeepSeek flash said "unclear") | Any unhandled exception in production mode becomes the text "Error processing request." (in Development, `ex.Message`); the status code comes only from `GetStatusCode`: ArgumentException gives 400, everything else 500. No permission on a directory, disk full, a database error: the administrator sees the same text in the panel, and the reason is only in the log. |
| C4 | src/Jellyfin.LiveTv/DefaultLiveTvService.cs:226 | dirty, low | `CreateTimer` sets `New` by hand from `Completed`/`Cancelled`; the check "from which status" is in the same function. In other branches (line 753) the condition is different (`!IsManual`). |
| C4 | src/Jellyfin.LiveTv/DefaultLiveTvService.cs:676 | dirty, low | `HandleDuplicateShowIds` sets `Cancelled` on duplicates by ShowId. The protection of an active recording is in the calling code (only inactive ones get into the list), not in the writer. |
| C6 | src/Jellyfin.Database/.../Locking/OptimisticLockBehavior.cs:58 | dirty, low to medium | The retry of a SQLite write is decided by `e.Message.Contains("database is locked")` / `"database table is locked"` on any nested exception. If the text in SQLite or the driver changes, retries are silently disabled, and the administrator will see "database is locked" errors during a library scan. The code `SqliteException.SqliteErrorCode` 5 and 6 is present on the same exception. |
| C3 | src/Jellyfin.LiveTv/Recordings/RecordingsManager.cs:135 | dirty formally, low | `GetActiveRecordingInfo` returns a recording only if `Timer.Status == InProgress`. The recording's own indicator is the cancellation token, which is checked next to it. For the user: on cancel the status is already `Cancelled`, so for a moment the file is considered inactive. |
| C15 | Jellyfin.Api/Controllers/VideosController.cs:198 | dirty, low | "Please supply at least two videos to merge." is returned also when 2 ids are passed but one is not a Video or is not available to the user (`OfType<Video>` silently drops it). The reason named is the wrong one. |
| C15 | Jellyfin.Api/Controllers/ImageController.cs:120, 371, 415, 1489, 1731; HlsSegmentController.cs:66, 140; LibraryStructureController.cs:170; LyricsController.cs:115; StartupController.cs:150 | dirty formally, no harm (10 places) | The refusal goes out as a string without a code and without `ProblemDetails`; the API has no enumeration of codes at all. Each place has one reason and its own text, the status (400/403/404/409) is correct, and the web client shows the text. Different reasons are told apart by different strings. |
| C4 (not from the list) | Emby.Server.Implementations/Plugins/PluginManager.cs:648, 694 | dirty, low | The plugin status is written directly, bypassing `ChangePluginState` (a writer exists there, but without a transition table). Line 694 changes `Superseded` to `Active` only in memory; it is not saved to the manifest. DeepSeek flash did not flag these two lines. |
| C8 | src/Jellyfin.LiveTv/LiveTvManager.cs:826, 1135; LiveTvMediaSourceProvider.cs:241 | dirty formally, low | `service is not DefaultLiveTvService` decides whether to raise the `TimerCancelled`/`TimerCreated` event and whether to change streams. The default service raises the events itself; a plugin service will get a second pair if it starts raising its own events. The user will see nothing until a second implementation appears. |
| C8 | MediaEncoding/Transcoding/TranscodeManager.cs:155 | dirty formally, no harm | `job.Type != Progressive` selects a 60 s timeout versus 10 s; other job kinds behave the same. |

## False positives, by reason

**Entity created in its initial state (2).**
- C4 DefaultLiveTvService.cs:725: `timer.Status = Cancelled` on a new timer before `_timerManager.Add`.
- C4 PluginManager.cs:527: `Malfunctioned` on a freshly built manifest before the first `SaveManifest`.

**Not a lifecycle (3) and a transition on an event (1).**
- C4 ItemUpdateController.cs:471: `series.Status` is data about the series (Continuing/Ended), edited by the user by hand.
- C8 SyncPlay/Group.cs:429, 799: `GroupStateType` is the state of a group and by the card belongs to C4. There is one writer, `SetState`, and it resets `GroupWaitDeadline` on leaving Waiting.
- C3 PluginManager.cs:957: the writer moves `previousVersion` on the event of the new plugin through `ChangePluginState`. This is a transition on an event, not a derivation of state.

**No shared object and no shared status (2).**
- C10 MusicArtistResolver.cs:93: `Parallel.ForEach` with `state.Stop()` is an early exit during a search; there is no result assembled from parts.
- C10 Video.cs:554: `Task.WhenAll` over the parts of stacked videos. There is no shared status, and the error goes to the scan log. Note: one part's failure aborts the version update in the same call.

**The refusal does not reach the user (6).**
- C15 ItemImageProvider.cs:255, 340; MetadataService.cs:862, 942, 1017: `RefreshResult.ErrorMessage` is never read (except for forwarding at line 889). The user sees nothing; the error is in the log. Side finding: the field is written but not used.
- C15 TmdbMissingEpisodeProvider.cs:398: the `catch` only writes to the log.

**One declaration (2).**
- C9 ServerConfiguration.cs:115: the defaults are declared once in the settings schema, and the sorting code reads them from the configuration.
- C9 LibraryController.cs:1023: one table in a `switch`; the repeated set in the `_` branch is a single one, no divergence is visible.

**Kind by type hierarchy, the action does not change (C8, 15 places from the sample).** Dto/DtoService.cs:1192, 1698; LibraryChangedNotifier.cs:362; LibraryManager.cs:331; UserDataManager.cs:465; SessionManager.cs:1484; ItemsController.cs:295; LibraryController.cs:830; BaseItem.cs:2108; Folder.cs:254, 957, 1776; Video.cs:381; ProviderManager.cs:558, 589. They formally match the `is not <Type>` template, but they choose what to write into a DTO, NFO or query. The choice is determined by the class type, and a new kind cannot appear at run time. The user loses nothing. The other 12 C8 places of the same form (LocalImageProvider, BaseXmlSaver, BaseNfoSaver, ImageSaver, ItemImageProvider.cs:117, MetadataService.cs:1264, LyricScheduledTask.cs:111) were not opened; the verdict by template is: probably false.

## Count

64 places: confirmed 21 (3 with noticeable consequences: RecordingsManager:408, ExceptionMiddleware:57, OptimisticLockBehavior:58; 18 formal, without harm), false 43 (of them 12 C8 places were not opened, verdict by template). Not among the 64, found nearby: PluginManager.cs:648, 694 (direct writes of the plugin status). DeepSeek flash was wrong most often on C15: 6 of 18 are false, and one "unclear" turned out to be confirmed.

## Three heaviest

### 1. RecordingsManager.cs:372-417: a stop by the server gives Completed without a retry

Scenario:
1. A series recording is in progress, the programme has not ended.
2. The administrator restarts the server (`RecordingsManager.Dispose` calls `CancellationTokenSource.Cancel()` on all active recordings).
3. `RecordStream` catches `OperationCanceledException` and sets `recordingStatus = Completed`; the retry condition `recordingStatus != Completed` is false.
4. The file exists, the timer is saved with `Status = Completed`; the rest of the stream is not recorded, and nobody will retry it until the series refresh runs (`existingTimer.Status = New` at line 753 applies only to non-manual timers).
5. The user sees "recorded" on a truncated recording.

Minimal fix: in `catch (OperationCanceledException)` distinguish the cause (user cancel or server stop) and in the second case set a status that triggers the retry. Caveat: checked by reading, there was no live run; the handler may not have time to write the timer when the process shuts down.

### 2. ExceptionMiddleware.cs:96-102: one reason for all exceptions

Scenario:
1. The administrator renames a library in the panel; the directory has no write permission.
2. `_directoryService.Move` throws `UnauthorizedAccessException`, and `GetStatusCode` returns 500 (the list has only ArgumentException, AuthenticationException, SecurityException, files, ResourceNotFound).
3. The response is "Error processing request." (not Development).
4. The panel shows a generic error; the reason is only in the server log.

Minimal fix: in `GetStatusCode` and in the response, add a refusal code from an enumeration (permissions, disk, database) for the expected exception classes, and keep the text "Error processing request." for everything else.

### 3. OptimisticLockBehavior.cs:58: retry by text

Scenario:
1. An update of SQLite or the driver changes the wording "database is locked".
2. `HandleInner` does not fire, and the policy does not retry.
3. Parallel writes during a library scan fail on the first attempt.
4. The administrator sees errors in the log and an incomplete library.

Minimal fix: a condition on `SqliteException.SqliteErrorCode` (5 is SQLITE_BUSY, 6 is SQLITE_LOCKED) instead of `Message.Contains`.
