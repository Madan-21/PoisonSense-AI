import React, { useState, useEffect } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";
import "../styles/BlogCommunity.css";

export default function BlogCommunity({ articleId }) {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [replyTo, setReplyTo] = useState(null);
  const [likes, setLikes] = useState(0);
  const [userLiked, setUserLiked] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComments();
    fetchLikes();
  }, [articleId]);

  const fetchComments = async () => {
    try {
      const response = await api.get(`/blog/community/articles/${articleId}/comments`);
      setComments(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching comments:", error);
      setLoading(false);
    }
  };

  const fetchLikes = async () => {
    try {
      const response = await api.get(`/blog/community/articles/${articleId}/likes`);
      setLikes(response.data.likes_count || 0);
      setUserLiked(response.data.user_liked || false);
    } catch (error) {
      console.error("Error fetching likes:", error);
    }
  };

  const handleComment = async () => {
    if (!newComment.trim()) return;
    
    if (!user) {
      alert("Please login to comment");
      return;
    }

    try {
      await api.post(`/blog/community/articles/${articleId}/comments`, {
        content: newComment,
        parent_id: replyTo
      });
      setNewComment("");
      setReplyTo(null);
      fetchComments();
    } catch (error) {
      console.error("Error posting comment:", error);
      alert("Failed to post comment. Please try again.");
    }
  };

  const handleLike = async () => {
    if (!user) {
      alert("Please login to like this article");
      return;
    }

    try {
      await api.post(`/blog/community/articles/${articleId}/like`);
      fetchLikes();
    } catch (error) {
      console.error("Error liking article:", error);
    }
  };

  const handleCommentLike = async (commentId) => {
    if (!user) {
      alert("Please login to like comments");
      return;
    }

    try {
      await api.post(`/blog/community/comments/${commentId}/like`);
      fetchComments(); // Refresh to show updated like count
    } catch (error) {
      console.error("Error liking comment:", error);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case "doctor":
        return <span className="badge doctor">🩺 Verified Doctor</span>;
      case "hospital_admin":
        return <span className="badge hospital">🏥 Hospital Staff</span>;
      case "admin":
        return <span className="badge admin">🛡️ Admin</span>;
      case "blog_reviewer":
        return <span className="badge moderator">⭐ Moderator</span>;
      default:
        return null;
    }
  };

  const renderComment = (comment, isReply = false) => (
    <div key={comment.id} className={`comment ${isReply ? 'reply' : ''}`}>
      <div className="comment-header">
        <div className="comment-author">
          <div className="avatar">
            {comment.author_name?.charAt(0) || "U"}
          </div>
          <div className="author-info">
            <span className="name">{comment.author_name}</span>
            {getRoleBadge(comment.author_role)}
            <span className="date">
              {new Date(comment.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
      <div className="comment-content">
        {comment.content}
      </div>
      <div className="comment-actions">
        <button className="action-btn" onClick={() => handleCommentLike(comment.id)}>
          <span className="icon">👍</span>
          <span>{comment.likes || 0}</span>
        </button>
        {!isReply && user && (
          <button 
            className="action-btn reply-btn" 
            onClick={() => {
              setReplyTo(comment.id);
              document.getElementById('comment-input').focus();
            }}
          >
            <span className="icon">💬</span>
            <span>Reply</span>
          </button>
        )}
      </div>
      {/* Render replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="replies-container">
          {comment.replies.map(reply => renderComment(reply, true))}
        </div>
      )}
    </div>
  );

  return (
    <div className="blog-community">
      {/* Likes Section */}
      <div className="likes-section">
        <button
          className={`like-btn ${userLiked ? "liked" : ""}`}
          onClick={handleLike}
          disabled={!user}
        >
          <span className="heart-icon">{userLiked ? "❤️" : "🤍"}</span>
          <span className="like-count">{likes}</span>
        </button>
        <span className="like-text">
          {likes === 1 ? "1 person likes" : `${likes} people like`} this article
        </span>
      </div>

      {/* Comments Section */}
      <div className="comments-section">
        <h3 className="comments-title">
          💬 Comments ({comments.length})
        </h3>

        {/* New Comment Form */}
        {user ? (
          <div className="new-comment">
            <div className="user-avatar">
              {user.full_name?.charAt(0) || "U"}
            </div>
            <div className="comment-input-container">
              {replyTo && (
                <div className="reply-indicator">
                  <span>Replying to comment...</span>
                  <button onClick={() => setReplyTo(null)}>✕</button>
                </div>
              )}
              <textarea
                id="comment-input"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder={replyTo ? "Write your reply..." : "Share your thoughts..."}
                rows="3"
              />
              <div className="comment-actions">
                <button className="post-btn" onClick={handleComment}>
                  {replyTo ? "Post Reply" : "Post Comment"}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="login-prompt">
            <p>Please <a href="/login">login</a> to comment on this article</p>
          </div>
        )}

        {/* Comments List */}
        {loading ? (
          <div className="loading">Loading comments...</div>
        ) : comments.length > 0 ? (
          <div className="comments-list">
            {comments.map(comment => renderComment(comment))}
          </div>
        ) : (
          <div className="no-comments">
            <p>No comments yet. Be the first to share your thoughts!</p>
          </div>
        )}
      </div>
    </div>
  );
}
