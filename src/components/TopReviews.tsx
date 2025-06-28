import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Star } from 'lucide-react'
import { reviews } from '@/lib/data'
import Link from "next/link"

export default function TopReviews() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-2xl font-bold text-gray-900">Top Reviews</h2>
          <Link href="/reviews" className="text-orange-600 hover:text-orange-700 font-medium">
            + SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {reviews.map((review) => (
            <Card key={review.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
              <Link href={review.href}>
                <div className="aspect-video relative overflow-hidden">
                  <img
                    src={review.image}
                    alt={review.brand}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-4 right-4">
                    <Badge className="bg-white text-gray-900 shadow-sm">
                      <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                      {review.rating}
                    </Badge>
                  </div>
                </div>
                <CardContent className="p-4">
                  <Badge variant="secondary" className="mb-2 text-xs">
                    {review.category}
                  </Badge>
                  <h3 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors">
                    {review.brand}
                  </h3>
                  <p className="text-gray-600 text-sm mt-1 line-clamp-2">
                    {review.excerpt}
                  </p>
                </CardContent>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
