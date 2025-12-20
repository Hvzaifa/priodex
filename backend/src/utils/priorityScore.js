
// Calculating priority based on recency and category
export function calculatePriority (article) {
    const timeNow = Date.now();
    let articleAge = timeNow - new Date(article.scrapedDate).getTime();
    const hoursOld = articleAge / (1000 * 60 * 60);

    // Decays exponentially: 100 at 0 hours, ~37 at 24 hours, ~14 at 48 hours
    const recencyScore = 100 * Math.exp(-hoursOld / 24);

    const categoryWeights = {
        'AI': 10,
        'Startups': 9,
        'BlockChain': 8.5,
        'Data': 8,
        'Science': 7.5,
        'Cloud': '7.2',
        'Cybersecurity': 7,
        'Developer': 6.5,
        'Cloud Computing': 6.3,
        'Programming': 6,
        'Hardware': 5,
        'default': 3
    };

    // Get highest category weight for this article
    const categoryScore = article.categories && article.categories.length > 0
        ? Math.max(...article.categories.map(cat => categoryWeights[cat] || categoryWeights.default))
        : categoryWeights.default;
    
    // Final score: weighted combination
    return (recencyScore * 0.7) + (categoryScore * 0.3);
}

