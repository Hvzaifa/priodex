import { MaxHeap } from "../dsa/maxHeap.js";
import Article from "../models/articles.js";
import { calculatePriority } from "../utils/priorityScore.js";

let globalHeap = null;

export const buildPriorityHeap = async () => {
    const articles = await Article.find({});
    const tempHeap = new MaxHeap();
    for (const article of articles) {
        const priorityScore = calculatePriority(article);
        tempHeap.insert(article, priorityScore);
    }
    globalHeap = tempHeap;
    console.log('Priority heap built'); 
}

export function getTopArticles(limit = 25) {
    if (!globalHeap || globalHeap.heap.length === 0) return [];

    const results = [];
    const tempHeap = new MaxHeap();

    // Cloning Heap to make sure data in the original isn't lost
    for (const item of globalHeap.heap) {
        tempHeap.insert(item.article, item.score);
    }

    const actualLimit = Math.min(limit, tempHeap.heap.length);  
    for (let i = 0; i < actualLimit; i++) {
        results.push(tempHeap.extractMax().article);
    }

    return results;
}