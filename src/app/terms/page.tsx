import { Card } from "@/components/ui/card"

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <section className="bg-white py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-gray-900">Terms of Service</h1>
          <p className="text-gray-600 mt-4">Last updated: December 2024</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="p-8">
            <div className="prose prose-lg max-w-none">
              <h2>Acceptance of Terms</h2>
              <p>
                By accessing and using ConsumerVoice.org, you accept and agree to be bound by the terms and provision of this agreement.
              </p>

              <h2>Use License</h2>
              <p>
                Permission is granted to temporarily download one copy of the materials on ConsumerVoice.org for personal, non-commercial transitory viewing only.
              </p>

              <h2>Disclaimer</h2>
              <p>
                The materials on ConsumerVoice.org are provided on an 'as is' basis. ConsumerVoice.org makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
              </p>

              <h2>Limitations</h2>
              <p>
                In no event shall ConsumerVoice.org or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on ConsumerVoice.org, even if ConsumerVoice.org or a ConsumerVoice.org authorized representative has been notified orally or in writing of the possibility of such damage.
              </p>

              <h2>Accuracy of Materials</h2>
              <p>
                The materials appearing on ConsumerVoice.org could include technical, typographical, or photographic errors. ConsumerVoice.org does not warrant that any of the materials on its website are accurate, complete, or current.
              </p>

              <h2>Links</h2>
              <p>
                ConsumerVoice.org has not reviewed all of the sites linked to our website and is not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by ConsumerVoice.org of the site.
              </p>

              <h2>Modifications</h2>
              <p>
                ConsumerVoice.org may revise these terms of service for its website at any time without notice. By using this website, you are agreeing to be bound by the then current version of these terms of service.
              </p>

              <h2>Contact Information</h2>
              <p>
                If you have any questions about these Terms of Service, please contact us at:
              </p>
              <p>
                Email: legal@consumervoice.org<br />
                Address: 500 E 4th St. PMB 263, Austin, TX 78701
              </p>
            </div>
          </Card>
        </div>
      </section>
    </div>
  )
}
