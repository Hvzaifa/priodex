import { rebuildIndexes } from "./heapRebuildJob.js";

const DEFAULT_REFRESH_MINUTES = 5;

function getRefreshIntervalMs() {
    const minutes = Number(process.env.INDEX_REFRESH_MINUTES);
    const refreshMinutes = minutes > 0 ? minutes : DEFAULT_REFRESH_MINUTES;
    return refreshMinutes * 60 * 1000;
}

// Picks up newly scraped articles and recalculates recency-based priority scores
export function startIndexRefreshJob() {
    let isRefreshing = false;

    setInterval(async () => {
        if (isRefreshing) return;
        isRefreshing = true;

        try {
            await rebuildIndexes();
        } catch (error) {
            // The previous indexes stay in place, so the API keeps serving
            console.error('Failed to refresh indexes: ', error);
        } finally {
            isRefreshing = false;
        }
    }, getRefreshIntervalMs());
}
