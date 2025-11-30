import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Google Calendar APIのサービスオブジェクトを取得する"""
    creds = None
    
    # スクリプトのディレクトリを基準にパスを設定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')
    client_secret_path = os.path.join(base_dir, 'client_secret.json')

    # token.json はユーザーのアクセストークンとリフレッシュトークンを保存します
    # 初回認証時に自動的に作成されます
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 有効な認証情報がない場合、ログインさせる
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # リフレッシュに失敗した場合は再認証
                creds = None
        
        if not creds:
            if not os.path.exists(client_secret_path):
                return None, f"client_secret.jsonが見つかりません。パス: {client_secret_path}\nGCPからダウンロードして配置してください。"
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                return None, f"認証フローでエラーが発生しました: {str(e)}"
        
        # 次回のために認証情報を保存
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service, None
    except Exception as e:
        return None, f"サービスの構築に失敗しました: {str(e)}"

def add_event_to_calendar(service, summary, start_time, end_time, description=None):
    """カレンダーに予定を追加する"""
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('htmlLink'), None
    except Exception as e:
        return None, str(e)
