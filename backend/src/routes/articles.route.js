import express from "express";
import { getAllFeed, displaySelectedCard, displaySummarizedArticle, searchArticleTitle } from "../controllers/articles.controller.js";
const router = express.Router();


router
    .route("/")
    .get(getAllFeed)

router 
    .route("/search")
    .get(searchArticleTitle)

router
    .route("/:id/summary")
    .get(displaySummarizedArticle)

router
    .route("/:id")
    .get(displaySelectedCard)


export default router;