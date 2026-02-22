# Proposal: Reset Progress on Progress Page

## Why

The progress page (`/progress`) currently displays two action buttons—"学新词" and "今日复习"—that duplicate functionality already available on the home page. This creates unnecessary UI redundancy. Additionally, users need a way to reset their learning progress for the current cycle, which currently requires manual database manipulation.

## What Changes

- Remove "学新词" and "今日复习" buttons from ProgressView
- Add "重置学习进度" button that:
  - Displays a confirmation dialog before executing
  - Deletes all learning progress for the current cycle
  - Returns user to a fresh state (level 0 for all words)

## Capabilities

### New Capabilities
- `reset-learning-progress`: Users can reset their current learning cycle through the UI

### Modified Capabilities
- `progress-page-ui`: Simplified by removing redundant navigation buttons

## Impact

- `frontend/src/views/ProgressView.vue`: Replace action buttons section with reset button
- `backend/src/wenyanwen/api/v1/review.py`: Add POST `/reset-progress` endpoint
- `frontend/src/api/client.ts`: Add API method for reset
