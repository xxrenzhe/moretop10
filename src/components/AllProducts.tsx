import { Card, CardContent } from '@/components/ui/card'
import { Headphones, Home, Baby, Heart, Car, Dog } from 'lucide-react'
import { productCategories as categoriesData } from '@/lib/data'
import Link from "next/link"

const iconMap = {
  'Headphones': Headphones,
  'Home': Home,
  'Baby': Baby,
  'Heart': Heart,
  'Car': Car,
  'Dog': Dog
}

const productCategories = categoriesData.map(category => ({
  ...category,
  icon: iconMap[category.icon as keyof typeof iconMap] || Home
}))

export default function AllProducts() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-2xl font-bold text-gray-900">All Products</h2>
          <Link href="/categories" className="text-orange-600 hover:text-orange-700 font-medium">
            + SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {productCategories.map((category) => (
            <Card key={category.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
              <Link href={category.href}>
                <div className="aspect-[4/3] relative overflow-hidden">
                  <img
                    src={category.image}
                    alt={category.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                      <category.icon className="w-4 h-4 text-orange-600" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                      {category.title}
                    </h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600 font-medium">
                        {category.subtitle}
                      </p>
                    </div>
                    {category.items?.map((item, itemIndex) => (
                      <p key={`${category.id}-${item}`} className="text-sm text-gray-600">
                        • {item}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
