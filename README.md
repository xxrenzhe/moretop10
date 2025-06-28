# moretop10

A complete 1:1 clone of the [ConsumerVoice.org](https://consumervoice.org/) website, built with modern web technologies to replicate the original site's functionality and design.

## 🌟 Project Overview

This project is a comprehensive recreation of ConsumerVoice.org, featuring all major pages and functionality including:

- **Homepage** - Complete with hero section, featured topics, top reviews, and all products showcase
- **How We Rank** - Detailed explanation of ranking methodology
- **Contact** - Contact form and information
- **Articles** - News and review articles
- **Coupons** - Deals and promotional offers
- **Category Pages** - Product category browsing
- **Review Details** - Individual product review pages
- **Search Functionality** - Site-wide search capabilities
- **Legal Pages** - Privacy Policy, Terms of Service, Opt-out

## 🚀 Tech Stack

- **Framework**: [Next.js 15](https://nextjs.org/) with App Router
- **Language**: TypeScript
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/) with Radix UI primitives
- **Icons**: [Lucide React](https://lucide.dev/)
- **Package Manager**: [Bun](https://bun.sh/)
- **Code Quality**: Biome for linting and formatting
- **Deployment**: Netlify-ready with configuration

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── api/               # API routes
│   ├── articles/          # Articles page
│   ├── categories/        # Category pages
│   ├── contact/           # Contact page
│   ├── coupons/           # Coupons page
│   ├── how-we-rank/       # Ranking methodology page
│   ├── opt-out/           # Opt-out page
│   ├── privacy/           # Privacy policy page
│   ├── reviews/           # Review detail pages
│   ├── search/            # Search results page
│   ├── terms/             # Terms of service page
│   ├── topics/            # Topic pages
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── Header.tsx        # Site header
│   ├── Footer.tsx        # Site footer
│   ├── HeroSection.tsx   # Homepage hero
│   └── ...               # Other components
├── contexts/             # React contexts
├── lib/                  # Utility functions and data
└── globals.css          # Global styles
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xxrenzhe/moretop10.git
   cd moretop10
   ```

2. **Install dependencies**:
   ```bash
   bun install
   ```

3. **Run the development server**:
   ```bash
   bun dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📋 Available Scripts

- `bun dev` - Start development server with Turbopack
- `bun build` - Build for production
- `bun start` - Start production server
- `bun lint` - Run Biome linter and TypeScript checks
- `bun format` - Format code with Biome

## 🎨 Features

### Core Functionality
- ✅ Responsive design matching original site
- ✅ Complete page structure and navigation
- ✅ Search functionality with results
- ✅ Product categories and filtering
- ✅ Review detail pages
- ✅ Article browsing
- ✅ Coupon listings
- ✅ Contact forms
- ✅ Legal pages (Privacy, Terms, Opt-out)

### Technical Features
- ✅ TypeScript for type safety
- ✅ Component-based architecture
- ✅ Responsive design with Tailwind CSS
- ✅ Accessible UI components
- ✅ SEO-optimized with Next.js
- ✅ Modern React patterns (hooks, context)
- ✅ Code quality tools (Biome, ESLint)

## 🌐 Deployment

This project is configured for deployment on Netlify:

1. **Build command**: `bun run build`
2. **Publish directory**: `out`
3. **Node version**: 18+

The project includes a `netlify.toml` configuration file for optimal deployment settings.

## 📝 Notes

- This is a clone project created for educational/demonstration purposes
- All content and design elements are replicated from the original ConsumerVoice.org website
- The project demonstrates modern web development practices and technologies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes. All content and design rights belong to their respective owners.

---

**Original Website**: [https://consumervoice.org/](https://consumervoice.org/)

**Project Repository**: [https://github.com/xxrenzhe/moretop10](https://github.com/xxrenzhe/moretop10)
