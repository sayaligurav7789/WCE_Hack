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
    
    def calculate_confidence(self, answer, context, sections, pages):
        """Calculate confidence score based on multiple factors"""
        confidence = 0.85  # Default high confidence
        
        # Factor 1: If answer contains "Not found", confidence is low
        if "not found" in answer.lower():
            return 0.0
        
        # Factor 2: More sections/pages = higher confidence
        section_score = min(len(sections) / 5, 0.3)  # Max 0.3
        page_score = min(len(pages) / 10, 0.3)       # Max 0.3
        
        # Factor 3: Answer length indicates completeness
        length_score = min(len(answer) / 500, 0.2)   # Max 0.2
        
        # Factor 4: Context presence
        context_score = 0.2 if context and len(context) > 100 else 0.0
        
        confidence = section_score + page_score + length_score + context_score
        
        # Ensure between 0 and 1
        return round(min(max(confidence, 0), 1), 3)
        
    def generate_html(self, query_id, question, answer, context, sections, pages):
        """Generate HTML for a single query"""
        
        # Extract keywords from question
        keywords = self.extract_keywords(question)
        
        # Highlight ONLY the context with keywords (NOT the answer)
        highlighted_context = self.highlight_keywords(context, keywords)
        
        # Keep answer as-is (NO highlighting)
        clean_answer = answer
        
        # Calculate confidence
        confidence = self.calculate_confidence(answer, context, sections, pages)
        
        # Determine confidence level and color
        if confidence >= 0.8:
            confidence_level = "high"
            confidence_label = "HIGH"
        elif confidence >= 0.6:
            confidence_level = "medium"
            confidence_label = "MEDIUM"
        else:
            confidence_level = "low"
            confidence_label = "LOW"
        
        # Calculate factors for display
        section_factor = min(len(sections) / 5, 1.0)
        page_factor = min(len(pages) / 10, 1.0)
        length_factor = min(len(answer) / 500, 1.0)
        context_factor = 1.0 if context and len(context) > 100 else 0.0
        
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
            
            .confidence-meter {{
                background: #f0f0f0;
                padding: 15px 30px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
                gap: 20px;
                flex-wrap: wrap;
            }}
            
            .confidence-bar {{
                flex: 1;
                height: 20px;
                background: #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
            }}
            
            .confidence-fill {{
                height: 100%;
                border-radius: 10px;
                transition: width 0.3s ease;
            }}
            
            .confidence-fill.high {{ background: linear-gradient(90deg, #4caf50, #8bc34a); }}
            .confidence-fill.medium {{ background: linear-gradient(90deg, #ff9800, #ffc107); }}
            .confidence-fill.low {{ background: linear-gradient(90deg, #f44336, #ff7043); }}
            
            .confidence-text {{
                font-size: 18px;
                font-weight: 600;
                min-width: 100px;
                text-align: center;
            }}
            
            .confidence-text.high {{ color: #4caf50; }}
            .confidence-text.medium {{ color: #ff9800; }}
            .confidence-text.low {{ color: #f44336; }}
            
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
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                padding: 20px 30px;
                background: white;
            }}
            
            .stat-item {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
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
            
            .stat-factor {{
                font-size: 11px;
                color: #999;
                margin-top: 5px;
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
                .stats {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
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
                <div class="keywords-title"><i class="fas fa-key"></i> Extracted Keywords:</div>
    """
        
        # Add keyword badges
        for keyword in keywords[:8]:
            html += f'<span class="keyword-badge">{keyword}</span>'
        
        html += f"""
            </div>
            
            <div class="confidence-meter">
                <i class="fas fa-bullseye"></i><span style="font-weight: 600;">Confidence:</span>
                <div class="confidence-bar">
                    <div class="confidence-fill {confidence_level}" style="width: {confidence*100}%;"></div>
                </div>
                <div class="confidence-text {confidence_level}">{confidence_label} ({confidence*100:.0f}%)</div>
            </div>
            
            <div class="answer-section">
                <h3><i class="fas fa-robot"></i> Generated Answer</h3>
                <div class="answer-content">
                    {clean_answer}
                </div>
            </div>
            
            <div class="evidence-section">
                <h3><i class="fas fa-book"></i> Evidence by Section</h3>
    """
        
        # Add evidence cards
        for i, section in enumerate(sections[:5]):
            page = pages[i] if i < len(pages) else (pages[0] if pages else "N/A")
            sample_text = context[:300] if context else f"Content from {section}..."
            highlighted_sample = self.highlight_keywords(sample_text, keywords)
            
            html += f"""
            <div class="evidence-card">
                <div class="evidence-header">
                    <span class="section-name">📖 {section}</span>
                    <span class="page-number">📄 Page {page}</span>
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
                    <div class="stat-factor">Factor: {section_factor:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Pages Referenced</div>
                    <div class="stat-value">{len(pages)}</div>
                    <div class="stat-factor">Factor: {page_factor:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Answer Length</div>
                    <div class="stat-value">{len(answer)}</div>
                    <div class="stat-factor">Factor: {length_factor:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Overall</div>
                    <div class="stat-value">{confidence*100:.0f}%</div>
                    <div class="stat-factor">{confidence_label}</div>
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
    
    def generate_all(self):
        """Generate HTML for all queries by loading from submission.json and queries.json"""
        
        # Load submission results
        submission_path = Path("output/submission.json")
        if not submission_path.exists():
            print("submission.json not found!")
            return
        
        with open(submission_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Load original questions from queries.json
        queries_path = Path("data/queries.json")
        if not queries_path.exists():
            print("queries.json not found!")
            return
        
        with open(queries_path, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        # Create mapping of query_id to question
        question_map = {}
        for q in queries:
            qid = str(q.get("query_id", q.get("ID", "")))
            question_map[qid] = q.get("question", "")
        
        print(f"Loaded {len(question_map)} questions from queries.json")
        print(f"Loaded {len(results)} results from submission.json")
        
        print(f"\nGenerating visualizations for {len(results)} queries...")
        
        for item in tqdm(results):
            query_id = str(item.get("ID", item.get("query_id", "unknown")))
            
            # Get question from map
            question = question_map.get(query_id, f"Question {query_id}")
            
            answer = item.get("answer", "")
            context = item.get("context", "")
            references = item.get("references", {})
            
            if isinstance(references, str):
                try:
                    references = json.loads(references)
                except:
                    references = {"sections": [], "pages": []}
            
            sections = references.get("sections", [])
            pages = references.get("pages", [])
            
            # Generate HTML
            html = self.generate_html(query_id, question, answer, context, sections, pages)
            
            # Save to file
            output_path = self.output_dir / f"viz_{query_id}.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"\nGenerated {len(results)} visualization files in {self.output_dir}")

if __name__ == "__main__":
    visualizer = EvidenceVisualizer()
    visualizer.generate_all()