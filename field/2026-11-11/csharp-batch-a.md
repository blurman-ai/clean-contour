# C# batch A: Radarr, duplicati, MassTransit

Read on 11 November 2026 (shallow clones of the default branches): DeepSeek flash gave a verdict on every candidate found by the cards' C# search signs, and Sonnet read what it flagged, with whole files and callers. Not reproduced on a running instance.

Scope of the reading: all 55 flagged places were read (no sampling of C4 and C6 was needed; there are at most 19 per card per repo). The state-machine files and the places that decide behavior were read whole with their callers; pure mapping functions (download client adapters) were read as whole methods.

Verdicts: "dirty" means the card's questions are answered yes after reading the callers. The consequence column says what the user or operator sees. Several dirty C4 places are marked "low": the state is written inline, but nothing visible breaks.

## Radarr

Count: 30 flagged, 9 dirty, 21 false. DeepSeek said dirty on 27 and unclear on 3; after reading, 9 stay dirty, 1 unclear (CompletedDownloadService.cs:152) became dirty, 2 unclear (C11) became false.

### Confirmed, by consequence

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C4 | src/NzbDrone.Core/Download/CompletedDownloadService.cs:152 (and :119, :203, :239) | dirty | `Import` sets the tracked download to `Importing` (line 139), then calls the import service; if that call throws (listing the folder, reading files, a database error), `DownloadProcessingService.Execute` catches it and logs at Debug level only, and the state stays `Importing`. `Check`, `ProcessFailed` and `Execute` act only on `Downloading`, `ImportBlocked`, `ImportPending` and `FailedPending`, and `TrackDownload` keeps an existing item that is not `Downloading`, so the download shows as importing in the queue and is never retried until the application restarts (the cache is in memory). The `ImportPending` reset on line 152 runs only on the non-exception path. |
| C4 | src/NzbDrone.Core/Download/Clients/RQBit/RQBit.cs:87 | dirty | `RQbitProxy` computes `HasError` from the torrent state (Error, Invalid) but nothing reads it; the status is built from `IsFinished` and `IsActive` only, so a torrent in error shows as Paused with the error text in the message. Failed-download handling (which needs Failed or Warning) never starts, and the user sees "Paused" for a broken torrent. |
| C6 | src/Radarr.Http/ErrorManagement/RadarrErrorPipeline.cs:71 | dirty | An API PUT or POST that hits a SQLite constraint returns HTTP 409 only if the exception message contains "constraint failed"; otherwise it returns 500. `SQLiteException.ResultCode` is available and already used elsewhere in the repo (`BasicRepository.cs:59`). Low: SQLite messages are not localized. |
| C6 | src/NzbDrone.Core/Indexers/HttpIndexerBase.cs:444 | dirty | The indexer "test" button picks the text "indexer's server is unavailable" by searching `WebException.Message` for 502/503/504/"timed out". When none of the strings match and the status is not name-resolution or connect failure, the `catch` falls through to `return null`, which the caller treats as a successful test. Low: modern HTTP calls throw `HttpException`/`HttpRequestException`, so this path is rarely reached. |
| C4 | src/NzbDrone.Core/Download/CompletedDownloadService.cs:119, :203, :239 | dirty (low) | `TrackedDownload.State` is written inline in 12 places over 4 files (`CompletedDownloadService`, `FailedDownloadService`, `ManualImportService`, `TrackedDownloadService`), with no table of allowed transitions and no failure transition for the `Importing` wait. This is the structural cause of the first row; the lines themselves show nothing wrong to the user. |
| C4 | src/NzbDrone.Core/Download/FailedDownloadService.cs:77 | dirty (low) | Same state, same lack of a writer; `Check` moves to `FailedPending` only when the download was grabbed by Radarr, otherwise it adds a warning. Nothing visible breaks. |
| C4 | src/NzbDrone.Core/MediaFiles/MovieImport/Manual/ManualImportService.cs:508 | dirty (low) | Manual import writes `Imported` directly, parallel to the automatic path; it writes it only if at least one file was imported. Nothing visible breaks. |

### False, grouped by reason

| card | file:line | verdict | reason |
|---|---|---|---|
| C4 | Download/Clients/Blackhole/ScanWatchFolder.cs:158; NzbVortex/NzbVortex.cs:263; Nzbget/Nzbget.cs:171; QBittorrent/QBittorrent.cs:297 and :350; Sabnzbd/Sabnzbd.cs:143; rTorrent/RTorrent.cs:174 (all under src/NzbDrone.Core/) | false | Each builds a new `DownloadClientItem` from the client's response on every poll; there is no stored entity and no state carried between polls. The qBittorrent mapping has an explicit default branch for unknown states that sets a message and logs it. |
| C4 | Download/TrackedDownloads/TrackedDownloadService.cs:124 | false | Initial state of a newly created tracked download, taken from the last download-history event; creation, not a transition. |
| C4 | Messaging/Commands/CommandQueue.cs:211; CommandQueueManager.cs:263 | false | `Dequeue` sets `Started` under the queue lock; `Update` is the single place that writes the final state and ends the command in the repository. |
| C4 | MetadataSource/SkyHook/SkyHookProxy.cs:294; Movies/RefreshMovieService.cs:91 | false | Mapping the TMDb answer into the movie metadata; the `Deleted` write is guarded by a check and followed by an event. |
| C3 | Download/FailedDownloadService.cs:67 | false | Moves the tracked download to `FailedPending` on the client's Failed status; this is a writer reacting to an event of another object, which the card excludes. |
| C3 | Download/Clients/RQBit/RQbitProxy.cs:130 | false | Flags computed from the client's response object; the consequence is in the RQBit.cs:87 row above. |
| C3 | HealthCheck/Checks/RemovedMovieCheck.cs:25 | false | `MovieMetadata.Status` is the movie's own status (the metadata is part of the movie), not another entity's. |
| C11 | Messaging/Commands/CommandQueueManager.cs:84 and :130 | false | `Queued` rows have a recovery path: on application start `OrphanStarted()` marks started commands as `Orphaned` and `Requeue()` reloads queued ones. |
| C6 | Common/Instrumentation/GlobalExceptionHandlers.cs:40 | false | Only chooses a log level for a known SignalR null-reference. |
| C6 | Common/Instrumentation/Sentry/SentryTarget.cs:309 | false | Decides whether an error report goes to Sentry (telemetry only). |
| C6 | Core/ImportLists/HttpImportListBase.cs:113; Core/Indexers/HttpIndexerBase.cs:205 | false | The message text only chooses a log line; the failure is recorded before, by exception status. |

## duplicati

Count: 16 flagged, 6 dirty, 10 false. DeepSeek said dirty on 15 and unclear on 1; after reading, 6 stay dirty, 10 become false.

### Confirmed, by consequence

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C6 | Duplicati/Library/Certificates/Platform/WindowsCATrustInstaller.cs:102 and :149 | dirty | Installing or removing the CA certificate in the Windows store maps `CryptographicException` to `RequiresElevation` only if the message contains "access" or "denied". On a non-English Windows the message is localized, so the result is `Failed`; `HttpsCommand` and `CertificateConfigurationHelper` then show a failure instead of "administrator rights required" and the operator is not told to rerun elevated. The exception's `HResult` (access denied) is not used. |
| C6 | Duplicati/Library/Backend/Rclone/Rclone.cs:184 | dirty | The backend throws `FolderMissingException` only if rclone's stderr contains the English text "directory not found". `BackendManager` and `RestoreHandler` use that exception type to create the folder automatically on the first backup. If a rclone version words it differently, the first backup to a new folder fails with a generic exception. In addition, any text on stderr (even a notice) throws a generic exception and discards the `killed` flag. |
| C6 | Duplicati/Library/Backend/FTP/FTPBackend.cs:469 | dirty | A PureFTPd listing is rejected as truncated only when reply code 226 and the English word "truncated" appear. If the server's text differs, the incomplete listing is used; the code comment says this "can lead to misleading backup/restore results" (files missing from the listing are treated as absent). |
| C6 | Duplicati/Library/Backend/FTP/FTPBackend.cs:834 | dirty | The switch to the Bouncy Castle TLS implementation (after a TLS session-resumption refusal) happens on code 522, or on code 425 with the word "resum" in the message. If a server words 425 differently, no fallback happens and the transfer fails with the TLS error. |
| C6 | proprietary/Office365/APIHelper.cs:362 | dirty (low) | HTTP status is checked first, then the message must contain "app-only" (OneNote) or "/todo/" (To Do) to classify the failure as "not available for this authentication"; if Microsoft changes the text, the source is reported as an error instead of being skipped. |

### False, grouped by reason

| card | file:line | verdict | reason |
|---|---|---|---|
| C2 | Duplicati/WebserverCore/Services/TaskQueueService.cs:64 | false | The flagged line is the not-found branch: a task absent from the queue with no cached result throws `NotFoundException`; "Waiting" is returned only for a task that is in the queue. |
| C4 | Library/Main/Operation/Common/TaskControl.cs:227; Library/RestAPI/LiveControls.cs:188 and :221 | false | These are the owning classes' own transition methods (`Resume`, `Init`, settings refresh), under a lock and with guards on the old value; the state is in memory and restored from settings at start. |
| C4 | Library/AutoUpdater/UpdateInstallCompletion.cs:100; UpdateHelper/HelperSession.cs:238 | false | `Stage` in the install result is the stage name recorded at the point of failure in a one-shot report, not a lifecycle that moves on. |
| C4 | Library/Backend/Duplicati/DuplicatiBackend.cs:457 | false | Caches the account information from the server's answer; it is data from the response, not a lifecycle state. |
| C4 | Library/Certificates/CertificateConfigurationHelper.cs:559 | false | Copies the installer's returned status into the result object. |
| C4 | Library/RestAPI/Runner.cs:964 | false | There is no state assignment on the flagged lines. |
| C6 | Library/Main/Database/ReusableTransaction.cs:157 | false | The exception type is checked first; the message prefix only narrows it, no typed member exists (the code comment says so), and the effect is to ignore a dispose of an already finished transaction. |

## MassTransit

Count: 9 flagged, 4 dirty, 5 false. DeepSeek said dirty on all 9; after reading, 4 stay dirty and 5 become false.

### Confirmed, by consequence

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C6 | src/Transports/MassTransit.RabbitMqTransport/RabbitMqTransport/Configuration/RabbitMqHostConfiguration.cs:45 | dirty | The retry policy for the receive transport retries a `NotSupportedException` only if its message contains "Pipelining of requests forbidden". If the client library changes the text, the exception is not retried and the receive endpoint stays faulted instead of reconnecting. |
| C6 | src/Transports/MassTransit.AmazonSqsTransport/AmazonSqsTransport/AmazonSqsClientContext.cs:78 | dirty | Subscribing a queue to a topic recovers from "subscription already exists" (reads the existing subscription and updates its attributes) only when `InvalidParameterException.Message` contains "exists". If AWS changes the text, the exception is thrown out of topology setup and the endpoint does not start. |
| C6 | src/Transports/MassTransit.Azure.ServiceBus.Core/AzureServiceBusTransport/ServiceBusSendTransportContext.cs:148 | dirty (low) | Cancelling a scheduled message ignores `InvalidOperationException` only if the message contains "already being cancelled"; otherwise the cancel throws to the caller. |
| C6 | src/Persistence/MassTransit.EntityFrameworkCoreIntegration/EntityFrameworkCoreIntegration/BusOutboxDeliveryService.cs:202 | dirty (low) | A concurrent update or transient failure of the outbox delivery is recognized by "concurrent update" or "transient failure" in the inner exception message. With a localized database message (PostgreSQL `lc_messages`) the failure is logged as an error and the transaction is rolled back; the delivery loop continues, so nothing gets stuck, only error log noise. |

### False, grouped by reason

| card | file:line | verdict | reason |
|---|---|---|---|
| C3 | src/MassTransit/JobService/JobService/SuperviseJobConsumer.cs:37 | false | The response reports the status of the in-process task that runs the job (the runtime fact); the stored job state lives in the saga and is not read here. |
| C4 | src/MassTransit/JobService/JobStateMachine.cs:608 | false | `JobState` is a dictionary of user job data (`Dictionary<string, object>`), not the state of the saga; the saga state is `CurrentState`, changed by the state machine. |
| C4 | src/MassTransit/MassTransitBus.cs:399 | false | The bus handle's own stop routine; it has a failure state (`Faulted`) with the exception recorded in the health message, and an observer call for the failure. |
| C4 | src/MassTransit/Transports/HealthResultReceiveEndpointObserver.cs:29 | false | The observer's transitions are guarded by an explicit list of allowed previous states in each method; the state is in memory and used for health reporting. |
| C4 | src/MassTransit/Util/TaskUtil.cs:343 | false | The class's own `ShutDown`, under a lock, with a guard on the old value. |

## Heaviest confirmed places

### 1. Radarr: a download stuck in `Importing` after an exception

Place: src/NzbDrone.Core/Download/CompletedDownloadService.cs:139 and src/NzbDrone.Core/Download/DownloadProcessingService.cs (the `catch` in `Execute`).

Steps to reproduce:
1. Take a completed download that is in `ImportPending` (a grabbed movie, completed download handling on).
2. Make the import service throw before it returns a result list (for example remove read permission on the download folder so listing video files throws, or make the database throw).
3. Run `ProcessMonitoredDownloadsCommand`. The exception is logged at Debug and swallowed.
4. Run the command again. The download still has state `Importing` and is neither imported nor retried; the queue shows it as importing.

Minimal fix: in `CompletedDownloadService.Import`, wrap the `ProcessPath` call so that an exception moves the state to `ImportBlocked` (with a warning carrying the reason) or back to `ImportPending`; or, in the `Execute` catch, reset a state left at `Importing`.

Test without external services: yes. Radarr's fixtures for `CompletedDownloadService` and `DownloadProcessingService` use mocks (no database, no network). A test sets the mocked `ProcessPath` to throw, calls `Execute`, and asserts that the state is not `Importing`; it fails before the fix.

### 2. duplicati: Windows CA trust install classified by localized message

Place: Duplicati/Library/Certificates/Platform/WindowsCATrustInstaller.cs:102 and :149.

Steps to reproduce:
1. On a Windows machine with a non-English display language, run the HTTPS configuration tool as a normal user and ask it to install the generated CA certificate into the machine store.
2. The store open or add throws `CryptographicException` with a localized access-denied message.
3. The tool reports a failed installation, not the "requires elevation" status.

Minimal fix: classify by `ex.HResult` (access denied, 0x80070005) or catch `UnauthorizedAccessException` first and use the HResult for `CryptographicException`; drop the message check.

Test without external services: yes, after extracting the classification into a static function that takes the exception (it is inline in a `catch` now). A pure unit test passes `new CryptographicException("Zugriff verweigert")` with HResult set to access denied and expects `RequiresElevation`; it fails before the fix. The store itself cannot be exercised on Linux, so the extracted function is the testable unit.

### 3. duplicati: rclone "directory not found" recognized by English stderr text

Place: Duplicati/Library/Backend/Rclone/Rclone.cs:184.

Steps to reproduce:
1. Point the rclone backend at a remote folder that does not exist, with auto-create of folders on.
2. Use an rclone binary whose error text for a missing directory differs from "directory not found" (a different version, or a wrapper script).
3. The first backup fails with a generic exception instead of creating the folder.

Minimal fix: also check the process exit code (rclone documents exit code 3 for "directory not found"; not verified in this read) before the text match, and throw `FolderMissingException` on it.

Test without external services: yes. The backend runs an executable chosen by an option, so a test points it at a small shell script that prints a different message to stderr and exits with code 3, then calls list and expects `FolderMissingException`; it fails before the fix. No rclone, network or account is needed.

### Not in the heaviest three

The MassTransit transport retry and subscribe text checks (RabbitMQ, SQS) would need a library exception with different wording to demonstrate; there is no typed member to assert on, so a failing test needs the fix design first. The duplicati FTP truncation check needs a FluentFTP client double and is heavier to build.

## Found while reading, outside the list

Radarr, src/NzbDrone.Core/Download/Clients/Sabnzbd/Sabnzbd.cs:140: a SABnzbd history item is treated as Warning (not Failed) only when `FailMessage` equals the English text "Unpacking failed, write error or disk is full?". Any other wording makes it Failed, which starts failed-download handling (the release is marked failed and a search for another release can start). This is a decision by message text that the C6 search did not flag.
