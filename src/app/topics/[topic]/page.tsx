import { notFound } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TopicPage from '@/components/TopicPage'
import { topics } from '@/lib/data'

interface TopicPageProps {
  params: Promise<{
    topic: string
  }>
}

export function generateStaticParams() {
  return topics.map((topic) => ({
    topic: topic.slug,
  }))
}

export default async function Topic({ params }: TopicPageProps) {
  const { topic: topicSlug } = await params
  const topic = topics.find(t => t.slug === topicSlug)

  if (!topic) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <TopicPage topic={topic} />
      </main>
      <Footer />
    </div>
  )
}

export async function generateMetadata({ params }: TopicPageProps) {
  const { topic: topicSlug } = await params
  const topic = topics.find(t => t.slug === topicSlug)

  if (!topic) {
    return {
      title: 'Topic Not Found',
    }
  }

  return {
    title: `${topic.name} - ConsumerVoice.org`,
    description: topic.description,
  }
}
