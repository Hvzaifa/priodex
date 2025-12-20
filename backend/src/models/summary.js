import mongoose from "mongoose";
import { Schema } from "mongoose";
import Article from "./articles.js"

const summarySchema = new Schema ({
    articleId: {
        type: Schema.Types.ObjectId,
        ref: Article,
        required: true,
        unique: true
    },
    summary: {
        type: String,
        required: true,
    },
    generatedAt: {
        type: Date,
        default: Date.now()
    }
});

const Summary = mongoose.model('Summary', summarySchema);
export default Summary;