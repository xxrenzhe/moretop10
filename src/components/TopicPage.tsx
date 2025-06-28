'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, Star, Users, TrendingUp, Shield } from 'lucide-react'
import { type Topic, type Review, reviews, productCategories } from '@/lib/data'

interface TopicPageProps {
  topic: Topic
}

export default function TopicPage({ topic }: TopicPageProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [topicReviews, setTopicReviews] = useState<Review[]>([])
  const [relatedCategories, setRelatedCategories] = useState<typeof productCategories>([])

  useEffect(() => {
    // Filter reviews for this topic
    const filteredReviews = reviews.filter(review =>
      review.category.toLowerCase().includes(topic.name.toLowerCase()) ||
      review.categorySlug === topic.slug
    )
    setTopicReviews(filteredReviews)

    // Find related categories
    const related = productCategories.filter(category =>
      category.title.toLowerCase().includes(topic.name.toLowerCase()) ||
      category.description.toLowerCase().includes(topic.name.toLowerCase())
    )
    setRelatedCategories(related)
  }, [topic])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (query === '') {
      const filteredReviews = reviews.filter(review =>
        review.category.toLowerCase().includes(topic.name.toLowerCase()) ||
        review.categorySlug === topic.slug
      )
      setTopicReviews(filteredReviews)
    } else {
      const filtered = topicReviews.filter(review =>
        review.title.toLowerCase().includes(query.toLowerCase()) ||
        review.brand.toLowerCase().includes(query.toLowerCase())
      )
      setTopicReviews(filtered)
    }
  }

  const averageRating = topicReviews.length > 0
    ? (topicReviews.reduce((sum, review) => sum + review.rating, 0) / topicReviews.length).toFixed(1)
    : '0'

  return (
    <div className="py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Topic Header */}
        <div className="text-center mb-12">
          <div className="mb-6">
            <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto">
              <Shield className="w-10 h-10 text-orange-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {topic.name}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            {topic.description}
          </p>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{topicReviews.length}</div>
              <div className="text-gray-600">Reviews</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-1">
                <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                {averageRating}
              </div>
              <div className="text-gray-600">Average Rating</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{relatedCategories.length}</div>
              <div className="text-gray-600">Categories</div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mb-8">
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              type="text"
              placeholder={`Search ${topic.name.toLowerCase()}...`}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Reviews Section */}
        {topicReviews.length > 0 && (
          <div className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Latest {topic.name} Reviews
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {topicReviews.map((review) => (
                <Card key={review.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
                  <a href={review.href}>
                    <div className="aspect-video relative overflow-hidden">
                      <img
                        src={review.image}
                        alt={review.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <div className="absolute top-4 right-4">
                        <Badge className="bg-white text-gray-900 shadow-sm">
                          <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                          {review.rating}
                        </Badge>
                      </div>
                    </div>
                    <CardContent className="p-6">
                      <Badge variant="secondary" className="mb-2 text-xs">
                        {review.category}
                      </Badge>
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
          </div>
        )}

        {/* Related Categories */}
        {relatedCategories.length > 0 && (
          <div className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Related Categories
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {relatedCategories.map((category) => (
                <Card key={category.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
                  <a href={category.href}>
                    <div className="aspect-[4/3] relative overflow-hidden">
                      <img
                        src={category.image}
                        alt={category.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    <CardContent className="p-6">
                      <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-600 transition-colors mb-2">
                        {category.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {category.subtitle}
                      </p>
                      <p className="text-xs text-gray-500">
                        {category.reviewCount} reviews
                      </p>
                    </CardContent>
                  </a>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* No Results */}
        {topicReviews.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No reviews found</h3>
            <p className="text-gray-500 mb-6">
              We don't have any reviews for {topic.name} yet, but check back soon!
            </p>
            <Button onClick={() => window.history.back()}>
              Go Back
            </Button>
          </div>
        )}

        {/* Call to Action */}
        <div className="bg-orange-50 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Stay Updated on {topic.name}
          </h3>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Get the latest reviews, comparisons, and buying guides delivered to your inbox.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <Input
              type="email"
              placeholder="Enter your email"
              className="flex-1"
            />
            <Button className="bg-orange-600 hover:bg-orange-700">
              Subscribe
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
