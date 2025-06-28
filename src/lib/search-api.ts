// 搜索数据类型定义
export interface SearchResult {
  id: string
  type: 'product' | 'review' | 'article' | 'topic' | 'category'
  title: string
  description: string
  url: string
  rating?: number
  reviewCount?: number
  imageUrl?: string
  category?: string
  tags?: string[]
  author?: string
  publishedAt?: string
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
  suggestions?: string[]
  filters?: {
    categories: string[]
    ratings: number[]
    types: string[]
  }
}

// 模拟数据库数据
const mockData: SearchResult[] = [
  // 产品评测
  {
    id: 'review-1',
    type: 'review',
    title: 'Mokwheel Electric Bike Review',
    description: 'A comprehensive review of the Mokwheel electric bike featuring excellent build quality and performance.',
    url: '/reviews/mokwheel-electric-bike',
    rating: 4.5,
    reviewCount: 127,
    imageUrl: 'https://ext.same-assets.com/2656189839/4256726469.jpeg',
    category: 'Electric Bikes',
    tags: ['electric bike', 'transportation', 'eco-friendly', 'commuting'],
    author: 'John Smith',
    publishedAt: '2024-01-15'
  },
  {
    id: 'review-2',
    type: 'review',
    title: 'My Patriot Supply Emergency Food Kits',
    description: 'Emergency food kits that provide long-term storage solutions for disaster preparedness.',
    url: '/reviews/my-patriot-supply',
    rating: 4.2,
    reviewCount: 89,
    imageUrl: 'https://ext.same-assets.com/2656189839/2382546874.jpeg',
    category: 'Emergency Food',
    tags: ['emergency', 'food storage', 'preparedness', 'survival'],
    author: 'Sarah Johnson',
    publishedAt: '2024-01-10'
  },
  {
    id: 'review-3',
    type: 'review',
    title: 'Saatva Mattress Complete Review',
    description: 'Luxury innerspring mattress offering hotel-quality comfort and support.',
    url: '/reviews/saatva-mattress',
    rating: 4.7,
    reviewCount: 203,
    imageUrl: 'https://ext.same-assets.com/2656189839/748255133.png',
    category: 'Mattresses',
    tags: ['mattress', 'sleep', 'luxury', 'comfort'],
    author: 'Mike Wilson',
    publishedAt: '2024-01-08'
  },

  // 产品类别
  {
    id: 'category-1',
    type: 'category',
    title: 'Electronics',
    description: 'Latest electronics, gadgets, and tech accessories including wireless earbuds, smartphones, and more.',
    url: '/categories/electronics',
    reviewCount: 25,
    imageUrl: 'https://ext.same-assets.com/2656189839/132898187.jpeg',
    category: 'Electronics',
    tags: ['electronics', 'technology', 'gadgets', 'reviews']
  },
  {
    id: 'category-2',
    type: 'category',
    title: 'Home & Kitchen',
    description: 'Home appliances, kitchen gadgets, and household essentials for modern living.',
    url: '/categories/home-kitchen',
    reviewCount: 42,
    imageUrl: 'https://ext.same-assets.com/2656189839/1722631724.jpeg',
    category: 'Home & Kitchen',
    tags: ['home', 'kitchen', 'appliances', 'household']
  },
  {
    id: 'category-3',
    type: 'category',
    title: 'Baby',
    description: 'Baby care products, monitors, and child safety items for new parents.',
    url: '/categories/baby',
    reviewCount: 18,
    imageUrl: 'https://ext.same-assets.com/2656189839/385441208.jpeg',
    category: 'Baby',
    tags: ['baby', 'children', 'parenting', 'safety']
  },

  // 主题页面
  {
    id: 'topic-1',
    type: 'topic',
    title: 'Dog Food',
    description: 'Premium dog food delivery services and nutrition reviews for your furry friends.',
    url: '/topics/dog-food',
    imageUrl: 'https://images.unsplash.com/photo-1551717743-49959800b1f6?w=400',
    category: 'Pet Care',
    tags: ['dog food', 'pets', 'nutrition', 'delivery']
  },
  {
    id: 'topic-2',
    type: 'topic',
    title: 'Identity Protection Services',
    description: 'Identity theft protection and monitoring services to keep your personal information safe.',
    url: '/topics/identity-protection',
    imageUrl: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400',
    category: 'Security',
    tags: ['identity protection', 'security', 'privacy', 'monitoring']
  },

  // 文章
  {
    id: 'article-1',
    type: 'article',
    title: 'What are the Top Project Management Tools?',
    description: 'Project management tools offer one of the most effective avenues for tackling everything from organization to communication.',
    url: '/articles/top-project-management-tools',
    imageUrl: 'https://ext.same-assets.com/2656189839/3938403337.jpeg',
    category: 'Business Tools',
    tags: ['project management', 'productivity', 'tools', 'business'],
    author: 'David Chen',
    publishedAt: '2024-01-20'
  }
]

// 搜索功能实现
export async function searchContent(
  query: string,
  options: {
    types?: string[]
    categories?: string[]
    limit?: number
    offset?: number
  } = {}
): Promise<SearchResponse> {
  const { types = [], categories = [], limit = 20, offset = 0 } = options

  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 100))

  let results = mockData

  // 类型筛选
  if (types.length > 0) {
    results = results.filter(item => types.includes(item.type))
  }

  // 类别筛选
  if (categories.length > 0) {
    results = results.filter(item =>
      item.category && categories.includes(item.category)
    )
  }

  // 全文搜索
  if (query.trim()) {
    const searchTerm = query.toLowerCase()
    results = results.filter(item => {
      const searchableText = [
        item.title,
        item.description,
        item.category,
        ...(item.tags || []),
        item.author || ''
      ].join(' ').toLowerCase()

      return searchableText.includes(searchTerm)
    })

    // 按相关性排序（简单实现）
    results.sort((a, b) => {
      const aScore = calculateRelevanceScore(a, searchTerm)
      const bScore = calculateRelevanceScore(b, searchTerm)
      return bScore - aScore
    })
  } else {
    // 没有查询时按评分和发布时间排序
    results.sort((a, b) => {
      if (a.rating && b.rating) {
        return b.rating - a.rating
      }
      if (a.publishedAt && b.publishedAt) {
        return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      }
      return 0
    })
  }

  const total = results.length
  const paginatedResults = results.slice(offset, offset + limit)

  return {
    results: paginatedResults,
    total,
    query,
    suggestions: await getSearchSuggestions(query),
    filters: {
      categories: [...new Set(mockData.map(item => item.category).filter(Boolean) as string[])],
      ratings: [5, 4, 3, 2, 1],
      types: ['review', 'category', 'topic', 'article']
    }
  }
}

// 计算搜索相关性得分
function calculateRelevanceScore(item: SearchResult, searchTerm: string): number {
  let score = 0
  const term = searchTerm.toLowerCase()

  // 标题匹配权重最高
  if (item.title.toLowerCase().includes(term)) {
    score += 10
  }

  // 描述匹配
  if (item.description.toLowerCase().includes(term)) {
    score += 5
  }

  // 类别匹配
  if (item.category?.toLowerCase().includes(term)) {
    score += 3
  }

  // 标签匹配
  if (item.tags?.some(tag => tag.toLowerCase().includes(term))) {
    score += 2
  }

  // 评分加成
  if (item.rating) {
    score += item.rating
  }

  return score
}

// 获取搜索建议
export async function getSearchSuggestions(query: string): Promise<string[]> {
  if (!query.trim()) return []

  const suggestions = [
    'wireless earbuds',
    'electric bikes',
    'dog food reviews',
    'home security',
    'kitchen appliances',
    'baby monitors',
    'mattress reviews',
    'project management tools'
  ]

  const term = query.toLowerCase()
  return suggestions
    .filter(suggestion => suggestion.includes(term))
    .slice(0, 5)
}

// 获取热门搜索
export async function getPopularSearches(): Promise<string[]> {
  return [
    'wireless earbuds',
    'electric bikes',
    'mattress reviews',
    'dog food',
    'home security',
    'kitchen appliances'
  ]
}

// 获取相关搜索
export async function getRelatedSearches(query: string): Promise<string[]> {
  const related: Record<string, string[]> = {
    'bike': ['electric bikes', 'mountain bikes', 'road bikes', 'bike accessories'],
    'food': ['dog food', 'cat food', 'emergency food', 'organic food'],
    'home': ['home security', 'home appliances', 'smart home', 'home improvement'],
    'electronics': ['smartphones', 'laptops', 'headphones', 'tablets']
  }

  const term = query.toLowerCase()
  for (const [key, suggestions] of Object.entries(related)) {
    if (term.includes(key)) {
      return suggestions
    }
  }

  return []
}

// 缓存相关功能
class SearchCache {
  private cache = new Map<string, { data: SearchResponse; timestamp: number }>()
  private readonly TTL = 5 * 60 * 1000 // 5分钟

  get(key: string): SearchResponse | null {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() - item.timestamp > this.TTL) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  set(key: string, data: SearchResponse): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  clear(): void {
    this.cache.clear()
  }
}

export const searchCache = new SearchCache()
