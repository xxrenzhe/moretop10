import { notFound } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import CategoryPage from '@/components/CategoryPage'
import { productCategories } from '@/lib/data'

interface CategoryPageProps {
  params: Promise<{
    category: string
  }>
}

export function generateStaticParams() {
  return productCategories.map((category) => ({
    category: category.slug,
  }))
}

export default async function Category({ params }: CategoryPageProps) {
  const { category: categorySlug } = await params
  const category = productCategories.find(cat => cat.slug === categorySlug)

  if (!category) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <CategoryPage category={category} />
      </main>
      <Footer />
    </div>
  )
}

export async function generateMetadata({ params }: CategoryPageProps) {
  const { category: categorySlug } = await params
  const category = productCategories.find(cat => cat.slug === categorySlug)

  if (!category) {
    return {
      title: 'Category Not Found',
    }
  }

  return {
    title: `${category.title} Reviews - ConsumerVoice.org`,
    description: category.description,
  }
}
