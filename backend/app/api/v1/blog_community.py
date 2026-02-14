# Blog Community API Endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.blog_submission import BlogSubmission
from app.models.blog_community import BlogComment, BlogLike, BlogBookmark
from app.schemas.blog_community import (
    BlogCommentCreate,
    BlogCommentResponse,
    BlogLikeResponse,
    BlogBookmarkResponse,
    BlogCommunityStats
)
from app.core.security import get_current_user, get_current_user_required

router = APIRouter(prefix="/blog/community", tags=["Blog Community"])


@router.post("/articles/{article_id}/comments", response_model=BlogCommentResponse)
async def add_comment(
    article_id: int,
    comment: BlogCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Add a comment to a published article"""
    # Check if article exists and is published
    article = db.query(BlogSubmission).filter(
        BlogSubmission.id == article_id,
        BlogSubmission.status == "approved"
    ).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or not published"
        )
    
    # If replying to a comment, verify parent exists
    if comment.parent_id:
        parent = db.query(BlogComment).filter(
            BlogComment.id == comment.parent_id,
            BlogComment.blog_id == article_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
    
    # Create comment
    db_comment = BlogComment(
        blog_id=article_id,
        user_id=current_user.id,
        parent_id=comment.parent_id,
        content=comment.content
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Add author info
    response = BlogCommentResponse(
        id=db_comment.id,
        blog_id=db_comment.blog_id,
        user_id=db_comment.user_id,
        parent_id=db_comment.parent_id,
        content=db_comment.content,
        is_edited=db_comment.is_edited,
        author_name=current_user.full_name or current_user.email,
        author_email=current_user.email,
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        replies_count=0
    )
    
    return response


@router.get("/articles/{article_id}/comments", response_model=List[BlogCommentResponse])
async def get_comments(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for an article"""
    comments = db.query(BlogComment, User).join(
        User, BlogComment.user_id == User.id
    ).filter(
        BlogComment.blog_id == article_id,
        BlogComment.is_deleted == False
    ).order_by(BlogComment.created_at.desc()).all()
    
    results = []
    for comment, user in comments:
        # Count replies
        replies_count = db.query(func.count(BlogComment.id)).filter(
            BlogComment.parent_id == comment.id,
            BlogComment.is_deleted == False
        ).scalar()
        
        results.append(BlogCommentResponse(
            id=comment.id,
            blog_id=comment.blog_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            content=comment.content,
            is_edited=comment.is_edited,
            author_name=user.full_name or user.email,
            author_email=user.email,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies_count=replies_count
        ))
    
    return results


@router.post("/articles/{article_id}/like", response_model=BlogLikeResponse)
async def toggle_like(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Toggle like on an article"""
    # Check if article exists
    article = db.query(BlogSubmission).filter(
        BlogSubmission.id == article_id,
        BlogSubmission.status == "approved"
    ).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if already liked
    existing_like = db.query(BlogLike).filter(
        BlogLike.blog_id == article_id,
        BlogLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        user_liked = False
    else:
        # Like
        new_like = BlogLike(
            blog_id=article_id,
            user_id=current_user.id
        )
        db.add(new_like)
        user_liked = True
    
    db.commit()
    
    # Get total likes
    total_likes = db.query(func.count(BlogLike.id)).filter(
        BlogLike.blog_id == article_id
    ).scalar()
    
    return BlogLikeResponse(
        blog_id=article_id,
        total_likes=total_likes,
        user_liked=user_liked
    )


@router.post("/articles/{article_id}/bookmark", response_model=BlogBookmarkResponse)
async def toggle_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Toggle bookmark on an article"""
    # Check if article exists
    article = db.query(BlogSubmission).filter(
        BlogSubmission.id == article_id,
        BlogSubmission.status == "approved"
    ).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if already bookmarked
    existing_bookmark = db.query(BlogBookmark).filter(
        BlogBookmark.blog_id == article_id,
        BlogBookmark.user_id == current_user.id
    ).first()
    
    if existing_bookmark:
        # Remove bookmark
        db.delete(existing_bookmark)
        is_bookmarked = False
    else:
        # Add bookmark
        new_bookmark = BlogBookmark(
            blog_id=article_id,
            user_id=current_user.id
        )
        db.add(new_bookmark)
        is_bookmarked = True
    
    db.commit()
    
    return BlogBookmarkResponse(
        blog_id=article_id,
        is_bookmarked=is_bookmarked
    )


@router.get("/articles/{article_id}/stats", response_model=BlogCommunityStats)
async def get_article_stats(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get community statistics for an article"""
    article = db.query(BlogSubmission).filter(
        BlogSubmission.id == article_id
    ).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Count likes
    likes_count = db.query(func.count(BlogLike.id)).filter(
        BlogLike.blog_id == article_id
    ).scalar()
    
    # Count comments (excluding deleted)
    comments_count = db.query(func.count(BlogComment.id)).filter(
        BlogComment.blog_id == article_id,
        BlogComment.is_deleted == False
    ).scalar()
    
    # Count bookmarks
    bookmarks_count = db.query(func.count(BlogBookmark.id)).filter(
        BlogBookmark.blog_id == article_id
    ).scalar()
    
    return BlogCommunityStats(
        blog_id=article_id,
        likes_count=likes_count,
        comments_count=comments_count,
        bookmarks_count=bookmarks_count,
        view_count=article.view_count
    )


@router.get("/my-bookmarks", response_model=List[int])
async def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get list of bookmarked article IDs for current user"""
    bookmarks = db.query(BlogBookmark.blog_id).filter(
        BlogBookmark.user_id == current_user.id
    ).all()
    
    return [b[0] for b in bookmarks]


# Reputation System Endpoints
@router.get("/users/{user_id}/reputation")
async def get_user_reputation(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's reputation and community stats"""
    from app.models.blog_community import UserReputation
    import json
    
    reputation = db.query(UserReputation).filter(UserReputation.user_id == user_id).first()
    
    if not reputation:
        # Create default reputation
        from app.models.blog_community import ReputationLevel
        reputation = UserReputation(user_id=user_id, level=ReputationLevel.NEWCOMER)
        db.add(reputation)
        db.commit()
        db.refresh(reputation)
    
    badges = json.loads(reputation.badges) if reputation.badges else []
    
    return {
        "points": reputation.points,
        "level": reputation.level.value,
        "badges": badges,
        "stats": {
            "articles_published": reputation.articles_published,
            "comments_posted": reputation.comments_posted,
            "likes_received": reputation.likes_received,
            "helpful_answers": reputation.helpful_answers
        }
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top contributors leaderboard"""
    from app.models.blog_community import UserReputation
    
    top_users = db.query(UserReputation, User).join(
        User, UserReputation.user_id == User.id
    ).order_by(UserReputation.points.desc()).limit(limit).all()
    
    result = []
    for reputation, user in top_users:
        result.append({
            "user_id": user.id,
            "name": user.full_name,
            "role": user.role.value,
            "points": reputation.points,
            "level": reputation.level.value,
            "articles_published": reputation.articles_published
        })
    
    return result


@router.post("/comments/{comment_id}/like")
async def toggle_comment_like(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Like or unlike a comment"""
    from app.models.blog_community import CommentLike
    
    # Check if comment exists
    comment = db.query(BlogComment).filter(BlogComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user already liked
    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        db.commit()
        return {"message": "Comment unliked", "liked": False}
    else:
        # Like
        like = CommentLike(
            comment_id=comment_id,
            user_id=current_user.id
        )
        db.add(like)
        db.commit()
        return {"message": "Comment liked", "liked": True}
