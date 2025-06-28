import { Card } from "@/components/ui/card"

export default function HowWeRankPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <img
              src="https://ext.same-assets.com/2656189839/2560185137.png"
              alt="ConsumerVoice Rankings"
              className="mx-auto mb-8 h-32 w-auto"
            />
            <h1 className="text-4xl font-bold text-gray-900 mb-6">
              How We Rank Companies on ConsumerVoice.org?
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              ConsumerVoice.org ranks companies using a proprietary algorithm incorporating expert and customer reviews, user experience, lifetime value, and overall brand trustworthiness.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-12">

            {/* Customer Reviews & Ratings */}
            <Card className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Customer Reviews & Ratings
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We determine a customer rating by scouring the internet for real reviews from individual users as well as review aggregators to determine a consumer review score. Additionally, we incorporate consumer preferences exhibited on our site including which brands shoppers prefer.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Our system pulls together thousands of data points for a single product or service into a single quantifiable rating that is designed to mimic, as well as simplify, the research process of a typical consumer.
              </p>
            </Card>

            {/* Expert Reviews */}
            <Card className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Expert Reviews
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                In addition to user preferences, our experts spend time researching and/or testing every product on our site. By developing category-level expertise, our writers are able to compare products, answer the most common questions shoppers have, and help determine an accurate ranking.
              </p>
              <p className="text-gray-700 leading-relaxed">
                We pride ourselves on ensuring the authenticity of the consumer reviews published on our site. Our Review Moderation Team verified every review we feature prior to publication. Reviews the team identifies as factually inaccurate, fraudulent, and/or purposely misleading are denied publication.
              </p>
            </Card>

            {/* Brand Signals & Affiliate Relationships */}
            <Card className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Brand Signals & Affiliate Relationships
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                To keep our site free for users, we may be compensated through affiliate relationships with the brands featured on our site. Many advertisers pay us a referral fee for customers who make a purchase or call the phone numbers featured on our website.
              </p>
              <p className="text-gray-700 leading-relaxed">
                In addition to enabling us to capture the revenue these relationships generate, the information shared by our partners gives us valuable insight into how customers perceive the stores with which we work, and how those stores value their customers. Partners may influence their position on our website, including the order in which they appear on the page through premium payouts, except where prohibited by law for the mortgage and other home lending products listed on this site. However, this is only a piece of a companies overall score.
              </p>
            </Card>

          </div>
        </div>
      </section>
    </div>
  )
}
