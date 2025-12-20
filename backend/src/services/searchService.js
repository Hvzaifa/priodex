import { Trie }  from "../dsa/trie.js";
import Article from "../models/articles.js";

let globalTrie = null;

export const buildSearchIndex = async () => {  
    const articles = await Article.find({});
    const tempTrie = new Trie();
    
    for (const article of articles) {
        const titleArray = article.title.split(" ");
        for (const word of titleArray) {
            if (word.length > 2 || word == 'AI') {  
                const cleanWord = word.replace(/[^\w\s]/g, ''); 
                if (cleanWord) {
                    tempTrie.insert(cleanWord, article._id);
                }
            }
        }
        
        if (article.keywords && article.keywords.length > 0) {
            for (const keyword of article.keywords) {
                tempTrie.insert(keyword, article._id);
            }
        }
    }
    
    globalTrie = tempTrie;
    console.log('Search index built');  
}

export function searchArticles(query) {
    if (!globalTrie) return [];  
    return globalTrie.searchPrefix(query);  
}

export function getTrie() { 
    return globalTrie;
}