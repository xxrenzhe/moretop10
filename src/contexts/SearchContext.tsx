'use client'

import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Review, ProductCategory, Article } from '@/lib/data'

interface SearchContextType {
  searchQuery: string
  setSearchQuery: (query: string) => void
  selectedCategory: string
  setSelectedCategory: (category: string) => void
  sortBy: string
  setSortBy: (sort: string) => void
  filterBy: string
  setFilterBy: (filter: string) => void
  searchResults: SearchResults
  performSearch: () => void
  isSearching: boolean
}

interface SearchResults {
  reviews: Review[]
  categories: ProductCategory[]
  articles: Article[]
  total: number
}

const SearchContext = createContext<SearchContextType | undefined>(undefined)

export function SearchProvider({ children }: { children: ReactNode }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState('relevance')
  const [filterBy, setFilterBy] = useState('all')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResults>({
    reviews: [],
    categories: [],
    articles: [],
    total: 0
  })

  const performSearch = async () => {
    setIsSearching(true)

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500))

    // Import data dynamically to avoid circular imports
    const { reviews, productCategories, articles } = await import('@/lib/data')

    let filteredReviews = reviews
    let filteredCategories = productCategories
    let filteredArticles = articles

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()

      filteredReviews = reviews.filter(review =>
        review.title.toLowerCase().includes(query) ||
        review.brand.toLowerCase().includes(query) ||
        review.category.toLowerCase().includes(query) ||
        review.excerpt.toLowerCase().includes(query)
      )

      filteredCategories = productCategories.filter(category =>
        category.title.toLowerCase().includes(query) ||
        category.subtitle.toLowerCase().includes(query) ||
        category.description.toLowerCase().includes(query)
      )

      filteredArticles = articles.filter(article =>
        article.title.toLowerCase().includes(query) ||
        article.excerpt.toLowerCase().includes(query) ||
        article.category.toLowerCase().includes(query)
      )
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filteredReviews = filteredReviews.filter(review =>
        review.categorySlug === selectedCategory
      )
    }

    // Filter by rating
    if (filterBy === 'high-rated') {
      filteredReviews = filteredReviews.filter(review => review.rating >= 4.0)
    } else if (filterBy === 'recent') {
      filteredReviews = filteredReviews.sort((a, b) =>
        new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      )
    }

    // Sort results
    if (sortBy === 'rating') {
      filteredReviews = filteredReviews.sort((a, b) => b.rating - a.rating)
    } else if (sortBy === 'date') {
      filteredReviews = filteredReviews.sort((a, b) =>
        new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      )
    } else if (sortBy === 'title') {
      filteredReviews = filteredReviews.sort((a, b) => a.title.localeCompare(b.title))
    }

    const results = {
      reviews: filteredReviews,
      categories: filteredCategories,
      articles: filteredArticles,
      total: filteredReviews.length + filteredCategories.length + filteredArticles.length
    }

    setSearchResults(results)
    setIsSearching(false)
  }

  const value = {
    searchQuery,
    setSearchQuery,
    selectedCategory,
    setSelectedCategory,
    sortBy,
    setSortBy,
    filterBy,
    setFilterBy,
    searchResults,
    performSearch,
    isSearching
  }

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  )
}

export function useSearch() {
  const context = useContext(SearchContext)
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider')
  }
  return context
}

export default SearchContext
