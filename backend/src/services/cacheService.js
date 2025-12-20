import Article from "../models/articles.js";

const articleCache = new Map();

export const buildArticleCache = async () => {
    const articles = await Article.find({});
    articleCache.clear();
    for (const article of articles) {
        articleCache.set(article._id.toString(), article);
    }
    console.log(`Article cache built with ${articles.length} articles`);
}

export function getArticleById(articleId) {
    return articleCache.get(articleId.toString());
}

export function hasArticle(articleId) {
    return articleCache.has(articleId.toString());
}

export function getArticlesByIds(articleIds) {
    console.log('📦 Getting articles for IDs:', articleIds.length);
    
    const articles = articleIds
        .map(id => {
            const article = articleCache.get(id.toString());
            if (!article) {
                console.warn(`Article not found in cache: ${id}`);
            }
            return article;
        })
        .filter(article => article !== undefined);
    
    console.log('Retrieved articles:', articles.length);
    return articles;
}