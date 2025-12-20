import { useFeedStore } from "../store/feedStore.js";
import { useEffect, useState } from "react";
import "../pages/HomePage.css";

export default function Example() {
    // 1. Get state from store
    const { 
        allArticles, 
        fetchArticles, 
        loading, 
        fetchSummary, 
        searchResults,      
        searchActive,      
        isSearching,                 
    } = useFeedStore();
    
    // 2. Local states
    const [loadingSummaryFor, setLoadingSummaryFor] = useState(null);
    const [summaries, setSummaries] = useState({});

    // 3. Effects
    useEffect(() => {
        fetchArticles();
    }, [fetchArticles]);

    // 4. ✅ NEW: Determine which articles to display
    const articlesToDisplay = searchActive ? searchResults : allArticles;
    const isLoading = searchActive ? isSearching : loading;

    // Handle summary fetch
    const handleFetchSummary = async (articleId) => {
        // Don't fetch if already loading or already have summary
        if (loadingSummaryFor === articleId || summaries[articleId]) {
            return;
        }

        setLoadingSummaryFor(articleId);
        
        try {
            const summary = await fetchSummary(articleId);
            
            if (summary) {
                setSummaries(prev => ({
                    ...prev,
                    [articleId]: summary
                }));
            }
        } catch (error) {
            console.error('Failed to fetch summary:', error);
        } finally {
            setLoadingSummaryFor(null);
        }
    };

    return (
        <div className="bg-gray-900 overflow-hidden min-h-screen">
            <div className="relative isolate px-6 pt-8 lg:px-8">
                
                {/* Sliding Tags */}
                <div className="py-4">
                    <div className="fade-mask-container">
                        <div className="flex gap-4 sm:gap-6 animate-slide-left whitespace-nowrap">
                            {[...Array(2)].map((_, listIndex) => (
                                <div key={listIndex} className="flex gap-4 sm:gap-6">
                                    {[
                                        "GitHub",
                                        "HackerNews",
                                        "Medium",
                                        "Tech Crunch",
                                        "DevTo",
                                        "Wired",
                                        "Venture Beat",
                                        "Indie Hackers",
                                        "Engadget",
                                        "ML Mastery"
                                    ].map((source) => (
                                        <div 
                                            key={`${source}-${listIndex}`} 
                                            className="relative rounded-full px-4 py-1.5 text-sm 
                                                     bg-gray-800/50 backdrop-blur-sm
                                                     border-2 border-transparent
                                                     bg-gradient-to-r from-sky-400/20 via-indigo-500/20 to-pink-600/20
                                                     hover:from-sky-400/40 hover:via-indigo-500/40 hover:to-pink-600/40
                                                     transition-all duration-300
                                                     shadow-[0_0_15px_rgba(56,189,248,0.3)]
                                                     hover:shadow-[0_0_25px_rgba(56,189,248,0.5)]"
                                        >
                                            <span className="text-gray-200 font-medium cursor-pointer">
                                                {source}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                
                {/* Header */}
                <div className="mx-auto max-w-4xl py-4">
                    <div className="text-center">
                        <h1 className="text-3xl font-bold tracking-tight text-white">
                            <span 
                                className="text-5xl font-extrabold
                                         text-transparent bg-clip-text 
                                         bg-gradient-to-r from-sky-400 via-indigo-500 to-pink-600 
                                         animate-gradient-flow"
                            >
                                PrioDex
                            </span>
                            <br />
                            <span className="text-2xl text-gray-300">
                                Your Hub to Relevant Tech News
                            </span>
                        </h1>
                    </div>
                </div>

                {/* Search Results Header */}
                {searchActive && (
                    <div className="max-w-7xl mx-auto px-4 mb-6">
                        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 
                                    bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-indigo-500/30">
                            <div>
                                <h2 className="text-xl font-semibold text-white">
                                    Search Results
                                </h2>
                                <p className="text-gray-400">
                                    Found {searchResults.length} article{searchResults.length !== 1 ? 's' : ''} matching your search
                                </p>
                            </div>
                            <button
                                onClick={() => {
                                    // Clear search by calling the navbar's clear function
                                    // Or you can import clearSearch from store
                                    const { clearSearch } = useFeedStore.getState();
                                    clearSearch();
                                }}
                                className="px-6 py-2 bg-gray-700 hover:bg-gray-600 
                                        text-white rounded-lg transition-colors
                                        border border-gray-600 flex items-center gap-2"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                Clear Search
                            </button>
                        </div>
                    </div>
                )}

                {/* Articles Grid */}
                <div className="max-w-7xl mx-auto mt-12 px-4 pb-12">
                    {/* Loading State */}
                    {isLoading ? (
                        <div className="text-center text-gray-400 py-12">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
                            <p className="text-xl">
                                {searchActive ? 'Searching...' : 'Loading articles...'}
                            </p>
                        </div>
                    ) : !articlesToDisplay || articlesToDisplay.length === 0 ? ( 
                        <div className="text-center text-gray-400 py-12">
                            {searchActive ? (
                                // Empty search results
                                <>
                                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                    <p className="text-xl mb-2">No results found</p>
                                    <p className="text-gray-500 mb-4">Try different keywords or check your spelling</p>
                                    <button 
                                        onClick={() => {
                                            const { clearSearch } = useFeedStore.getState();
                                            clearSearch();
                                        }}
                                        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 
                                                text-white rounded-lg transition-colors"
                                    >
                                        Back to All Articles
                                    </button>
                                </>
                            ) : (
                                // No articles loaded at all
                                <>
                                    <p className="text-xl">No articles found.</p>
                                    <button 
                                        onClick={fetchArticles}
                                        className="mt-4 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 
                                                text-white rounded-lg transition-colors"
                                    >
                                        Retry
                                    </button>
                                </>
                            )}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {articlesToDisplay.map((article, index) => (
                                <div key={article._id || index} className="group">
                                    {/* Article Card - Click to open modal */}
                                    <label 
                                        htmlFor={`modal-${article._id}`}
                                        className="block bg-gray-800 rounded-lg p-6 
                                                 transition-all duration-300 cursor-pointer 
                                                 border-2 border-gray-700 
                                                 hover:border-indigo-500 hover:shadow-lg
                                                 hover:shadow-indigo-500/20
                                                 hover:-translate-y-1 h-full"
                                    >
                                        {/* Source Badge */}
                                        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                                            <span className="text-xs px-3 py-1 bg-indigo-600 text-white rounded-full font-medium">
                                                {article.source}
                                            </span>
                                            {article.categories && article.categories[0] && (
                                                <span className="text-xs px-3 py-1 bg-gray-700 text-gray-300 rounded-full">
                                                    {article.categories[0]}
                                                </span>
                                            )}
                                        </div>

                                        {/* Title */}
                                        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2 
                                                     group-hover:text-indigo-400 transition-colors">
                                            {article.title}
                                        </h3>

                                        {/* Content Preview */}
                                        <p className="text-gray-400 text-sm line-clamp-3 mb-3">
                                            {article.content}
                                        </p>

                                        {/* Date */}
                                        <p className="text-xs text-gray-500">
                                            {new Date(article.scrapedDate).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                                year: 'numeric'
                                            })}
                                        </p>

                                        {/* Keywords */}
                                        {article.keywords && article.keywords.length > 0 && (
                                            <div className="flex flex-wrap gap-2 mt-3">
                                                {article.keywords.slice(0, 3).map((keyword, i) => (
                                                    <span 
                                                        key={i} 
                                                        className="text-xs px-2 py-1 bg-gray-900 
                                                                 text-gray-400 rounded-md border border-gray-700"
                                                    >
                                                        {keyword}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </label>

                                    {/* Modal for this article */}
                                    <input 
                                        type="checkbox" 
                                        id={`modal-${article._id}`} 
                                        className="modal-toggle" 
                                    />
                                    <div className="modal" role="dialog">
                                        <div className="modal-box max-w-4xl bg-gray-800 text-white max-h-[90vh] overflow-y-auto">
                                            {/* Close button */}
                                            <label 
                                                htmlFor={`modal-${article._id}`}
                                                className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2 
                                                         text-gray-400 hover:text-white hover:bg-gray-700"
                                            >
                                                ✕
                                            </label>

                                            {/* Modal Content */}
                                            <div className="space-y-4 pt-2">
                                                {/* Source and Category */}
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    <span className="px-3 py-1 bg-indigo-600 text-white 
                                                                   rounded-full text-sm font-medium">
                                                        {article.source}
                                                    </span>
                                                    {article.categories && article.categories.map((cat, i) => (
                                                        <span 
                                                            key={i}
                                                            className="px-3 py-1 bg-gray-700 text-gray-300 
                                                                     rounded-full text-sm"
                                                        >
                                                            {cat}
                                                        </span>
                                                    ))}
                                                </div>

                                                {/* Title */}
                                                <h3 className="text-2xl font-bold text-white pr-8">
                                                    {article.title}
                                                </h3>

                                                {/* Date */}
                                                <p className="text-sm text-gray-400">
                                                    Published: {new Date(article.scrapedDate).toLocaleDateString('en-US', {
                                                        weekday: 'long',
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric'
                                                    })}
                                                </p>

                                                {/* Divider */}
                                                <div className="border-t border-gray-700"></div>

                                                {/* Full Content */}
                                                <div className="prose prose-invert max-w-none">
                                                    <p className="text-gray-300 leading-relaxed text-base">
                                                        {article.content}
                                                    </p>
                                                </div>

                                                {/* AI Summary Section */}
                                                {summaries[article._id] && (
                                                    <>
                                                        <div className="border-t border-gray-700"></div>
                                                        <div className="bg-gradient-to-r from-indigo-900/30 to-purple-900/30 
                                                                      rounded-lg p-4 border border-indigo-700/50">
                                                            <div className="flex items-center gap-2 mb-3">
                                                                <svg 
                                                                    className="w-5 h-5 text-indigo-400" 
                                                                    fill="none" 
                                                                    viewBox="0 0 24 24" 
                                                                    stroke="currentColor"
                                                                >
                                                                    <path 
                                                                        strokeLinecap="round" 
                                                                        strokeLinejoin="round" 
                                                                        strokeWidth={2} 
                                                                        d="M13 10V3L4 14h7v7l9-11h-7z" 
                                                                    />
                                                                </svg>
                                                                <h4 className="text-lg font-semibold text-indigo-300">
                                                                    AI Summary
                                                                </h4>
                                                            </div>
                                                            <p className="text-gray-200 leading-relaxed">
                                                                {summaries[article._id]}
                                                            </p>
                                                        </div>
                                                    </>
                                                )}

                                                {/* Keywords */}
                                                {article.keywords && article.keywords.length > 0 && (
                                                    <div>
                                                        <h4 className="text-sm font-semibold text-gray-400 mb-2">
                                                            Keywords
                                                        </h4>
                                                        <div className="flex flex-wrap gap-2">
                                                            {article.keywords.map((keyword, i) => (
                                                                <span 
                                                                    key={i}
                                                                    className="px-3 py-1 bg-gray-900 
                                                                             text-gray-300 rounded-full text-sm
                                                                             border border-gray-700"
                                                                >
                                                                    {keyword}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Action Buttons */}
                                                <div className="flex gap-3 pt-4 flex-wrap">
                                                    <a 
                                                        href={article.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="flex-1 min-w-[200px] px-6 py-3 
                                                                 bg-indigo-600 hover:bg-indigo-700 
                                                                 text-white rounded-lg text-center
                                                                 transition-colors font-medium
                                                                 shadow-lg hover:shadow-xl"
                                                    >
                                                        Read Original Article
                                                    </a>
                                                    <button 
                                                        className={`flex-1 min-w-[200px] px-6 py-3
                                                                 text-white rounded-lg
                                                                 transition-colors font-medium
                                                                 border flex items-center justify-center gap-2
                                                                 ${summaries[article._id] 
                                                                     ? 'bg-green-700 hover:bg-green-600 border-green-600 cursor-default' 
                                                                     : 'bg-gray-700 hover:bg-gray-600 border-gray-600'
                                                                 } ${loadingSummaryFor === article._id ? 'opacity-70 cursor-wait' : ''}`}
                                                        onClick={() => handleFetchSummary(article._id)}
                                                        disabled={loadingSummaryFor === article._id || summaries[article._id]}
                                                    >
                                                        {loadingSummaryFor === article._id ? (
                                                            <>
                                                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                                                <span>Generating...</span>
                                                            </>
                                                        ) : summaries[article._id] ? (
                                                            <>
                                                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                                </svg>
                                                                <span>Summary Generated</span>
                                                            </>
                                                        ) : (
                                                            'Summarize with AI'
                                                        )}
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        <label 
                                            className="modal-backdrop cursor-pointer" 
                                            htmlFor={`modal-${article._id}`}
                                        >
                                        </label>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}