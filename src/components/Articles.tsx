import { Card } from "@/components/ui/card"
import Link from "next/link"

const articles = [
  {
    id: "what-are-the-top-project-management-tools",
    title: "What are the Top Project Management Tools?",
    excerpt: "Project management tools offer one of the most effective avenues for tackling everything from organization to communication. Packed full of useful ...",
    image: "https://ext.same-assets.com/2656189839/4143656215.jpeg",
    href: "/articles/what-are-the-top-project-management-tools"
  },
  {
    id: "how-to-manage-remote-teams-using-project-management-software",
    title: "How to Manage Remote Teams Using Project Management Software",
    excerpt: "In today's modern world the existence of remote teams and workers is becoming more common, and as a manager this can be a challenging change from h...",
    image: "https://ext.same-assets.com/2656189839/84477253.jpeg",
    href: "/articles/how-to-manage-remote-teams-using-project-management-software"
  }
]

export default function Articles() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-2xl font-bold text-gray-900">Articles</h2>
          <Link href="/articles" className="text-orange-600 hover:text-orange-700 font-medium">
            + SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {articles.map((article, index) => (
            <Card key={article.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
              <Link href={article.href}>
                <div className="aspect-[16/9] relative overflow-hidden">
                  <img
                    src={article.image}
                    alt={article.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-orange-600 transition-colors mb-3 leading-tight">
                    {article.title}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {article.excerpt}
                  </p>
                </div>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
