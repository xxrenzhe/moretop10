export interface Topic {
  id: string
  name: string
  slug: string
  icon: string
  description: string
  href: string
}

export interface Review {
  id: string
  title: string
  category: string
  categorySlug: string
  brand: string
  rating: number
  image: string
  excerpt: string
  href: string
  pros: string[]
  cons: string[]
  features: string[]
  pricing: string
  verdict: string
  content: string
  author: string
  publishedAt: string
}

export interface ProductCategory {
  id: string
  title: string
  slug: string
  subtitle: string
  description: string
  items?: string[]
  icon: string
  image: string
  href: string
  reviewCount: number
}

export interface Article {
  id: string
  title: string
  excerpt: string
  content: string
  image: string
  href: string
  author: string
  publishedAt: string
  category: string
}

export interface Coupon {
  id: string
  name: string
  brand: string
  logo: string
  discount: string
  code?: string
  href: string
  expiresAt: string
}

// Featured Topics Data
export const topics: Topic[] = [
  {
    id: '1',
    name: 'Dog Food',
    slug: 'dog-food',
    icon: 'Dog',
    description: 'Premium dog food delivery services and nutrition reviews',
    href: '/top-dog-food-delivery'
  },
  {
    id: '2',
    name: 'Identity Protection Services',
    slug: 'identity-protection',
    icon: 'Shield',
    description: 'Identity theft protection and monitoring services',
    href: '/top-identity-protection-services'
  },
  {
    id: '3',
    name: 'Life Insurance',
    slug: 'life-insurance',
    icon: 'Heart',
    description: 'Life insurance policies and coverage options',
    href: '/top-life-insurance'
  },
  {
    id: '4',
    name: 'Pet Insurance Plans',
    slug: 'pet-insurance',
    icon: 'Shield',
    description: 'Comprehensive pet insurance coverage and plans',
    href: '/top-pet-insurance'
  },
  {
    id: '5',
    name: 'Meal Delivery',
    slug: 'meal-delivery',
    icon: 'Truck',
    description: 'Meal kit delivery services and subscription boxes',
    href: '/top-meal-delivery-services'
  },
  {
    id: '6',
    name: 'Electric Bikes',
    slug: 'electric-bikes',
    icon: 'Bike',
    description: 'Electric bicycle reviews and comparisons',
    href: '/top-electric-bikes'
  },
  {
    id: '7',
    name: 'Auto Insurance',
    slug: 'auto-insurance',
    icon: 'Car',
    description: 'Car insurance providers and coverage options',
    href: '/top-auto-insurance'
  }
]

// Product Categories Data
export const productCategories: ProductCategory[] = [
  {
    id: '1',
    title: 'Electronics',
    slug: 'electronics',
    subtitle: 'Wireless Earbuds',
    description: 'Latest electronics, gadgets, and tech accessories',
    icon: 'Headphones',
    image: 'https://ext.same-assets.com/2656189839/132898187.jpeg',
    href: '/best-wireless-earbuds',
    reviewCount: 25
  },
  {
    id: '2',
    title: 'Home & Kitchen',
    slug: 'home-kitchen',
    subtitle: 'Keurig Coffee Makers',
    description: 'Home appliances, kitchen gadgets, and household essentials',
    items: ['Water Filtration'],
    icon: 'Home',
    image: 'https://ext.same-assets.com/2656189839/1722631724.jpeg',
    href: '/best-keurig-coffee-makers',
    reviewCount: 42
  },
  {
    id: '3',
    title: 'Baby',
    slug: 'baby',
    subtitle: 'Baby Monitors',
    description: 'Baby care products, monitors, and child safety items',
    items: ['Baby Rockers'],
    icon: 'Baby',
    image: 'https://ext.same-assets.com/2656189839/385441208.jpeg',
    href: '/best-baby-monitors',
    reviewCount: 18
  },
  {
    id: '4',
    title: 'Beauty & Health',
    slug: 'beauty-health',
    subtitle: 'Moisturizers with SPF',
    description: 'Beauty products, skincare, and health accessories',
    items: ['Rowing Machines'],
    icon: 'Heart',
    image: 'https://ext.same-assets.com/2656189839/826846371.jpeg',
    href: '/best-moisturizers-with-spf',
    reviewCount: 33
  },
  {
    id: '5',
    title: 'Automotive',
    slug: 'automotive',
    subtitle: 'Cargo Boxes',
    description: 'Car accessories, automotive tools, and vehicle gear',
    items: ['Car Phone Mounts'],
    icon: 'Car',
    image: 'https://ext.same-assets.com/2656189839/826846371.jpeg',
    href: '/best-cargo-boxes',
    reviewCount: 29
  },
  {
    id: '6',
    title: 'Pets',
    slug: 'pets',
    subtitle: 'Cat Beds',
    description: 'Pet care products, accessories, and health items',
    items: ['Dog Treats'],
    icon: 'Dog',
    image: 'https://ext.same-assets.com/2656189839/948572364.jpeg',
    href: '/best-cat-beds',
    reviewCount: 37
  }
]

// Reviews Data
export const reviews: Review[] = [
  {
    id: '1',
    title: 'Mokwheel Electric Bike Review',
    category: 'Electric Bikes',
    categorySlug: 'electric-bikes',
    brand: 'Mokwheel',
    rating: 4.5,
    image: 'https://ext.same-assets.com/2656189839/4256726469.jpeg',
    excerpt: 'A comprehensive review of the Mokwheel electric bike featuring excellent build quality and performance.',
    href: '/mokwheel-review',
    pros: ['Excellent build quality', 'Long battery life', 'Smooth ride', 'Great value for money'],
    cons: ['Heavy weight', 'Limited color options'],
    features: ['750W motor', '48V 15Ah battery', '50-mile range', 'Shimano 7-speed'],
    pricing: '$1,299 - $1,599',
    verdict: 'The Mokwheel electric bike offers exceptional value with its powerful motor and long-lasting battery, making it perfect for daily commuting.',
    content: 'Full review content would go here...',
    author: 'John Smith',
    publishedAt: '2024-01-15'
  },
  {
    id: '2',
    title: 'My Patriot Supply Emergency Food Kits',
    category: 'Emergency Food Kits',
    categorySlug: 'emergency-food',
    brand: 'My Patriot Supply',
    rating: 4.2,
    image: 'https://ext.same-assets.com/2656189839/2382546874.jpeg',
    excerpt: 'Emergency food kits that provide long-term storage solutions for disaster preparedness.',
    href: '/my-patriot-supply-review',
    pros: ['25-year shelf life', 'Variety of meals', 'Easy preparation', 'Compact storage'],
    cons: ['Higher price point', 'Some flavors bland'],
    features: ['25-year shelf life', '2,000+ calories per day', 'Just add water', 'Gluten-free options'],
    pricing: '$99 - $2,999',
    verdict: 'My Patriot Supply offers reliable emergency food storage with impressive shelf life, though flavors could be improved.',
    content: 'Full review content would go here...',
    author: 'Sarah Johnson',
    publishedAt: '2024-01-10'
  },
  {
    id: '3',
    title: 'Saatva Mattress Complete Review',
    category: 'Mattresses',
    categorySlug: 'mattresses',
    brand: 'Saatva',
    rating: 4.7,
    image: 'https://ext.same-assets.com/2656189839/748255133.png',
    excerpt: 'Luxury innerspring mattress offering hotel-quality comfort and support.',
    href: '/saatva-review',
    pros: ['Excellent support', 'Luxury feel', 'Durable construction', 'Free white glove delivery'],
    cons: ['Higher price', 'Heavy weight', 'May be too firm for some'],
    features: ['Innerspring coils', 'Organic cotton cover', 'Edge support', '180-night trial'],
    pricing: '$1,395 - $2,995',
    verdict: 'Saatva delivers on its promise of luxury comfort with excellent support, justifying its premium price point.',
    content: 'Full review content would go here...',
    author: 'Mike Wilson',
    publishedAt: '2024-01-08'
  }
]

// Articles Data
export const articles: Article[] = [
  {
    id: '1',
    title: 'What are the Top Project Management Tools?',
    excerpt: 'Project management tools offer one of the most effective avenues for tackling everything from organization to communication. Packed full of useful ...',
    content: 'Full article content would go here...',
    image: 'https://ext.same-assets.com/2656189839/3938403337.jpeg',
    href: '/articles/what-are-the-top-project-management-tools',
    author: 'David Chen',
    publishedAt: '2024-01-20',
    category: 'Business Tools'
  },
  {
    id: '2',
    title: 'How to Manage Remote Teams Using Project Management Software',
    excerpt: 'In today\'s modern world the existence of remote teams and workers is becoming more common, and as a manager this can be a challenging change from h...',
    content: 'Full article content would go here...',
    image: 'https://ext.same-assets.com/2656189839/4019245528.jpeg',
    href: '/articles/how-to-manage-remote-teams-using-project-management-software',
    author: 'Lisa Park',
    publishedAt: '2024-01-18',
    category: 'Remote Work'
  }
]

// Coupons Data
export const coupons: Coupon[] = [
  {
    id: '1',
    name: 'Bright Cellars coupons',
    brand: 'Bright Cellars',
    logo: 'https://ext.same-assets.com/2656189839/2419869815.png',
    discount: '25% off first order',
    code: 'WINE25',
    href: '/bright-cellars-coupons',
    expiresAt: '2024-02-29'
  },
  {
    id: '2',
    name: 'Byte coupons',
    brand: 'Byte',
    logo: 'https://ext.same-assets.com/2656189839/2710791357.png',
    discount: '$100 off aligners',
    code: 'SMILE100',
    href: '/byte-coupons',
    expiresAt: '2024-03-15'
  },
  {
    id: '3',
    name: 'DreamCloud Sleep coupons',
    brand: 'DreamCloud',
    logo: 'https://ext.same-assets.com/2656189839/3847251069.png',
    discount: '$200 off mattress',
    code: 'DREAM200',
    href: '/dreamcloud-sleep-coupons',
    expiresAt: '2024-03-30'
  },
  {
    id: '4',
    name: 'Ghostbed coupons',
    brand: 'Ghostbed',
    logo: 'https://ext.same-assets.com/2656189839/1726385497.png',
    discount: '30% off + free pillows',
    code: 'GHOST30',
    href: '/ghostbed-coupons',
    expiresAt: '2024-04-15'
  },
  {
    id: '5',
    name: 'Identity Guard coupons',
    brand: 'Identity Guard',
    logo: 'https://ext.same-assets.com/2656189839/1615848933.png',
    discount: '25% off first year',
    code: 'GUARD25',
    href: '/identity-guard-coupons',
    expiresAt: '2024-04-30'
  },
  {
    id: '6',
    name: 'Leesa coupons',
    brand: 'Leesa',
    logo: 'https://ext.same-assets.com/2656189839/3024651748.png',
    discount: '$150 off + free pillows',
    code: 'LEESA150',
    href: '/leesa-coupons',
    expiresAt: '2024-05-15'
  },
  {
    id: '7',
    name: 'Nectar coupons',
    brand: 'Nectar',
    logo: 'https://ext.same-assets.com/2656189839/2196397333.png',
    discount: '$100 off + accessories',
    code: 'NECTAR100',
    href: '/nectar-coupons',
    expiresAt: '2024-05-31'
  }
]
