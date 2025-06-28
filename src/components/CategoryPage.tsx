'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, Filter, Grid, List, Star } from 'lucide-react'
import { type ProductCategory, type Review, reviews } from '@/lib/data'
import { useSearch } from '@/contexts/SearchContext'

interface CategoryPageProps {
  category: ProductCategory
}

export default function CategoryPage({ category }: CategoryPageProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('rating')
  const [categoryReviews, setCategoryReviews] = useState<Review[]>([])
  const { setSearchQuery, setSelectedCategory } = useSearch()

  useEffect(() => {
    // Filter reviews for this category
    const filteredReviews = reviews.filter(review =>
      review.categorySlug === category.slug ||
      review.category.toLowerCase().includes(category.title.toLowerCase())
    )
    setCategoryReviews(filteredReviews)
    setSelectedCategory(category.slug)
  }, [category, setSelectedCategory])

  const handleLocalSearch = (query: string) => {
    setLocalSearchQuery(query)
    const filtered = reviews.filter(review => {
      const matchesCategory = review.categorySlug === category.slug ||
        review.category.toLowerCase().includes(category.title.toLowerCase())
      const matchesQuery = query === '' ||
        review.title.toLowerCase().includes(query.toLowerCase()) ||
        review.brand.toLowerCase().includes(query.toLowerCase())
      return matchesCategory && matchesQuery
    })
    setCategoryReviews(filtered)
  }

  const handleSort = (value: string) => {
    setSortBy(value)
    const sorted = [...categoryReviews]

    switch (value) {
      case 'rating':
        sorted.sort((a, b) => b.rating - a.rating)
        break
      case 'date':
        sorted.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
        break
      case 'title':
        sorted.sort((a, b) => a.title.localeCompare(b.title))
        break
    }

    setCategoryReviews(sorted)
  }

  return (
    <div className="py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Category Header */}
        <div className="text-center mb-12">
          <div className="mb-6">
            <img
              src={category.image}
              alt={category.title}
              className="w-32 h-32 mx-auto rounded-2xl object-cover shadow-lg"
            />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {category.title} Reviews
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
            {category.description}
          </p>
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
            <span>{categoryReviews.length} Reviews</span>
            <span>•</span>
            <span>Updated Weekly</span>
            <span>•</span>
            <span>Expert Tested</span>
          </div>
        </div>

        {/* Search and Filter Bar */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col md:flex-row gap-4 items-center">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder={`Search ${category.title.toLowerCase()}...`}
                value={localSearchQuery}
                onChange={(e) => handleLocalSearch(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => handleSort(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="rating">Sort by Rating</option>
              <option value="date">Sort by Date</option>
              <option value="title">Sort by Title</option>
            </select>

            {/* View Mode */}
            <div className="flex border border-gray-200 rounded-md">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className="rounded-r-none"
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                className="rounded-l-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Results */}
        {categoryReviews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No reviews found for this category yet.</p>
            <p className="text-gray-400 mt-2">Check back soon for more reviews!</p>
          </div>
        ) : (
          <div className={viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-6'
          }>
            {categoryReviews.map((review) => (
              <Card key={review.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
                <a href={review.href}>
                  <div className={viewMode === 'grid' ? 'aspect-video relative overflow-hidden' : 'flex'}>
                    <img
                      src={review.image}
                      alt={review.title}
                      className={viewMode === 'grid'
                        ? 'w-full h-full object-cover group-hover:scale-105 transition-transform duration-300'
                        : 'w-48 h-32 object-cover flex-shrink-0'
                      }
                    />
                    {viewMode === 'grid' && (
                      <div className="absolute top-4 right-4">
                        <Badge className="bg-white text-gray-900 shadow-sm">
                          <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                          {review.rating}
                        </Badge>
                      </div>
                    )}
                  </div>
                  <CardContent className={viewMode === 'grid' ? 'p-6' : 'p-6 flex-1'}>
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="secondary" className="text-xs">
                        {review.category}
                      </Badge>
                      {viewMode === 'list' && (
                        <Badge className="bg-white text-gray-900 shadow-sm border">
                          <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                          {review.rating}
                        </Badge>
                      )}
                    </div>
                    <h3 className="font-bold text-lg text-gray-900 group-hover:text-orange-600 transition-colors mb-2">
                      {review.title}
                    </h3>
                    <p className="text-gray-600 text-sm leading-relaxed mb-3">
                      {review.excerpt}
                    </p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>By {review.author}</span>
                      <span>{new Date(review.publishedAt).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </a>
              </Card>
            ))}
          </div>
        )}

        {/* Category Features */}
        {category.items && category.items.length > 0 && (
          <div className="mt-16 bg-gray-50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              Popular in {category.title}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.items.map((item, index) => (
                <div key={index} className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h3 className="font-semibold text-gray-900">{item}</h3>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
