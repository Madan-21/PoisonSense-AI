<<<<<<< HEAD
import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Blog.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Blog() {
  const navigate = useNavigate();

  // Dummy data (replace with API later)
  const featured = {
    tag: "Prevention",
    badge: "Featured",
    title: "Understanding Common Household Poisons: A Parent's Guide",
    excerpt:
      "Learn about the most common household items that can be dangerous to children and how to prevent accidental poisoning.",
    author: "Dr. Sarah Mitchell",
    date: "March 15, 2024",
    read: "5 min read",
    image:
      "https://images.unsplash.com/photo-1556912167-f556f1f39faa?q=80&w=1400&auto=format&fit=crop",
  };

  const posts = [
    {
      id: 1,
      tag: "Prevention",
      title: "Understanding Common Household Poisons: A Parent's Guide",
      excerpt:
        "Learn about the most common household items that can be dangerous to children and how to prevent accidental poisoning.",
      author: "Dr. Sarah Mitchell",
      read: "5 min read",
      image:
        "https://images.unsplash.com/photo-1556912167-f556f1f39faa?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 2,
      tag: "First Aid",
      title: "First Aid for Chemical Burns: What You Need to Know",
      excerpt:
        "Essential steps to take when someone experiences a chemical burn, including immediate actions and when to seek help.",
      author: "Dr. Michael Chen",
      read: "6 min read",
      image:
        "https://images.unsplash.com/photo-1580281657527-47f249e8f8f9?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 3,
      tag: "Case Studies",
      title: "Case Study: Quick Response Saves Life in Opioid Overdose",
      excerpt:
        "A real-life account of how rapid intervention and naloxone administration prevented a tragic outcome.",
      author: "Dr. Emily Rodriguez",
      read: "7 min read",
      image:
        "https://images.unsplash.com/photo-1603398938378-e54eab446dde?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 4,
      tag: "Research",
      title: "Latest Research: AI in Poison Identification and Treatment",
      excerpt:
        "Exploring how artificial intelligence is revolutionizing poison control centers and improving patient outcomes.",
      author: "Dr. James Patterson",
      read: "8 min read",
      image:
        "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 5,
      tag: "Safety Tips",
      title:
        "Workplace Safety: Preventing Chemical Exposure in Industrial Settings",
      excerpt:
        "Best practices for maintaining a safe work environment and protecting workers from hazardous chemical exposure.",
      author: "Robert Thompson",
      read: "6 min read",
      image:
        "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 6,
      tag: "Antidotes",
      title:
        "Antidote Availability: Ensuring Access in Emergency Situations",
      excerpt:
        "Understanding which antidotes should be readily available and how systems ensure access during emergencies.",
      author: "Dr. Lisa Anderson",
      read: "7 min read",
      image:
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=1400&auto=format&fit=crop",
    },
  ];

=======
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";
import "../styles/Blog.css";

const Blog = () => {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  // Fetch published articles from the API
  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const response = await fetch("/api/v1/blog/articles");
        
        if (response.ok) {
          const data = await response.json();
          // Map API fields to component expected fields
          const mappedArticles = data.map(article => ({
            ...article,
            author: article.author_name,
            date: new Date(article.published_at).toLocaleDateString('en-US', {
              month: 'long',
              year: 'numeric'
            }),
            readTime: article.read_time || '5 min read',
            image: article.featured_image || '/images/default-article.jpg',
            featured: false // Set based on your logic or backend field
          }));
          setArticles(mappedArticles);
        } else {
          console.error("Failed to fetch articles");
          setError("Failed to load articles");
        }
      } catch (err) {
        console.error("Error fetching articles:", err);
        setError("Failed to load articles");
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  const handleSubmitClick = () => {
    if (!user) {
      navigate("/login");
    } else {
      navigate("/submit-article");
    }
  };

  const categories = [
    "All",
    "Prevention",
    "First Aid",
    "Case Studies",
    "Research",
    "Safety Tips",
    "Antidotes",
  ];

  const filteredArticles = articles.filter((article) => {
    const matchesCategory =
      selectedCategory === "All" || article.category === selectedCategory;
    const matchesSearch =
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const featuredArticle = articles.find((article) => article.featured);

>>>>>>> main
  return (
    <>
      <Navbar />

<<<<<<< HEAD
      {/* HERO */}
      <section className="blog-hero">
        <div className="blog-hero-inner">
          <h1>PoisonGuard Blog</h1>
=======
      <div className="blog-container">
        {/* Header */}
        <div className="blog-header">
          <h1>PoisonAI Blog</h1>
>>>>>>> main
          <p>
            Expert insights, safety tips, and the latest research in poison
            prevention and emergency care
          </p>
<<<<<<< HEAD

          <button
            type="button"
            className="btn-ghost"
            onClick={() => navigate("/submit-article")}
          >
            ✍️ Add Your Blog
          </button>
        </div>
      </section>

      <main className="blog-page">
        {/* FEATURED */}
        <section className="blog-section">
          <h2 className="section-title">Featured Article</h2>

          <article className="featured-card">
            <div
              className="featured-image"
              style={{ backgroundImage: `url(${featured.image})` }}
            />
            <div className="featured-content">
              <div className="badge-row">
                <span className="pill pill-green">{featured.tag}</span>
                <span className="pill pill-yellow">⭐ {featured.badge}</span>
              </div>

              <h3 className="featured-title">{featured.title}</h3>
              <p className="featured-excerpt">{featured.excerpt}</p>

              <div className="meta-row">
                <span>👤 {featured.author}</span>
                <span>📅 {featured.date}</span>
                <span>⏱ {featured.read}</span>
              </div>
            </div>
          </article>
        </section>

        {/* LATEST */}
        <section className="blog-section">
          <h2 className="section-title">Latest Articles</h2>

          <div className="blog-grid">
            {posts.map((p) => (
              <article className="post-card" key={p.id}>
                <div
                  className="post-image"
                  style={{ backgroundImage: `url(${p.image})` }}
                />
                <div className="post-body">
                  <div className="badge-row">
                    <span className="pill pill-soft">{p.tag}</span>
                  </div>

                  <h3 className="post-title">{p.title}</h3>
                  <p className="post-excerpt">{p.excerpt}</p>

                  <div className="meta-row">
                    <span>👤 {p.author}</span>
                    <span>⏱ {p.read}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="blog-cta">
=======
          <button className="submit-story-btn" onClick={handleSubmitClick}>
            <span>📝</span> Add your own blog
          </button>
        </div>

        {/* Search and Filter */}
        <div className="blog-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search articles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>

          <div className="category-filters">
            {categories.map((category) => (
              <button
                key={category}
                className={`filter-btn ${selectedCategory === category ? "active" : ""}`}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="loading-state" style={{textAlign: 'center', padding: '40px'}}>
            <p>Loading articles...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-state" style={{textAlign: 'center', padding: '40px', color: 'red'}}>
            <p>{error}</p>
          </div>
        )}

        {/* Featured Article */}
        {!loading && !error && selectedCategory === "All" && !searchTerm && featuredArticle && (
          <div className="featured-section">
            <h2>Featured Article</h2>
            <Link to={`/blog/${featuredArticle.id}`} className="featured-link">
              <div className="featured-article">
                <div className="featured-image">
                  <img
                    src={featuredArticle.image}
                    alt={featuredArticle.title}
                  />
                </div>
                <div className="featured-content">
                  <div className="article-badges">
                    <span className="badge">{featuredArticle.category}</span>
                    <span className="badge featured-badge">⭐ Featured</span>
                  </div>
                  <h3>{featuredArticle.title}</h3>
                  <p>{featuredArticle.description}</p>
                  <div className="article-meta">
                    <div className="author-info">
                      <img
                        src="/images/default-avatar.jpg"
                        alt={featuredArticle.author}
                        className="avatar"
                      />
                      <div>
                        <p className="author-name">{featuredArticle.author}</p>
                        <p className="article-date">
                          {featuredArticle.date} • {featuredArticle.readTime}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        )}

        {/* Articles Grid */}
        {!loading && !error && (
          <div className="articles-section">
          <h2>Latest Articles</h2>
          {filteredArticles.length > 0 ? (
            <div className="articles-grid">
              {filteredArticles.map((article) => (
                <Link
                  key={article.id}
                  to={`/blog/${article.id}`}
                  className="article-link"
                >
                  <div className="article-card">
                    <div className="article-image">
                      <img src={article.image} alt={article.title} />
                    </div>
                    <div className="article-body">
                      <div className="article-badges">
                        <span className="badge">{article.category}</span>
                        {article.featured && (
                          <span className="badge featured-badge">⭐</span>
                        )}
                      </div>
                      <h3>{article.title}</h3>
                      <p>{article.description}</p>
                      <div className="article-footer">
                        <div className="author-info-small">
                          <img
                            src="/images/default-avatar.jpg"
                            alt={article.author}
                            className="avatar-small"
                          />
                          <div>
                            <p className="author-name-small">
                              {article.author}
                            </p>
                            <p className="article-date-small">
                              {article.date} • {article.readTime}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="no-articles">
              <p>No articles found matching your search.</p>
            </div>
          )}
        </div>
        )}

        {/* Share Experience Section */}
        <div className="share-experience">
>>>>>>> main
          <h2>Share Your Experience</h2>
          <p>
            Have a poison safety story or prevention tip? Help others by sharing
            your knowledge.
          </p>
<<<<<<< HEAD

          <button
            type="button"
            className="btn-white"
            onClick={() => navigate("/submit-article")}
          >
            ✍️ Add Your Article
          </button>
        </section>
      </main>

      <Footer />
    </>
  );
}
=======
          <button className="submit-article-btn" onClick={handleSubmitClick}>
            <span>📝</span> Add your own blog
          </button>
        </div>
      </div>
      
      <Footer />
    </>
  );
};

export default Blog;
>>>>>>> main
