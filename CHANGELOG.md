# Changelog

All notable changes to MetaFlow Clockwork are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-21

### Added

- deterministic `MetaTag` and `ClockworkEngine` runtime
- append-only ledger emission with `events.jsonl` and `events.sha256`
- ledger summary, replay, and verification commands
- run-spec validation and execution for checked-in JSON specs
- Apache-2.0 OSS baseline
- public docs, contributor guidance, and GitHub CI
- source-tree and built-artifact validation path
- public prompt hygiene, prompt template, and self-contained execution doctrine docs
- public example role contract and prompt validation test

### Notes

- public package line is `metaflow-clockwork`
- import path is `metaflow_clockwork`
- the public repo should avoid the bare `metaflow` name to prevent confusion with Netflix Metaflow
- the public 0.1.0 line intentionally excludes live QRBT bridge execution
- legacy `QRBTBridge`, `QRBTBridgeError`, `validate --profile-id/--op`, and `bridge-envelope` remain only as compatibility notices that report the removed surface
