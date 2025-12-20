import { create } from 'zustand';
import { axiosInstance } from '../lib/axios.js';
import toast from 'react-hot-toast';

export const useFeedStore = create((set, get) => ({
    allArticles: [],
    searchQuery: '',
    searchResults: [],
    searchActive: false,
    isSearching: false,
    loading: false,

    fetchArticles: async () => {
        set({ loading: true});
        
        try {
            const response = await axiosInstance.get("/articles");
            
            if (response.data.success) {
                set({ 
                    allArticles: response.data.data, 
                    loading: false 
                });
                toast.success(`✓ Loaded ${response.data.count} articles`);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {            
            set({ 
                loading: false,
                allArticles: []
            });
            console.error('Error in useFeedStore while fetching articles:', error);
        }
    },

    fetchSummary: async (articleId) => {
        try {
            const response = await axiosInstance.get(`/articles/${articleId}/summary`);
            
            if (response.data.success) {
                toast.success('Summary generated');
                return response.data.data.summary;
            } else {
                toast.error('Summary not available');
                return null;
            }
        } catch (error) {
            console.error('Error fetching summary:', error);
            
            if (error.response?.status === 404) {
                toast.error('No summary available for this article');
            } else {
                toast.error('Failed to fetch summary');
            }
            return null;
        }
    },

    setSearchQuery: (query) => {
        set({ searchQuery: query });
    },

    performSearch: async (query) => {
        if (query.length < 2) {
            return;
        }
        set({ isSearching: true });
        try {
            const response = await axiosInstance.get(`/articles/search?q=${query}`)
            set({ searchResults: response.data.data, searchActive: true, isSearching: false });
        } catch (error) {
            toast.error('Failed to search');
            console.error('Error in while performing search: ', error);
        }
    },

    clearSearch: () => {
        set({searchQuery: '', searchResults: [], searchActive: false});
    }
}));