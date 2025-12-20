import { useFeedStore } from "../store/feedStore.js";
import { useState, useEffect } from "react";
import "../components/Navbar.css";


export default function Navbar() {

  const [inputValue, setInputValue] = useState('');
  const { searchQuery, isSearching, setSearchQuery, performSearch, clearSearch } = useFeedStore();

  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue.length >= 2) {
        performSearch(inputValue);
      } else if (inputValue === 0) {
        clearSearch();
      } 
    }, 300)
    return () => clearTimeout(timer)
  }, [inputValue]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  }

  const handleClear = () => {
    setInputValue('')
    clearSearch()
  }

  return (
    <div className="navbar bg-gray-900 shadow-2xl px-6 sticky top-0 z-50">
      
      {/* LEFT */}
      <div className="navbar-start">
        <a
          className="text-3xl font-extrabold 
                     text-transparent bg-clip-text 
                     bg-gradient-to-r from-sky-400 via-indigo-500 to-pink-600 
                     animate-gradient-flow"
        >
          priodex
        </a>
      </div>

      {/* SEARCH BAR */}
      <div
        className="
          absolute 
          right-4 
          lg:left-1/2 lg:right-auto 
          lg:-translate-x-1/2
        "
      >
        <div className="relative w-56 sm:w-64 lg:w-96">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Search..."
            className="w-full rounded-full bg-gray-800 text-gray-100 
                       placeholder-gray-400 px-5 py-2 
                       focus:outline-none focus:ring-2 
                       focus:ring-indigo-500"
          />
          {/* Loading Spinner or Search Icon */}
          <span className="absolute right-10 top-1/2 -translate-y-1/2 text-gray-400">
            {isSearching ? (
              <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              '🔍'
            )}
          </span>
          
          {/* Clear Button (X) */}
          {inputValue && (
            <button
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 
                       text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

    </div>
  );
}
