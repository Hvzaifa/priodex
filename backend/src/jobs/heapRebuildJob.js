import Article from "../models/articles.js";
import { buildArticleCache } from "../services/cacheService.js";
import { buildSearchIndex } from "../services/searchService.js";
import { buildPriorityHeap } from "../services/heapService.js";

// One query feeds all three structures, so they always describe the same articles
export const rebuildIndexes = async () => {
    const articles = await Article.find({});

    buildArticleCache(articles);
    buildSearchIndex(articles);
    buildPriorityHeap(articles);
}
