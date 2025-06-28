import { notFound } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import ReviewDetail from '@/components/ReviewDetail'
import { reviews } from '@/lib/data'

interface ReviewPageProps {
  params: Promise<{
    reviewId: string
  }>
}

export function generateStaticParams() {
  return reviews.map((review) => ({
    reviewId: review.href.split('/').pop() || '',
  }))
}

export default async function ReviewPage({ params }: ReviewPageProps) {
  const { reviewId } = await params
  const review = reviews.find(r =>
    r.href.split('/').pop() === reviewId ||
    r.id === reviewId
  )

  if (!review) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <ReviewDetail review={review} />
      </main>
      <Footer />
    </div>
  )
}

export async function generateMetadata({ params }: ReviewPageProps) {
  const { reviewId } = await params
  const review = reviews.find(r =>
    r.href.split('/').pop() === reviewId ||
    r.id === reviewId
  )

  if (!review) {
    return {
      title: 'Review Not Found',
    }
  }

  return {
    title: `${review.title} - ConsumerVoice.org`,
    description: review.excerpt,
  }
}
