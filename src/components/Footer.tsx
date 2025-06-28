import Link from "next/link"

export default function Footer() {
  return (
    <footer className="bg-white">
      {/* Trust Section */}
      <section className="py-20 bg-cv-gray">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-16">
            Why Trust ConsumerVoice.org?
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-4xl mx-auto">
            {/* Research */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <img
                  src="https://consumervoice.org/wp-content/uploads/2021/04/research.svg"
                  alt="Research Icon"
                  className="w-16 h-16"
                />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">Research</h3>
            </div>

            {/* Reviews */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <img
                  src="https://consumervoice.org/wp-content/uploads/2021/04/reviews.svg"
                  alt="Reviews Icon"
                  className="w-16 h-16"
                />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">Reviews</h3>
            </div>

            {/* Recommendations */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <img
                  src="https://consumervoice.org/wp-content/uploads/2021/04/recommendations.svg"
                  alt="Recommendations Icon"
                  className="w-16 h-16"
                />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">Recommendations</h3>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Links */}
      <div className="py-10 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between">
          <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 mb-6 sm:mb-0">
            <Link href="/how-we-rank" className="text-sm text-gray-600 hover:text-cv-gold-500">
              How We Rank
            </Link>
            <Link href="/contact" className="text-sm text-gray-600 hover:text-cv-gold-500">
              Contact
            </Link>
            <Link href="/privacy" className="text-sm text-gray-600 hover:text-cv-gold-500">
              Privacy
            </Link>
            <Link href="/terms" className="text-sm text-gray-600 hover:text-cv-gold-500">
              Terms
            </Link>
            <Link href="/opt-out" className="text-sm text-gray-600 hover:text-cv-gold-500">
              Do Not Sell My Personal Information
            </Link>
          </div>
          <div className="flex-shrink-0">
             <Link href="/">
              <img
                src="https://consumervoice.org/wp-content/uploads/2021/04/logo-black.svg"
                alt="ConsumerVoice.org"
                className="h-7"
              />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
