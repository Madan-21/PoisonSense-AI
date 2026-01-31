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

  return (
    <>
      <Navbar />

      <div className="blog-container">
        {/* Header */}
        <div className="blog-header">
          <h1>PoisonAI Blog</h1>
          <p>
            Expert insights, safety tips, and the latest research in poison
            prevention and emergency care
          </p>
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
          <h2>Share Your Experience</h2>
          <p>
            Have a poison safety story or prevention tip? Help others by sharing
            your knowledge.
          </p>
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
