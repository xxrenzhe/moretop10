import Link from "next/link"

const coupons = [
  {
    name: 'Bright Cellars coupons',
    logo: 'https://ext.same-assets.com/2656189839/2419869815.png',
    href: '#'
  },
  {
    name: 'Byte coupons',
    logo: 'https://ext.same-assets.com/2656189839/2710791357.png',
    href: '#'
  },
  {
    name: 'DreamCloud Sleep coupons',
    logo: 'https://ext.same-assets.com/2656189839/482784027.png',
    href: '#'
  },
  {
    name: 'Ghostbed coupons',
    logo: 'https://ext.same-assets.com/2656189839/3846251626.png',
    href: '#'
  },
  {
    name: 'Identity Guard coupons',
    logo: 'https://ext.same-assets.com/2656189839/2275215110.png',
    href: '#'
  },
  {
    name: 'Leesa coupons',
    logo: 'https://ext.same-assets.com/2656189839/702220216.jpeg',
    href: '#'
  },
  {
    name: 'Nectar coupons',
    logo: 'https://ext.same-assets.com/2656189839/1619287959.png',
    href: '#'
  }
]

export default function Coupons() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-2xl font-bold text-gray-900">Coupons</h2>
          <Link href="/coupons" className="text-orange-600 hover:text-orange-700 font-medium">
            + SEE ALL
          </Link>
        </div>

        <div className="relative">
          {/* Desktop view */}
          <div className="hidden md:grid md:grid-cols-7 gap-6">
            {coupons.map((coupon, index) => (
              <a
                key={index}
                href={coupon.href}
                className="group text-center hover:bg-gray-50 p-4 rounded-xl transition-colors"
              >
                <div className="w-16 h-16 bg-white border border-gray-200 rounded-lg mx-auto mb-3 flex items-center justify-center group-hover:border-orange-300 transition-colors shadow-sm">
                  <img
                    src={coupon.logo}
                    alt={coupon.name}
                    className="w-12 h-12 object-contain"
                  />
                </div>
                <h3 className="text-sm font-medium text-gray-900 group-hover:text-orange-600 leading-tight">
                  {coupon.name}
                </h3>
              </a>
            ))}
          </div>

          {/* Mobile view - horizontal scroll */}
          <div className="md:hidden">
            <div className="flex space-x-6 overflow-x-auto pb-4 scrollbar-hide">
              {coupons.map((coupon, index) => (
                <a
                  key={index}
                  href={coupon.href}
                  className="group text-center flex-none w-20 hover:bg-gray-50 p-2 rounded-xl transition-colors"
                >
                  <div className="w-14 h-14 bg-white border border-gray-200 rounded-lg mx-auto mb-2 flex items-center justify-center group-hover:border-orange-300 transition-colors shadow-sm">
                    <img
                      src={coupon.logo}
                      alt={coupon.name}
                      className="w-10 h-10 object-contain"
                    />
                  </div>
                  <h3 className="text-xs font-medium text-gray-900 group-hover:text-orange-600 leading-tight">
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
