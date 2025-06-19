from flask import Flask, request, jsonify, render_template_string
import requests
import os
from urllib.parse import quote

app = Flask(__name__)

class WebURLShortener:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def shorten_url(self, long_url):
        """서버에서 TinyURL API 호출"""
        
        # URL 보정
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url
        
        # 1. TinyURL - 가장 안정적
        try:
            safe_chars = ':/?#[]@!$&()*+,;='
            encoded_url = quote(long_url, safe=safe_chars)
            api_url = 'http://tinyurl.com/api-create.php?url=' + encoded_url
            
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url and 'tinyurl.com' in short_url and not short_url.startswith('Error'):
                    return {
                        "success": True, 
                        "short_url": short_url,  # 실제 TinyURL 그대로
                        "original_url": long_url, 
                        "service": "TinyURL (하이마트 서비스)"
                    }
        except Exception as e:
            print('TinyURL 오류: ' + str(e))
        
        # 2. is.gd - 백업
        try:
            data = {'format': 'simple', 'url': long_url}
            response = requests.post(
                'https://is.gd/create.php',
                data=data,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url and 'is.gd' in short_url and not short_url.startswith('Error'):
                    return {
                        "success": True, 
                        "short_url": short_url,  # 실제 링크 그대로
                        "original_url": long_url, 
                        "service": "is.gd (하이마트 서비스)"
                    }
        except Exception as e:
            print('is.gd 오류: ' + str(e))
        
        # 3. v.gd - 추가 백업
        try:
            data = {'format': 'simple', 'url': long_url}
            response = requests.post(
                'https://v.gd/create.php',
                data=data,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url and 'v.gd' in short_url and not short_url.startswith('Error'):
                    return {
                        "success": True, 
                        "short_url": short_url,  # 실제 링크 그대로
                        "original_url": long_url, 
                        "service": "v.gd (하이마트 서비스)"
                    }
        except Exception as e:
            print('v.gd 오류: ' + str(e))
            
        return {
            "success": False, 
            "error": "현재 모든 단축 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요."
        }

# 인스턴스 생성
shortener = WebURLShortener()

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔗 CRM TFT URL 단축기</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .badge {
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        
        .url-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .url-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .shorten-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .shorten-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 107, 53, 0.3);
        }
        
        .shorten-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .result-item {
            margin-bottom: 15px;
        }
        
        .result-item:last-child {
            margin-bottom: 0;
        }
        
        .result-label {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .result-url {
            background: rgba(255,255,255,0.7);
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            font-family: monospace;
            position: relative;
        }
        
        .copy-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .copy-btn:hover {
            background: #0056b3;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff6b35;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .info-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            border-left: 4px solid #ff6b35;
        }
        
        .info-box h3 {
            color: #e17055;
            margin-bottom: 10px;
        }
        
        .info-box p {
            color: #333;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        
        .feature-item {
            color: #e17055;
            font-size: 14px;
            display: flex;
            align-items: center;
        }
        
        .feature-item::before {
            content: "✓";
            color: #00b894;
            font-weight: bold;
            margin-right: 8px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .feature-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 CRM TFT 단축기</h1>
        </div>
        
        <form id="shortenForm">
            <div class="form-group">
                <label for="urlInput">단축할 URL을 입력하세요:</label>
                <input 
                    type="text" 
                    id="urlInput" 
                    class="url-input" 
                    placeholder="예: https://www.google.com 또는 www.naver.com"
                    required
                >
            </div>
            
            <button type="submit" class="shorten-btn" id="shortenBtn">
                🚀 단축링크 생성하기
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>단축링크를 생성하는 중...</p>
        </div>
        
        <div class="result" id="result">
            <div class="result-item">
                <div class="result-label">📄 원본 URL:</div>
                <div class="result-url" id="originalUrl"></div>
            </div>
            <div class="result-item">
                <div class="result-label">✨ 단축 URL: <span id="serviceUsed" style="font-size: 12px; color: #666;"></span></div>
                <div class="result-url" id="shortUrl">
                    <span id="shortUrlText"></span>
                    <button class="copy-btn" onclick="copyToClipboard('shortUrlText')">복사</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('shortenForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const urlInput = document.getElementById('urlInput');
            const shortenBtn = document.getElementById('shortenBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            const url = urlInput.value.trim();
            
            if (!url) {
                alert('URL을 입력해주세요!');
                return;
            }
            
            // UI 상태 변경
            shortenBtn.disabled = true;
            shortenBtn.textContent = '⏳ 단축링크 생성 중...';
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.success) {
                    result.className = 'result success';
                    document.getElementById('originalUrl').textContent = data.original_url;
                    document.getElementById('shortUrlText').textContent = data.short_url;
                    document.getElementById('serviceUsed').textContent = '(' + data.service + ')';
                } else {
                    result.className = 'result error';
                    result.innerHTML = '<strong>오류:</strong> ' + data.error;
                }
                
            } catch (error) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.className = 'result error';
                result.innerHTML = '<strong>오류:</strong> 서버와의 연결을 확인해주세요.';
            }
            
            shortenBtn.disabled = false;
            shortenBtn.textContent = '🚀 단축링크 생성하기';
        });
        
        function copyToClipboard(elementId) {
            const text = document.getElementById(elementId).textContent;
            navigator.clipboard.writeText(text).then(function() {
                alert('단축링크가 복사되었습니다! 📋');
            }).catch(function() {
                // 폴백: 텍스트 선택
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('단축링크가 복사되었습니다! 📋');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/shorten', methods=['POST'])
def shorten():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'URL이 필요합니다.'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': 'URL을 입력해주세요.'}), 400
        
        result = shortener.shorten_url(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'서버 오류: {str(e)}'}), 500

@app.route('/health')
def health():
    """헬스체크용 엔드포인트"""
    return jsonify({'status': 'ok', 'message': 'CRM TFT URL 단축 서비스가 정상 작동 중입니다.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 CRM TFT URL 단축기를 시작합니다!")
    print(f"📱 포트: {port}")
    
    if debug:
        print("📍 로컬 테스트: http://localhost:5000")
    else:
        print("🌍 프로덕션 모드: 모든 IP에서 접속 가능")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
