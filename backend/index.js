import express from 'express';
import cors from 'cors';
import { connectDB } from "./src/config/database.js";
import articleRoutes from "./src/routes/articles.route.js"
import { buildSearchIndex } from './src/services/searchService.js';
import { buildPriorityHeap } from './src/services/heapService.js';
import { buildArticleCache } from './src/services/cacheService.js'; 
import dotenv from 'dotenv';


dotenv.config();

const app = express();

app.use(cors({
    origin: "http://localhost:5173",
    credentials: true
}));

app.use(express.json());

app.use("/articles", articleRoutes)

app.get('/', (req, res) => {
    res.json({message: 'TechStream Radar API is running'})
})

async function initializeDSAs() {
    try {
        console.log('Initializing data structures...')

        await buildArticleCache();
        await buildSearchIndex();
        await buildPriorityHeap();

        console.log('DSAs initializion successful ');
    } catch (error) {
        console.error('Failed to initialize DSA: ', error);
        process.exit(1);
    }
}

const PORT = process.env.PORT;

app.listen(PORT, async() => {
    try {
        await connectDB();

        await initializeDSAs();

        console.log("Server is running on port:" + PORT);
    } catch (error) {
        console.error('Failed to start server: ', error);
    }
})