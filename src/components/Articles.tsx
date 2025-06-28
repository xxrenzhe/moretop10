import Link from "next/link"

const articles = [
  {
    id: "what-are-the-top-project-management-tools",
    title: "What are the Top Project Management Tools?",
    excerpt: "Project management tools offer one of the most effective avenues for tackling everything from organization to communication. Packed full of useful ...",
    image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    href: "/articles/what-are-the-top-project-management-tools"
  },
  {
    id: "how-to-manage-remote-teams-using-project-management-software",
    title: "How to Manage Remote Teams Using Project Management Software",
    excerpt: "In today's modern world the existence of remote teams and workers is becoming more common, and as a manager this can be a challenging change from h...",
    image: "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    href: "/articles/how-to-manage-remote-teams-using-project-management-software"
  }
]

export default function Articles() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Articles</h2>
          <Link href="/articles" className="text-sm font-bold text-gray-900 hover:text-cv-gold-500 flex items-center">
            <span className="w-2 h-2 bg-cv-gold-500 rounded-full mr-2"></span>
            SEE ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {articles.map((article) => (
            <Link key={article.id} href={article.href} className="group block bg-white rounded-3xl shadow-sm hover:shadow-md transition-all overflow-hidden">
                <div className="aspect-video relative overflow-hidden">
                  <img
                    src={article.image}
                    alt={article.title}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                </div>
                <div className="p-8">
                  <h3 className="text-2xl font-bold text-gray-800 group-hover:text-cv-gold-500 transition-colors mb-4 leading-snug">
                    {article.title}
                  </h3>
                  <p className="text-base text-gray-600 leading-relaxed">
                    {article.excerpt}
                  </p>
                </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}
