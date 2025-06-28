import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function OptOutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <section className="bg-white py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-gray-900">Do Not Sell My Personal Information</h1>
          <p className="text-gray-600 mt-4">Manage your privacy preferences</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="p-8">
            <div className="prose prose-lg max-w-none mb-8">
              <h2>Your California Privacy Rights</h2>
              <p>
                Under the California Consumer Privacy Act (CCPA), California residents have the right to opt-out of the sale of their personal information.
              </p>

              <h3>What Information We Collect</h3>
              <p>
                We may collect the following categories of personal information:
              </p>
              <ul>
                <li>Identifiers (name, email address, IP address)</li>
                <li>Commercial information (products or services purchased)</li>
                <li>Internet or electronic network activity information</li>
                <li>Geolocation data</li>
                <li>Inferences drawn from other personal information</li>
              </ul>

              <h3>How We Use Your Information</h3>
              <p>
                We use your personal information to provide our services, improve user experience, and for marketing purposes.
              </p>
            </div>

            <div className="border-t pt-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Submit an Opt-Out Request</h3>
              <form className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <Input
                    type="email"
                    id="email"
                    placeholder="Enter your email address"
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <Input
                    type="text"
                    id="name"
                    placeholder="Enter your full name"
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="request" className="block text-sm font-medium text-gray-700 mb-2">
                    Request Details (Optional)
                  </label>
                  <textarea
                    id="request"
                    rows={4}
                    placeholder="Please provide any additional details about your request"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>

                <Button className="w-full bg-orange-600 hover:bg-orange-700 text-white">
                  Submit Opt-Out Request
                </Button>
              </form>

              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>Note:</strong> We will process your request within 30 days and send you a confirmation email.
                  You may also contact us directly at privacy@consumervoice.org for any privacy-related questions.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  )
}
