'use client'

import { Heart, Shield, Dog, Car, Truck, Bike, Car as CarIcon, ChevronRight } from 'lucide-react'
import { topics as topicsData } from '@/lib/data'
import Link from "next/link"
import { useRef, useState, useEffect } from 'react'

const iconMap = {
  'Dog': Dog,
  'Shield': Shield,
  'Heart': Heart,
  'Truck': Truck,
  'Bike': Bike,
  'Car': CarIcon
}

const topics = topicsData.map(topic => ({
  ...topic,
  icon: topic.icon ? (iconMap[topic.icon as keyof typeof iconMap] || Dog) : Dog
}))

export default function FeaturedTopics() {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [canScrollRight, setCanScrollRight] = useState(true)

  const checkScrollability = () => {
    const container = scrollContainerRef.current
    if (container) {
      const { scrollLeft, scrollWidth, clientWidth } = container
      // Add a small buffer to account for floating point inaccuracies
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 5)
    }
  }
  
  const scroll = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 350, behavior: 'smooth' })
    }
  }

  useEffect(() => {
    const container = scrollContainerRef.current
    if (container) {
      // Defer the initial check to allow layout to settle
      const timeoutId = setTimeout(checkScrollability, 100);
      
      container.addEventListener('scroll', checkScrollability, { passive: true })
      window.addEventListener('resize', checkScrollability)

      return () => {
        clearTimeout(timeoutId);
        container.removeEventListener('scroll', checkScrollability)
        window.removeEventListener('resize', checkScrollability)
      }
    }
  }, [])

  return (
    <section className="py-16 bg-cv-gray">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-12 px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900">Featured Topics</h2>
          <Link href="/topics" className="text-sm font-bold text-gray-900 hover:text-cv-gold-500 flex items-center">
            <span className="w-2 h-2 bg-cv-gold-500 rounded-full mr-2"></span>
            SEE ALL
          </Link>
        </div>

        <div className="relative">
          {/* Desktop view */}
          <div className="hidden md:flex items-center">
            <div
              className="flex-1 flex items-center space-x-4 overflow-x-auto pb-4 scrollbar-hide pl-4 sm:pl-6 lg:pl-8"
              ref={scrollContainerRef}
            >
              {topics.map((topic, index) => (
                <a
                  key={index}
                  href={topic.href}
                  className="group text-center bg-white shadow-sm hover:shadow-md p-6 rounded-3xl transition-all duration-300 flex-none w-40 flex flex-col justify-center items-center h-48"
                >
                  <div className="w-20 h-20 bg-gray-100 rounded-full mx-auto mb-4 flex items-center justify-center group-hover:bg-cv-gold-50 transition-colors">
                    <topic.icon className="w-10 h-10 text-gray-700 group-hover:text-cv-gold-500" />
                  </div>
                  <h3 className="text-base font-semibold text-gray-800 group-hover:text-cv-gold-500 leading-tight">
                    {topic.name}
                  </h3>
                </a>
              ))}
            </div>
             {canScrollRight && (
              <button onClick={scroll} className="p-2 pr-4 sm:pr-6 lg:pr-8">
                <ChevronRight className="w-8 h-8 text-gray-400 hover:text-gray-700" />
              </button>
            )}
          </div>

          {/* Mobile view - horizontal scroll */}
          <div className="md:hidden">
            <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide px-4 sm:px-6">
              {topics.map((topic, index) => (
                <a
                  key={index}
                  href={topic.href}
                  className="group text-center flex-none w-32 bg-white shadow-sm hover:shadow-md p-4 rounded-2xl transition-all duration-300"
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-full mx-auto mb-2 flex items-center justify-center group-hover:bg-cv-gold-50 transition-colors">
                    <topic.icon className="w-8 h-8 text-gray-700 group-hover:text-cv-gold-500" />
                  </div>
                  <h3 className="text-sm font-medium text-gray-800 group-hover:text-cv-gold-500 leading-tight">
                    {topic.name}
                  </h3>
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}