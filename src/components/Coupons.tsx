'use client'

import Link from "next/link"
import { ChevronRight } from 'lucide-react'
import { useRef, useState, useEffect } from 'react'

const coupons = [
  { name: 'Bright Cellars', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Bright-Cellars.png', href: '#' },
  { name: 'Byte', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Byte.png', href: '#' },
  { name: 'DreamCloud Sleep', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/DreamCloud.png', href: '#' },
  { name: 'Ghostbed', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Ghostbed.png', href: '#' },
  { name: 'Identity Guard', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Identity-Guard.png', href: '#' },
  { name: 'Leesa', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/leesa-sleep.png', href: '#' },
  { name: 'Nectar', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Nectar.png', href: '#' },
  { name: 'Saatva', logo: 'https://consumervoice.org/wp-content/uploads/2021/04/Saatva.png', href: '#' }
]

const extendedCoupons = [...coupons, ...coupons.slice(0, 4)];

export default function Coupons() {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [canScrollRight, setCanScrollRight] = useState(true)

  const checkScrollability = () => {
    const container = scrollContainerRef.current
    if (container) {
      const { scrollLeft, scrollWidth, clientWidth } = container
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
          <h2 className="text-3xl font-bold text-gray-900">Coupons</h2>
          <Link href="/coupons" className="text-sm font-bold text-gray-900 hover:text-cv-gold-500 flex items-center">
            <span className="w-2 h-2 bg-cv-gold-500 rounded-full mr-2"></span>
            SEE ALL
          </Link>
        </div>

        <div className="relative">
          <div className="hidden md:flex items-center">
            <div className="flex-1 flex items-center space-x-4 overflow-x-auto pb-4 scrollbar-hide pl-4 sm:pl-6 lg:pl-8" ref={scrollContainerRef}>
              {extendedCoupons.map((coupon, index) => (
                <a key={index} href={coupon.href} className="group text-center bg-white shadow-sm hover:shadow-md p-6 rounded-3xl transition-all duration-300 flex-none w-40 flex flex-col justify-center items-center h-48">
                  <div className="w-24 h-24 bg-white rounded-full mx-auto mb-4 flex items-center justify-center p-2">
                    <img src={coupon.logo} alt={coupon.name} className="h-full w-auto max-w-full object-contain" />
                  </div>
                  <h3 className="text-base font-semibold text-gray-800 group-hover:text-cv-gold-500 leading-tight">
                    {coupon.name}
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
          
          <div className="md:hidden">
            <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide px-4 sm:px-6">
              {coupons.map((coupon, index) => (
                 <a key={index} href={coupon.href} className="group text-center flex-none w-32 bg-white shadow-sm hover:shadow-md p-4 rounded-2xl transition-all duration-300">
                  <div className="w-20 h-20 bg-white rounded-full mx-auto mb-2 flex items-center justify-center p-2">
                     <img src={coupon.logo} alt={coupon.name} className="h-full w-auto max-w-full object-contain" />
                  </div>
                  <h3 className="text-sm font-medium text-gray-800 group-hover:text-cv-gold-500 leading-tight">
                    {coupon.name}
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
