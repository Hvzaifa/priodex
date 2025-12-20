import mongoose from "mongoose";
import { Schema } from "mongoose";

const articleSchema = new Schema ({
    title: {
        type: String,
        required: true,
        index: true
    },
    url: {
        type: String,
        unique: true,
        index: true
    },
    source: {
        type: String,
        index: true
    },
    content: {
        type: String,
        required: true
    },
    scrapedDate: {
        type: Date,
        index: true,
        default: Date.now()
    },
    categories: {
        type: [String],
        index: true
    },
    keywords: {
        type: [String]
    },
    processed: {
        type: Boolean,
        index: true
    },
});

const Article = mongoose.model('Article', articleSchema);
export default Article;