import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

const articles = [
  {
    id: "how-to-take-meeting-minutes-using-software-for-project-management",
    title: "How to Take Meeting Minutes Using Software for Project Management",
    date: "Sep 16, 2022",
    excerpt: "They may not be loved by everyone involved, but meetings are an essential component to any workplace that gives everyone a chance to come together and collaborate. A fundamental requirement, especially during a project life cycle, they open the do...",
    image: "https://ext.same-assets.com/2656189839/1514386506.png"
  },
  {
    id: "how-does-software-for-project-management-boost-productivity",
    title: "How Does Software for Project Management Boost Productivity?",
    date: "Sep 16, 2022",
    excerpt: "Often seen as the secret weapon inside every productive workplace, the best software for project management is an all-encompassing tool that is designed to help teams and individuals plan, execute, and track the projects they are working on. Equip...",
    image: "https://ext.same-assets.com/2656189839/3486248999.png"
  },
  {
    id: "top-reports-within-the-best-software-for-project-management",
    title: "Top Reports Within the Best Software for Project Management",
    date: "Sep 16, 2022",
    excerpt: "Navigating the complexities of a project is no easy job, and as a manager you need to be able to stay on top of, and stay aware of, everything that is happening under you. From what your team is working on to how your resources are allocated, ther...",
    image: "https://ext.same-assets.com/2656189839/622785419.png"
  },
  {
    id: "critical-questions-project-managers-should-ask-their-teams",
    title: "Critical Questions Project Managers Should Ask Their Teams",
    date: "Sep 16, 2022",
    excerpt: "Strong communication skills are an absolute must for any project manager, and if youre in charge of leading and guiding your team towards success then you need to be able to effectively connect with them each step of the way. Fulfilling communica...",
    image: "https://ext.same-assets.com/2656189839/1327087978.png"
  },
  {
    id: "what-is-project-quality-management",
    title: "What Is Project Quality Management?",
    date: "Sep 16, 2022",
    excerpt: "Project quality management is a key component to any successful project, and it includes the methods and techniques that managers employ to consistently measure how a project is progressing and whether or not the on-going tasks and activities are ...",
    image: "https://ext.same-assets.com/2656189839/891129640.png"
  },
  {
    id: "security-measures-every-project-manager-should-implement",
    title: "Security Measures Every Project Manager Should Implement",
    date: "Sep 14, 2022",
    excerpt: "Data security is a topic that isnt discussed frequently enough among project managers, however it is a highly important and integral part of doing business that needs to be considered. From the measures in place inside the ...",
    image: "https://ext.same-assets.com/2656189839/3973181521.png"
  },
  {
    id: "how-to-create-a-budget-using-software-for-project-management",
    title: "How to Create a Budget Using Software for Project Management",
    date: "Sep 14, 2022",
    excerpt: "Completing a project successfully requires more than just a goal and some hope, and in order to achieve the best results possible you want to plan ahead and prepare you and your team for whats to come. Early planning is an essential factor in suc...",
    image: "https://ext.same-assets.com/2656189839/3629670938.png"
  },
  {
    id: "agile-vs-waterfall-which-one-should-you-use",
    title: "Agile vs. Waterfall: Which One Should You Use?",
    date: "Sep 14, 2022",
    excerpt: "Encompassing all of the procedures, methods, tools, and techniques you use when completing a project, methodologies are robust frameworks that house everything you need and will use when doing your work. For many newcomers to the world of project ...",
    image: "https://ext.same-assets.com/2656189839/1344065956.png"
  }
]

export default function ArticlesPage() {
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
                <span className="text-gray-900 font-medium">All Articles</span>
              </li>
            </ol>
          </nav>
        </div>
      </div>

      {/* Header */}
      <section className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-gray-900">All Articles</h1>
        </div>
      </section>

      {/* Articles Grid */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-8">
            {articles.map((article) => (
              <Card key={article.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-start space-x-4">
                    <img
                      src={article.image}
                      alt={article.title}
                      className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="secondary" className="text-xs">
                          Created at {article.date}
                        </Badge>
                      </div>
                      <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-orange-600">
                        <Link href={`/articles/${article.id}`}>
                          {article.title}
                        </Link>
                      </h2>
                      <p className="text-gray-600 mb-4 leading-relaxed">
                        {article.excerpt}
                      </p>
                      <Link
                        href={`/articles/${article.id}`}
                        className="inline-flex items-center text-orange-600 hover:text-orange-700 font-medium"
                      >
                        Read
                        <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </Link>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-center items-center space-x-4 mt-12">
            <div className="flex items-center space-x-2">
              <span className="px-3 py-2 bg-orange-600 text-white rounded font-medium">1</span>
              <Link href="/articles?page=2" className="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">2</Link>
              <Link href="/articles?page=3" className="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">3</Link>
              <Link href="/articles?page=4" className="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">4</Link>
              <span className="px-3 py-2 text-gray-500">...</span>
              <Link href="/articles?page=12" className="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">12</Link>
              <Link href="/articles?page=2" className="px-3 py-2 text-orange-600 hover:text-orange-700 font-medium">Next</Link>
              <Link href="/articles?page=12" className="px-3 py-2 text-orange-600 hover:text-orange-700 font-medium">Last</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
