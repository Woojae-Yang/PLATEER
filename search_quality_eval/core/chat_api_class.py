import os
import json
import uuid
import time
import threading
import requests
import re
from typing import Optional


# ============================================================
# 세션 ID 생성 (싱글턴/멀티턴 공용)
# ============================================================
def generate_session_id(scenario_id: str, readable: bool = True) -> str:
    """시나리오별 고유 세션 ID 생성 (시나리오 내 모든 턴에서 재사용)"""
    if readable:
        short_uuid = uuid.uuid4().hex[:8]
        safe_scenario = "".join(c for c in str(scenario_id) if c.isalnum() or c in "-_")
        return f"sess-{safe_scenario}-{short_uuid}"
    return f"sess-{uuid.uuid4().hex}"


# ============================================================
# 턴 번호 파싱 (멀티턴 전용)
# ============================================================
def parse_turn_number(raw: str) -> Optional[int]:
    """다양한 턴 표기에서 숫자만 추출. 'Turn 1', '1', 'ターン 2', '턴 3' 등."""
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None

    last_token = text.split()[-1]
    try:
        return int(last_token)
    except ValueError:
        pass

    match = re.search(r'\d+', text)
    if match:
        return int(match.group())

    return None


# ============================================================
# Gelatto API 클라이언트 : Gelatto Chat API 호출 캡슐화
# ============================================================
class GelattoClient:
    """
    한 인스턴스 = 하나의 (api_base_url, lang_code, business_type, vendor_id) 조합.
    동일한 프로파일로 여러 쿼리를 처리할 때 워커들이 같은 인스턴스를 공유 가능
    (requests 라이브러리는 thread-safe).
    """

    def __init__(
        self,
        api_base_url: str,
        lang_code: str,
        business_type: str,
        vendor_id: Optional[str],
        chat_endpoint: str,
        product_history_endpoint: str,
        chat_timeout: int,
        product_timeout: int,
        product_size: int,
    ):
        self.api_base_url = api_base_url
        self.lang_code = lang_code
        self.business_type = business_type
        self.vendor_id = vendor_id
        self.chat_endpoint = chat_endpoint
        self.product_history_endpoint = product_history_endpoint
        self.chat_timeout = chat_timeout
        self.product_timeout = product_timeout
        self.product_size = product_size

    @classmethod
    def from_config(cls, config: dict) -> "GelattoClient":
        """build_config 결과 dict에서 client 인스턴스 생성."""
        return cls(
            api_base_url=config["api_base_url"],
            lang_code=config["lang_code"],
            business_type=config["business_type"],
            vendor_id=config.get("vendor_id"),
            chat_endpoint=config["chat_endpoint"],
            product_history_endpoint=config["product_history_endpoint"],
            chat_timeout=config["chat_timeout"],
            product_timeout=config["product_timeout"],
            product_size=config["product_size"],
        )

    def _common_headers(self, user_id: str) -> dict:
        """공통 HTTP 헤더 (vendor_id는 있을 때만 포함)."""
        h = {
            "User-Id": user_id,
            "Lang": self.lang_code,
            "Business-Type": self.business_type,
        }
        if self.vendor_id:
            h["Vendor-Id"] = self.vendor_id
        return h

    def send_chat(self, query: str, session_id: str, user_id: str) -> dict:
        """
        POST /api/chat (SSE)
        Returns: dict with chat_request_id, chat_session_id, latency, answer_text,
                 progress_data, sse_products, sse_products_has_next, has_products_event,
                 has_products_key, keywords, finish_reason, error, http_status
        """
        url = f"{self.api_base_url}{self.chat_endpoint}"

        if not session_id or not str(session_id).strip():
            print(f"    ❌ session_id가 비어있음 - 요청 중단")
            return {
                'chat_request_id': None, 'chat_session_id': None, 'latency': 0.0,
                'answer_text': "", 'progress_data': [], 'sse_products': [],
                'sse_products_has_next': False, 'has_products_event': False,
                'has_products_key': False, 'keywords': [], 'finish_reason': None,
                'faq_data': {},
                'error': {'code': 'CLIENT_VALIDATION', 'message': 'session_id is empty'},
                'http_status': None,
            }

        payload = {
            "query": query,
            "session_id": session_id,
            "client_type": "qa"
        }
        headers = {
            **self._common_headers(user_id),
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        print(f"    📤 POST {url}")
        print(f"       Query: {query}")
        print(f"       session_id (req): {session_id}")
        print(f"       Headers: User-Id={user_id}, Lang={self.lang_code}, Business-Type={self.business_type}"
              + (f", Vendor-Id={self.vendor_id}" if self.vendor_id else ""))

        result = {
            'chat_request_id': None, 'chat_session_id': None, 'latency': 0.0,
            'answer_text': "", 'progress_data': [], 'sse_products': [],
            'sse_products_has_next': False, 'has_products_event': False,
            'has_products_key': False, 'keywords': [], 'finish_reason': None,
            'faq_data': {},
            'error': None, 'http_status': None,
        }

        start_time = time.time()

        try:
            response = requests.post(url, json=payload, headers=headers,
                                     timeout=self.chat_timeout, stream=True)
            result['http_status'] = response.status_code

            if response.status_code >= 400:
                try:
                    error_body = response.json()
                    result['error'] = error_body.get('error') or {'raw': error_body}
                    print(f"    ❌ HTTP {response.status_code}: {result['error']}")
                except Exception:
                    result['error'] = {'code': f'HTTP_{response.status_code}', 'raw': response.text[:500]}
                    print(f"    ❌ HTTP {response.status_code}: {response.text[:300]}")
                result['latency'] = round(time.time() - start_time, 2)
                return result

            print(f"    📡 SSE 스트리밍 시작...")

            for line in response.iter_lines():
                if not line:
                    continue
                line_text = line.decode('utf-8')
                if not line_text.startswith('data:'):
                    continue
                data_text = line_text[5:].strip()
                if not data_text:
                    continue

                try:
                    data_json = json.loads(data_text)
                except json.JSONDecodeError:
                    continue

                if data_json.get('success') is False and data_json.get('error'):
                    result['error'] = data_json['error']
                    print(f"    ⚠️  SSE 에러 이벤트: {data_json['error']}")
                    continue

                chat_event = data_json.get('chat_event')

                if not result['chat_request_id'] and data_json.get('chat_request_id'):
                    result['chat_request_id'] = data_json['chat_request_id']
                    print(f"    ✓ chat_request_id: {result['chat_request_id']}")
                if not result['chat_session_id'] and data_json.get('chat_session_id'):
                    result['chat_session_id'] = data_json['chat_session_id']

                if chat_event == 'message':
                    result['answer_text'] += data_json.get('data', {}).get('text', '')
                elif chat_event == 'progress':
                    progress_item = data_json.get('data', {})
                    if progress_item:
                        result['progress_data'].append(progress_item)
                        print(f"    ✓ progress: {progress_item.get('type')} / {progress_item.get('status')}")
                elif chat_event == 'products':
                    products_data = data_json.get('data', {})
                    has_products_key = isinstance(products_data, dict) and 'products' in products_data
                    new_products = products_data.get('products', []) if has_products_key else []

                    # 누적 (덮어쓰기 X)
                    result['sse_products'].extend(new_products)

                    # has_next는 마지막 이벤트 기준
                    result['sse_products_has_next'] = (
                        bool(products_data.get('has_next', False))
                        if isinstance(products_data, dict)
                        else False
                    )
                    result['has_products_event'] = True

                    # has_products_key는 한 번이라도 True였으면 유지
                    if has_products_key:
                        result['has_products_key'] = True

                    print(
                        f"    ✓ SSE products 이벤트: +{len(new_products)}개 "
                        f"(누적 {len(result['sse_products'])}개, "
                        f"has_key={has_products_key}, has_next={result['sse_products_has_next']})"
                    )
                elif chat_event == 'keywords':
                    kw_data = data_json.get('data', {})
                    result['keywords'] = kw_data.get('list', []) if isinstance(kw_data, dict) else []
                    print(f"    ✓ keywords: {result['keywords']}")
                elif chat_event == 'faq':
                    result['faq_data'] = data_json.get('data', {})
                    print(f"    ✓ faq 이벤트 수신 (RAG 문서 응답)")
                elif chat_event == 'finish':
                    result['finish_reason'] = data_json.get('data', {}).get('reason')
                    print(f"    ✓ finish (reason={result['finish_reason']}, 답변 {len(result['answer_text'])}자)")
                    break

            result['latency'] = round(time.time() - start_time, 2)
            print(f"    ✓ POST {self.chat_endpoint} 완료 ({result['latency']}초)")
            return result

        except requests.exceptions.Timeout:
            print(f"    ⚠️  타임아웃 ({self.chat_timeout}초)")
            result['latency'] = float(self.chat_timeout)
            result['error'] = {'code': 'TIMEOUT', 'message': f'{self.chat_timeout}s exceeded'}
            return result

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    result['http_status'] = e.response.status_code
                    print(f"    ⚠️  응답 상태: {e.response.status_code}")
                    print(f"    ⚠️  응답 본문: {e.response.text[:300]}")
                except Exception:
                    pass
            print(f"    ⚠️  오류: {error_detail}")
            result['latency'] = round(time.time() - start_time, 2)
            result['error'] = {'code': 'REQUEST_EXCEPTION', 'message': error_detail}
            return result

        except Exception as e:
            print(f"    ⚠️  예상치 못한 오류: {e}")
            result['latency'] = round(time.time() - start_time, 2)
            result['error'] = {'code': 'UNEXPECTED', 'message': str(e)}
            return result

    def get_product_histories(self, chat_request_id: str, user_id: str) -> tuple:
        """GET /api/product/histories/{chat_request_id}?size=N (SSE has_next=True일 때만 호출)"""
        url = f"{self.api_base_url}{self.product_history_endpoint}/{chat_request_id}"
        params = {"size": self.product_size}
        headers = self._common_headers(user_id)

        print(f"    📥 GET {url}?size={self.product_size}")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.product_timeout)
            response.raise_for_status()
            product_data = response.json()

            product_count = 0
            if isinstance(product_data, dict):
                if 'data' in product_data and isinstance(product_data['data'], dict):
                    if 'products' in product_data['data']:
                        product_count = len(product_data['data']['products'])
                        print(f"    ✓ data.products에서 추출: {product_count}개")
                elif 'products' in product_data:
                    product_count = len(product_data['products'])
                    print(f"    ✓ products에서 추출: {product_count}개")

            return product_data, product_count

        except requests.exceptions.Timeout:
            print(f"    ⚠️  GET {self.product_history_endpoint} 타임아웃")
            return None, 0
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  GET {self.product_history_endpoint} 오류: {e}")
            return None, 0
        except Exception as e:
            print(f"    ⚠️  예상치 못한 오류: {e}")
            return None, 0


# ============================================================
# 단일 쿼리 처리 (재시도 + 상품 수집)
# ============================================================
def process_query(client: GelattoClient, query: str, session_id: str, config: dict) -> dict:
    """
    단일 쿼리 처리
    - row마다 unique user_id 생성 (백엔드 페르소나 캐싱 회피)
    - 429일 때만 재시도 (4xx/5xx는 즉시 실패)
    - 상품 데이터: SSE products 우선, has_next=True일 때만 GET 보강
    """
    # row마다 unique user_id (멀티턴은 config["user_id"]로 외부 주입)
    user_id = config.get("user_id") or \
              f"{config.get('user_id_prefix', 'qa')}-{uuid.uuid4().hex[:8]}"

    chat_result = None

    for attempt in range(config["max_retries"]):
        chat_result = client.send_chat(query, session_id, user_id)

        if chat_result.get('http_status') == 429:
            if attempt < config["max_retries"] - 1:
                wait_time = config["retry_delay"]
                print(f"    ⏳ Rate Limit(429) - {wait_time}초 대기 후 재시도 ({attempt + 1}/{config['max_retries']})")
                time.sleep(wait_time)
                continue
            print(f"    ⚠️  최대 재시도 횟수 초과")
        break

    chat_request_id = chat_result['chat_request_id']

    # 에러 요약
    error_summary = ""
    if chat_result['error']:
        err = chat_result['error']
        if isinstance(err, dict):
            error_summary = f"[{err.get('code', 'ERR')}] {err.get('message', '')} {err.get('detail', '')}".strip()
        else:
            error_summary = str(err)

    if not chat_request_id:
        return {
            'session_id': chat_result['chat_session_id'] or session_id,
            'answer_text': chat_result['answer_text'],
            'progress_data': json.dumps(chat_result['progress_data'], ensure_ascii=False),
            'keywords': json.dumps(chat_result['keywords'], ensure_ascii=False),
            'latency': chat_result['latency'],
            'chat_request_id': None,
            'product_count': 0,
            'response_type': "error",
            'response_text': "[오류: chat_request_id 없음]",
            'error': error_summary or "[chat_request_id 없음]",
        }

    # FAQ 응답 분기 (chat_event == 'faq'로 수신된 경우 — RAG 문서 응답, 상품 없음)
    # products 이벤트가 아니라 faq 이벤트로 데이터가 왔을 때만 여기로 들어오므로,
    # intent 값을 별도로 안 받아도 faq_data 존재 여부만으로 분기 가능.
    faq_data = chat_result.get('faq_data') or {}
    if faq_data:
        return {
            'session_id': chat_result['chat_session_id'] or session_id,
            'answer_text': chat_result['answer_text'],
            'progress_data': json.dumps(chat_result['progress_data'], ensure_ascii=False),
            'keywords': json.dumps(chat_result['keywords'], ensure_ascii=False),
            'latency': chat_result['latency'],
            'chat_request_id': chat_request_id,
            'product_count': 0,
            'response_type': "faq",
            'response_text': "faq",
            'error': error_summary,
            'faq_description': faq_data.get('description', ''),
            'faq_summary': faq_data.get('summary', ''),
            'faq_detail': faq_data.get('detail', ''),
            'faq_resource': json.dumps(faq_data.get('resource', []), ensure_ascii=False),
            'faq_length_type': faq_data.get('length_type', ''),
        }

    # 상품 데이터: SSE 우선, has_next=True일 때만 GET 보강
    sse_has_next = chat_result.get('sse_products_has_next', False)
    has_products_key = chat_result.get('has_products_key', False)
    products_list = chat_result.get('sse_products', []) or []

    # 상품 데이터 처리 직전에
    progress_list = chat_result.get('progress_data', []) or []
    tool_was_called = any(
        isinstance(p, dict) and p.get('type') == 'TOOL_RUNNING'
        for p in progress_list
    )


    # SSE가 일부 상품만 내려준 경우(has_next=True)에는 GET으로 전체 상품을 보강한다.
    # products 키 유무는 응답 분류에만 사용하고, 보강 여부는 has_next 기준으로 판단한다.
    if sse_has_next:
        product_data, _ = client.get_product_histories(chat_request_id, user_id)
        if product_data:
            get_products = product_data.get('data', {}).get('products', [])
            if get_products:
                products_list = get_products
                has_products_key = True
                print(f"    ✓ GET으로 상품 보강: {len(products_list)}개")

    product_count = len(products_list)

    # response_text 결정
    if products_list:
        response_type = "products"
        filtered_products = []
        for p in products_list:
            custom = p.get('custom') or {} 
            filtered_products.append({
                'vendor_id': p.get('vendor_id'),
                'product_id': p.get('product_id'),
                'title': p.get('title'),
                'brand_name': p.get('brand_name'),
                'product_url_pc': p.get('product_url_pc'),
                'original_price': p.get('original_price'),
                'selling_price': p.get('selling_price'),
                'currency': p.get('currency'),
                'cdn_main_url': p.get('cdn_main_url'),
                'origin': p.get('origin'),
                'availability': p.get('availability'),
                'attribute': p.get('attribute'),
                'custom': {
                    'sku': custom.get('sku'),
                    'sizes': custom.get('sizes'),
                    'description': custom.get('description'),
                    '_g': custom.get('_g'),
                    'colors': custom.get('colors'),
                    'price_max': custom.get('price_max'),
                    'price_min': custom.get('price_min'),
                    },
            })
        response_text = json.dumps(filtered_products, ensure_ascii=False)

    elif has_products_key:
        response_type = "응답 건수 0"
        response_text = "응답 건수 0"

    else:
        response_type = "역질문"
        response_text = "역질문"

    return {
        'session_id': chat_result['chat_session_id'] or session_id,
        'answer_text': chat_result['answer_text'],
        'progress_data': json.dumps(chat_result['progress_data'], ensure_ascii=False),
        'keywords': json.dumps(chat_result['keywords'], ensure_ascii=False),
        'latency': chat_result['latency'],
        'chat_request_id': chat_request_id,
        'product_count': product_count,
        'response_type': response_type,
        'response_text': response_text,
        'error': error_summary,
    }


# ============================================================
# 새 API (shw-adk2-front / ADK2) 상품 정규화
# ============================================================
def normalize_adk_front_product(p: dict) -> dict:
    """
    새 API의 products.items 상품을 기존 다운스트림(core/scoring.py 등)이
    기대하는 키로 매핑한다. (selling_price / cdn_main_url / availability ...)

    매핑:
      price_current   → selling_price
      price_max       → original_price (없으면 None)
      hero_image_url  → cdn_main_url
      in_stock(bool)  → availability ('in_stock' / 'out_of_stock')
    새 API에 없는 필드(brand_name / product_url_pc / origin)는 None.
    평가에 유용한 신규 필드(sku / category_path / relevance / score / s)는 추가로 보존.
    """
    if not isinstance(p, dict):
        return {}

    in_stock = p.get("in_stock")
    if in_stock is True:
        availability = "in_stock"
    elif in_stock is False:
        availability = "out_of_stock"
    else:
        availability = None

    gd_attrs = p.get("gd_attrs") if isinstance(p.get("gd_attrs"), dict) else {}

    return {
        # ── 기존 스키마 호환 키 ──────────────────────────────
        "vendor_id":      p.get("vendor_id"),
        "product_id":     p.get("product_id"),
        "title":          p.get("title"),
        "brand_name":     gd_attrs.get("brand"),          # 새 API엔 보통 없음 → None
        "product_url_pc": p.get("product_url_pc"),         # 새 API엔 없음 → None
        "original_price": p.get("price_max"),
        "selling_price":  p.get("price_current"),
        "currency":       p.get("currency"),
        "cdn_main_url":   p.get("hero_image_url"),
        "origin":         None,
        "availability":   availability,
        # ── 새 API 추가 필드 (평가 활용) ────────────────────
        "sku":            p.get("sku"),
        "category_path":  p.get("category_path"),
        "relevance":      p.get("relevance"),
        "score":          p.get("score"),
        "s":              p.get("s"),
    }


# ============================================================
# 새 API (shw-adk2-front) 클라이언트 : 표준 SSE(event:/data:) + IAP 인증
# ============================================================
class AdkFrontClient:
    """
    신규 ADK2-front API 클라이언트.

    기존 GelattoClient 대비 변경점:
      - SSE가 표준 형식: 'event:' 줄 + 'data:' 줄 페어 (기존은 data 안 chat_event)
      - 본문 텍스트 이벤트: delta (기존 message)
      - 상품 이벤트: data.items (기존 data.products), has_next 없음 (GET 보강 불필요)
      - 추천 이벤트: actions → data.chips (기존 keywords → data.list)
      - 요청 ID: data.rid (기존 top-level chat_request_id)
      - 종료: finish → data.rid (reason 없음)
      - 라우팅: 헤더(Business-Type/Vendor-Id) + 쿼리 prefix → body의 tab/lang/mode/search_backend
      - 인증: Google IAP (Authorization: Bearer <OIDC ID 토큰>)

    send_chat()는 GelattoClient.send_chat()와 동일한 키의 result dict를 반환하므로
    core.chat_api_class.process_query() 를 그대로 재사용할 수 있다.
    """

    def __init__(
        self,
        api_base_url: str,
        lang_code: str,
        chat_endpoint: str,
        chat_timeout: int,
        tab: Optional[str] = None,
        mode: str = "agent",
        search_backend: str = "atlas",
        iap_audience: Optional[str] = None,
        iap_credentials_file: Optional[str] = None,
        iap_token: Optional[str] = None,
        iap_cookie: Optional[str] = None,
        origin: Optional[str] = None,
    ):
        self.api_base_url = api_base_url
        self.lang_code = lang_code
        self.chat_endpoint = chat_endpoint
        self.chat_timeout = chat_timeout
        self.tab = tab
        self.mode = mode
        self.search_backend = search_backend
        self.iap_audience = iap_audience
        self.iap_credentials_file = iap_credentials_file
        self._static_token = iap_token
        self.iap_cookie = iap_cookie
        self.origin = origin

        # 토큰 캐시 (스레드 안전) — OIDC ID 토큰은 보통 1시간 유효
        self._token_lock = threading.Lock()
        self._cached_token: Optional[str] = None
        self._token_fetched_at: float = 0.0
        self._token_ttl = 50 * 60  # 50분

    @classmethod
    def from_config(cls, config: dict) -> "AdkFrontClient":
        """
        build_config 결과 dict에서 client 인스턴스 생성.

        IAP 인증 우선순위 (위가 높음):
          1) config['iap_cookie'] / 환경변수 IAP_COOKIE   ← 브라우저 IAP 세션 쿠키(Cookie 헤더)
          2) config['iap_token']  / 환경변수 IAP_TOKEN    ← 직접 주입한 Bearer ID 토큰
          3) iap_audience + iap_credentials_file (또는 ADC) 로 자동발급
        쿠키가 있으면 토큰/JSON보다, 토큰이 있으면 JSON보다 우선한다.
        (JSON 전용 SA를 아직 못 받았을 때, 화이트리스트된 브라우저 계정의 쿠키로 임시 테스트 가능.)
        """
        return cls(
            api_base_url=config["api_base_url"],
            lang_code=config["lang_code"],
            chat_endpoint=config.get("chat_endpoint", "/api/chat"),
            chat_timeout=config.get("chat_timeout", 180),
            tab=config.get("tab"),
            mode=config.get("mode", "agent"),
            search_backend=config.get("search_backend", "atlas"),
            iap_audience=config.get("iap_audience"),
            iap_credentials_file=config.get("iap_credentials_file"),
            iap_token=config.get("iap_token") or os.getenv("IAP_TOKEN"),
            iap_cookie=config.get("iap_cookie") or os.getenv("IAP_COOKIE"),
            origin=config.get("origin"),
        )

    # ── IAP 토큰 발급 ──────────────────────────────────────
    def _get_iap_token(self) -> Optional[str]:
        """
        IAP용 OIDC ID 토큰을 반환한다.
          1) config로 주입된 정적 토큰(iap_token)이 있으면 그대로 사용.
          2) iap_audience가 있으면 서비스계정/ADC로 ID 토큰을 자동 발급(캐시).
        둘 다 없으면 None (인증 헤더 생략).
        """
        if self._static_token:
            return self._static_token

        if not self.iap_audience:
            return None

        with self._token_lock:
            now = time.time()
            if self._cached_token and (now - self._token_fetched_at) < self._token_ttl:
                return self._cached_token

            token = self._fetch_oidc_token()
            if token:
                self._cached_token = token
                self._token_fetched_at = now
            return token

    def _fetch_oidc_token(self) -> Optional[str]:
        """서비스계정 JSON(iap_credentials_file) 또는 ADC로 target_audience용 ID 토큰 발급."""
        try:
            from google.auth.transport.requests import Request as GoogleRequest
        except ImportError:
            print("    ⚠️  google-auth 미설치 — IAP 토큰 자동발급 불가 (pip install google-auth)")
            return None

        try:
            if self.iap_credentials_file:
                from google.oauth2 import service_account
                creds = service_account.IDTokenCredentials.from_service_account_file(
                    self.iap_credentials_file,
                    target_audience=self.iap_audience,
                )
                creds.refresh(GoogleRequest())
                return creds.token

            # 서비스계정 파일 미지정 → ADC(Application Default Credentials) 사용
            # (1) SA 키 / 메타데이터 서버 ADC: fetch_id_token 으로 audience 지정 토큰 발급
            from google.oauth2 import id_token as google_id_token
            try:
                return google_id_token.fetch_id_token(GoogleRequest(), self.iap_audience)
            except Exception as e_sa:
                # (2) 유저 ADC(gcloud auth application-default login): 위가 실패함.
                #     로그인 시 함께 발급된 openid id_token 을 사용한다.
                #     ⚠️ 이 토큰의 aud 는 gcloud ADC 클라이언트라, IAP가 audience를
                #        엄격 검증하면 거부될 수 있다(그땐 SA 또는 쿠키 방식 사용).
                import google.auth
                creds, _ = google.auth.default(
                    scopes=[
                        "openid",
                        "https://www.googleapis.com/auth/userinfo.email",
                    ]
                )
                creds.refresh(GoogleRequest())
                tok = getattr(creds, "id_token", None)
                if tok:
                    print("    ℹ️  유저 ADC id_token 사용 (IAP가 aud 거부 시 SA/쿠키로 전환 필요)")
                    return tok
                raise e_sa

        except Exception as e:
            print(f"    ⚠️  IAP 토큰 발급 실패: {e}")
            return None

    def _build_headers(self, user_id: str) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Id": user_id,
        }
        if self.origin:
            headers["Origin"] = self.origin

        # 1) 브라우저 IAP 세션 쿠키가 있으면 그걸로 인증 (토큰 발급 불필요)
        if self.iap_cookie:
            headers["Cookie"] = self.iap_cookie
            return headers

        # 2) 아니면 Bearer OIDC 토큰 (정적 주입 또는 SA 자동발급)
        token = self._get_iap_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def send_chat(self, query: str, session_id: str, user_id: str) -> dict:
        """
        POST {chat_endpoint} (표준 SSE: event:/data:)
        GelattoClient.send_chat()와 동일한 키의 dict를 반환 → process_query 재사용 가능.
        """
        url = f"{self.api_base_url}{self.chat_endpoint}"

        result = {
            'chat_request_id': None, 'chat_session_id': None, 'latency': 0.0,
            'answer_text': "", 'progress_data': [], 'sse_products': [],
            'sse_products_has_next': False, 'has_products_event': False,
            'has_products_key': False, 'keywords': [], 'finish_reason': None,
            'error': None, 'http_status': None,
        }

        if not session_id or not str(session_id).strip():
            print(f"    ❌ session_id가 비어있음 - 요청 중단")
            result['error'] = {'code': 'CLIENT_VALIDATION', 'message': 'session_id is empty'}
            return result

        payload = {
            "session_id": session_id,
            "query": query,
            "tab": self.tab,
            "lang": self.lang_code,
            "mode": self.mode,
            "search_backend": self.search_backend,
            "client_type": "qa"
        }
        headers = self._build_headers(user_id)

        print(f"    📤 POST {url}")
        print(f"       Query: {query}")
        print(f"       session_id (req): {session_id}")
        print(f"       Body: tab={self.tab}, lang={self.lang_code}, "
              f"mode={self.mode}, search_backend={self.search_backend}")

        start_time = time.time()

        try:
            response = requests.post(url, json=payload, headers=headers,
                                     timeout=self.chat_timeout, stream=True)
            result['http_status'] = response.status_code

            if response.status_code >= 400:
                try:
                    error_body = response.json()
                    result['error'] = error_body.get('error') or {'raw': error_body}
                    print(f"    ❌ HTTP {response.status_code}: {result['error']}")
                except Exception:
                    result['error'] = {'code': f'HTTP_{response.status_code}', 'raw': response.text[:500]}
                    print(f"    ❌ HTTP {response.status_code}: {response.text[:300]}")
                result['latency'] = round(time.time() - start_time, 2)
                return result

            # SSE가 아니면(예: IAP 로그인 페이지로 302→HTML) 진단 정보를 남기고 종료
            ctype = response.headers.get('Content-Type', '')
            if 'text/event-stream' not in ctype:
                snippet = response.text[:300]
                result['error'] = {
                    'code': 'NOT_SSE',
                    'message': f'status={response.status_code}, content-type={ctype}',
                    'raw': snippet,
                }
                print(f"    ❌ SSE 응답 아님 (status={response.status_code}, content-type={ctype})")
                if response.history:
                    print(f"       리다이렉트 발생: {[h.status_code for h in response.history]} "
                          f"→ 최종 URL {response.url}")
                    print(f"       (쿠키/토큰 호스트 불일치 또는 만료일 가능성 — base URL을 쿠키 발급 호스트와 맞추세요)")
                print(f"       본문 앞부분: {snippet[:200]}")
                result['latency'] = round(time.time() - start_time, 2)
                return result

            print(f"    📡 SSE 스트리밍 시작...")
            self._consume_sse(response, result)

            result['latency'] = round(time.time() - start_time, 2)
            print(f"    ✓ POST {self.chat_endpoint} 완료 ({result['latency']}초)")
            return result

        except requests.exceptions.Timeout:
            print(f"    ⚠️  타임아웃 ({self.chat_timeout}초)")
            result['latency'] = float(self.chat_timeout)
            result['error'] = {'code': 'TIMEOUT', 'message': f'{self.chat_timeout}s exceeded'}
            return result
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  오류: {e}")
            result['latency'] = round(time.time() - start_time, 2)
            result['error'] = {'code': 'REQUEST_EXCEPTION', 'message': str(e)}
            return result
        except Exception as e:
            print(f"    ⚠️  예상치 못한 오류: {e}")
            result['latency'] = round(time.time() - start_time, 2)
            result['error'] = {'code': 'UNEXPECTED', 'message': str(e)}
            return result

    def _consume_sse(self, response, result: dict) -> None:
        """표준 SSE 스트림(event:/data: 페어)을 파싱해 result를 채운다."""
        current_event = None
        for raw_line in response.iter_lines():
            if raw_line is None:
                continue
            line = raw_line.decode('utf-8') if isinstance(raw_line, (bytes, bytearray)) else raw_line

            # 빈 줄 = 이벤트 경계
            if not line.strip():
                current_event = None
                continue

            if line.startswith('event:'):
                current_event = line[len('event:'):].strip()
                continue
            if not line.startswith('data:'):
                continue

            data_text = line[len('data:'):].strip()
            if not data_text:
                continue
            try:
                data = json.loads(data_text)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue

            # rid = 요청 ID (progress/finish 등 어디서든 처음 보이면 채택)
            if not result['chat_request_id'] and data.get('rid'):
                result['chat_request_id'] = data['rid']

            ev = current_event

            if ev == 'delta':
                result['answer_text'] += data.get('text', '')

            elif ev == 'progress':
                result['progress_data'].append(data)
                ptype = data.get('type')
                if ptype == 'tool':
                    print(f"    ✓ progress: tool={data.get('tool')} detail={data.get('detail')}")
                else:
                    print(f"    ✓ progress: {ptype}")

            elif ev == 'products':
                items = data.get('items', []) if isinstance(data, dict) else []
                normalized = [normalize_adk_front_product(p) for p in items]
                result['sse_products'].extend(normalized)
                result['has_products_event'] = True
                result['has_products_key'] = True   # items 키 존재 = 검색 수행됨
                result['sse_products_has_next'] = False  # 새 API는 SSE 한방, GET 보강 없음
                print(f"    ✓ SSE products: +{len(normalized)}개 "
                      f"(누적 {len(result['sse_products'])}개, mode={data.get('mode')})")

            elif ev == 'actions':
                chips = data.get('chips', [])
                result['keywords'] = chips if isinstance(chips, list) else []
                print(f"    ✓ actions(chips): {result['keywords']}")

            elif ev == 'error':
                result['error'] = data.get('error') or data
                print(f"    ⚠️  SSE 에러 이벤트: {result['error']}")

            elif ev == 'finish':
                result['finish_reason'] = data.get('reason') or data.get('rid') or 'stop'
                print(f"    ✓ finish (rid={data.get('rid')}, 답변 {len(result['answer_text'])}자)")
                break

    def get_product_histories(self, chat_request_id: str, user_id: str) -> tuple:
        """새 API는 상품을 SSE products 이벤트로만 내려준다 (has_next 없음). no-op."""
        return None, 0


# ============================================================
# gcloud identity 토큰 발급 (Cloud Run IAM "allow authenticated" 용)
# ============================================================
def fetch_gcloud_identity_token(audiences: Optional[str] = None) -> Optional[str]:
    """
    `gcloud auth print-identity-token` 으로 OIDC ID 토큰을 발급한다.
    IAP(audience+서비스계정 OIDC)가 아니라, Cloud Run 기본 IAM 인증
    (서비스가 'allow authenticated')에 쓰는 호출자 본인의 identity token.

    audiences가 지정되면 `--audiences=<url>` 로 토큰의 aud를 서비스 URL에 맞춘다.
    (지정하지 않으면 curl 예시와 동일하게 기본 토큰을 발급)
    """
    import subprocess
    cmd = ["gcloud", "auth", "print-identity-token"]
    if audiences:
        cmd.append(f"--audiences={audiences}")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            print(f"    ⚠️  gcloud identity token 발급 실패: {out.stderr.strip()[:300]}")
            return None
        token = out.stdout.strip()
        return token or None
    except FileNotFoundError:
        print("    ⚠️  gcloud CLI 미설치 — identity token 발급 불가 "
              "(gcloud SDK 설치 또는 iap_token/IAP_TOKEN 으로 토큰 직접 주입)")
        return None
    except Exception as e:
        print(f"    ⚠️  gcloud identity token 발급 오류: {e}")
        return None


# ============================================================
# Cloud Run IAM 인증 클라이언트 (qa-gelatto-genserd-chat 등)
# ============================================================
class GcloudRunClient(AdkFrontClient):
    """
    Cloud Run 기본 IAM 인증('allow authenticated') 환경 전용 클라이언트.

    요청 body / SSE 포맷은 AdkFrontClient(ADK2-front)와 완전히 동일하므로
    send_chat / _consume_sse / get_product_histories / process_query 를 그대로 재사용한다.
    유일한 차이는 인증 방식이다.

      AdkFrontClient : IAP (audience + 서비스계정 OIDC 토큰, 또는 IAP 세션 쿠키)
      GcloudRunClient: Cloud Run IAM → Authorization: Bearer $(gcloud auth print-identity-token)

    토큰 우선순위 (위가 높음):
      1) 정적 토큰 (config['iap_token'] / 환경변수 IAP_TOKEN / ID_TOKEN)  ← 직접 주입
      2) 서비스계정 JSON (config['iap_credentials_file']) → SA OIDC ID 토큰 자동발급
         - gcloud CLI 불필요 → EC2 등 헤드리스 자동화에 권장
         - Cloud Run 은 aud=서비스 URL 을 요구하므로 target_audience 는
           config['gcloud_audiences'] 또는 api_base_url 로 자동 설정
      3) `gcloud auth print-identity-token` (로컬에 gcloud 가 있을 때, 50분 캐시)
         - config['gcloud_audiences'] 가 있으면 `--audiences` 로 aud 지정
    2)·3) 은 모두 50분 캐시.
    """

    def __init__(self, *args, gcloud_audiences: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gcloud_audiences = gcloud_audiences

    @classmethod
    def from_config(cls, config: dict) -> "GcloudRunClient":
        api_base = config["api_base_url"]
        # SA JSON 으로 ID 토큰을 발급할 때 Cloud Run 은 aud=서비스 URL 을 요구한다.
        # (adk_front 의 IAP client-ID audience 와는 다름)
        sa_audience = config.get("gcloud_audiences") or api_base
        return cls(
            api_base_url=api_base,
            lang_code=config["lang_code"],
            chat_endpoint=config.get("chat_endpoint", "/api/chat"),

            chat_timeout=config.get("chat_timeout", 180),
            tab=config.get("tab"),
            mode=config.get("mode", "agent"),
            search_backend=config.get("search_backend", "atlas"),
            iap_audience=sa_audience,                              # SA JSON 발급용 target_audience
            iap_credentials_file=config.get("iap_credentials_file"),
            iap_token=(config.get("iap_token")
                       or os.getenv("IAP_TOKEN")
                       or os.getenv("ID_TOKEN")),
            origin=config.get("origin"),
            gcloud_audiences=config.get("gcloud_audiences"),
        )

    def _get_iap_token(self) -> Optional[str]:
        """정적 토큰 → SA JSON → gcloud CLI 순으로 토큰 확보 (2·3은 50분 캐시)."""
        if self._static_token:
            return self._static_token

        with self._token_lock:
            now = time.time()
            if self._cached_token and (now - self._token_fetched_at) < self._token_ttl:
                return self._cached_token

            if self.iap_credentials_file:
                # 서비스계정 JSON → target_audience(self.iap_audience=서비스 URL) 로 ID 토큰 발급
                token = self._fetch_oidc_token()
            else:
                # gcloud CLI 발급 (gcloud_audiences 없으면 curl 예시처럼 기본 토큰)
                token = fetch_gcloud_identity_token(self.gcloud_audiences)

            if token:
                self._cached_token = token
                self._token_fetched_at = now
            return token

    def _build_headers(self, user_id: str) -> dict:
        """
        qa-gelatto-genserd-chat 용 헤더.

        ⚠️ 새 qa API 는 curl 예시처럼 Authorization + Content-Type 만 받는다.
        AdkFrontClient 의 기본 헤더에 들어가는 'User-Id' 를 그대로 보내면,
        앱이 그 user-id 를 Genser Discovery 접근 주체로 검사 → 화이트리스트에 없어 403.
        인가는 Bearer 토큰의 SA 신원만으로 충분하므로 User-Id 는 보내지 않는다.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if self.origin:
            headers["Origin"] = self.origin
        if self.iap_cookie:
            headers["Cookie"] = self.iap_cookie
            return headers
        token = self._get_iap_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers