'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Star, ThumbsUp, ThumbsDown, Share2, Bookmark, Check, X, DollarSign, Clock, User } from 'lucide-react'
import { type Review, reviews } from '@/lib/data'

interface ReviewDetailProps {
  review: Review
}

export default function ReviewDetail({ review }: ReviewDetailProps) {
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [showFullContent, setShowFullContent] = useState(false)

  // Get related reviews
  const relatedReviews = reviews.filter(r =>
    r.id !== review.id &&
    (r.categorySlug === review.categorySlug || r.category === review.category)
  ).slice(0, 3)

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${
          i < Math.floor(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : i < rating
            ? 'fill-yellow-200 text-yellow-200'
            : 'fill-gray-200 text-gray-200'
        }`}
      />
    ))
  }

  return (
    <div className="py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <nav className="text-sm text-gray-500 mb-4">
            <Link href="/" className="hover:text-orange-600">Home</Link>
            <span className="mx-2">/</span>
            <a href={`/categories/${review.categorySlug}`} className="hover:text-orange-600">{review.category}</a>
            <span className="mx-2">/</span>
            <span className="text-gray-900">{review.brand}</span>
          </nav>

          <div className="flex flex-col lg:flex-row gap-8">
            {/* Hero Image */}
            <div className="lg:w-1/2">
              <img
                src={review.image}
                alt={review.title}
                className="w-full h-80 object-cover rounded-2xl shadow-lg"
              />
            </div>

            {/* Review Summary */}
            <div className="lg:w-1/2">
              <Badge variant="secondary" className="mb-4">
                {review.category}
              </Badge>

              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {review.title}
              </h1>

              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {renderStars(review.rating)}
                  </div>
                  <span className="text-2xl font-bold text-gray-900">{review.rating}</span>
                  <span className="text-gray-500">/5</span>
                </div>
              </div>

              <p className="text-lg text-gray-600 mb-6">
                {review.excerpt}
              </p>

              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <User className="w-4 h-4" />
                  <span>By {review.author}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>{new Date(review.publishedAt).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant={isBookmarked ? "default" : "outline"}
                  onClick={() => setIsBookmarked(!isBookmarked)}
                  className="flex items-center gap-2"
                >
                  <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
                  {isBookmarked ? 'Saved' : 'Save'}
                </Button>
                <Button variant="outline" className="flex items-center gap-2">
                  <Share2 className="w-4 h-4" />
                  Share
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                <span className="text-2xl font-bold text-gray-900">{review.rating}</span>
              </div>
              <p className="text-gray-600">Overall Rating</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="text-lg font-bold text-gray-900">Value</span>
              </div>
              <p className="text-gray-600">{review.pricing}</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Check className="w-5 h-5 text-green-600" />
                <span className="text-lg font-bold text-gray-900">Recommended</span>
              </div>
              <p className="text-gray-600">Expert Pick</p>
            </CardContent>
          </Card>
        </div>

        {/* Pros and Cons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <ThumbsUp className="w-5 h-5 text-green-600" />
                Pros
              </h3>
              <ul className="space-y-2">
                {review.pros.map((pro, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{pro}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <ThumbsDown className="w-5 h-5 text-red-600" />
                Cons
              </h3>
              <ul className="space-y-2">
                {review.cons.map((con, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <X className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{con}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Key Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {review.features.map((feature, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <span className="text-gray-900 font-medium">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Verdict */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Our Verdict</h3>
            <div className="bg-orange-50 border-l-4 border-orange-500 p-6 rounded-r-lg">
              <p className="text-gray-700 leading-relaxed">{review.verdict}</p>
            </div>
          </CardContent>
        </Card>

        {/* Full Review Content */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Detailed Review</h3>
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed mb-4">
                {review.content || "This is where the full review content would appear. Our expert team has thoroughly tested this product over several weeks to provide you with comprehensive insights and recommendations."}
              </p>
              {!showFullContent && (
                <Button
                  variant="outline"
                  onClick={() => setShowFullContent(true)}
                  className="mt-4"
                >
                  Read Full Review
                </Button>
              )}
              {showFullContent && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-700">
                    [Full review content would be loaded here dynamically. This would include detailed analysis, testing methodology, comparison with competitors, and expert recommendations.]
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Related Reviews */}
        {relatedReviews.length > 0 && (
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Related Reviews</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {relatedReviews.map((relatedReview) => (
                <Card key={relatedReview.id} className="group hover:shadow-lg transition-shadow cursor-pointer">
                  <a href={relatedReview.href}>
                    <div className="aspect-video relative overflow-hidden">
                      <img
                        src={relatedReview.image}
                        alt={relatedReview.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <div className="absolute top-4 right-4">
                        <Badge className="bg-white text-gray-900 shadow-sm">
                          <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                          {relatedReview.rating}
                        </Badge>
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <Badge variant="secondary" className="mb-2 text-xs">
                        {relatedReview.category}
                      </Badge>
                      <h4 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors text-sm">
                        {relatedReview.title}
                      </h4>
                    </CardContent>
                  </a>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
