# External OSS contributions

Updated 2026-11-14 (Moscow). This is a handoff ledger, not a substitute for the live GitHub status. Recheck the linked PR before acting.

| Contribution | Current state | Next step |
| --- | --- | --- |
| [Elsa #9230](https://github.com/elsa-workflows/elsa-core/pull/9230) | Review changes pushed in `1e44b212`; 43 tests pass; reviewer feedback answered | Wait for Code Review and CI on new head |
| [Prefect schedule slugs #23849](https://github.com/PrefectHQ/prefect/pull/23849) | Type fix pushed in `f8d034645`; 18 API tests and Pyright pass; maintainer answered | Wait for review and CI; reviewer re-request was denied by GitHub permissions |
| [Prefect transfer #23848](https://github.com/PrefectHQ/prefect/pull/23848) | Missing-pool descendant fix pushed in `c7b547f75`; 64 tests pass; maintainer answered | Wait for review and CI |
| [Ombi #5492](https://github.com/Ombi-app/Ombi/pull/5492) | Pending reset fix pushed in `0f1fcf4`; 24 tests pass; review thread answered | Wait for maintainer |
| [crewAI #9440](https://github.com/crewAIInc/crewAI/pull/9440) | New PR with original patch, linked to reproducible [issue #9438](https://github.com/crewAIInc/crewAI/issues/9438); focused tests pass | Wait for first-contributor gate and review; old #9368 closed by bot |
| [Radarr #12088](https://github.com/Radarr/Radarr/pull/12088) | [Issue #12097](https://github.com/Radarr/Radarr/issues/12097) filed with real trace and steps; linked on PR | Maintainer to assess; Blackhole reproduction confirms cleanup exception, not stable-ID Importing persistence |
| [Tuti #530](https://github.com/omnivision-solutions/tuti/pull/530) | Open; CLA signed, but old CLA check red; bot review flags a race in failure cleanup | Fix race and rerun/check CLA before requesting merge |
| [SimplCommerce #1155](https://github.com/simplcommerce/SimplCommerce/pull/1155) | Open; FOSSA checks were red on upstream master too | Wait for maintainer |
| [eShop #1077](https://github.com/dotnet/eShop/pull/1077), [Hangfire #2599](https://github.com/HangfireIO/Hangfire/pull/2599), [BTCPay #7800](https://github.com/btcpayserver/btcpayserver/pull/7800), [Smartstore #1606](https://github.com/smartstore/Smartstore/pull/1606), [wairz #1](https://github.com/ander1044/wairz/pull/1) | Open, no outstanding human change request found on 2026-11-14 | Wait for maintainers |
| [mvidarr #582](https://github.com/prefect421/mvidarr/pull/582) | Patch incorporated in maintainer's merged #589; original closed | Done |
| [zot #4574](https://github.com/project-zot/zot/pull/4574) | Superseded by maintainer's merged #4622; [issue #4573](https://github.com/project-zot/zot/issues/4573) closed | Done |
| [career-ops #4085](https://github.com/career-ops-hq/career-ops/issues/4085) | Closed after #4235 fixed it | Done |

Earlier architecture PRs: [Traffic Server #13403](https://github.com/apache/trafficserver/pull/13403) and [Gambit #1](https://github.com/abhi-saurav-saroya/Gambit/pull/1)/[#2](https://github.com/abhi-saurav-saroya/Gambit/pull/2) merged; [gRPC #43010](https://github.com/grpc/grpc/pull/43010) and [Envoy #46370](https://github.com/envoyproxy/envoy/pull/46370) closed without merge (Envoy after a real CI failure and inactivity); [RocksDB #14944](https://github.com/meta/rocksdb/pull/14944) remains open.

Local evidence from this follow-up is in `/home/localadm/projects/clean-contour-oss-2026-11-11/evidence/2026-11-14/`. The original Claude session is `/home/localadm/.claude/projects/-home-localadm-projects-clean-contour/2cdbf851-d4a7-4558-9fe3-79638b779421.jsonl`.
