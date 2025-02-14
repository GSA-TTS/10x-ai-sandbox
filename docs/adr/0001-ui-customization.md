# 1. UI Customizations

Date: 2025-02-12

## Status

Accepted

## Context

This project relies on an open source project called Open Web UI. When Open Web UI is updated, it is a wholesale update that includes front end and backend changes. We need a way to customize the UI where we can override the default Open Web UI interface in a granular way and still use the default Open Web UI where appropriate. We want to be able to preserve our customizations without fear of losing them due to an update coming from the upstream dependency.

## Decision

There is now a directory called `src/upstream-overrides` that allows selective route overrides for the Open Web UI default routes that are located in `src/routes`.

## Consequences

Any page and layout customizations should be done by copying the file from `src/routes` to an identical relative path within the `src/upstream-overrides` directory. In other words, to make changes to the file `src/routes/(app)/+page.svelte` file, create a copy of that file and place it at `src/upstream-overrides/(app)/+page.svelte`.

There are mechanisms during the build process and during local development to maintain behavior like hot reloading and to make sure the expected file is the one that is rendered in the application UI.

This will safeguard the UI from getting overridden by upstream changes as Open Web UI is updated.

## Alternatives considered

Alternative solutions involving Sveltekit `hooks` and a separate solution evaluating Sveltekit's advanced routing was also considered before making the decision.
