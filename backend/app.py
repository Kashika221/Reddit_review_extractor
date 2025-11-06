from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import json
from datetime import datetime
from pathlib import Path
import asyncio

from compile_data import BrandDataCompiler
from sentiment_analysis import SentimentAnalyzer

app = FastAPI(
    title="Brand Sentiment Analysis API",
    description="Scrape and analyze brand sentiment from multiple sources",
    version="1.0.0"
)

# Store job status
jobs: Dict[str, Dict] = {}

class BrandRequest(BaseModel):
    brand_name: str
    twitter_max: Optional[int] = 50
    news_max: Optional[int] = 50
    reddit_limit: Optional[int] = 25

class JobStatus(BaseModel):
    job_id: str
    brand_name: str
    status: str
    progress: str
    created_at: str
    completed_at: Optional[str] = None
    results_path: Optional[str] = None

def get_brand_dir(brand_name: str) -> str:
    return f"data/sentiment_analysis/{brand_name.lower().replace(' ', '_')}"

def brand_exists(brand_name: str) -> bool:
    results_dir = get_brand_dir(brand_name)
    return os.path.exists(results_dir) and os.path.exists(
        f"{results_dir}/sentiment_analysis_results.csv"
    )

async def analyze_brand_background(job_id: str, brand_name: str):
    """Background task for brand analysis"""
    try:
        jobs[job_id]["status"] = "scraping"
        jobs[job_id]["progress"] = "Collecting data from sources..."
        
        compiler = BrandDataCompiler()
        compiler.scrape_and_compile(brand_name)
        
        jobs[job_id]["status"] = "analyzing"
        jobs[job_id]["progress"] = "Running sentiment analysis..."
        
        compiled_file = f"data/compiled/{brand_name.lower().replace(' ', '_')}/compiled_normalized.json"
        
        if not os.path.exists(compiled_file):
            raise FileNotFoundError(f"Compiled data not found at {compiled_file}")
        
        with open(compiled_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analyzer = SentimentAnalyzer()
        df = analyzer.analyze_dataset(data)
        
        jobs[job_id]["status"] = "generating_insights"
        jobs[job_id]["progress"] = "Generating insights and visualizations..."
        
        insights = analyzer.generate_insights(df)
        output_dir = get_brand_dir(brand_name)
        analyzer.save_results(df, insights, brand_name, output_dir)
        analyzer.visualize_results(df, brand_name, output_dir)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = "Analysis complete"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["results_path"] = output_dir
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = f"Error: {str(e)}"
        jobs[job_id]["error"] = str(e)

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Brand Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - Server health check",
            "POST /analyze - Start brand analysis",
            "GET /jobs/{job_id} - Check job status",
            "GET /results/{brand_name} - Get analysis results",
            "GET /results/{brand_name}/csv - Download CSV",
            "GET /results/{brand_name}/report - Get summary report",
            "GET /results/{brand_name}/insights - Get insights JSON"
        ]
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", tags=["Analysis"])
async def start_analysis(
    request: BrandRequest,
    background_tasks: BackgroundTasks
):
    """Start sentiment analysis for a brand"""
    brand_name = request.brand_name.strip()
    
    if not brand_name:
        raise HTTPException(status_code=400, detail="Brand name cannot be empty")
    
    # Check if analysis already exists
    if brand_exists(brand_name):
        return {
            "message": "Analysis already exists for this brand",
            "brand_name": brand_name,
            "results_path": get_brand_dir(brand_name),
            "status": "completed"
        }
    
    job_id = f"{brand_name}_{datetime.now().timestamp()}"
    
    jobs[job_id] = {
        "job_id": job_id,
        "brand_name": brand_name,
        "status": "queued",
        "progress": "Waiting to start...",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "results_path": None
    }
    
    background_tasks.add_task(
        analyze_brand_background,
        job_id,
        brand_name
    )
    
    return {
        "job_id": job_id,
        "brand_name": brand_name,
        "status": "queued",
        "message": f"Analysis started for {brand_name}. Check status with /jobs/{job_id}",
        "check_status_url": f"/jobs/{job_id}"
    }

@app.get("/jobs/{job_id}", tags=["Jobs"])
async def get_job_status(job_id: str):
    """Get the status of a background job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/results/{brand_name}", tags=["Results"])
async def get_results(brand_name: str):
    """Get analysis results for a brand"""
    if not brand_exists(brand_name):
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for {brand_name}. Run /analyze first."
        )
    
    output_dir = get_brand_dir(brand_name)
    insights_path = f"{output_dir}/insights.json"
    
    if not os.path.exists(insights_path):
        raise HTTPException(status_code=404, detail="Insights file not found")
    
    with open(insights_path, 'r', encoding='utf-8') as f:
        insights = json.load(f)
    
    return {
        "brand_name": brand_name,
        "results_path": output_dir,
        "insights": insights
    }

@app.get("/results/{brand_name}/csv", tags=["Results"])
async def download_csv(brand_name: str):
    """Download sentiment analysis results as CSV"""
    output_dir = get_brand_dir(brand_name)
    csv_path = f"{output_dir}/sentiment_analysis_results.csv"
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=f"{brand_name}_sentiment_analysis.csv"
    )

@app.get("/results/{brand_name}/report", tags=["Results"])
async def get_report(brand_name: str):
    """Get summary report as text"""
    output_dir = get_brand_dir(brand_name)
    report_path = f"{output_dir}/summary_report.txt"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = f.read()
    
    return {
        "brand_name": brand_name,
        "report": report
    }

@app.get("/results/{brand_name}/insights", tags=["Results"])
async def get_insights(brand_name: str):
    """Get detailed insights as JSON"""
    output_dir = get_brand_dir(brand_name)
    insights_path = f"{output_dir}/insights.json"
    
    if not os.path.exists(insights_path):
        raise HTTPException(status_code=404, detail="Insights not found")
    
    with open(insights_path, 'r', encoding='utf-8') as f:
        insights = json.load(f)
    
    return insights

@app.get("/results/{brand_name}/visualizations", tags=["Results"])
async def list_visualizations(brand_name: str):
    """List available visualizations"""
    output_dir = get_brand_dir(brand_name)
    
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="Results directory not found")
    
    visualizations = [
        f for f in os.listdir(output_dir)
        if f.endswith('.png')
    ]
    
    return {
        "brand_name": brand_name,
        "visualizations": visualizations,
        "download_url_template": f"/results/{brand_name}/visualization/{{filename}}"
    }

@app.get("/results/{brand_name}/visualization/{filename}", tags=["Results"])
async def download_visualization(brand_name: str, filename: str):
    """Download a specific visualization"""
    output_dir = get_brand_dir(brand_name)
    file_path = f"{output_dir}/{filename}"
    
    # Security: prevent path traversal
    if ".." in filename or not filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=filename
    )

@app.get("/jobs", tags=["Jobs"])
async def list_jobs():
    """List all jobs"""
    return {
        "total_jobs": len(jobs),
        "jobs": list(jobs.values())
    }

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def cancel_job(job_id: str):
    """Cancel or remove a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] in ["completed", "failed"]:
        del jobs[job_id]
        return {"message": f"Job {job_id} removed"}
    else:
        return {"message": f"Job {job_id} status: {job['status']}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)