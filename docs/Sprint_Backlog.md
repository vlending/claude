# 먹은대로 MVP 개발 백로그

**기간:** 4주 (2 x 2주 스프린트)
**목표:** 코어 기능 개발 + QA
**팀 구성 가정:** 백엔드 2명, 프론트엔드 2명, AI/ML 1명, 디자이너 1명

---

## Sprint 0: 사전 준비 (1주, 스프린트 1 시작 전)

### 인프라 & 개발 환경 세팅

| ID | 작업 | 담당 | 우선순위 | 예상 SP |
|----|------|------|---------|---------|
| S0-1 | AWS 계정 생성 + VPC/서브넷 구성 | DevOps | P0 | 3 |
| S0-2 | PostgreSQL RDS 인스턴스 생성 | Backend | P0 | 2 |
| S0-3 | S3 버킷 생성 (이미지 저장) | Backend | P0 | 1 |
| S0-4 | Docker 개발 환경 구성 (docker-compose) | Backend | P0 | 3 |
| S0-5 | GitHub 저장소 생성 + CI/CD 파이프라인 (기본) | DevOps | P0 | 5 |
| S0-6 | Anthropic API 키 발급 + 테스트 | AI/ML | P0 | 1 |
| S0-7 | React Native 프로젝트 초기화 (Expo) | Frontend | P0 | 2 |
| S0-8 | 디자인 시스템 기본 컴포넌트 라이브러리 선정 | Frontend | P1 | 1 |

**총 SP:** 18
**완료 기준:** 로컬 개발 환경에서 Hello World API + 앱 실행 성공

---

## Sprint 1: 온보딩 + 건강검진 + 기본 인증 (2주)

### 목표
- 사용자 가입/로그인 가능
- 건강 프로필 입력 가능
- 건강검진표 업로드 및 파싱 가능

---

### 백엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD (완료 조건) |
|----|------|---------|------|---------|----|----|
| BE-1.1 | DB 스키마 구현 | `users`, `health_checks` 테이블 생성 | Backend | P0 | 3 | 스키마 마이그레이션 성공, 샘플 데이터 삽입 가능 |
| BE-1.2 | 사용자 인증 API | POST /auth/register, /auth/login (JWT) | Backend | P0 | 5 | 회원가입 → 로그인 → 토큰 발급 성공 |
| BE-1.3 | 사용자 프로필 API | GET/PATCH /auth/me | Backend | P0 | 3 | 프로필 조회 및 수정 가능 |
| BE-1.4 | 건강검진 CRUD API | POST/GET/PATCH/DELETE /health-checks | Backend | P0 | 5 | 수동 입력 검진 데이터 저장 가능 |
| BE-1.5 | 이미지 업로드 (S3) | POST /files/upload-url (pre-signed URL) | Backend | P0 | 3 | 클라이언트에서 S3 직접 업로드 성공 |
| BE-1.6 | 건강검진 OCR 통합 | POST /health-checks/upload (Claude Vision API) | AI/ML | P0 | 8 | 검진표 이미지 → JSON 파싱 성공 (정확도 >80%) |
| BE-1.7 | 리스크 프로필 계산 로직 | 검진 수치 → risk_profile 자동 생성 | Backend | P0 | 5 | 혈압/혈당/지질 정상/경계/이상 분류 |

**백엔드 총 SP:** 32

---

### 프론트엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| FE-1.1 | 온보딩 화면 1: 건강 프로필 입력 | 성별, 나이대, 키/몸무게, 목표 선택 | Frontend | P0 | 5 | 입력 후 다음 단계 이동 |
| FE-1.2 | 온보딩 화면 2: 약물/알레르기 입력 | 체크박스 + 기타 입력란 | Frontend | P1 | 3 | 선택적 입력 후 스킵 가능 |
| FE-1.3 | 온보딩 화면 3: 건강검진 업로드 | 카메라/갤러리 선택 → S3 업로드 | Frontend | P0 | 5 | 이미지 업로드 후 로딩 → 파싱 결과 표시 |
| FE-1.4 | 건강검진 파싱 결과 확인/수정 | 추출된 수치 표시 + 수동 수정 가능 | Frontend | P0 | 5 | 수정 후 저장 성공 |
| FE-1.5 | 로그인/회원가입 화면 | 이메일/비밀번호 폼 + JWT 저장 | Frontend | P0 | 5 | 로그인 → 홈 화면 이동 |
| FE-1.6 | 토큰 관리 (AsyncStorage) | JWT 저장 및 자동 로그인 | Frontend | P0 | 3 | 앱 재실행 시 자동 로그인 |
| FE-1.7 | 공통 컴포넌트 | Button, Input, Card, Loading Spinner | Frontend | P1 | 3 | 재사용 가능한 컴포넌트 라이브러리 |

**프론트엔드 총 SP:** 29

---

### AI/ML 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| ML-1.1 | 건강검진 OCR 프롬프트 개발 | 검진표 파싱 프롬프트 작성 + 테스트 | AI/ML | P0 | 5 | 10개 샘플 검진표 파싱 정확도 >85% |
| ML-1.2 | 리스크 분류 로직 구현 | 검진 수치 → normal/borderline/high | AI/ML | P0 | 3 | 단위 테스트 통과 |

**AI/ML 총 SP:** 8

---

### 디자인 작업

| ID | 작업 | 담당 | 우선순위 | SP |
|----|------|------|---------|-----|
| DS-1.1 | 온보딩 화면 UI 디자인 (3개 화면) | Designer | P0 | 5 |
| DS-1.2 | 로그인/회원가입 화면 디자인 | Designer | P0 | 2 |
| DS-1.3 | 디자인 시스템 (색상, 타이포그래피, 아이콘) | Designer | P0 | 5 |

**디자인 총 SP:** 12

---

### Sprint 1 완료 기준 (Definition of Done)

- [ ] 사용자 회원가입 → 건강 프로필 입력 → 건강검진 업로드 → 파싱 완료까지 E2E 테스트 통과
- [ ] 10개 실제 검진표로 OCR 테스트 (정확도 >80%)
- [ ] 모든 API 엔드포인트 Postman 테스트 통과
- [ ] 앱에서 온보딩 완료 후 홈 화면 진입 가능

---

## Sprint 2: 식사 전/후 코칭 (2주)

### 목표
- 식사 전 사진 업로드 → RED/YELLOW/GREEN 판정 가능
- 식사 후 사진 업로드 → 자동 기록 가능
- 하루 요약 조회 가능

---

### 백엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| BE-2.1 | DB 스키마 구현 | `meals`, `daily_summaries` 테이블 | Backend | P0 | 2 | 스키마 마이그레이션 성공 |
| BE-2.2 | 식사 전 분석 API | POST /meals/pre-analyze | Backend | P0 | 8 | 이미지 → AI 분석 → 판정 결과 반환 |
| BE-2.3 | 식사 후 기록 API | POST /meals | Backend | P0 | 8 | 이미지 → 영양 성분 추정 → DB 저장 |
| BE-2.4 | 식사 조회 API | GET /meals (필터링, 페이지네이션) | Backend | P0 | 3 | 날짜 범위로 식사 목록 조회 |
| BE-2.5 | 일일 요약 API | GET /reports/daily/{date} | Backend | P0 | 5 | 하루 총 칼로리/영양 집계 |
| BE-2.6 | 일일 요약 자동 계산 | Meal 생성 시 daily_summaries 업데이트 | Backend | P0 | 5 | Meal 저장 시 자동 집계 |
| BE-2.7 | 레드라인 임계값 계산 | 사용자 리스크 프로필 → 개인화된 임계값 | Backend | P0 | 5 | 검진 이상 시 임계값 50% 하향 |

**백엔드 총 SP:** 36

---

### AI/ML 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| ML-2.1 | 식사 전 분석 프롬프트 개발 | 이미지 → 판정 + 이유 + 대안 | AI/ML | P0 | 8 | 20개 샘플 이미지 테스트 (판정 정확도 >85%) |
| ML-2.2 | 식사 후 기록 프롬프트 개발 | 이미지 → 영양 성분 JSON | AI/ML | P0 | 8 | 20개 샘플 이미지 (영양소 오차 ±15%) |
| ML-2.3 | 한식 음식 DB 구축 | 100개 주요 한식 메뉴 영양 데이터 | AI/ML | P1 | 5 | AI 프롬프트에 few-shot 예시로 활용 |
| ML-2.4 | 불확실성 처리 로직 | Confidence < 0.7 시 질문 생성 | AI/ML | P0 | 5 | Edge case 테스트 통과 |

**AI/ML 총 SP:** 26

---

### 프론트엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| FE-2.1 | 홈 화면 | 오늘 요약 (칼로리/나트륨/점수) + CTA 버튼 | Frontend | P0 | 5 | 일일 요약 데이터 표시 |
| FE-2.2 | 식사 전 카메라 화면 | 카메라 촬영 or 갤러리 선택 → 업로드 | Frontend | P0 | 5 | 사진 촬영 → S3 업로드 성공 |
| FE-2.3 | 식사 전 분석 중 로딩 | AI 분석 중 로딩 애니메이션 (3초) | Frontend | P1 | 2 | 로딩 → 결과 화면 전환 |
| FE-2.4 | 식사 전 판정 결과 화면 | RED/YELLOW/GREEN + 이유 + 대안 | Frontend | P0 | 8 | 스크롤 가능, 대안 메뉴 클릭 시 상세 |
| FE-2.5 | 식사 후 카메라 화면 | 카메라 촬영 → 업로드 | Frontend | P0 | 3 | 식사 전과 동일 컴포넌트 재사용 |
| FE-2.6 | 식사 후 기록 완료 화면 | 영양 성분 + 간단 피드백 | Frontend | P0 | 5 | 기록 후 홈으로 이동 |
| FE-2.7 | 식사 기록 리스트 화면 | 달력 뷰 + 일별 상세 | Frontend | P1 | 8 | 날짜 선택 → 식사 목록 표시 |
| FE-2.8 | AI 질문 모달 | Confidence 낮을 때 질문 팝업 | Frontend | P0 | 3 | 답변 선택 → 재분석 |

**프론트엔드 총 SP:** 39

---

### 디자인 작업

| ID | 작업 | 담당 | 우선순위 | SP |
|----|------|------|---------|-----|
| DS-2.1 | 홈 화면 디자인 | Designer | P0 | 3 |
| DS-2.2 | 식사 전 판정 결과 화면 (RED/YELLOW/GREEN 차별화) | Designer | P0 | 5 |
| DS-2.3 | 식사 후 기록 완료 화면 | Designer | P0 | 3 |
| DS-2.4 | 아이콘 디자인 (경고, 대안, 영양소 등) | Designer | P1 | 3 |

**디자인 총 SP:** 14

---

### Sprint 2 완료 기준

- [ ] 식사 전 사진 업로드 → 3초 내 판정 결과 표시
- [ ] 20개 샘플 음식 이미지 테스트 (판정 정확도 >85%)
- [ ] 식사 후 사진 업로드 → 자동 기록 → 하루 요약 업데이트
- [ ] 영양 성분 추정 오차 ±15% 이내 (10개 샘플)
- [ ] E2E 테스트: 하루 3끼 기록 → 일일 요약 정확

---

## Sprint 3: 게임화 + 리포트 (2주)

### 목표
- 스트릭, 배지, 포인트 시스템 구현
- 주간 리포트 자동 생성
- 푸시 알림 (일일 리포트)

---

### 백엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| BE-3.1 | DB 스키마 구현 | `user_gamification`, `weekly_reports`, `notifications` | Backend | P0 | 2 | 스키마 마이그레이션 |
| BE-3.2 | 스트릭 계산 로직 | Meal 생성 시 current_streak 업데이트 | Backend | P0 | 5 | 연속 기록 시 스트릭 증가 |
| BE-3.3 | 배지 시스템 | 조건 달성 시 badges 배열에 추가 | Backend | P0 | 5 | 스트릭 3/7/14일 배지 자동 부여 |
| BE-3.4 | 목표별 점수 계산 로직 | 일일 식사 → weight/bp/lipid/glucose/gerd 점수 (0~100) | Backend | P0 | 8 | 점수 산정 로직 단위 테스트 통과 |
| BE-3.5 | 주간 리포트 생성 API | POST /reports/weekly (수동 트리거) | Backend | P0 | 8 | 7일 데이터 → 리포트 생성 |
| BE-3.6 | 주간 리포트 조회 API | GET /reports/weekly, GET /reports/weekly/{week_start} | Backend | P0 | 3 | 리포트 조회 가능 |
| BE-3.7 | 크론 작업 (주간 리포트 자동 생성) | 매주 일요일 21시 자동 생성 | Backend | P1 | 5 | Cron 테스트 (수동 트리거) |
| BE-3.8 | 푸시 알림 API | POST /notifications (FCM 통합) | Backend | P1 | 5 | 테스트 푸시 전송 성공 |

**백엔드 총 SP:** 41

---

### AI/ML 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| ML-3.1 | 주간 리포트 프롬프트 개발 | 7일 데이터 → TOP3 문제/습관 + 미션 | AI/ML | P0 | 8 | 3개 샘플 사용자 리포트 생성 테스트 |
| ML-3.2 | 점수 산정 알고리즘 설계 | 목표별 점수 계산 공식 최적화 | AI/ML | P0 | 5 | 점수 로직 문서화 |

**AI/ML 총 SP:** 13

---

### 프론트엔드 작업

| ID | 작업 | 세부 사항 | 담당 | 우선순위 | SP | DoD |
|----|------|---------|------|---------|----|----|
| FE-3.1 | 홈 화면에 스트릭 표시 | "🔥 7일 연속 기록 중!" | Frontend | P0 | 2 | 스트릭 데이터 표시 |
| FE-3.2 | 배지 컬렉션 화면 | 획득한 배지 + 미획득 배지 (그레이) | Frontend | P1 | 5 | 배지 리스트 표시 |
| FE-3.3 | 주간 리포트 화면 | 점수 그래프 + TOP3 분석 + 다음 주 미션 | Frontend | P0 | 8 | 스크롤 가능, 그래프 라이브러리 통합 |
| FE-3.4 | 푸시 알림 설정 | FCM 토큰 등록 + 알림 권한 요청 | Frontend | P1 | 5 | 푸시 수신 테스트 |
| FE-3.5 | 일일 리포트 푸시 알림 | 21시에 "오늘 목표 달성도 75% 🎉" | Frontend | P1 | 3 | 푸시 클릭 → 앱 열림 |

**프론트엔드 총 SP:** 23

---

### 디자인 작업

| ID | 작업 | 담당 | 우선순위 | SP |
|----|------|------|---------|-----|
| DS-3.1 | 배지 아이콘 디자인 (10개) | Designer | P1 | 5 |
| DS-3.2 | 주간 리포트 UI 디자인 | Designer | P0 | 5 |
| DS-3.3 | 점수 그래프 디자인 (5개 목표별) | Designer | P0 | 3 |

**디자인 총 SP:** 13

---

### Sprint 3 완료 기준

- [ ] 연속 3일 기록 시 배지 획득 확인
- [ ] 주간 리포트 자동 생성 (일요일 21시)
- [ ] 주간 리포트 화면에서 점수 그래프 표시
- [ ] 푸시 알림 전송 성공 (일일 리포트)
- [ ] 3명 실사용자 1주일 테스트 → 리포트 정확도 확인

---

## Sprint 4: QA + 폴리싱 (2주)

### 목표
- 버그 수정 및 성능 최적화
- UI/UX 개선
- 클로즈 베타 준비

---

### 작업

| ID | 작업 | 담당 | 우선순위 | SP | DoD |
|----|------|------|---------|----|----|
| QA-4.1 | E2E 테스트 (전체 플로우) | QA | P0 | 8 | 회원가입 → 온보딩 → 3끼 기록 → 리포트 조회 |
| QA-4.2 | 이미지 인식 정확도 테스트 (100개 샘플) | AI/ML | P0 | 5 | 정확도 >85% 확인 |
| QA-4.3 | API 성능 테스트 | Backend | P1 | 5 | 응답 시간 <500ms (P95) |
| QA-4.4 | 보안 검토 (OWASP Top 10) | Backend | P0 | 5 | SQL Injection, XSS 방어 확인 |
| QA-4.5 | 접근성 검토 (폰트 크기, 색 대비) | Frontend | P1 | 3 | WCAG AA 기준 통과 |
| BE-4.1 | 에러 처리 개선 | Backend | P0 | 5 | 모든 API에 일관된 에러 응답 |
| FE-4.1 | 로딩 상태 개선 (Skeleton UI) | Frontend | P1 | 3 | 모든 비동기 작업에 로딩 표시 |
| FE-4.2 | 오프라인 모드 지원 (기본) | Frontend | P2 | 5 | 네트워크 끊김 시 안내 메시지 |
| DS-4.1 | UI 폴리싱 (여백, 애니메이션) | Designer | P1 | 5 | 디자이너 최종 검수 통과 |
| DOC-4.1 | API 문서화 (Swagger) | Backend | P1 | 3 | OpenAPI 스펙 최신화 |
| DOC-4.2 | 사용자 가이드 작성 | PM | P1 | 3 | 앱 내 튜토리얼 또는 도움말 |

**총 SP:** 50

---

### Sprint 4 완료 기준

- [ ] 100개 음식 이미지 테스트 (정확도 >85%)
- [ ] E2E 테스트 모든 시나리오 통과
- [ ] 보안 취약점 0건
- [ ] 성능 테스트 통과 (응답 시간 <500ms)
- [ ] 클로즈 베타 20명 초대 준비 완료

---

## 전체 일정 요약

| Sprint | 기간 | 핵심 목표 | 완료 기준 |
|--------|-----|---------|---------|
| **Sprint 0** | 1주 | 인프라 & 환경 세팅 | Hello World 앱 실행 |
| **Sprint 1** | 2주 | 온보딩 + 건강검진 | 검진표 파싱 성공 |
| **Sprint 2** | 2주 | 식사 전/후 코칭 | 판정 정확도 >85% |
| **Sprint 3** | 2주 | 게임화 + 리포트 | 주간 리포트 자동 생성 |
| **Sprint 4** | 2주 | QA + 폴리싱 | 클로즈 베타 준비 |

**총 기간:** 9주 (Sprint 0 포함)

---

## 리스크 관리

### 기술 리스크

| 리스크 | 확률 | 영향 | 완화 방안 |
|-------|-----|-----|---------|
| AI 이미지 인식 정확도 부족 | 중 | 높음 | 한식 데이터셋 자체 라벨링 (100장), Few-shot 프롬프트 개선 |
| 검진표 OCR 파싱 실패 | 중 | 중 | 수동 입력 폴백 옵션 제공, GPT-4 Vision 활용 |
| API 응답 시간 >3초 | 낮 | 중 | 이미지 크기 제한 (2MB), Claude API timeout 최적화 |
| S3 업로드 실패 | 낮 | 중 | 재시도 로직 (3회), 사용자 안내 메시지 |

### 일정 리스크

| 리스크 | 완화 방안 |
|-------|---------|
| AI 프롬프트 개발 지연 | Sprint 1부터 프롬프트 개발 시작 (병렬 작업) |
| 디자인 지연 | Sprint 0에 디자인 시스템 먼저 확정 |
| QA 병목 | Sprint 2부터 점진적 QA 진행 (일일 테스트) |

---

## 우선순위 정의

- **P0 (Must Have):** MVP 핵심 기능, 없으면 출시 불가
- **P1 (Should Have):** 중요하지만 v1.1로 연기 가능
- **P2 (Nice to Have):** 출시 후 추가 가능

---

## Story Points (SP) 가이드

- **1 SP:** 1~2시간 (단순 설정)
- **2 SP:** 반나절 (간단한 API)
- **3 SP:** 1일 (중간 복잡도 API)
- **5 SP:** 2~3일 (복잡한 기능)
- **8 SP:** 1주 (AI 프롬프트 개발, 복잡한 UI)
- **13 SP:** 1주 이상 (큰 작업, 분할 고려)

---

## 데일리 스탠드업 (Daily Standup) 템플릿

매일 아침 10시, 15분

**질문:**
1. 어제 뭐 했나?
2. 오늘 뭐 할 건가?
3. 블로커 있나?

**포맷 (Slack):**
```
[BE] 김개발
- 어제: BE-1.2 JWT 인증 API 완료
- 오늘: BE-1.3 프로필 API 작업
- 블로커: Redis 설정 필요 (DevOps 지원 요청)
```

---

## 스프린트 리뷰 & 회고 (Sprint Review & Retro)

### 스프린트 리뷰 (마지막 금요일, 1시간)
- 데모: 완료된 기능 시연
- 참석: 전체 팀 + 스테이크홀더

### 회고 (마지막 금요일, 30분)
- **Keep:** 잘한 것
- **Problem:** 문제점
- **Try:** 다음 스프린트 개선 사항

---

## 목표별 점수 산정 로직 (상세)

### 체중 점수 (Weight Score)

```python
def calculate_weight_score(daily_avg_kcal, user_target_kcal=1800):
    diff = abs(daily_avg_kcal - user_target_kcal)
    if diff <= 200:
        return 90 + (200 - diff) / 20  # 90~100점
    elif diff <= 400:
        return 70 + (400 - diff) / 10  # 70~89점
    elif diff <= 600:
        return 40 + (600 - diff) / 10  # 40~69점
    else:
        return max(0, 40 - (diff - 600) / 20)  # 0~39점
```

### 혈압 점수 (BP Score)

```python
def calculate_bp_score(daily_avg_sodium_mg, risk_level='normal'):
    # 임계값 설정
    if risk_level == 'high':
        threshold = 1500
    else:
        threshold = 2000

    if daily_avg_sodium_mg < threshold * 0.75:
        return 95
    elif daily_avg_sodium_mg < threshold:
        return 80
    elif daily_avg_sodium_mg < threshold * 1.5:
        return 50
    else:
        return max(0, 50 - (daily_avg_sodium_mg - threshold * 1.5) / 50)
```

### 지질 점수 (Lipid Score)

```python
def calculate_lipid_score(daily_avg_sat_fat_g, risk_level='normal'):
    if risk_level == 'high':
        threshold = 10
    else:
        threshold = 15

    if daily_avg_sat_fat_g < threshold * 0.7:
        return 95
    elif daily_avg_sat_fat_g < threshold:
        return 80
    elif daily_avg_sat_fat_g < threshold * 1.3:
        return 50
    else:
        return max(0, 50 - (daily_avg_sat_fat_g - threshold * 1.3) * 2)
```

### 혈당 점수 (Glucose Score)

```python
def calculate_glucose_score(daily_avg_sugar_g, risk_level='normal'):
    if risk_level == 'high':
        threshold = 20
    else:
        threshold = 30

    if daily_avg_sugar_g < threshold * 0.7:
        return 95
    elif daily_avg_sugar_g < threshold:
        return 80
    elif daily_avg_sugar_g < threshold * 1.5:
        return 50
    else:
        return max(0, 50 - (daily_avg_sugar_g - threshold * 1.5))
```

### 위장 점수 (GERD Score)

```python
def calculate_gerd_score(late_night_meals, daily_avg_caffeine_mg):
    score = 100

    # 야식 패널티 (21시 이후)
    score -= late_night_meals * 15  # 1회당 -15점

    # 카페인 패널티
    if daily_avg_caffeine_mg > 500:
        score -= 30
    elif daily_avg_caffeine_mg > 300:
        score -= 15

    return max(0, score)
```

---

## 배지 시스템 (Badge System)

### 배지 목록

| 배지 ID | 이름 | 조건 | 포인트 |
|--------|-----|-----|-------|
| `streak_3` | 🔥 3일 연속 | 스트릭 3일 | 10 |
| `streak_7` | 🔥🔥 1주 완주 | 스트릭 7일 | 30 |
| `streak_14` | 🔥🔥🔥 2주 마스터 | 스트릭 14일 | 50 |
| `streak_30` | 👑 한 달 챔피언 | 스트릭 30일 | 100 |
| `sodium_master` | 🧂 나트륨 킬러 | 나트륨 800mg 이하 주 5회 | 20 |
| `no_late_night` | 🌙 야식 제로 | 야식 0회 (1주) | 20 |
| `green_week` | 🟢 완벽한 한 주 | 일주일 모두 GREEN 판정 | 50 |
| `red_avoid` | 🚫 레드 회피 | RED 판정 음식 먹지 않음 (5회) | 15 |
| `veggie_lover` | 🥗 채소 러버 | 식이섬유 25g 이상 (주 5회) | 20 |
| `pre_meal_pro` | 📸 식전 프로 | 식전 사진 업로드 주 10회 | 15 |

---

## 클로즈 베타 계획

### 목표
- **참여자:** 20명
- **기간:** 2주
- **목적:** 실사용 피드백 수집, 버그 발견, AI 정확도 검증

### 선정 기준
- 건강검진에서 이상 소견 있는 사람 (고혈압, 고지혈증, 당뇨 전단계)
- 역류성 식도염 또는 위염 진단 받은 사람
- 스마트폰 사용에 익숙한 30~50대

### 수집 데이터
- [ ] AI 판정 정확도 (사용자 피드백)
- [ ] 영양 성분 추정 오차 (실제 영양 성분과 비교)
- [ ] 사용자 이탈 시점 (어느 단계에서 그만두는지)
- [ ] 가장 유용한 기능 / 불필요한 기능
- [ ] 톤에 대한 반응 (경고성 톤이 스트레스인지 동기부여인지)

### 피드백 수집 방법
- 앱 내 피드백 버튼
- 주 1회 설문 (Google Forms)
- 1:1 인터뷰 (5명, 30분)

---

## 출시 체크리스트

### 기술
- [ ] 모든 API 엔드포인트 테스트 통과
- [ ] 이미지 인식 정확도 >85%
- [ ] 영양 성분 추정 오차 ±15% 이내
- [ ] E2E 테스트 모든 시나리오 통과
- [ ] 보안 취약점 0건
- [ ] 성능 테스트 통과 (응답 시간 <500ms)

### 법률/규제
- [ ] 개인정보 처리방침 작성
- [ ] 이용약관 작성
- [ ] "의료기기 아님" 면책 조항 포함
- [ ] 건강 데이터 암호화 확인

### 운영
- [ ] 모니터링 대시보드 (Grafana) 구축
- [ ] 에러 알림 (Slack 통합) 설정
- [ ] 백업 스케줄 (일 1회) 설정
- [ ] 고객 지원 이메일/채널 준비

### 마케팅
- [ ] 앱스토어 설명 작성 (한국어/영어)
- [ ] 스크린샷 5개 준비
- [ ] 랜딩 페이지 제작 (선택)
- [ ] 초기 사용자 확보 계획 (SNS, 커뮤니티)

---

**문서 끝**
