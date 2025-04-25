import os
from celery import Celery
from datetime import datetime
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.data_fetching.cache import Cache
from backend.data_fetching.youtube_fetcher import fetch_recent_videos, fetch_channel_details
from backend.risk_analysis.analyzer import Analyzer
from backend.models.base import RiskCategory, AlertType, AuditActionType, PlatformType
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.repositories.analyzed_video import AnalyzedVideoRepository
from backend.repositories.analysis_result import AnalysisResultRepository
from backend.repositories.alert import AlertRepository
from backend.repositories.audit_log import AuditLogRepository


# Initialize Celery app
celery_app = Celery(
    "worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_ignore_result=False,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Initialize repositories
linked_account_repo = LinkedAccountRepository()
child_profile_repo = ChildProfileRepository()
subscribed_channel_repo = SubscribedChannelRepository()
analyzed_video_repo = AnalyzedVideoRepository()
analysis_result_repo = AnalysisResultRepository()
alert_repo = AlertRepository()
audit_log_repo = AuditLogRepository()


@celery_app.task(bind=True, name="perform_account_scan")
def perform_account_scan(self, linked_account_id: int) -> Dict[str, Any]:
    """
    Celery task to perform data fetching and analysis for a linked account.
    Fetches subscribed channels and their recent videos, analyzes content,
    and stores results in the database.
    
    Args:
        linked_account_id: ID of the linked account to scan
        
    Returns:
        Dictionary with scan results summary
    """
    task_id = self.request.id
    self.update_state(state="STARTED", meta={"message": f"Starting scan for linked account ID: {linked_account_id}"})
    print(f"Starting scan for linked account ID: {linked_account_id}, task ID: {task_id}")
    
    db = None
    try:
        # Initialize DB session and Cache client within the task
        db = SessionLocal()
        cache = Cache(settings.redis_url)
        
        # Get the linked account with its OAuth tokens
        linked_account = linked_account_repo.get(db, linked_account_id)
        if not linked_account:
            print(f"Linked account with ID {linked_account_id} not found.")
            return {
                "linked_account_id": linked_account_id,
                "status": "failed",
                "message": "Linked account not found"
            }
        
        # Get the child profile for this linked account
        child_profile = child_profile_repo.get(db, linked_account.child_profile_id)
        if not child_profile:
            print(f"Child profile with ID {linked_account.child_profile_id} not found.")
            return {
                "linked_account_id": linked_account_id,
                "status": "failed",
                "message": "Child profile not found"
            }
        
        # In a production environment, we would fetch the user's subscribed channels
        # using the OAuth access token
        access_token = linked_account.access_token
        
        # For demonstration purposes, we'll use a placeholder channel ID
        # In production, this would be replaced with:
        # subscribed_channels = fetch_subscribed_channels(access_token)
        channel_ids = ["UCBR8-60-B28hp2BmDPdntcQ"]  # Example YouTube channel ID (GoogleDevelopers)
        
        # Log the scan initiation in audit log
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SCAN_TRIGGERED,
            parent_id=child_profile.parent_id,
            resource_type="linked_account",
            resource_id=linked_account.id,
            details={
                "platform": linked_account.platform,
                "task_id": task_id
            }
        )
        
        # Process each channel
        all_videos_processed = 0
        all_flags_found = 0
        
        for channel_id in channel_ids:
            # Update task state
            self.update_state(
                state="PROCESSING",
                meta={
                    "message": f"Fetching channel details for channel ID: {channel_id}",
                    "progress": 10
                }
            )
        
            # Fetch channel details (or use cache if available)
            cached_channel = cache.get(f"channel_details:{channel_id}")
            if cached_channel:
                print(f"Using cached details for channel ID: {channel_id}")
                channel_details = cached_channel
            else:
                print(f"Fetching details for channel ID: {channel_id}")
                channel_details = fetch_channel_details(channel_id)
                if channel_details:
                    cache.set(f"channel_details:{channel_id}", channel_details, ttl=86400)  # Cache for 24 hours
            
            if not channel_details:
                print(f"Could not fetch details for channel ID: {channel_id}")
                
                # Log error in audit log
                audit_log_repo.log_action(
                    db,
                    action=AuditActionType.SYSTEM_ERROR,
                    parent_id=child_profile.parent_id,
                    resource_type="linked_account",
                    resource_id=linked_account.id,
                    details={
                        "error": "Failed to fetch channel details",
                        "channel_id": channel_id,
                        "task_id": task_id
                    }
                )
                
                # Skip this channel and continue with others
                continue
        
            # Update task state
            self.update_state(
                state="PROCESSING",
                meta={
                    "message": f"Storing channel details for channel ID: {channel_id}",
                    "progress": 20
                }
            )
            
            # Store or update the channel in the database
            existing_channel = subscribed_channel_repo.get_by_channel_id(db, linked_account.id, channel_id)
            
            if existing_channel:
                # Update existing channel
                channel_data = {
                    "title": channel_details.get("snippet", {}).get("title", ""),
                    "description": channel_details.get("snippet", {}).get("description", ""),
                    "thumbnail_url": channel_details.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url", ""),
                    "subscriber_count": channel_details.get("statistics", {}).get("subscriberCount"),
                    "video_count": channel_details.get("statistics", {}).get("videoCount"),
                    "topic_details": channel_details.get("topicDetails", {}),
                    "last_fetched_at": datetime.now()
                }
                
                db_channel = subscribed_channel_repo.update(db, db_obj=existing_channel, obj_in=channel_data)
                print(f"Updated channel: {db_channel.title}")
            else:
                # Create new channel
                channel_data = {
                    "linked_account_id": linked_account.id,
                    "channel_id": channel_id,
                    "title": channel_details.get("snippet", {}).get("title", ""),
                    "description": channel_details.get("snippet", {}).get("description", ""),
                    "thumbnail_url": channel_details.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url", ""),
                    "subscriber_count": channel_details.get("statistics", {}).get("subscriberCount"),
                    "video_count": channel_details.get("statistics", {}).get("videoCount"),
                    "topic_details": channel_details.get("topicDetails", {}),
                    "last_fetched_at": datetime.now()
                }
                
                db_channel = subscribed_channel_repo.create(db, obj_in=channel_data)
                print(f"Created new channel: {db_channel.title}")
            
            # Update task state
            self.update_state(
                state="PROCESSING",
                meta={
                    "message": f"Fetching recent videos for channel ID: {channel_id}",
                    "progress": 30
                }
            )
            
            # Fetch recent videos
            print(f"Fetching recent videos for channel ID: {channel_id}")
            cached_videos = cache.get(f"recent_videos:{channel_id}")
            if cached_videos:
                print(f"Using cached videos for channel ID: {channel_id}")
                recent_videos = cached_videos
            else:
                recent_videos = fetch_recent_videos(channel_id, max_results=10)  # Fetching 10 recent videos
                if recent_videos:
                    cache.set(f"recent_videos:{channel_id}", recent_videos, ttl=86400)  # Cache for 24 hours
            
            if not recent_videos:
                print(f"No recent videos found for channel ID: {channel_id}")
                
                # Skip this channel and continue with others
                continue
        
            # Update task state
            self.update_state(
                state="PROCESSING",
                meta={
                    "message": f"Analyzing {len(recent_videos)} videos",
                    "progress": 40
                }
            )
            
            # Initialize analyzer
            analyzer = Analyzer()
            channel_analysis_results = []
            
            # Process each video
            for i, video in enumerate(recent_videos):
                # Update task state with progress
                progress = 40 + (i / len(recent_videos) * 50)  # Progress from 40% to 90%
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "message": f"Analyzing video {i+1} of {len(recent_videos)}",
                        "progress": progress
                    }
                )
                
                video_id = video.get("id", {}).get("videoId") if "id" in video and isinstance(video["id"], dict) else video.get("id")
                video_title = video.get("snippet", {}).get("title", "")
                video_description = video.get("snippet", {}).get("description", "")
                thumbnail_url = video.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url", "")
                published_at_str = video.get("snippet", {}).get("publishedAt")
                
                # Convert published_at to datetime if present
                published_at = None
                if published_at_str:
                    try:
                        from dateutil import parser
                        published_at = parser.parse(published_at_str)
                    except Exception as e:
                        print(f"Error parsing date: {e}")
                
                # Check if video already exists in database
                existing_video = analyzed_video_repo.get_by_platform_id(db, video_id)
                
                if not existing_video:
                    # Create new video entry
                    video_data = {
                        "channel_id": db_channel.id,
                        "video_platform_id": video_id,
                        "title": video_title,
                        "description": video_description,
                        "thumbnail_url": thumbnail_url,
                        "published_at": published_at,
                        "duration": video.get("contentDetails", {}).get("duration"),
                        "view_count": video.get("statistics", {}).get("viewCount"),
                        "like_count": video.get("statistics", {}).get("likeCount"),
                    }
                    
                    db_video = analyzed_video_repo.create(db, obj_in=video_data)
                    print(f"Created new video: {db_video.title}")
                else:
                    # Update existing video
                    video_data = {
                        "title": video_title,
                        "description": video_description,
                        "thumbnail_url": thumbnail_url,
                        "view_count": video.get("statistics", {}).get("viewCount"),
                        "like_count": video.get("statistics", {}).get("likeCount"),
                    }
                    
                    db_video = analyzed_video_repo.update(db, db_obj=existing_video, obj_in=video_data)
                    print(f"Updated video: {db_video.title}")
                
                # Analyze video content using the enhanced analyzer
                analysis_results = analyzer.analyze_content(video_title, video_description)
                
                # Store analysis results if risks were found
                if analysis_results["has_risk"]:
                    for risk_category in analysis_results["risk_categories"]:
                        keywords = analysis_results["categorized_keywords"].get(risk_category, [])
                        
                        # Convert risk category string to enum
                        try:
                            # Handle both enum name format (HATE_SPEECH) and value format (hate_speech)
                            if risk_category.upper() in [e.name for e in RiskCategory]:
                                risk_cat_enum = RiskCategory[risk_category.upper()]
                            else:
                                # Find the enum by value
                                risk_cat_enum = next((e for e in RiskCategory if e.value == risk_category), None)
                                if not risk_cat_enum:
                                    print(f"Warning: Risk category {risk_category} not found in enum")
                                    continue
                        except (KeyError, AttributeError) as e:
                            print(f"Warning: Error processing risk category {risk_category}: {e}")
                            continue
                        
                        # Create analysis result
                        result_data = {
                            "video_id": db_video.id,
                            "channel_id": db_channel.id,
                            "risk_category": risk_cat_enum,
                            "severity": analysis_results["overall_severity"],
                            "flagged_text": f"{video_title} {video_description}"[:200],  # Truncate to avoid very long text
                            "keywords_matched": keywords,
                            "confidence_score": analysis_results["confidence_score"]
                        }
                        
                        db_result = analysis_result_repo.create(db, obj_in=result_data)
                        channel_analysis_results.append(db_result)
                        all_flags_found += len(keywords)
                        
                        print(f"Created analysis result for {db_video.title}: {risk_category} ({analysis_results['overall_severity']})")
                
                # Count this video as processed regardless of whether risks were found
                all_videos_processed += 1
        
        # After processing all channels, create alerts and update scan status
        # Update task state
        self.update_state(
            state="PROCESSING",
            meta={
                "message": "Creating alerts",
                "progress": 90
            }
        )
        
        # Create alert for the scan
        alert_repo.create_scan_complete_alert(
            db,
            child_profile_id=child_profile.id,
            channels_count=len(channel_ids),
            flagged_count=all_flags_found
        )
        
        # If any flags were found, create a new flags alert
        if all_flags_found > 0:
            # Extract unique categories from the analysis results for this child profile
            all_categories = []
            
            # Get all analysis results for this child profile
            for channel in subscribed_channel_repo.list_by_linked_account(db, linked_account.id):
                results = analysis_result_repo.list(db, channel_id=channel.id)
                for result in results:
                    all_categories.append(str(result.risk_category.value))
            
            unique_categories = list(set(all_categories))
            
            alert_repo.create_new_flags_alert(
                db,
                child_profile_id=child_profile.id,
                new_flags_count=all_flags_found,
                categories=unique_categories
            )
        
        # Log scan completion in audit log
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SCAN_COMPLETED,
            parent_id=child_profile.parent_id,
            resource_type="linked_account",
            resource_id=linked_account.id,
            details={
                "scan_type": "youtube_channel_scan",
                "channels_scanned": len(channel_ids),
                "videos_analyzed": all_videos_processed,
                "flags_found": all_flags_found,
                "task_id": task_id
            }
        )
        
        # Update last scan time for the linked account
        linked_account_repo.update_last_scan(db, linked_account.id)
        
        # Update task state
        self.update_state(
            state="SUCCESS",
            meta={
                "message": f"Scan completed for linked account ID: {linked_account_id}",
                "progress": 100
            }
        )
        
        print(f"Scan completed for linked account ID: {linked_account_id}")
        return {
            "linked_account_id": linked_account_id,
            "status": "completed",
            "channels_scanned": len(channel_ids),
            "videos_analyzed": all_videos_processed,
            "flags_found": all_flags_found
        }

    except Exception as e:
        print(f"Error during scan for linked account ID {linked_account_id}: {e}")
        if db:
            # Log error in audit log
            try:
                audit_log_repo.log_action(
                    db,
                    action=AuditActionType.SYSTEM_ERROR,
                    resource_type="linked_account",
                    resource_id=linked_account_id,
                    details={
                        "error": str(e),
                        "task": "perform_account_scan",
                        "task_id": task_id
                    }
                )
            except Exception as log_error:
                print(f"Error logging audit: {log_error}")
        
        # Update task state
        self.update_state(
            state="FAILURE", 
            meta={
                "message": f"Error during scan: {str(e)}",
                "error": str(e)
            }
        )
        
        return {
            "linked_account_id": linked_account_id, 
            "status": "failed", 
            "error": str(e)
        }
    finally:
        if db:
            db.close()  # Ensure DB session is closed


@celery_app.task(bind=True, name="perform_scheduled_scans")
def perform_scheduled_scans(self) -> Dict[str, Any]:
    """
    Celery task to perform scheduled scans for all active linked accounts.
    This task can be scheduled to run periodically (e.g., daily).
    
    Returns:
        Dictionary with scan results summary
    """
    task_id = self.request.id
    self.update_state(state="STARTED", meta={"message": "Starting scheduled scans for all linked accounts"})
    print(f"Starting scheduled scans, task ID: {task_id}")
    
    db = None
    try:
        # Initialize DB session
        db = SessionLocal()
        
        # Get all active linked accounts
        active_accounts = linked_account_repo.list(db, is_active=True)
        
        if not active_accounts:
            print("No active linked accounts found.")
            return {
                "status": "completed",
                "message": "No active linked accounts found",
                "accounts_scanned": 0
            }
        
        # Log the scheduled scan initiation
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SCAN_TRIGGERED,
            resource_type="system",
            details={
                "scan_type": "scheduled_scan",
                "accounts_count": len(active_accounts),
                "task_id": task_id
            }
        )
        
        # Queue individual scan tasks for each linked account
        for i, account in enumerate(active_accounts):
            progress = (i / len(active_accounts) * 100)
            self.update_state(
                state="PROCESSING",
                meta={
                    "message": f"Queuing scan for linked account {i+1} of {len(active_accounts)}",
                    "progress": progress
                }
            )
            
            # Queue the scan task
            perform_account_scan.delay(account.id)
            print(f"Queued scan for linked account ID: {account.id}")
        
        # Update task state
        self.update_state(
            state="SUCCESS",
            meta={
                "message": f"Scheduled scans queued for {len(active_accounts)} linked accounts",
                "progress": 100
            }
        )
        
        print(f"Scheduled scans completed, queued {len(active_accounts)} account scans")
        return {
            "status": "completed",
            "accounts_scanned": len(active_accounts)
        }
    
    except Exception as e:
        print(f"Error during scheduled scans: {e}")
        if db:
            # Log error in audit log
            try:
                audit_log_repo.log_action(
                    db,
                    action=AuditActionType.SYSTEM_ERROR,
                    resource_type="system",
                    details={
                        "error": str(e),
                        "task": "perform_scheduled_scans",
                        "task_id": task_id
                    }
                )
            except Exception as log_error:
                print(f"Error logging audit: {log_error}")
        
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={
                "message": f"Error during scheduled scans: {str(e)}",
                "error": str(e)
            }
        )
        
        return {
            "status": "failed",
            "error": str(e)
        }
    finally:
        if db:
            db.close()  # Ensure DB session is closed


if __name__ == "__main__":
    celery_app.start()