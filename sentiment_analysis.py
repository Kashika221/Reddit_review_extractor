import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
import re
import torch

from transformers import pipeline
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

from compile_data import BrandDataCompiler

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SentimentAnalyzer:
    def __init__(self, model_name : str = "distilbert-base-uncased-finetuned-sst-2-english"):
        print(f"Loading sentiment model: {model_name}")
        self.sentiment_pipeline = pipeline("sentiment-analysis", model = model_name)
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text : str) -> str:
        if not text or not isinstance(text, str):
            return ""
        
        text = re.sub(r'http\S+|www.\S+', '', text)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_sentiment_transformer(self, text : str) -> Dict:
        if not text:
            return {"label" : "NEUTRAL", "score" : 0.5}
        try:
            text = text[:512]
            result = self.sentiment_pipeline(text)[0]
            return result
        except Exception as e:
            print(f"Error in transformer analysis: {e}")
            return {"label" : "NEUTRAL", "score" : 0.5}
    
    def analyze_sentiment_textblob(self, text : str) -> Dict:
        if not text:
            return {"polarity" : 0.0, "subjectivity" : 0.5}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                label = "POSITIVE"
            elif polarity < -0.1:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
            
            return {
                "label" : label,
                "polarity" : polarity,
                "subjectivity" : subjectivity
            }
        except Exception as e:
            print(f"Error in TextBlob analysis: {e}")
            return {"label": "NEUTRAL", "polarity": 0.0, "subjectivity": 0.5}
    
    def extract_keywords(self, text : str, top_n : int = 10) -> List[str]:
        if not text:
            return []
        
        tokens = word_tokenize(text.lower())
        keywords = [word for word in tokens 
                   if word.isalnum() and word not in self.stop_words and len(word) > 3]
        
        freq_dist = nltk.FreqDist(keywords)
        return [word for word, _ in freq_dist.most_common(top_n)]
    
    def analyze_dataset(self, data : List[Dict]) -> pd.DataFrame:
        results = []
        
        for idx, item in enumerate(data):
            if idx % 10 == 0:
                print(f"Analyzing item {idx + 1}/{len(data)}")
            
            text = item.get('text', '')
            cleaned_text = self.preprocess_text(text)
            transformer_result = self.analyze_sentiment_transformer(cleaned_text)
            textblob_result = self.analyze_sentiment_textblob(cleaned_text)
            keywords = self.extract_keywords(cleaned_text)
            
            result = {
                'source' : item.get('source', ''),
                'author' : item.get('author', ''),
                'text' : text,
                'cleaned_text' : cleaned_text,
                'created_at' : item.get('created_at', ''),
                'url' : item.get('url', ''),
                
                'sentiment_label' : transformer_result['label'],
                'sentiment_score' : transformer_result['score'],
                
                'polarity' : textblob_result.get('polarity', 0.0),
                'subjectivity' : textblob_result.get('subjectivity', 0.5),
                'textblob_label' : textblob_result.get('label', 'NEUTRAL'),
                
                'text_length' : len(text),
                'keywords' : ', '.join(keywords[:5]),
                
                'engagement' : item.get('engagement', 0),
                'likes' : item.get('likes', 0),
                'score' : item.get('score', 0),
                'subreddit' : item.get('subreddit', ''),
            }
            
            results.append(result)
        
        df = pd.DataFrame(results)
        df['sentiment_numeric'] = df['sentiment_label'].map({
            'POSITIVE' : 1,
            'NEGATIVE' : -1,
            'NEUTRAL' : 0
        })
        
        return df
    
    def generate_insights(self, df: pd.DataFrame) -> Dict:
        insights = {
            'total_items' : len(df),
            'sentiment_distribution' : df['sentiment_label'].value_counts().to_dict(),
            'average_polarity' : df['polarity'].mean(),
            'average_subjectivity' : df['subjectivity'].mean(),
            'source_breakdown' : df['source'].value_counts().to_dict(),
        }
        ##error hai iss line main don't uncomment
        #insights['sentiment_by_source'] = df.groupby('source')['sentiment_label'].value_counts().to_dict() 
        insights['top_positive'] = df.nlargest(5, 'polarity')[['text', 'polarity', 'source']].to_dict('records')
        insights['top_negative'] = df.nsmallest(5, 'polarity')[['text', 'polarity', 'source']].to_dict('records')
        insights['avg_sentiment_by_source'] = df.groupby('source')['sentiment_numeric'].mean().to_dict()
        
        return insights
    
    def visualize_results(self, df : pd.DataFrame, brand_name : str, output_dir : str):
        os.makedirs(output_dir, exist_ok = True)
        
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        
        fig, axes = plt.subplots(2, 2, figsize = (15, 12))
        
        sentiment_counts = df['sentiment_label'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        axes[0, 0].pie(sentiment_counts.values, labels = sentiment_counts.index, 
                       autopct = '%1.1f%%', colors = colors, startangle = 90)
        axes[0, 0].set_title(f'Overall Sentiment Distribution - {brand_name}', fontsize = 14, fontweight = 'bold')
        
        sentiment_by_source = pd.crosstab(df['source'], df['sentiment_label'])
        sentiment_by_source.plot(kind='bar', ax = axes[0, 1], color = colors)
        axes[0, 1].set_title('Sentiment by Source', fontsize = 14, fontweight = 'bold')
        axes[0, 1].set_xlabel('Source')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].legend(title = 'Sentiment')
        axes[0, 1].tick_params(axis = 'x', rotation = 45)
        
        axes[1, 0].hist(df['polarity'], bins = 30, color = 'skyblue', edgecolor = 'black')
        axes[1, 0].axvline(df['polarity'].mean(), color = 'red', linestyle = '--', 
                          label = f'Mean: {df["polarity"].mean():.2f}')
        axes[1, 0].set_title('Polarity Distribution', fontsize = 14, fontweight = 'bold')
        axes[1, 0].set_xlabel('Polarity Score')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        
        axes[1, 1].hist(df['sentiment_score'], bins = 30, color = 'lightcoral', edgecolor = 'black')
        axes[1, 1].set_title('Confidence Score Distribution', fontsize = 14, fontweight = 'bold')
        axes[1, 1].set_xlabel('Confidence Score')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sentiment_overview.png', dpi = 300, bbox_inches = 'tight')
        plt.close()
        fig, axes = plt.subplots(1, 2, figsize = (16, 6))
        
        positive_text = ' '.join(df[df['sentiment_label'] == 'POSITIVE']['cleaned_text'].astype(str))
        negative_text = ' '.join(df[df['sentiment_label'] == 'NEGATIVE']['cleaned_text'].astype(str))
        
        if positive_text:
            wordcloud_pos = WordCloud(width = 800, height = 400, background_color = 'white', 
                                     colormap = 'Greens').generate(positive_text)
            axes[0].imshow(wordcloud_pos, interpolation = 'bilinear')
            axes[0].set_title('Positive Sentiment Word Cloud', fontsize = 14, fontweight = 'bold')
            axes[0].axis('off')
        
        if negative_text:
            wordcloud_neg = WordCloud(width = 800, height = 400, background_color = 'white', 
                                     colormap = 'Reds').generate(negative_text)
            axes[1].imshow(wordcloud_neg, interpolation = 'bilinear')
            axes[1].set_title('Negative Sentiment Word Cloud', fontsize = 14, fontweight = 'bold')
            axes[1].axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/wordclouds.png', dpi = 300, bbox_inches = 'tight')
        plt.close()
        
        if 'created_at' in df.columns and df['created_at'].notna().any():
            try:
                df['date'] = pd.to_datetime(df['created_at'], errors = 'coerce')
                df_time = df.dropna(subset = ['date'])
                
                if len(df_time) > 0:
                    df_time = df_time.set_index('date').sort_index()
                    daily_sentiment = df_time.resample('D')['sentiment_numeric'].mean()
                    
                    plt.figure(figsize = (14, 6))
                    plt.plot(daily_sentiment.index, daily_sentiment.values, marker = 'o', linewidth = 2)
                    plt.axhline(y = 0, color = 'gray', linestyle = '--', alpha = 0.5)
                    plt.title(f'Sentiment Trend Over Time - {brand_name}', fontsize = 14, fontweight = 'bold')
                    plt.xlabel('Date')
                    plt.ylabel('Average Sentiment Score')
                    plt.grid(True, alpha = 0.3)
                    plt.tight_layout()
                    plt.savefig(f'{output_dir}/sentiment_timeline.png', dpi = 300, bbox_inches = 'tight')
                    plt.close()
            except Exception as e:
                print(f"Could not create timeline: {e}")
        
        print(f"Visualizations saved to {output_dir}")
    
    def save_results(self, df : pd.DataFrame, insights : Dict, brand_name : str, output_dir : str):
        os.makedirs(output_dir, exist_ok = True)
        
        csv_path = f"{output_dir}/sentiment_analysis_results.csv"
        df.to_csv(csv_path, index = False, encoding = 'utf-8')
        print(f"Results saved to {csv_path}")
        
        insights_path = f"{output_dir}/insights.json"
        with open(insights_path, 'w', encoding = 'utf-8') as f:
            json.dump(insights, f, indent = 4, ensure_ascii = False, default = str)
        print(f"Insights saved to {insights_path}")
        
        report_path = f"{output_dir}/summary_report.txt"
        with open(report_path, 'w', encoding = 'utf-8') as f:
            f.write(f"Sentiment Analysis Report - {brand_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Items Analyzed: {insights['total_items']}\n\n")
            
            f.write("Sentiment Distribution:\n")
            for sentiment, count in insights['sentiment_distribution'].items():
                percentage = (count / insights['total_items']) * 100
                f.write(f"  {sentiment}: {count} ({percentage:.1f}%)\n")
            
            f.write(f"\nAverage Polarity: {insights['average_polarity']:.3f}\n")
            f.write(f"Average Subjectivity: {insights['average_subjectivity']:.3f}\n\n")
            
            f.write("Source Breakdown:\n")
            for source, count in insights['source_breakdown'].items():
                f.write(f"  {source}: {count}\n")
            
            f.write("\nAverage Sentiment by Source:\n")
            for source, score in insights['avg_sentiment_by_source'].items():
                f.write(f"  {source}: {score:.3f}\n")
        
        print(f"Summary report saved to {report_path}")


def analyze_brand_sentiment(brand_name : str):
    compiler = BrandDataCompiler()
    compiler.scrape_and_compile(brand_name)

    compiled_file = f"data/compiled/{brand_name.lower().replace(' ', '_')}/compiled_normalized.json"
    
    if not os.path.exists(compiled_file):
        raise FileNotFoundError(f"Compiled data not found at {compiled_file}. Run scraper first.")
    
    print(f"Loading data from {compiled_file}")
    with open(compiled_file, 'r', encoding = 'utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items for analysis\n")

    analyzer = SentimentAnalyzer()
    
    print("Starting sentiment analysis...")
    df = analyzer.analyze_dataset(data)
    
    print("\nGenerating insights...")
    insights = analyzer.generate_insights(df)
    
    output_dir = f"data/sentiment_analysis/{brand_name.lower().replace(' ', '_')}"
    
    print("\nSaving results...")
    analyzer.save_results(df, insights, brand_name, output_dir)
    
    print("\nCreating visualizations...")
    analyzer.visualize_results(df, brand_name, output_dir)
    
    print(f"\n{'='*60}")
    print("Sentiment Analysis Complete!")
    print(f"{'='*60}")
    print(f"\nResults saved in: {output_dir}")
    print(f"- CSV: sentiment_analysis_results.csv")
    print(f"- Insights: insights.json")
    print(f"- Summary: summary_report.txt")
    print(f"- Visualizations: *.png files")
    
    return df, insights


if __name__ == "__main__":
    brand_name = "flipkart" 
    
    try:
        df, insights = analyze_brand_sentiment(brand_name)
        
        print("\n" + "="*60)
        print("QUICK SUMMARY")
        print("="*60)
        print(f"Total items: {len(df)}")
        print(f"\nSentiment breakdown:")
        for sentiment, count in insights['sentiment_distribution'].items():
            print(f"  {sentiment}: {count}")
        print(f"\nAverage polarity: {insights['average_polarity']:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")