import { Card } from "@/components/ui/card"

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">
              Contact Us
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get in touch with our team at ConsumerVoice.org
            </p>
          </div>
        </div>
      </section>

      {/* Contact Information */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Offices</h2>

            {/* Office Tabs */}
            <div className="border-b border-gray-200 mb-8">
              <nav className="-mb-px flex space-x-8">
                <button className="border-b-2 border-orange-500 py-2 px-1 text-sm font-medium text-orange-600">
                  Austin
                </button>
              </nav>
            </div>

            {/* Austin Office */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Austin Office</h3>
                <div className="text-gray-700">
                  <p>500 E 4th St. PMB 263</p>
                  <p>Austin, TX 78701</p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Email</h3>
                <a
                  href="mailto:info@consumervoice.org"
                  className="text-orange-600 hover:text-orange-700 font-medium"
                >
                  info@consumervoice.org
                </a>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  )
}
