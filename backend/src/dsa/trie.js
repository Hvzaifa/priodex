// Trie: tree structure for fast prefix-based search
class TrieNode {
    constructor() {
        this.children = {};  // Map of character -> TrieNode
        this.isEndOfWord = false;
        this.articleIds = [];  // Store article IDs that match this word
    }
}

export class Trie {
    constructor() {
        this.root = new TrieNode();
    }
    
    // Add word to trie with associated article ID
    insert(word, articleId) {
        let node = this.root;
        word = word.toLowerCase();  // Case-insensitive
        
        for (const char of word) {
            if (!node.children[char]) {
                node.children[char] = new TrieNode();
            }
            node = node.children[char];
        }
        
        node.isEndOfWord = true;
        if (!node.articleIds.includes(articleId)) {
            node.articleIds.push(articleId);
        }
    }
    
    // Find all words with given prefix
    searchPrefix(prefix) {
        let node = this.root;
        prefix = prefix.toLowerCase();
        
        // Navigate to prefix node
        for (const char of prefix) {
            if (!node.children[char]) {
                return [];  // Prefix doesn't exist
            }
            node = node.children[char];
        }
        
        // Collect all article IDs from this point
        return this._collectArticleIds(node);
    }
    
    // Recursively collect all article IDs from node downward
    _collectArticleIds(node) {
        let results = [...node.articleIds];
        
        for (const child of Object.values(node.children)) {
            results = results.concat(this._collectArticleIds(child));
        }
        
        return [...new Set(results)];  // Remove duplicates
    }
}

