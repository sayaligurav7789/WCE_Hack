# src/generate_viz.py
import os
import json
import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm

class EvidenceVisualizer:
    """Generate HTML visualizations for each query"""
    
    def __init__(self):
        self.output_dir = Path("output") / "EvidenceVisualization"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def highlight_keywords(self, text, keywords):
        """Highlight keywords in text with yellow background"""
        if not text or not keywords:
            return text
        
        # Sort keywords by length (longest first) to avoid nested highlighting issues
        keywords = sorted(set(keywords), key=len, reverse=True)
        
        for keyword in keywords:
            if len(keyword) < 3:  # Skip very short words
                continue
            # Case-insensitive replacement with highlight
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(
                f'<mark style="background-color: #ffeb3b; font-weight: bold;">{keyword}</mark>',
                text
            )
        
        return text
    
    def extract_keywords(self, question):
        """Extract meaningful keywords from question"""
        # Common stopwords to filter out
        stopwords = {'what', 'is', 'are', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'and', 'or', 'but', 'this', 'that', 'these', 'those',
                    'how', 'why', 'when', 'where', 'which', 'who', 'whom', 'whose', 'can', 
                    'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must'}
        
        # Extract words, remove punctuation, filter stopwords and short words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())
        keywords = [w for w in words if w not in stopwords]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def generate_html(self, query_data):
        """Generate HTML for a single query"""
        query_id = query_data.get("ID", query_data.get("query_id", "unknown"))
        question = query_data.get("question", "")
        answer = query_data.get("answer", "")
        
        # Extract keywords from question
        keywords = self.extract_keywords(question)
        
        # Parse references
        references = query_data.get("references", {})
        if isinstance(references, str):
            try:
                references = json.loads(references)
            except:
                references = {"sections": [], "pages": []}
        
        sections = references.get("sections", [])
        pages = references.get("pages", [])
        
        # Get context
        context = query_data.get("context", "")
        if not context:
            # Try to get from other fields
            context = query_data.get("retrieved_context", "")
        
        # Highlight the context with keywords
        highlighted_context = self.highlight_keywords(context, keywords)
        
        # Also highlight the answer with same keywords (optional)
        highlighted_answer = self.highlight_keywords(answer, keywords)
        
        # Create HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evidence Visualization - Question {query_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        
        .header .question {{
            font-size: 18px;
            opacity: 0.9;
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            line-height: 1.5;
        }}
        
        .keywords-bar {{
            background: #f0f0f0;
            padding: 15px 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .keywords-title {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .keyword-badge {{
            display: inline-block;
            background: #ffeb3b;
            color: #333;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            margin: 0 5px 5px 0;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .answer-section {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .answer-section h3 {{
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .answer-section h3 i {{
            color: #667eea;
        }}
        
        .answer-content {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            line-height: 1.8;
            color: #444;
            border-left: 4px solid #667eea;
        }}
        
        .answer-content mark {{
            background-color: #ffeb3b;
            padding: 2px 0;
            font-weight: 500;
        }}
        
        .evidence-section {{
            padding: 30px;
        }}
        
        .evidence-section h3 {{
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .evidence-section h3 i {{
            color: #667eea;
        }}
        
        .evidence-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .evidence-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .section-name {{
            font-weight: 600;
            color: #333;
            background: #e8eaf6;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
        }}
        
        .page-number {{
            color: #666;
            background: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            border: 1px solid #e0e0e0;
        }}
        
        .relevance {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
        }}
        
        .term-badge {{
            display: inline-block;
            background: #ffeb3b;
            color: #333;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 12px;
            margin: 0 5px 5px 0;
            font-weight: 500;
        }}
        
        .evidence-text {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            color: #555;
            line-height: 1.6;
            margin: 15px 0 0 0;
            border: 1px solid #e0e0e0;
        }}
        
        .evidence-text mark {{
            background-color: #ffeb3b;
            padding: 2px 0;
            font-weight: 500;
        }}
        
        .highlighted-context {{
            padding: 30px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .highlighted-context h3 {{
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .context-box {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            line-height: 1.8;
            font-size: 14px;
        }}
        
        .context-box mark {{
            background-color: #ffeb3b;
            padding: 2px 0;
            font-weight: 500;
        }}
        
        .stats {{
            display: flex;
            gap: 15px;
            padding: 20px 30px;
            background: white;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: #f8f9fa;
            padding: 10px 20px;
            border-radius: 10px;
            flex: 1;
            min-width: 120px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: #667eea;
        }}
        
        .footer {{
            padding: 20px 30px;
            background: #f0f0f0;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 20px;
            }}
            
            .answer-section,
            .evidence-section,
            .highlighted-context {{
                padding: 20px;
            }}
            
            .evidence-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Evidence Visualization</h1>
            <div class="question">
                <strong>Question {query_id}:</strong> {question}
            </div>
        </div>
        
        <div class="keywords-bar">
            <div class="keywords-title">🔑 Extracted Keywords:</div>
"""
        
        # Add keyword badges
        for keyword in keywords[:8]:  # Show top 8 keywords
            html += f'<span class="keyword-badge">{keyword}</span>'
        
        html += f"""
        </div>
        
        <div class="answer-section">
            <h3><i class="fas fa-robot"></i> Generated Answer</h3>
            <div class="answer-content">
                {highlighted_answer}
            </div>
        </div>
        
        <div class="evidence-section">
            <h3><i class="fas fa-book"></i> Evidence by Section</h3>
"""
        
        # Add evidence cards
        for i, section in enumerate(sections[:5]):
            # Simulate relevance score
            relevance = round(0.7 + (i * 0.05), 3)
            
            # Get page for this section
            page = pages[i] if i < len(pages) else (pages[0] if pages else "N/A")
            
            # Sample text (you can replace with actual chunk text)
            sample_text = f"This section discusses {section.lower()}. The content here is relevant to your question about {question.lower()[:100]}..."
            highlighted_sample = self.highlight_keywords(sample_text, keywords)
            
            html += f"""
            <div class="evidence-card">
                <div class="evidence-header">
                    <span class="section-name">📖 {section}</span>
                    <span class="page-number">📄 Page {page}</span>
                    <span class="relevance">⭐ Relevance: {relevance}</span>
                </div>
                <div>
"""
            
            # Add term badges for this section
            for keyword in keywords[:4]:
                html += f'<span class="term-badge">{keyword}</span>'
            
            html += f"""
                </div>
                <div class="evidence-text">
                    {highlighted_sample}
                </div>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="highlighted-context">
            <h3><i class="fas fa-highlighter"></i> Highlighted Context</h3>
            <div class="context-box">
                {highlighted_context}
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Sections Used</div>
                <div class="stat-value">{len(sections)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Pages Referenced</div>
                <div class="stat-value">{len(pages)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Keywords Found</div>
                <div class="stat-value">{len(keywords)}</div>
            </div>
        </div>
        
        <div class="footer">
            Generated from Psychology 2e Textbook • Question {query_id} • {pd.Timestamp.now().strftime('%Y-%m-%d')}
        </div>
    </div>
    
    <!-- Font Awesome for icons -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
</body>
</html>"""
        
        return html
    
    def generate_all(self, submission_file="output/submission.json"):
        """Generate HTML for all queries"""
        # Load submission data
        with open(submission_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Generating visualizations for {len(data)} queries...")
        
        for item in tqdm(data):
            query_id = item.get("ID", item.get("query_id", "unknown"))
            
            # Generate HTML
            html = self.generate_html(item)
            
            # Save to file
            output_path = self.output_dir / f"viz_{query_id}.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Generated {len(data)} visualization files in {self.output_dir}")

if __name__ == "__main__":
    visualizer = EvidenceVisualizer()
    
    # Get absolute paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    
    submission_json = os.path.join(output_dir, "submission.json")
    submission_csv = os.path.join(output_dir, "submission.csv")
    
    if os.path.exists(submission_json):
        print(f"Found submission.json")
        visualizer.generate_all(submission_json)
        
    elif os.path.exists(submission_csv):
        print(f"Found submission.csv")
        
        # Load queries.json to fetch question text
        query_map = {}
        queries_path = os.path.join(base_dir, "data", "queries.json")
        
        print(f"Looking for queries at: {queries_path}")
        
        if os.path.exists(queries_path):
            with open(queries_path, "r", encoding="utf-8") as qf:
                queries_data = json.load(qf)
                query_map = {
                    str(q.get("query_id", q.get("ID", ""))): q.get("question", "")
                    for q in queries_data
                }
            print(f"Loaded {len(query_map)} questions")
            
            # Print sample for debugging
            if query_map:
                sample_id = list(query_map.keys())[0]
                print(f"Sample - ID {sample_id}: {query_map[sample_id][:50]}...")
        else:
            print(f"Queries file not found at {queries_path}")
        
        # Read submission.csv
        df = pd.read_csv(submission_csv)
        print(f"CSV columns: {df.columns.tolist()}")
        
        data = []
        
        for _, row in df.iterrows():
            refs = row.get("references", "{}")
            
            try:
                if isinstance(refs, str):
                    refs = json.loads(refs)
                else:
                    refs = {}
            except:
                refs = {"sections": [], "pages": []}
            
            query_id = str(row.get("ID", ""))
            
            # Get question from map or use placeholder
            question_text = query_map.get(query_id, f"Question {query_id}")
            
            item = {
                "ID": query_id,
                "question": question_text,
                "answer": row.get("answer", ""),
                "context": row.get("context", ""),
                "references": refs
            }
            
            data.append(item)
        
        print(f"Prepared {len(data)} items for visualization")
        
        # Temporary JSON file
        temp_path = os.path.join(output_dir, "temp_submission.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        visualizer.generate_all(temp_path)
        
        os.remove(temp_path)
        print(f"Temporary file cleaned up")
        
    else:
        print("No submission file found in output folder")
        print(f"Checked: {submission_json}")
        print(f"Checked: {submission_csv}")