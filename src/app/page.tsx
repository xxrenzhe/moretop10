import Header from '@/components/Header'
import HeroSection from '@/components/HeroSection'
import FeaturedTopics from '@/components/FeaturedTopics'
import TopReviews from '@/components/TopReviews'
import AllProducts from '@/components/AllProducts'
import Articles from '@/components/Articles'
import Coupons from '@/components/Coupons'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <HeroSection />
        <FeaturedTopics />
        <TopReviews />
        <AllProducts />
        <Articles />
        <Coupons />
      </main>
      <Footer />
    </div>
  )
}
