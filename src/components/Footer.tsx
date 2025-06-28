import Link from "next/link"
import { Search, FileText, Star } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-white">
      {/* Trust Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-16">
            Why Trust ConsumerVoice.org?
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {/* Research */}
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center">
                <img
                  src="https://ext.same-assets.com/2656189839/3051735051.svg"
                  alt="Research Icon"
                  className="w-10 h-10"
                />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Research</h3>
            </div>

            {/* Reviews */}
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
                <img
                  src="https://ext.same-assets.com/2656189839/2804017162.svg"
                  alt="Reviews Icon"
                  className="w-10 h-10"
                />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Reviews</h3>
            </div>

            {/* Recommendations */}
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-orange-100 rounded-full flex items-center justify-center">
                <img
                  src="https://ext.same-assets.com/2656189839/267995921.svg"
                  alt="Recommendations Icon"
                  className="w-10 h-10"
                />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Recommendations</h3>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Links */}
      <div className="py-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
            <div className="space-y-4">
              <Link href="/how-we-rank" className="block text-gray-700 hover:text-orange-600 font-medium">
                How We Rank
              </Link>
            </div>

            <div className="space-y-4">
              <Link href="/contact" className="block text-gray-700 hover:text-orange-600 font-medium">
                Contact
              </Link>
            </div>

            <div className="space-y-4">
              <Link href="/privacy" className="block text-gray-700 hover:text-orange-600 font-medium">
                Privacy
              </Link>
            </div>

            <div className="space-y-4">
              <Link href="/terms" className="block text-gray-700 hover:text-orange-600 font-medium">
                Terms
              </Link>
            </div>

            <div className="space-y-4">
              <Link href="/opt-out" className="block text-gray-700 hover:text-orange-600 font-medium">
                Do Not Sell My Personal Information
              </Link>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-200 flex justify-center">
            <Link href="/" className="flex items-center">
              <img
                src="https://ext.same-assets.com/2656189839/2868950229.svg"
                alt="ConsumerVoice.org"
                className="h-8"
              />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
