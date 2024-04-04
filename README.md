# CSI_Group_Project
스파르타 AI 6기 조별 프로젝트 + 공부 공유 커뮤니티
# 프로젝트 소개
각자 작성한 TIL을 공유, 작성 횟수에 따른 리더보드 내 순위 나열
# 개발 기간
* 2024.04.01일 - 2024.04.05일
## 멤버 구성
* 양승조(팀원) - 메인화면 구현, navbar,footer 구현, 게시글(Create, Read) 기능, html 리팩토링, 전반적인 css 작업
* 이원도(팀원) - 메인화면 구현, 게시글(Create, Read, Update, Delte) 기능, 로그인/회원가입 구현, 게시물 내 좋아요 count 구현, 전체 코드 리팩토링, Color CSS 통합
* 이혜민(팀장) - TIL 목록 구현
* 임현경(팀원) - 로그인/회원가입 구현, 마이페이지 구현, 세션 적용
* 현유경(팀원) - 리더보드 목록 구현
## 개발 환경
* HTML
* CSS
* python : Flask
* DB : SQLite

# 주요 기능
**로그인**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(Login))
  * DB값 검증
  * 로그인 시 세션(Session) 생성
  * 회원가입창으로 이동

**회원가입**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(Register))
  * ID,PW 규칙(길이제한, 영문,숫자,특수문자 포함) 체크
  * ID 중복 체크
  * PW 암호화(SHA-256)

**네이게이션 바**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(Nav-bar))
  * Home(Main)으로 이동
  * TIL 전체 리스트 조회
  * Leaderboard 이동

**My 메뉴**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(Nav-bar)#%EF%B8%8Fmy-%EB%A9%94%EB%89%B4)
  * 내 정보 확인
  * 내가 쓴 TIL목록
  * TIL 새로 작성
  * 로그아웃
  
**메인**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/Main-%ED%99%94%EB%A9%B4-%EA%B5%AC%EC%84%B1)
  * 가장 최신 TIL 3개 표시
  * TIL box 애니메이션 효과(CSS)
    * 앞면 - 썸네일, 제목
    * 뒷면 - 작성자,좋아요 수, 작성일자, 게시물 링크

**TIL_LIST**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(TIL_LIST))
  * 전체 TIL을 조회
  * user_id를 통해 특정 조회
  * 페이지네이션 

**Leaderboard**  📎[Wiki](https://github.com/luna-negra/csi_group_project/wiki/%EC%A3%BC%EC%9A%94-%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C(Leaderboard))
  * 연속일자로 등록한 유저순으로 순위 표시
  * 페이지네이션
