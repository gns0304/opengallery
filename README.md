## 오픈갤러리 기술과제 개발 작업 내역

### 프로젝트 개요
- Djagno 기반 풀스택 웹 서비스 구현
- 대고객 페이지, 작가 페이지, 관리자 페이지 구현
- [기술 스택]
  - Python, Django(5.2.5), Bootstrap, JavaScript
  - AWS Lightsail Instance, Lightsail RDS(PostgreSQL), S3
  - Docker Compose + Nginx + Gunicorn + Certbot 으로 배포
- [배포 엔드포인트]
  - https://opengallery.hanjihoon.com

### 개발 일지 및 주요 반영 사항

#### 8월 12일 (화) – 프로젝트 세팅 및 모델링

##### [개발 사항]

- Django 프로젝트 및 앱 초기화
- accounts, artist, gallery, admin_panel 앱 생성
- Custom User 모델 구현
- ArtistProfile, ArtistApplication 모델 분리 설계
    - 작가와 관련된 정보는 ArtistProfile(승인된 작가의 프로필)과 ArtistApplication(작가 등록 신청 정보)으로 구분
    - 사용자가 신청서를 제출 후 관리자가 승인 시 별도의 프로필 생성 흐름을 구현
    - 이를 통하여 관리자 도메인에서 별도의 감사 기록을 유지할 수 있도록 구현
    - 추후 작가 프로필 이관 시 발생할 수 있는 경합 문제 방지를 위해 상태 플래그 추가
- 전화번호 RegexValidator, 가격·사이즈 제약조건 설정
- 작품 관련 Artwork 모델 및 전시 위한 Exhibition 모델 구현
  - 작품 이미지 업로드를 위한 업로드 경로 함수 구현
  - 최신 작품 조회 최적화를 위한 작가 및 시작일의 복합 인덱스 구현


##### [세부 사항]

- 단일 사용자 계정의 중복 신청에 대한 고민에 대해서
  - UniqueConstraint를 사용하여 동일 사용자의 복수 신청 제한
  - 반려된 경우에 신청 가능토록 설계
  - 이후 프로필 일괄 승인 시 발생할 수 있는 오류 사항에 대해 PROCESSING 및 ERROR 상태를 추가
- 작가 프로필과 유저 모델 통합에 대한 고민에 대해서
  - 유저 모델의 차후 확장(소셜 로그인 등)을 위해서 별도의 작가 프로필을 유지하는 것으로 선택
  - 작가 신청 시 프로필 생성이 아닌 신청서 생성으로 설계
  - 이는 관리자 도메인에서 신청서 관리 및 승인 후 프로필 생성 흐름을 구현하여 신청 내역을 보존할 수 있게 끔 설계

#### 8월 13일 (수) – 사용자 인증 및 작가 등록 신청 기능 구현

##### [개발 사항]

- 이메일 기반 로그인/회원가입 구현
  - SignupForm, EmailAuthenticationForm 작성
  - 로그인 상태에서 접근을 막기 위한 RedirectIfAuthenticatedMixin 적용
  - 로그인/로그아웃 메시지 처리 및 UX 개선
- ArtistApplicationCreateView 구현 (승인 전 사용자만 신청 가능)
  - 중복 신청 방지 로직
  - Bootstrap 기반 폼 검증 및 에러 메시지 처리
- 베이스 템플릿 및 헤더(navbar) 공통 컴포넌트 구축
  - 사용자 권한별 메뉴 노출 제어 (비로그인/작가/관리자 구분)
  - 반응형 네비게이션 구현 (모바일 드롭다운/데스크탑 Navbar)

##### [세부 사항]

- 이메일 기반으로 사용자 계정 구현
  - Django의 기본 User 모델을 확장
- 작가 등록 신청 페이지 구현
  - ArtistApplicationCreateView를 개발 (LoginRequiredMixin 사용하여 로그인 사용자만 신청 가능토록 처리)
  - dispatch 단계에서 현재 사용자 계정에 ArtistProfile이 존재하고 승인되었다면 메시지를 띄우고 리다이렉트
  - PENDING/PROCESSING/ERROR 상태 신청이 이미 있는 경우 메시지와 함께 메인으로 리다이렉트시켜 중복 신청을 방지
  - 모델에 건 UniqueConstraint와 중복으로 예외 처리

#### 8월 14일 (목) – 관리자 기능 개발 (승인/반려 처리, 통계)

##### [개발 사항]
- AdminOnlyMixin 적용, 관리자 전용 ApplicationListView 구현
  - 작가 신청 내역 조회 페이지 구현 (테이블/체크박스 선택)
  - 일괄 승인/반려 처리 로직 구현 (process_multiple_approve/reject)
  - 승인 시 ArtistProfile 자동 이관 및 상태 갱신
  - 처리 결과 성공/스킵/실패 카운트 및 메시지 반환
  - 예외 처리: 잘못된 ID, 중복 처리, 알 수 없는 오류 메시지 출력
  - status 필드 확장 (PROCESSING, ERROR 추가)
  - last_error_message 필드 도입 (에러 원인 기록)

##### [세부 사항]

- 작가 신청 승인/반려 기능 구현
  - 다중 처리 위하여 ApplicationMultipleProcessView 구현
  - 여러 건의 신청을 어떻게 효율적으로 처리할 것인가에 대한 이슈 발생
    - 작가 지원서의 데이터를 작가 프로필로 이관하는 작업에서 원자성 있는 처리가 중요하다고 판단
    - 여러 관리자가 동시에 프로필 이관 시 프로필이 중복 생성되는 이슈 등이 발생할 수 있다 판단
    - 혹은 일괄 작업 시에도 마찬가지로 프로필 중복 생성에 대한 이슈가 발생할 수 있을 것으로 봄
    - select_for_update로 관리자 동시 승인 방지
    - atomic 트랜잭션으로 프로필 이관 작업을 원자적으로 처리
      - 작업 중인 신청서의 상태를 PROCESSING으로 변경
      - 프로필 이관 작업이 성공적으로 완료되면 신청서 상태를 APPROVED
    - IntegrityError 및 일반 예외 발생 상태와 에러 메시지 저장
    - 처리 결과를 APPROVE/SKIPPED/FAILED로 구분해 반환

#### 8월 15일 (금) – 작가 공개 목록 및 검색 기능 구현

##### [개발 사항]

- 작가 신청 내역 검색 기능 구현 및 페이지네이션 적용
- ApprovedArtistRequiredMixin 구현
  - 승인된 작가 전용 접근 제어 믹스인 구현
- Artwork와 Exhibition 리스트뷰 구현
  - 전시 날짜 검증 및 작품 선택 검증 로직 구현
  - 가격 입력에 대해서 콤마를 삽입하는 포맷팅 구현
  - 작가 관리 페이지 구현
- 관리자 작가 통계 페이지 구현
    - 작품 개수, 평균 가격, 전시 수, 최근 활동일, 가격 범위 등 집계

##### [세부 사항]
- 작가 검색 관련
  - 이름, 이메일, 연락처는 __icontains로 부분 일치 검색을 구현
- 통계 페이지 구현
  - N+1 문제를 최소화 하기 위하여 통계 데이터 annotate을 통해 단일 JOIN 쿼리로 일괄 조회

#### 8월 16일 (토) – 작품 및 작가 목록 페이지 구현

##### [개발 사항]

- 작품 목록(ArtworkListView) 검색 기능 추가
  - 제목, 가격범위, 호수 범위 포함 AND 검색
- 작가 목록(ArtistListView) 검색 기능 추가
  - 이름, 이메일, 연락처, 생년월일 포함 AND 검색
- 페이지네이션 및 검색 파라미터 유지 기능 구현
- 최신 작품 이미지 썸네일을 작가 목록에 표시하도록 annotate 추가

##### [세부 사항]

- 최신 작품 이미지 썸네일을 작가 목록에 표시하기 위하여
  - 해당 작가가 등록한 작품 중 가장 최신 작품 썸네일을 사용
  - 존재하지 않을 시 지속적으로 그 다음 최신 작품 썸네일을 탐색
  - 구현은 Subquery를 사용한 쿼리로 해결
  - 최신 등록 작품의 이미지 가지고 오는 Subquery를 annotate로 추가

#### 8월 17일 (일) – 배포

##### [개발 사항]

- AWS Lightsail 서버에 Django 애플리케이션 배포
- Docker Compose를 이용한 컨테이너화
- Nginx를 Reverse Proxy로 설정
- Certbot을 이용한 SSL 인증서 발급 및 HTTPS 적용
- Lightsail RDS(PostgreSQL) 데이터베이스 연결
- 정적 파일 및 미디어 파일 S3로 이전
- 도메인 연결 및 HTTPS 적용
- 배포 후 CSRF 인증 문제 해결
  - CSRF_TRUSTED_ORIGINS 설정 추가
  - HTTPS 헤더 인식 설정

##### [세부 사항]

- RDS 연결 시 발생한 문제 해결
  - 비밀번호 오류 및 DB 이름 오류 수정
  - .env.prod 파일에서 올바른 DB_NAME, DB_USER, DB_PASSWORD 설정
- static 파일 처리 문제 해결
  - collectstatic 명령어 실행 및 Nginx 설정 수정
  - dockerignore 파일 수정으로 static/ 폴더 포함
- 로그인 시 403 CSRF verification failed
  - HTTPS 환경에서 CSRF_TRUSTED_ORIGINS 설정 추가
    - settings.py에 ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SECURE_PROXY_SSL_HEADER 설정 추가
    - Nginx에서 proxy_set_header X-Forwarded-Proto https; 추가
