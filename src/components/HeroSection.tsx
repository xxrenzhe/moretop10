'use client'

import { useState } from 'react'
import { Search, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function HeroSection() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <section className="relative bg-cv-beige py-16 lg:py-24 overflow-hidden">
      {/* Background decorative shapes */}
      <div className="absolute inset-0 opacity-60">
        <div className="absolute top-10 left-10 w-12 h-12 bg-cv-gold-200 rounded-full"></div>
        <div className="absolute top-32 right-20 w-8 h-8 bg-cv-gold-500 rounded-full"></div>
        <div className="absolute bottom-20 left-32 w-6 h-6 bg-cv-cream rounded-full"></div>
        <div className="absolute bottom-40 right-10 w-10 h-10 bg-cv-gold-100 rounded-full"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8">
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 leading-tight">
              The Best Products in{' '}
              <span className="text-cv-gold-600">Every Category</span>
            </h1>

            <p className="text-xl text-gray-600">
              <span className="font-semibold">Rating</span> and{' '}
              <span className="font-semibold">Reviews</span> of the best products
            </p>

            {/* Search Box */}
            <div className="max-w-md">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  type="text"
                  placeholder="Search a Topic"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-12 pr-12 py-3 text-lg border-gray-200 focus:border-cv-gold-500 focus:ring-cv-gold-500 rounded-full"
                />
                {searchQuery && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8"
                    onClick={() => setSearchQuery('')}
                  >
                    <X className="h-4 w-4 text-gray-400" />
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Illustration */}
          <div className="relative lg:pl-8">
            <div className="relative w-full max-w-lg mx-auto">
              {/* Main illustration placeholder */}
              <div className="bg-gradient-to-br from-cv-gold-100 to-cv-cream rounded-2xl p-8 h-80 flex items-center justify-center">
                <div className="text-center space-y-4">
                  {/* Simulated shopping elements */}
                  <div className="flex justify-center space-x-4">
                    <div className="w-16 h-16 bg-white rounded-lg shadow-lg flex items-center justify-center">
                      <div className="w-8 h-8 bg-cv-gold-500 rounded"></div>
                    </div>
                    <div className="w-16 h-16 bg-white rounded-lg shadow-lg flex items-center justify-center">
                      <div className="w-8 h-8 bg-cv-gold-600 rounded-full"></div>
                    </div>
                    <div className="w-16 h-16 bg-white rounded-lg shadow-lg flex items-center justify-center">
                      <div className="w-8 h-8 bg-cv-gold-700 rounded"></div>
                    </div>
                  </div>

                  {/* Person illustration */}
                  <div className="w-24 h-24 bg-cv-gold-200 rounded-full mx-auto flex items-center justify-center">
                    <div className="w-16 h-16 bg-cv-gold-500 rounded-full"></div>
                  </div>

                  {/* Shopping cart */}
                  <div className="w-12 h-12 bg-cv-gold-600 rounded mx-auto"></div>
                </div>
              </div>

              {/* Floating elements */}
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-cv-cream rounded-full animate-bounce"></div>
              <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-cv-gold-200 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
