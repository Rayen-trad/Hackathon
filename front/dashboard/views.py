import os
import shutil
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Import existing AI services from parent directory
from services.speech_to_text import transcribe_call
from ai.hate_detector import detect_hate_from_textfile

def upload_audio(request):
    if request.method == 'POST':
        print(f"DEBUG: POST request received. Files: {request.FILES.keys()}")
        if request.FILES.get('audio_file'):
            audio_file = request.FILES['audio_file']
            print(f"DEBUG: Processing file: {audio_file.name}")
            
            # Ensure media directory exists
            fs = FileSystemStorage()
            filename = fs.save(audio_file.name, audio_file)
            uploaded_file_url = fs.path(filename)
            print(f"DEBUG: File saved at: {uploaded_file_url}")
            
            # 1. Transcribe audio to text
            try:
                print("DEBUG: Starting transcription...")
                transcript_text = transcribe_call(uploaded_file_url)
                print("DEBUG: Transcription complete.")
            except Exception as e:
                print(f"DEBUG: Transcription failed: {str(e)}")
                return render(request, 'dashboard/upload.html', {'error': f"Transcription failed: {str(e)}"})

            # 2. Save transcript for hate detection
            base_data_dir = os.path.join(settings.BASE_DIR.parent, 'data', 'transcripts', 'django_agent')
            os.makedirs(base_data_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            conversation_id = f"django_{timestamp}"
            txt_path = os.path.join(base_data_dir, f"{conversation_id}.txt")
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
                
            # 3. Run hate detector
            print("DEBUG: Starting hate detection...")
            try:
                report = detect_hate_from_textfile(txt_path)
                print("DEBUG: Hate detection complete.")
            except Exception as e:
                print(f"DEBUG: Hate detection failed: {str(e)}")
                return render(request, 'dashboard/upload.html', {'error': f"Hate detection failed: {str(e)}"})
            
            # Store report in session
            request.session['last_report'] = report
            request.session['raw_transcript'] = transcript_text
            
            print("DEBUG: Redirecting to report.")
            return redirect('report')
        else:
            print("DEBUG: No audio_file in request.FILES")
        
    return render(request, 'dashboard/upload.html')

def report_view(request):
    report = request.session.get('last_report')
    raw_transcript = request.session.get('raw_transcript', '')
    
    if not report:
        return redirect('upload')
        
    context = {
        'report': report,
        'raw_lines': raw_transcript.split('\n')
    }
    return render(request, 'dashboard/report.html', context)

def admin_dashboard(request):
    """Admin dashboard showing all reports with statistics."""
    import glob
    from collections import defaultdict
    
    # Get all transcript files
    base_data_dir = os.path.join(settings.BASE_DIR.parent, 'data', 'transcripts', 'django_agent')
    
    if not os.path.exists(base_data_dir):
        os.makedirs(base_data_dir, exist_ok=True)
    
    transcript_files = glob.glob(os.path.join(base_data_dir, "*.txt"))
    
    reports = []
    total_incidents = 0
    total_severity = 0
    high_risk_count = 0
    severity_distribution = defaultdict(int)
    
    for txt_file in transcript_files:
        try:
            # Run hate detector on each file
            report_data = detect_hate_from_textfile(txt_file)
            
            # Get file timestamp
            file_stat = os.stat(txt_file)
            created_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            report_data['created_at'] = created_time
            report_data['file_path'] = txt_file
            
            reports.append(report_data)
            
            # Aggregate statistics
            total_incidents += report_data['incident_count']
            total_severity += report_data['overall_severity']
            
            if report_data['overall_severity'] >= 0.7:
                high_risk_count += 1
            
            # Severity distribution for graph
            severity = report_data['overall_severity']
            if severity == 0:
                severity_distribution['safe'] += 1
            elif severity < 0.5:
                severity_distribution['passive'] += 1
            elif severity < 0.7:
                severity_distribution['abusive'] += 1
            else:
                severity_distribution['critical'] += 1
                
        except Exception as e:
            print(f"Error processing {txt_file}: {e}")
            continue
    
    # Sort reports by creation time (newest first)
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Calculate averages
    avg_severity = (total_severity / len(reports)) if reports else 0
    
    context = {
        'reports': reports,
        'total_reports': len(reports),
        'total_incidents': total_incidents,
        'avg_severity': round(avg_severity, 2),
        'high_risk_count': high_risk_count,
        'severity_distribution': dict(severity_distribution),
    }
    
    return render(request, 'dashboard/admin.html', context)
