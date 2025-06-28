import { Card } from "@/components/ui/card"
import Link from "next/link"

const couponCategories = [
  {
    category: "Accounts Payable Software",
    href: "/top-accounts-payable-software",
    coupons: [
      { name: "Bill.com Coupons", href: "/billcom-coupons", logo: "https://ext.same-assets.com/2656189839/4288140269.jpeg" }
    ]
  },
  {
    category: "Ad Blockers",
    href: "/top-adblockers",
    coupons: [
      { name: "Atlas VPN Coupons", href: "/atlas-vpn-coupons", logo: "https://ext.same-assets.com/2656189839/192925316.jpeg" },
      { name: "IPVanish Coupons", href: "/ipvanish-coupons", logo: "https://ext.same-assets.com/2656189839/2061471696.png" },
      { name: "NordVPN Antivirus Coupons", href: "/nordvpn-d6bb964c-4f98-436d-92e9-fe4fe6d01b49-coupons", logo: "https://ext.same-assets.com/2656189839/4183823254.jpeg" },
      { name: "Surfshark Coupons", href: "/surfshark-coupons", logo: "https://ext.same-assets.com/2656189839/194475946.jpeg" },
      { name: "Total Adblock Coupons", href: "/total-adblock-coupons", logo: "https://ext.same-assets.com/2656189839/2167711835.jpeg" }
    ]
  },
  {
    category: "Antivirus Software",
    href: "/top-antivirus-software",
    coupons: [
      { name: "Aura Coupons", href: "/aura-91a762cc-6e0a-4742-9f70-d3595890c206-coupons", logo: "https://ext.same-assets.com/2656189839/817511782.jpeg" },
      { name: "Avast Coupons", href: "/avast-coupons", logo: "https://ext.same-assets.com/2656189839/3759193221.false" },
      { name: "Bitdefender Coupons", href: "/bitdefender-coupons", logo: "https://ext.same-assets.com/2656189839/1028067676.jpeg" },
      { name: "Guardio Coupons", href: "/guardio-coupons", logo: "https://ext.same-assets.com/2656189839/2936334862.jpeg" },
      { name: "iolo Coupons", href: "/iolo-coupons", logo: "https://ext.same-assets.com/2656189839/527420601.png" },
      { name: "McAfee Coupons", href: "/mcaffe-coupons", logo: "https://ext.same-assets.com/2656189839/1683654460.jpeg" },
      { name: "Norton Coupons", href: "/norton-coupons", logo: "https://ext.same-assets.com/2656189839/4172524936.jpeg" },
      { name: "TotalAV Coupons", href: "/totalav-coupons", logo: "https://ext.same-assets.com/2656189839/3879588659.jpeg" },
      { name: "VIPRE Coupons", href: "/vipre-coupons", logo: "https://ext.same-assets.com/2656189839/3323873033.jpeg" },
      { name: "Webroot Coupons", href: "/webroot-coupons", logo: "https://ext.same-assets.com/2656189839/3349708600.jpeg" }
    ]
  },
  {
    category: "Christmas Cards",
    href: "/top-christmas-cards",
    coupons: [
      { name: "Mixbook Coupons", href: "/mixbook-coupons", logo: "https://ext.same-assets.com/2656189839/1884972287.jpeg" },
      { name: "Shutterfly Coupons", href: "/shutterfly-coupons", logo: "https://ext.same-assets.com/2656189839/1334423217.jpeg" },
      { name: "Snapfish Coupons", href: "/snapfish-coupons", logo: "https://ext.same-assets.com/2656189839/74778196.jpeg" }
    ]
  },
  {
    category: "Cold Plunge Tubs",
    href: "/top-cold-plunge-tubs",
    coupons: [
      { name: "Ice Barrel Coupons", href: "/ice-barrel-coupons", logo: "https://ext.same-assets.com/2656189839/1728820581.jpeg" },
      { name: "Nordik Recovery Coupons", href: "/nordik-recovery-coupons", logo: "https://ext.same-assets.com/2656189839/1722608250.jpeg" },
      { name: "Plunge Coupons", href: "/plunge-coupons", logo: "https://ext.same-assets.com/2656189839/2593608302.jpeg" },
      { name: "Sun Home Saunas Coupons", href: "/sun-home-saunas-coupons", logo: "https://ext.same-assets.com/2656189839/2438529435.jpeg" }
    ]
  },
  {
    category: "Collagen Supplements",
    href: "/top-collagen-supplements",
    coupons: [
      { name: "AnnieMak Coupons", href: "/anniemak-coupons", logo: "https://ext.same-assets.com/2656189839/1261955606.jpeg" },
      { name: "Mindbodygreen Coupons", href: "/mindbodygreen-coupons", logo: "https://ext.same-assets.com/2656189839/2563722886.jpeg" },
      { name: "Organifi Coupons", href: "/organifi-coupons", logo: "https://ext.same-assets.com/2656189839/1384873249.jpeg" },
      { name: "SkinnyFit Coupons", href: "/skinnyfit-coupons", logo: "https://ext.same-assets.com/2656189839/3753931819.jpeg" }
    ]
  },
  {
    category: "Credit Monitoring Software",
    href: "/top-credit-monitoring-software",
    coupons: [
      { name: "EverSafe Coupons", href: "/eversafe-coupons", logo: "https://ext.same-assets.com/2656189839/2335523406.jpeg" },
      { name: "IdentityForce Coupons", href: "/identity-force-coupons", logo: "https://ext.same-assets.com/2656189839/614432677.jpeg" },
      { name: "IdentityIQ Coupons", href: "/identity-iq-coupons", logo: "https://ext.same-assets.com/2656189839/2605263461.jpeg" },
      { name: "Incogni Coupons", href: "/incogni-coupons", logo: "https://ext.same-assets.com/2656189839/3174845052.jpeg" },
      { name: "LifeLock Coupons", href: "/lifelock-coupons", logo: "https://ext.same-assets.com/2656189839/2048514165.jpeg" },
      { name: "myFico Coupons", href: "/myfico-coupons", logo: "https://ext.same-assets.com/2656189839/1807281343.jpeg" },
      { name: "OmniWatch Coupons", href: "/omniwatch-coupons", logo: "https://ext.same-assets.com/2656189839/3147604219.jpeg" }
    ]
  }
]

export default function CouponsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav className="flex" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link href="/" className="text-gray-500 hover:text-gray-700">
                  Main
                </Link>
              </li>
              <li>
                <span className="text-gray-400">/</span>
              </li>
              <li>
                <span className="text-gray-900 font-medium">All Coupons</span>
              </li>
            </ol>
          </nav>
        </div>
      </div>

      {/* Header */}
      <section className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-gray-900">All Coupons</h1>
        </div>
      </section>

      {/* Coupons Categories */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-12">
            {couponCategories.map((category) => (
              <div key={category.category}>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  <Link href={category.href} className="hover:text-orange-600">
                    {category.category}
                  </Link>
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {category.coupons.map((coupon) => (
                    <Card key={coupon.name} className="overflow-hidden hover:shadow-lg transition-shadow">
                      <Link href={coupon.href} className="block p-6">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            <img
                              src={coupon.logo}
                              alt={coupon.name}
                              className="w-12 h-12 object-contain rounded-lg"
                            />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-medium text-gray-900 group-hover:text-orange-600">
                              {coupon.name}
                            </h3>
                          </div>
                        </div>
                      </Link>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
