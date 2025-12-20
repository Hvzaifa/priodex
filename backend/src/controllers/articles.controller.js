import Article from "../models/articles.js"
import { getTopArticles } from "../services/heapService.js";
import { getArticleById, getArticlesByIds } from "../services/cacheService.js";
import { searchArticles } from "../services/searchService.js";
import Summary from "../models/summary.js";
import mongoose from "mongoose";


export const getAllFeed = async (req, res) => {
    try {
        const topArticles = getTopArticles(25);

        res.status(200).json({
            success: true,
            count: topArticles.length,
            data: topArticles
        });
    } catch (error) {
        console.error('Error fetching articles: ', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch articles'
        });
    }
};

export const displaySelectedCard = async (req, res) => {
    try {
        const articleId = req.params.id;

        const article = getArticleById(articleId);

        if (! article) {
            return res.status(404).json({
                success: false,
                message: 'Article not found'
            });
        }

        res.status(200).json({
            success: true,
            data: article
        });
    } catch (error) {
        console.error('Error fetching article: ', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch article'
        });
    }
}

export const displaySummarizedArticle = async (req, res) => {
    try {
        const articleId = req.params.id;
        const objectId = new mongoose.Types.ObjectId(articleId);

        const summary = await Summary.findOne({articleId: objectId});

        if (!summary) {
            return res.status(404).json({
                success: false,
                summary: 'Summary not available for article'
            });
        }

        res.status(200).json({
            success: true,
            data: summary
        });
    } catch (error) {
        console.error('Error fetching summary: ', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch summary'
        });
    }
};

export const searchArticleTitle = async (req, res) => {
    try {
        const query = req.query.q;

        if (!query || query.length < 2) {
            return res.status(400).json({
                success: false,
                message: 'Search query must be atleast 2 characters'
            });
        }

        // search using Trie (returns article IDs)
        const articleIds = searchArticles(query.trim());

        if (! articleIds || articleIds.length === 0) {
            return res.status(200).json({
                success: false,
                count: 0,
                data: []
            });
        }
        // get full article data from cache
        const articles = getArticlesByIds(articleIds);

        // Filter out any undefined/null articles
        const validArticles = articles.filter(article => article !== null && article !== undefined);

        // limiting results to 15
        const limitedResults = articles.slice(0, 15);

        console.log(`🔍 Search "${query}": Found ${articleIds.length} IDs, ${validArticles.length} valid articles`);
        
        res.status(200).json({
            success: true,
            count: limitedResults.length,
            data: limitedResults
        });
    } catch (error) {
        console.error('Error searching articles: ', error);
        res.status(500).json({
            success: false,
            message: 'Search failed'
        });
    }
};
