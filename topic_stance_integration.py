"""
Topic-Based Stance Analysis Integration.

Combines topic modeling results with stance analysis to show:
Topic → Posts → Comments with Stance Analysis
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_topic_stance_data(results_dir: str, timestamp: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load and integrate topic modeling and stance analysis data.

    Args:
        results_dir: Path to results directory
        timestamp: Timestamp string (e.g., '20260505_061312')

    Returns:
        Tuple of (posts_with_topics, comments_with_stance, merged_data)
    """
    results_path = Path(results_dir)

    # Load posts with topics
    posts_file = results_path / f"posts_with_topics_{timestamp}.csv"
    if not posts_file.exists():
        raise FileNotFoundError(f"Posts with topics file not found: {posts_file}")

    posts_df = pd.read_csv(posts_file)
    posts_df['post_id'] = posts_df.index.astype(str)  # Add post_id for joining

    # Load comments with stance
    comments_file = results_path / f"comments_with_stance_{timestamp}.csv"
    if not comments_file.exists():
        raise FileNotFoundError(f"Comments with stance file not found: {comments_file}")

    comments_df = pd.read_csv(comments_file)
    comments_df['comment_id'] = comments_df.index.astype(str)  # Add comment_id for joining

    # Load original data for conversation_id mapping
    original_file = results_path / f"original_data_{timestamp}.csv"
    if not original_file.exists():
        raise FileNotFoundError(f"Original data file not found: {original_file}")

    original_df = pd.read_csv(original_file)

    # Create mapping between posts and comments using conversation_id_str
    # Posts are the root conversations, comments are replies
    merged_data = []

    # Group original data by conversation_id_str
    for conv_id, group in original_df.groupby('conversation_id_str'):
        # The first row is usually the post
        post_row = group.iloc[0]
        post_text = post_row['full_text']

        # Find topic for this post
        topic_match = posts_df[posts_df['full_text'] == post_text]
        if len(topic_match) > 0:
            topic_id = topic_match.iloc[0]['Topik']
        else:
            topic_id = -1  # Unknown topic

        # Add post data
        merged_data.append({
            'conversation_id': str(conv_id),
            'post_id': f"post_{len(merged_data)}",
            'post_text': post_text,
            'topic_id': topic_id,
            'created_at': post_row['created_at'],
            'type': 'post'
        })

        # Add comment data (all rows except the first)
        for idx, comment_row in group.iloc[1:].iterrows():
            comment_text = comment_row['full_text_comments']

            # Find stance analysis for this comment
            stance_match = comments_df[comments_df['full_text_comments'] == comment_text]
            if len(stance_match) > 0:
                stance_label = stance_match.iloc[0].get('stance_label', 'Netral')
                stance_weight = stance_match.iloc[0].get('stance_weight', 0.5)
                stance_reasoning = stance_match.iloc[0].get('stance_reasoning', '')
            else:
                stance_label = 'Netral'
                stance_weight = 0.5
                stance_reasoning = 'Stance analysis not available'

            merged_data.append({
                'conversation_id': str(conv_id),
                'post_id': f"post_{len(merged_data) - 1}",  # Reference to post
                'comment_id': f"comment_{idx}",
                'post_text': post_text,
                'comment_text': comment_text,
                'topic_id': topic_id,
                'stance_label': stance_label,
                'stance_weight': stance_weight,
                'stance_reasoning': stance_reasoning,
                'created_at': comment_row['created_at'],
                'type': 'comment'
            })

    merged_df = pd.DataFrame(merged_data)

    # Separate posts and comments
    posts_only = merged_df[merged_df['type'] == 'post'].copy()
    comments_only = merged_df[merged_df['type'] == 'comment'].copy()

    return posts_only, comments_only, merged_df


def get_topic_summary(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for each topic.

    Returns DataFrame with columns:
    - topic_id
    - post_count
    - comment_count
    - mendukung_count, menolak_count, netral_count
    - avg_stance_weight
    """
    topic_stats = []

    for topic_id in sorted(merged_df['topic_id'].unique()):
        if topic_id == -1:  # Skip unknown topics
            continue

        topic_data = merged_df[merged_df['topic_id'] == topic_id]
        posts_in_topic = topic_data[topic_data['type'] == 'post']
        comments_in_topic = topic_data[topic_data['type'] == 'comment']

        # Count stances
        stance_counts = comments_in_topic['stance_label'].value_counts()

        topic_stats.append({
            'topic_id': topic_id,
            'post_count': len(posts_in_topic),
            'comment_count': len(comments_in_topic),
            'mendukung_count': stance_counts.get('Mendukung', 0),
            'menolak_count': stance_counts.get('Menolak', 0),
            'netral_count': stance_counts.get('Netral', 0),
            'avg_stance_weight': comments_in_topic['stance_weight'].mean() if len(comments_in_topic) > 0 else 0,
            'mendukung_pct': stance_counts.get('Mendukung', 0) / len(comments_in_topic) * 100 if len(comments_in_topic) > 0 else 0,
            'menolak_pct': stance_counts.get('Menolak', 0) / len(comments_in_topic) * 100 if len(comments_in_topic) > 0 else 0,
            'netral_pct': stance_counts.get('Netral', 0) / len(comments_in_topic) * 100 if len(comments_in_topic) > 0 else 0
        })

    return pd.DataFrame(topic_stats)


def get_available_timestamps(results_dir: str) -> List[str]:
    """
    Get list of available timestamps from results directory.
    """
    results_path = Path(results_dir)
    timestamps = []

    for file in results_path.glob("posts_with_topics_*.csv"):
        timestamp = file.stem.replace("posts_with_topics_", "")
        timestamps.append(timestamp)

    return sorted(timestamps, reverse=True)  # Most recent first


def load_topic_modeling_results(results_dir: str, timestamp: str) -> Optional[Dict]:
    """
    Load topic modeling results (top_topics, topic_metrics) for additional context.
    """
    results_path = Path(results_dir)

    # Load top topics
    top_topics_file = results_path / f"top_topics_{timestamp}.csv"
    if top_topics_file.exists():
        top_topics_df = pd.read_csv(top_topics_file)
        top_topics = {}
        for _, row in top_topics_df.iterrows():
            top_topics[row['Topic']] = {
                'name': row.get('Name', f'Topic {row["Topic"]}'),
                'words': row.get('Top_Words', ''),
                'count': row.get('Count', 0)
            }
        return top_topics

    return None


if __name__ == "__main__":
    # Example usage
    results_dir = "results"
    timestamp = "20260505_061312"  # Use latest available

    try:
        posts_df, comments_df, merged_df = load_topic_stance_data(results_dir, timestamp)
        topic_summary = get_topic_summary(merged_df)

        print("✅ Data loaded successfully!")
        print(f"Posts: {len(posts_df)}, Comments: {len(comments_df)}")
        print(f"Topics found: {len(topic_summary)}")
        print("\nTopic Summary:")
        print(topic_summary.head())

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
