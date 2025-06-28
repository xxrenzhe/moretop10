import Link from 'next/link';
import { reviews } from '@/lib/data';

// We'll use the first 6 reviews for this complex grid layout
const reviewData = reviews.slice(0, 6); 

export default function TopReviews() {
  const firstReview = reviewData[0];
  const otherReviews = reviewData.slice(1);

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Top Reviews</h2>
          <Link href="/reviews" className="text-sm font-bold text-gray-900 hover:text-cv-gold-500 flex items-center">
            <span className="w-2 h-2 bg-cv-gold-500 rounded-full mr-2"></span>
            SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 h-auto md:h-[600px] lg:h-[720px]">
          {/* Main large review */}
          {firstReview && (
            <a href={firstReview.href} className="md:col-span-2 lg:col-span-2 md:row-span-2 relative group overflow-hidden rounded-3xl shadow-sm hover:shadow-md transition-all">
              <img src={firstReview.image} alt={firstReview.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
              <div className="absolute bottom-0 left-0 p-8 text-white">
                <h3 className="text-3xl font-bold">{firstReview.title}</h3>
                <p className="text-lg">{firstReview.brand}</p>
              </div>
            </a>
          )}

          {/* Smaller reviews on the right */}
          {otherReviews.slice(0, 2).map((review) => (
            <a key={review.id} href={review.href} className="lg:col-span-2 relative group overflow-hidden rounded-3xl shadow-sm hover:shadow-md transition-all min-h-[300px] md:min-h-0">
              <img src={review.image} alt={review.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors"></div>
              <div className="absolute bottom-0 left-0 p-6 text-white">
                <h3 className="text-xl font-bold">{review.title}</h3>
                <p>{review.brand}</p>
              </div>
            </a>
          ))}
          
          {/* Smaller reviews at the bottom */}
          {otherReviews.slice(2, 5).map((review) => (
             <a key={review.id} href={review.href} className="relative group overflow-hidden rounded-3xl shadow-sm hover:shadow-md transition-all min-h-[300px] md:min-h-0">
              <img src={review.image} alt={review.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
               <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors"></div>
              <div className="absolute bottom-0 left-0 p-6 text-white">
                <h3 className="text-xl font-bold">{review.title}</h3>
                <p>{review.brand}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
