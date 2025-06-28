import { Suspense } from 'react'
import Header from '@/components/Header'
import SearchResults from '@/components/SearchResults'

export default function SearchPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main>
        <Suspense fallback={<div className="flex justify-center items-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cv-gold-600" /></div>}>
          <SearchResults />
        </Suspense>
      </main>
    </div>
  )
}

export const metadata = {
  title: 'Search Results - ConsumerVoice.org',
  description: 'Search results for products, reviews, and articles',
}
