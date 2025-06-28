import Link from 'next/link';
import { productCategories as categoriesData } from '@/lib/data';

const categories = categoriesData.slice(0, 7); // Use first 7 for the layout

export default function AllProducts() {
  const mainCategory = categories[0];
  const otherCategories = categories.slice(1);

  return (
    <section className="py-16 bg-cv-gray">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-3xl font-bold text-gray-900">All Products</h2>
          <Link href="/categories" className="text-sm font-bold text-gray-900 hover:text-cv-gold-500 flex items-center">
            <span className="w-2 h-2 bg-cv-gold-500 rounded-full mr-2"></span>
            SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Main large category */}
          {mainCategory && (
            <a href={mainCategory.href} className="lg:col-span-2 relative group bg-white overflow-hidden rounded-3xl shadow-sm hover:shadow-md transition-all flex flex-col">
              <div className="relative h-64 overflow-hidden">
                <img src={mainCategory.image} alt={mainCategory.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                 <div className="absolute bottom-0 left-0 p-8">
                  <h3 className="text-3xl font-bold text-white">{mainCategory.title}</h3>
                  <p className="text-lg text-white/90">{mainCategory.subtitle}</p>
                </div>
              </div>
            </a>
          )}

          {/* Other smaller categories */}
          {otherCategories.map((category) => (
            <a key={category.id} href={category.href} className="relative group bg-white overflow-hidden rounded-3xl shadow-sm hover:shadow-md transition-all flex flex-col">
              <div className="relative h-48 overflow-hidden">
                <img src={category.image} alt={category.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
              </div>
              <div className="p-6 flex-1 flex flex-col">
                <h3 className="text-xl font-bold text-gray-800">{category.title}</h3>
                {category.items && (
                  <div className="mt-2 text-gray-600 space-y-1">
                    {category.items.slice(0, 2).map((item, index) => (
                      <p key={index} className="text-sm">• {item}</p>
                    ))}
                  </div>
                )}
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
