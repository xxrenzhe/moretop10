import { Heart, Shield, Dog, Car, Truck, Bike, Car as CarIcon } from 'lucide-react'
import { topics as topicsData } from '@/lib/data'
import Link from "next/link"

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
  icon: iconMap[topic.icon as keyof typeof iconMap] || Dog
}))

export default function FeaturedTopics() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-2xl font-bold text-gray-900">Featured Topics</h2>
          <Link href="/topics" className="text-cv-gold-600 hover:text-cv-gold-700 font-medium">
            + SEE ALL
          </Link>
        </div>

        <div className="relative">
          {/* Desktop view */}
          <div className="hidden md:grid md:grid-cols-7 gap-6">
            {topics.map((topic, index) => (
              <a
                key={index}
                href={topic.href}
                className="group text-center hover:bg-gray-50 p-4 rounded-xl transition-colors"
              >
                <div className="w-16 h-16 bg-gray-100 rounded-full mx-auto mb-3 flex items-center justify-center group-hover:bg-cv-gold-100 transition-colors">
                  <topic.icon className="w-8 h-8 text-gray-600 group-hover:text-cv-gold-600" />
                </div>
                <h3 className="text-sm font-medium text-gray-900 group-hover:text-cv-gold-600 leading-tight">
                  {topic.name}
                </h3>
              </a>
            ))}
          </div>

          {/* Mobile view - horizontal scroll */}
          <div className="md:hidden">
            <div className="flex space-x-6 overflow-x-auto pb-4 scrollbar-hide">
              {topics.map((topic, index) => (
                <a
                  key={index}
                  href={topic.href}
                  className="group text-center flex-none w-20 hover:bg-gray-50 p-2 rounded-xl transition-colors"
                >
                  <div className="w-14 h-14 bg-gray-100 rounded-full mx-auto mb-2 flex items-center justify-center group-hover:bg-cv-gold-100 transition-colors">
                    <topic.icon className="w-6 h-6 text-gray-600 group-hover:text-cv-gold-600" />
                  </div>
                  <h3 className="text-xs font-medium text-gray-900 group-hover:text-cv-gold-600 leading-tight">
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
