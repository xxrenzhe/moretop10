'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Menu, Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { useSearch } from '@/contexts/SearchContext'
import { topics, productCategories } from '@/lib/data'

export default function Header() {
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  const { setSearchQuery, setSelectedCategory } = useSearch()
  const router = useRouter()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (localSearchQuery.trim()) {
      setSearchQuery(localSearchQuery)
      setSelectedCategory('all')
      router.push(`/search?q=${encodeURIComponent(localSearchQuery)}`)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch(e as React.FormEvent)
    }
  }

  return (
    <header className="w-full bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Mobile menu button */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-6 w-6 text-cv-gold-600" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <div className="py-6">
                <h3 className="font-semibold text-lg mb-4">Topics</h3>
                <div className="space-y-3 mb-6">
                  {topics.map((topic) => (
                    <a
                      key={topic.id}
                      href={topic.href}
                      className="block text-gray-700 hover:text-cv-gold-600"
                    >
                      {topic.name}
                    </a>
                  ))}
                </div>
                <h3 className="font-semibold text-lg mb-4">Categories</h3>
                <div className="space-y-3">
                  {productCategories.map((category) => (
                    <a
                      key={category.id}
                      href={category.href}
                      className="block text-gray-700 hover:text-cv-gold-600"
                    >
                      {category.title}
                    </a>
                  ))}
                </div>
              </div>
            </SheetContent>
          </Sheet>

          {/* Desktop Topics Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <div className="relative group">
              <Button variant="ghost" className="text-gray-700 hover:text-cv-gold-600 font-medium">
                <Menu className="h-4 w-4 mr-2 text-cv-gold-600" />
                Topics
              </Button>
              {/* Dropdown Menu */}
              <div className="absolute top-full left-0 mt-2 w-80 bg-white shadow-lg rounded-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="p-6">
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Featured Topics</h4>
                      <div className="space-y-2">
                        {topics.slice(0, 4).map((topic) => (
                          <a
                            key={topic.id}
                            href={topic.href}
                            className="block text-gray-600 hover:text-cv-gold-600 text-sm"
                          >
                            {topic.name}
                          </a>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Categories</h4>
                      <div className="space-y-2">
                        {productCategories.slice(0, 4).map((category) => (
                          <a
                            key={category.id}
                            href={category.href}
                            className="block text-gray-600 hover:text-cv-gold-600 text-sm"
                          >
                            {category.title}
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-lg mx-4">
            <form onSubmit={handleSearch}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  type="text"
                  placeholder="Search products, reviews, articles..."
                  value={localSearchQuery}
                  onChange={(e) => setLocalSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-10 pr-10 border-gray-200 focus:border-cv-gold-500 focus:ring-cv-gold-500"
                />
                {localSearchQuery && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8"
                    onClick={() => setLocalSearchQuery('')}
                  >
                    <X className="h-4 w-4 text-gray-400" />
                  </Button>
                )}
              </div>
            </form>
          </div>

          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-cv-gold-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">C</span>
              </div>
              <span className="font-bold text-xl text-gray-800">
                CONSUMER<span className="text-cv-gold-600">VOICE</span>
              </span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
